#!/usr/bin/env python3
"""
EDB 通告智能分析系統 — 爬蟲及 LLM 分析管線 v1.0.0
EDB Circular Scraper + gpt-5-nano Analyzer

用法 / Usage:
  python3 edb_scraper.py --days 30 --output ./circulars.json [-v]
  python3 edb_scraper.py --days 365 --output ./circulars.json -v
  python3 edb_scraper.py --school-year --output ./circulars.json -v
  python3 edb_scraper.py --days 7  --output ./circulars.json --dry-run
  python3 edb_scraper.py --llm-only --output ./circulars.json

參數 / Arguments:
  --days N         抓取最近 N 天通告（預設 30；最大建議 365）
  --school-year    抓取本學年通告（由9月1日起至今，覆蓋完整學年）
                   與 --days 互斥，--school-year 優先
  --output PATH    輸出 circulars.json 路徑（必須）
  --llm-only       跳過爬取，只重新分析已有 PDF 快取
  --model MODEL    LLM 模型（預設 gpt-5-nano）
  --dry-run        只爬取元數據，不呼叫 LLM（網絡測試用）
  -v / --verbose   詳細輸出

環境變數 / Environment:
  OPENAI_API_KEY  OpenAI API 金鑰（必須，--dry-run 除外）

重要規則 / Key rules (DO NOT CHANGE):
  - LLM model : gpt-5-nano (可 override 但預設不變)
  - temperature: 1  ← 固定，不可更改
  - output format: json_schema Structured Output
  - --llm-only 必須搭配 --output
  - --school-year 學年由每年9月1日起計（如9月前則取上一年9月1日）
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ── optional deps ────────────────────────────────────────────────────────────
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  Missing: requests + beautifulsoup4")
    print("   pip install requests beautifulsoup4")

try:
    import fitz  # PyMuPDF — fast, no pdfminer DEBUG log flood
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️  Missing: PyMuPDF — PDF text extraction disabled")
    print("   pip install PyMuPDF")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  Missing: openai — LLM analysis disabled")
    print("   pip install openai")

# =============================================================================
# CONFIGURATION
# =============================================================================

EDB_BASE        = "https://applications.edb.gov.hk"
EDB_LIST_URL    = f"{EDB_BASE}/circular/circular.aspx?langno=2"   # 繁體中文版
REQUEST_DELAY   = 1.5    # seconds — be polite to the server
PDF_MAX_PAGES   = 25     # max pages per PDF to extract
PDF_MAX_CHARS   = 8000   # cap PDF text sent to LLM
CACHE_DIR       = Path(".edb_cache")

# LLM — ⚠️ FIXED RULES:
LLM_MODEL_DEFAULT = "gpt-5-nano"
LLM_TEMPERATURE   = 1     # DO NOT CHANGE — project spec rule

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}

# =============================================================================
# LLM JSON SCHEMA  (gpt-5-nano Structured Output / strict mode)
# =============================================================================

_ROLE_OBJ = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "r":    {"type": "boolean"},
        "pts":  {"type": "array", "items": {"type": "string"}},
        "acts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["r", "pts", "acts"],
}

CIRCULAR_SCHEMA = {
    "name":   "circular_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "impact", "compliance", "urgency", "scope",
            "topics", "tags", "summary",
            "grant_info", "roles", "deadlines", "actions", "diff",
        ],
        "properties": {
            "impact":     {"type": "string", "enum": ["high", "mid", "low"]},
            "compliance": {"type": "string", "enum": ["mandatory", "recommended", "informational"]},
            "urgency":    {"type": "string", "enum": ["immediate", "high", "medium", "low"]},
            "scope":      {"type": "string", "enum": ["pri", "sec", "both_sec_pri", "spe", "kgn", "all"]},
            "topics": {
                "type": "array",
                "items": {"type": "string", "enum": [
                    "curriculum", "student", "finance", "hr",
                    "it", "activity", "exam", "safety", "procurement",
                ]},
            },
            "tags": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"},
            "grant_info": {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "amount_hkd", "amount_label", "resource_value_hkd", "note"],
                "properties": {
                    "type":               {"type": "string", "enum": ["applicable", "resource", "none"]},
                    "amount_hkd":         {"anyOf": [{"type": "number"}, {"type": "null"}]},
                    "amount_label":       {"anyOf": [{"type": "string"}, {"type": "null"}]},
                    "resource_value_hkd": {"anyOf": [{"type": "number"}, {"type": "null"}]},
                    "note":               {"type": "string"},
                },
            },
            "roles": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "principal", "vice_principal", "department_head",
                    "teacher", "eo_admin", "supplier",
                ],
                "properties": {
                    "principal":       _ROLE_OBJ,
                    "vice_principal":  _ROLE_OBJ,
                    "department_head": _ROLE_OBJ,
                    "teacher":         _ROLE_OBJ,
                    "eo_admin":        _ROLE_OBJ,
                    "supplier":        _ROLE_OBJ,
                },
            },
            "deadlines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["date", "desc", "type", "roles", "label"],
                    "properties": {
                        "date":  {"type": "string"},
                        "desc":  {"type": "string"},
                        "type":  {"type": "string", "enum": [
                            "apply_deadline", "submission_deadline", "awareness_deadline",
                        ]},
                        "roles": {"type": "array", "items": {"type": "string"}},
                        "label": {"type": "string"},
                    },
                },
            },
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["text", "role", "dl", "note"],
                    "properties": {
                        "text": {"type": "string"},
                        "role": {"type": "string"},
                        "dl":   {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "note": {"type": "string"},
                    },
                },
            },
            "diff": {
                "anyOf": [
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["summary", "changes"],
                        "properties": {
                            "summary": {"type": "string"},
                            "changes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["type", "field", "old", "new"],
                                    "properties": {
                                        "type":  {"type": "string", "enum": ["add", "mod", "del"]},
                                        "field": {"type": "string"},
                                        "old":   {"type": "string"},
                                        "new":   {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    {"type": "null"},
                ],
            },
        },
    },
}

# =============================================================================
# LLM SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """你是一個香港教育局（EDB）通告分析專家，服務對象包括學校校長、副校長、科主任、教師、行政主任和供應商。

你的任務是閱讀 EDB 通告全文，提取結構化資訊，以 JSON 格式輸出分析結果。

━━━ 分析標準 ━━━

impact（影響程度）：
  high  — 必須全校配合、涉及龐大資金（>$100,000）、違規有嚴重後果、截止日期緊迫
  mid   — 影響部分教職員、涉及中等資金、需提交文件報告
  low   — 純資訊、無需具體行動、影響範圍窄

compliance（行動要求）：
  mandatory     — 通告明確要求必須執行（"須"、"必須"、"強制"、"不得"）
  recommended   — 建議但不強制（"建議"、"宜"、"可考慮"）
  informational — 純參考（"知悉"、"參考"、"公布"）

scope（學校類別）：
  both_sec_pri — 中小學
  sec          — 中學
  pri          — 小學
  spe          — 特殊學校
  kgn          — 幼稚園
  all          — 所有學校（含幼稚園、特殊）

grant_info：
  applicable         — 學校可直接申請的撥款，amount_hkd 填數字（港元）
  resource           — 政府提供但非直接申請（培訓、設備等），resource_value_hkd 估值
  none               — 無資助，amount_hkd / amount_label / resource_value_hkd 填 null

roles（每角色分析）：
  r    — 此通告是否與該角色相關（true/false）
  pts  — 重點事項，最多 3 項中文短句
  acts — 具體行動，最多 3 項（如無需行動則為空數組）
  角色清單：principal, vice_principal, department_head, teacher, eo_admin, supplier

deadlines（截止日期）：
  apply_deadline      — 申請撥款/服務的截止
  submission_deadline — 提交文件/報告的截止
  awareness_deadline  — 知悉/生效日期
  日期格式：YYYY-MM-DD

actions（具體行動步驟）：
  按時間先後排列，role 欄只用：principal, vice_principal, department_head, teacher, eo_admin, supplier
  dl 填 YYYY-MM-DD 或 null

diff（版本比較）：
  如通告標題或內容含「(修訂)」「更新」「修改」「updated」「revised」等，分析主要變更
  否則返回 null

━━━ 輸出注意 ━━━
1. 日期格式必須為 YYYY-MM-DD
2. 金額單位為港元（HKD），只填數字不加逗號
3. tags 最多 5 個，用 2-6 字中文描述
4. summary 詳細中文摘要 300-600 字，包括背景、主要要求、注意事項
5. 如無截止日期，deadlines 為空數組 []
6. 如無撥款，grant_info.type = "none"，其餘欄填 null / ""
"""

# =============================================================================
# SCRAPER
# =============================================================================

class EDBScraper:
    """Scrapes EDB circular listing and detail pages using ASP.NET ViewState."""

    def __init__(self, verbose: bool = False):
        if not HAS_REQUESTS:
            raise RuntimeError("requests + beautifulsoup4 required")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.verbose = verbose
        self.log = logging.getLogger("Scraper")
        CACHE_DIR.mkdir(exist_ok=True)

    # ── HTTP helpers ────────────────────────────────────────────────────────

    def _fetch(self, url: str, data: dict = None) -> Optional["BeautifulSoup"]:
        """GET or POST a page with retry (3×). Returns BeautifulSoup or None."""
        for attempt in range(3):
            try:
                if data:
                    resp = self.session.post(url, data=data, timeout=30)
                else:
                    resp = self.session.get(url, timeout=30)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or "utf-8"
                return BeautifulSoup(resp.text, "html.parser")
            except Exception as exc:
                self.log.warning(f"  attempt {attempt+1}/3 failed ({url}): {exc}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return None

    def _viewstate(self, soup: "BeautifulSoup") -> dict:
        """
        Extract ASP.NET hidden form fields by NAME (positional-safe).
        Returns dict of field_name → value.
        """
        fields = {}
        for name in [
            "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION",
            "__EVENTTARGET", "__EVENTARGUMENT",
        ]:
            el = soup.find("input", {"name": name})
            if el:
                fields[name] = el.get("value", "")
        return fields

    # ── Listing page ─────────────────────────────────────────────────────────

    def get_circular_list(self, days: int = 30, date_from: str = None) -> list:
        """
        Fetch EDB circular listing.

        Args:
            days:       Number of past days to fetch (used when date_from is None).
            date_from:  Explicit start date in DD/MM/YYYY format (overrides days).
                        Use for --school-year mode or any fixed start date.

        Returns list of dicts: {number, title, date, type, detail_url, pdf_urls}
        """
        self.log.info(f"[Step 1] GET listing page: {EDB_LIST_URL}")
        soup = self._fetch(EDB_LIST_URL)
        if not soup:
            self.log.error("Failed to load listing page")
            return []

        vs = self._viewstate(soup)
        today  = datetime.now().strftime("%d/%m/%Y")
        if date_from:
            cutoff = date_from
        else:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%d/%m/%Y")

        # ASP.NET POST — field names verified from live page source (2026-03-10)
        # PlaceholderID = MainContentPlaceHolder  (NOT ContentPlaceHolder1)
        # Date fields   = txtPeriodFrom / txtPeriodTo  (NOT txtFromDate/txtToDate)
        # Search button = btnSearch2  (triggered by JS in the page)
        # Tab selection = lbltab_circular → value '通告'
        post_data = {
            **vs,
            "__EVENTTARGET":  "",
            "__EVENTARGUMENT": "",
            "ctl00$currentSection": "2",
            # Select the "Circular" tab (not "Form" tab)
            "ctl00$MainContentPlaceHolder$lbltab_circular": "通告",
            # Filters — all school types, all circular types
            "ctl00$MainContentPlaceHolder$ddlSchoolType2":  "",
            "ctl00$MainContentPlaceHolder$ddlCircularType": "",
            # Date range filter
            "ctl00$MainContentPlaceHolder$txtPeriodFrom":   cutoff,
            "ctl00$MainContentPlaceHolder$txtPeriodTo":     today,
            # Search button (btnSearch2 matches JS click handler in page)
            "ctl00$MainContentPlaceHolder$btnSearch2":      "搜尋",
        }

        label = f"school-year from {cutoff}" if date_from else f"past {days} days: {cutoff}"
        self.log.info(f"[Step 2] POST search ({label} – {today})")
        time.sleep(REQUEST_DELAY)
        soup = self._fetch(EDB_LIST_URL, post_data)
        if not soup:
            self.log.error("POST search failed")
            return []

        return self._parse_list(soup)

    def _parse_list(self, soup: "BeautifulSoup") -> list:
        """
        Parse circular listing.
        Structure verified from live EDB website (2026-03-10):

          Each circular = <tr> with 3× <td class="circularResultRow circulartRow">
            Cell[0]  日期     — <div class="table_text_mobile_app"> → "日期DD/MM/YYYY"
            Cell[1]  主題     — <div class="table_text_mobile_app">
                                  direct text nodes      → title
                                  <div class="circulars_result_remark"> → circular number
                                  <div> (no class)       → school types (ignored)
            Cell[2]  語言下載  — <a href="../circular/upload/EDBCM/EDBCMyyNNNC.pdf">繁體中文</a>
                                  3 PDFs: C=繁中, E=英文, S=簡體 (prefer C for LLM)

        No per-circular detail page links exist on the listing page.
        """
        circulars = []

        for row in soup.find_all("tr"):
            cells = row.find_all("td", class_="circularResultRow")
            if len(cells) < 2:
                continue

            # ── Circular number (from div.circulars_result_remark in Cell[1]) ──
            remark = cells[1].find("div", class_="circulars_result_remark")
            if not remark:
                continue
            num_match = re.search(r"EDB(?:CM|CL)\d{3}/\d{4}", remark.get_text())
            if not num_match:
                continue
            num_text = num_match.group(0)

            # ── Title (direct text nodes of table_text_mobile_app, before subdiv) ──
            content_div = cells[1].find("div", class_="table_text_mobile_app")
            if content_div:
                # Only direct (non-recursive) string children
                title_parts = [
                    s.strip()
                    for s in content_div.strings
                    if s.parent == content_div and s.strip()
                ]
                title = re.sub(r"\s+", " ", " ".join(title_parts)).strip()
                # Strip summary text appended after "摘要" or "摘要：" (EDB page includes it as direct text node)
                title = re.sub(r"\s*摘要[：:].*$", "", title, flags=re.DOTALL).strip()
                # Remove any leaked remark brackets just in case
                title = re.sub(r"\(通告編號[：:][^\)]*\)", "", title).strip()
            else:
                title = num_text

            # ── Date (strip "日期" label prefix) ──
            date_div = cells[0].find("div", class_="table_text_mobile_app")
            date_raw = date_div.get_text(strip=True) if date_div else cells[0].get_text(strip=True)
            date_raw = re.sub(r"^日期", "", date_raw).strip()
            date_iso = _parse_date(date_raw)

            # ── PDF links (Cell[2]) — prefer C.pdf (繁中) for LLM text extraction ──
            pdf_urls = []
            if len(cells) > 2:
                for a in cells[2].find_all("a"):
                    href = a.get("href", "")
                    if href:
                        pdf_urls.append(_abs_url(href))
            # Sort: C (繁中) first, E (英文) second, S (簡體) last
            def _pdf_rank(u: str) -> int:
                u_up = u.upper()
                if u_up.endswith("C.PDF"):
                    return 0
                if u_up.endswith("E.PDF"):
                    return 1
                return 2
            pdf_urls.sort(key=_pdf_rank)

            circ_type = "EDBCM" if "CM" in num_text else "EDBCL"
            entry = {
                "number":     num_text,
                "title":      title,
                "date":       date_iso,
                "type":       circ_type,
                "detail_url": None,   # No per-circular detail links on listing page
                "pdf_urls":   pdf_urls,
                "official":   "",
                "pdf_text":   "",
            }
            circulars.append(entry)
            if self.verbose:
                self.log.debug(f"  {num_text} — {title[:60]}")

        self.log.info(f"  Parsed {len(circulars)} circulars from listing")
        return circulars

    # ── Detail page ──────────────────────────────────────────────────────────

    def enrich_detail(self, circ: dict) -> dict:
        """
        Fetch the detail page for a circular to get official summary text
        and any additional PDF links not found in the listing.
        Mutates and returns circ.
        """
        if not circ.get("detail_url"):
            return circ

        self.log.info(f"  Fetching detail: {circ['detail_url']}")
        time.sleep(REQUEST_DELAY)
        soup = self._fetch(circ["detail_url"])
        if not soup:
            return circ

        # Extract official summary text — POSITIONAL:
        # Look for the longest paragraph block that contains Chinese text
        # and mentions 教育局 or uses the circular number.
        best_text = ""
        for el in soup.find_all(["p", "div", "td"]):
            text = el.get_text(strip=True)
            if (
                len(text) > 80
                and len(text) > len(best_text)
                and any(c > "\u4e00" for c in text)   # has Chinese chars
                and el.find_parent("table") is not None
                    or len(text) > 200
            ):
                best_text = text
        circ["official"] = best_text[:1000]

        # Collect additional PDF links
        existing_pdfs = set(circ.get("pdf_urls", []))
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if ".pdf" in href.lower():
                url = _abs_url(href)
                if url and url not in existing_pdfs:
                    circ["pdf_urls"].append(url)
                    existing_pdfs.add(url)

        return circ

    # ── PDF download ─────────────────────────────────────────────────────────

    def download_pdf(self, url: str, circular_num: str) -> Optional[Path]:
        """Download PDF and cache locally. Returns cached path or None."""
        safe = re.sub(r"[^\w\-]", "_", circular_num)
        path = CACHE_DIR / f"{safe}.pdf"

        if path.exists():
            self.log.debug(f"  PDF cached: {path}")
            return path

        self.log.info(f"  Downloading PDF: {url}")
        time.sleep(REQUEST_DELAY)
        try:
            resp = self.session.get(url, timeout=60, stream=True)
            resp.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(8192):
                    fh.write(chunk)
            kb = path.stat().st_size / 1024
            self.log.info(f"  Saved {safe}.pdf ({kb:.0f}KB)")
            return path
        except Exception as exc:
            self.log.warning(f"  PDF download failed: {exc}")
            return None


# =============================================================================
# PDF EXTRACTOR
# =============================================================================

def extract_pdf_text(pdf_path: Path, max_pages: int = PDF_MAX_PAGES, timeout_secs: int = 10) -> str:
    """Extract text from a PDF using PyMuPDF (fitz).

    PyMuPDF uses MuPDF C library — fast, no DEBUG log flood, no subprocess needed.
    Still uses subprocess with timeout as safety net for rare corrupted PDFs.
    """
    if not HAS_PDF:
        return ""
    import subprocess, sys as _sys
    # Inline script: PyMuPDF has no logging issues, but subprocess isolates
    # against rare hangs on malformed PDFs (timeout + SIGKILL).
    script = (
        "import sys, fitz;"
        "doc=fitz.open(sys.argv[1]);"
        "ps=[doc[i].get_text() for i in range(min(len(doc),int(sys.argv[2])))];"
        "sys.stdout.write(chr(10)*2 .join(p.strip() for p in ps if p.strip()))"
    )
    try:
        proc = subprocess.Popen(
            [_sys.executable, "-c", script, str(pdf_path), str(max_pages)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        try:
            stdout, _ = proc.communicate(timeout=timeout_secs)
            return stdout[:PDF_MAX_CHARS]
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(2)
            logging.getLogger("PDF").warning(
                f"Skipped ({pdf_path.name}): exceeded {timeout_secs}s — process killed"
            )
            return ""
    except Exception:
        return ""


class LLMAnalyzer:
    """Wraps gpt-5-nano Structured Output analysis."""

    def __init__(self, model: str = LLM_MODEL_DEFAULT, verbose: bool = False):
        if not HAS_OPENAI:
            raise RuntimeError("openai package not installed")
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client  = OpenAI(api_key=api_key)
        self.model   = model
        self.verbose = verbose
        self.log     = logging.getLogger("LLM")

    def analyze(self, circ: dict) -> Optional[dict]:
        """
        Analyze one circular. Returns structured dict or None on error.
        Uses temperature=1 (FIXED) and json_schema response_format.
        """
        prompt = self._build_prompt(circ)

        self.log.info(f"  → LLM ({self.model}, temp={LLM_TEMPERATURE})")
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=LLM_TEMPERATURE,        # ⚠️ FIXED — do not change
                response_format={
                    "type":        "json_schema",
                    "json_schema": CIRCULAR_SCHEMA,
                },
                messages=[
                    # gpt-5-nano is a reasoning model — use "developer" role (not "system")
                    {"role": "developer", "content": SYSTEM_PROMPT},
                    {"role": "user",      "content": prompt},
                ],
                max_completion_tokens=16000,   # reasoning model needs extra budget for internal reasoning tokens
            )
            raw = resp.choices[0].message.content
            result = json.loads(raw)
            if self.verbose:
                self.log.debug(
                    f"  ← impact={result.get('impact')} "
                    f"compliance={result.get('compliance')} "
                    f"deadlines={len(result.get('deadlines', []))} "
                    f"actions={len(result.get('actions', []))}"
                )
            return result
        except json.JSONDecodeError as exc:
            self.log.error(f"  LLM returned invalid JSON: {exc}")
            return None
        except Exception as exc:
            self.log.error(f"  LLM API error: {exc}")
            return None

    def _build_prompt(self, circ: dict) -> str:
        """Build user prompt for LLM."""
        lines = [
            f"通告號：{circ.get('number', '?')}",
            f"標題：{circ.get('title', '?')}",
            f"發佈日期：{circ.get('date', '?')}",
            f"通告類型：{circ.get('type', 'EDBCM')}",
            "",
        ]
        if circ.get("official"):
            lines += ["【官方摘要 / 網頁文字】", circ["official"], ""]
        if circ.get("pdf_text"):
            lines += ["【通告全文（PDF 提取）】", circ["pdf_text"]]
        elif not circ.get("official"):
            lines.append("（注意：未能提取通告全文，請根據標題及通告號作合理推斷）")
        return "\n".join(lines)


# =============================================================================
# UTILITIES
# =============================================================================

def _abs_url(href: str) -> str:
    """
    Convert relative URL to absolute, using the EDB listing page as base.
    Correctly resolves ../ paths (e.g. ../circular/upload/EDBCM/EDBCMyyNNNC.pdf
    → https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCMyyNNNC.pdf).
    """
    from urllib.parse import urljoin
    if not href:
        return ""
    href = href.strip()
    if href.startswith("http"):
        return href
    return urljoin(EDB_LIST_URL, href)


def _parse_date(date_str: str) -> str:
    """Parse various date formats → YYYY-MM-DD. Fallback = today."""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    # Handle Chinese months
    CH_MONTHS = {
        "一月": "01", "二月": "02", "三月": "03", "四月": "04",
        "五月": "05", "六月": "06", "七月": "07", "八月": "08",
        "九月": "09", "十月": "10", "十一月": "11", "十二月": "12",
    }
    for ch, en in CH_MONTHS.items():
        date_str = date_str.replace(ch, en)

    date_str = re.sub(r"\s+", " ", date_str.strip())

    fmts = [
        "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d",
        "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%d %m %Y",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Last resort: extract digits
    nums = re.findall(r"\d+", date_str)
    if len(nums) >= 3:
        try:
            d, m, y = nums[0], nums[1], nums[2]
            if len(y) == 2:
                y = "20" + y
            return datetime(int(y), int(m), int(d)).strftime("%Y-%m-%d")
        except (ValueError, OverflowError):
            pass

    return datetime.now().strftime("%Y-%m-%d")


def _is_new(date_str: str, days: int = 7) -> bool:
    """True if date_str is within the last `days` days."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - d).days <= days
    except ValueError:
        return False


def school_year_start() -> datetime:
    """
    Return September 1 of the current Hong Kong school year.
    School year starts on Sep 1. If today is before Sep 1, the school year
    started on Sep 1 of the previous calendar year.

    Examples (HK):
      2026-03-10  →  2025-09-01  (mid school year 2025/26)
      2026-10-01  →  2026-09-01  (start of school year 2026/27)
    """
    today = datetime.now()
    year = today.year if today.month >= 9 else today.year - 1
    return datetime(year, 9, 1)


def _empty_analysis() -> dict:
    """Return a safe default analysis for circulars that LLM failed on."""
    return {
        "impact": "low",
        "compliance": "informational",
        "urgency": "low",
        "scope": "both_sec_pri",
        "topics": [],
        "tags": [],
        "summary": "",
        "grant_info": {
            "type": "none",
            "amount_hkd": None,
            "amount_label": None,
            "resource_value_hkd": None,
            "note": "",
        },
        "roles": {r: {"r": False, "pts": [], "acts": []}
                  for r in ["principal", "vice_principal", "department_head",
                             "teacher", "eo_admin", "supplier"]},
        "deadlines": [],
        "actions": [],
        "diff": None,
    }


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(args) -> int:
    """Orchestrate scrape → PDF extract → LLM analyze → save."""

    # ── Logging ──────────────────────────────────────────────────────────────
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)-7s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("main")

    # ── Validate output path ─────────────────────────────────────────────────
    output_path = Path(args.output)
    if not output_path.parent.exists():
        log.error(f"Output directory does not exist: {output_path.parent}")
        return 1

    # ── Init scraper ─────────────────────────────────────────────────────────
    if not args.llm_only:
        if not HAS_REQUESTS:
            log.error("requests + beautifulsoup4 required for scraping")
            return 1
        scraper = EDBScraper(verbose=args.verbose)

    # ── Init LLM ─────────────────────────────────────────────────────────────
    analyzer = None
    if not args.dry_run:
        if not HAS_OPENAI:
            log.error("openai package required (pip install openai)")
            return 1
        if not os.environ.get("OPENAI_API_KEY"):
            log.error("OPENAI_API_KEY not set. Export it before running.")
            return 1
        try:
            analyzer = LLMAnalyzer(model=args.model, verbose=args.verbose)
            log.info(f"LLM ready: {args.model}  temperature={LLM_TEMPERATURE} (fixed)")
        except RuntimeError as exc:
            log.error(str(exc))
            return 1

    # ── Load existing data (incremental mode) ────────────────────────────────
    existing: dict[str, dict] = {}
    if output_path.exists():
        try:
            with open(output_path, encoding="utf-8") as fh:
                saved = json.load(fh)
            saved_list = saved.get("circulars", saved) if isinstance(saved, dict) else saved
            existing = {c["number"]: c for c in saved_list
                        if isinstance(c, dict) and "number" in c}
            log.info(f"Loaded {len(existing)} existing circulars from {output_path}")
        except Exception as exc:
            log.warning(f"Could not read existing file: {exc}")

    # ── Resolve date range ────────────────────────────────────────────────────
    # --school-year takes priority over --days
    if getattr(args, 'school_year', False):
        sy = school_year_start()
        date_from_str = sy.strftime("%d/%m/%Y")      # DD/MM/YYYY for POST
        date_from_iso = sy.strftime("%Y-%m-%d")       # ISO for JSON output
        range_label   = f"school-year (from {date_from_iso})"
    else:
        date_from_str = None
        date_from_iso = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        range_label   = f"past {args.days} days (from {date_from_iso})"

    # =========================================================================
    # PHASE 1 — SCRAPE
    # =========================================================================
    if args.llm_only:
        log.info("━━━ Phase 1: SKIP (--llm-only) ━━━")
        raw = list(existing.values())
    else:
        log.info(f"━━━ Phase 1: SCRAPE  ({range_label}) ━━━")
        raw = scraper.get_circular_list(days=args.days, date_from=date_from_str)
        if not raw:
            log.error("No circulars found. Check network access to edb.gov.hk")
            log.error("Tip: Run from Mac Terminal (not the Claude VM)")
            return 1

        log.info(f"━━━ Phase 1b: ENRICH DETAIL PAGES ({len(raw)} circulars) ━━━")
        for idx, circ in enumerate(raw):
            log.info(f"[{idx+1}/{len(raw)}] {circ['number']} — detail page")
            raw[idx] = scraper.enrich_detail(circ)

    # =========================================================================
    # PHASE 2 — PDF EXTRACTION
    # =========================================================================
    log.info(f"━━━ Phase 2: PDF EXTRACTION ({len(raw)} circulars) ━━━")
    for circ in raw:
        # Reuse existing PDF text if available
        num = circ.get("number", "")
        if circ.get("pdf_text"):
            log.debug(f"  {num}: pdf_text already present")
            continue
        if num in existing and existing[num].get("pdf_text"):
            circ["pdf_text"] = existing[num]["pdf_text"]
            log.debug(f"  {num}: restored pdf_text from cache")
            continue

        pdf_urls = circ.get("pdf_urls", [])
        if not pdf_urls:
            log.info(f"  {num}: no PDF URL")
            circ["pdf_text"] = ""
            continue

        # First URL = TC version (traditional Chinese — primary)
        pdf_path = scraper.download_pdf(pdf_urls[0], num) if not args.llm_only else None
        if pdf_path and HAS_PDF:
            circ["pdf_text"] = extract_pdf_text(pdf_path)
            log.info(f"  {num}: {len(circ['pdf_text'])} chars extracted")
        else:
            circ["pdf_text"] = ""

    # =========================================================================
    # PHASE 3 — LLM ANALYSIS
    # =========================================================================
    if args.dry_run:
        log.info("━━━ Phase 3: SKIP (--dry-run) ━━━")
    else:
        log.info(f"━━━ Phase 3: LLM ANALYSIS ({len(raw)} circulars, {args.model}) ━━━")
        for idx, circ in enumerate(raw):
            num = circ["number"]
            log.info(f"[{idx+1}/{len(raw)}] {num}")

            # Incremental: skip if already fully analysed
            if (not args.llm_only
                    and num in existing
                    and existing[num].get("summary")):
                log.info(f"  → Skip (already analysed — use --llm-only to force re-run)")
                for key in _empty_analysis():
                    if key not in circ:
                        circ[key] = existing[num].get(key)
                continue

            if not circ.get("pdf_text") and not circ.get("official"):
                log.warning(f"  → No text content — LLM will rely on title only")

            result = analyzer.analyze(circ)
            if result:
                circ.update(result)
            else:
                log.warning(f"  → LLM failed — using empty analysis defaults")
                circ.update(_empty_analysis())

            # Polite rate-limiting
            if idx < len(raw) - 1:
                time.sleep(0.3)

    # =========================================================================
    # PHASE 4 — MERGE + SAVE
    # Merge this run's results into the existing dataset so that incremental
    # (days-3) runs do NOT overwrite school-year full data.
    # New/updated records take priority; existing records not in this run are kept.
    # =========================================================================
    log.info("━━━ Phase 4: MERGE + SAVE ━━━")

    # Merge: start with existing, then overlay with this run's fresh results
    merged: dict[str, dict] = dict(existing)
    for circ in raw:
        num = circ.get("number", "")
        if num:
            merged[num] = circ  # new/updated overwrites existing entry

    # Sort merged results by date descending (newest first)
    merged_sorted = sorted(merged.values(),
                           key=lambda c: c.get("date", "1970-01-01"),
                           reverse=True)

    new_count     = sum(1 for c in raw if c.get("number") and c["number"] not in existing)
    updated_count = sum(1 for c in raw if c.get("number") and c["number"] in existing)
    kept_count    = len(merged) - len(raw)
    log.info(f"  Merge result: {new_count} new + {updated_count} updated + {kept_count} kept "
             f"= {len(merged)} total")

    output_list = []
    for idx, circ in enumerate(merged_sorted):
        # Merge defaults for any missing fields
        defaults = _empty_analysis()
        for key, val in defaults.items():
            if key not in circ:
                circ[key] = val

        # Official text: prefer detail-page text, fall back to first 500 chars of PDF
        official_text = (circ.get("official") or
                         circ.get("pdf_text", "")[:500]).strip()

        # Build pdf_urls: already sorted C/E/S order by _parse_list
        pdf_urls = circ.get("pdf_urls", [])

        record = {
            "id":         idx,
            "number":     circ.get("number", f"UNKNOWN_{idx}"),
            "type":       circ.get("type", "EDBCM"),
            "date":       circ.get("date", datetime.now().strftime("%Y-%m-%d")),
            "isNew":      _is_new(circ.get("date", "")),
            "title":      circ.get("title", ""),
            "official":   official_text,
            "impact":     circ.get("impact", "low"),
            "compliance": circ.get("compliance", "informational"),
            "urgency":    circ.get("urgency", "low"),
            "scope":      circ.get("scope", "both_sec_pri"),
            "topics":     circ.get("topics", []),
            "tags":       circ.get("tags", []),
            "grant_info": circ.get("grant_info", defaults["grant_info"]),
            "summary":    circ.get("summary", ""),
            "roles":      circ.get("roles", defaults["roles"]),
            "deadlines":  circ.get("deadlines", []),
            "actions":    circ.get("actions", []),
            "diff":       circ.get("diff", None),
            "pdf_urls":   pdf_urls,   # [C.pdf, E.pdf, S.pdf] — sorted TC/EN/SC
        }
        output_list.append(record)

    # Compute actual date range across all merged circulars
    all_dates = [c["date"] for c in output_list if c.get("date") and c["date"] != "1970-01-01"]
    actual_date_from = min(all_dates) if all_dates else date_from_iso
    actual_date_to   = max(all_dates) if all_dates else datetime.now().strftime("%Y-%m-%d")

    output = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model":        args.model if not args.dry_run else "dry-run",
        "temperature":  LLM_TEMPERATURE,
        "range":        range_label,
        "date_from":    actual_date_from,    # earliest date in merged dataset
        "date_to":      actual_date_to,      # latest date in merged dataset
        "days":         args.days,           # kept for backward-compat
        "count":        len(output_list),
        "circulars":    output_list,
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)

    size_kb = output_path.stat().st_size / 1024
    log.info(f"✅ Saved {len(output_list)} circulars → {output_path}  ({size_kb:.1f}KB)")
    return 0


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="edb_scraper.py",
        description="EDB 通告爬蟲 + gpt-5-nano 分析管線 v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 抓取最近30天並分析
  python3 edb_scraper.py --days 30 --output ./circulars.json -v

  # 抓取本學年全部通告（9月1日至今）
  python3 edb_scraper.py --school-year --output ./circulars.json -v

  # 抓取最近365天通告
  python3 edb_scraper.py --days 365 --output ./circulars.json -v

  # 只爬取不分析（測試網絡）
  python3 edb_scraper.py --days 7 --output ./circulars.json --dry-run

  # 重新分析已快取的 PDF（不重新爬取）
  python3 edb_scraper.py --llm-only --output ./circulars.json

  # 使用較強模型
  python3 edb_scraper.py --school-year --output ./circulars.json --model gpt-4.1-mini
""",
    )
    parser.add_argument(
        "--days", type=int, default=30, metavar="N",
        help="抓取最近 N 天通告（預設 30；最大建議 365）",
    )
    parser.add_argument(
        "--school-year", action="store_true",
        help="抓取本學年通告，由9月1日起至今（與 --days 互斥，此旗標優先）",
    )
    parser.add_argument(
        "--output", required=True, metavar="PATH",
        help="circulars.json 輸出路徑（必須）",
    )
    parser.add_argument(
        "--llm-only", action="store_true",
        help="跳過爬取，只重新進行 LLM 分析（需已有 PDF 快取）",
    )
    parser.add_argument(
        "--model", default=LLM_MODEL_DEFAULT, metavar="MODEL",
        help=f"LLM 模型（預設 {LLM_MODEL_DEFAULT}）",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只爬取元數據，不呼叫 LLM（網絡測試用）",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="詳細輸出",
    )

    args = parser.parse_args()

    # Determine range label for display
    if args.school_year:
        sy = school_year_start()
        range_display = f"school-year (from {sy.strftime('%Y-%m-%d')})"
    else:
        range_display = f"past {args.days} days"

    print(f"\n{'='*60}")
    print(f"  EDB Circular Scraper + Analyzer  v1.0.0")
    print(f"  Model      : {args.model}")
    print(f"  Temperature: {LLM_TEMPERATURE}  (fixed)")
    print(f"  Output     : {args.output}")
    if args.llm_only:
        print(f"  Mode       : llm-only (re-analyse cached PDFs)")
    elif args.dry_run:
        print(f"  Mode       : dry-run  ({range_display})")
    else:
        print(f"  Mode       : full     ({range_display})")
    print(f"{'='*60}\n")

    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
