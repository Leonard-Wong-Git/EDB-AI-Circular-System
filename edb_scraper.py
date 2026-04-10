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
import copy
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
K1_KNOWLEDGE_URL = "https://leonard-wong-git.github.io/edb-knowledge/knowledge.json"
K1_GUIDELINES_URL = "https://leonard-wong-git.github.io/edb-knowledge/guidelines.json"
ROLE_FACTS_PATH = Path("dev/knowledge/role_facts.json")

# LLM — ⚠️ FIXED RULES:
LLM_MODEL_DEFAULT = "gpt-5-nano"
LLM_TEMPERATURE   = 1     # DO NOT CHANGE — project spec rule
ROLE_FACTS_MAX_TOPICS = 3
ROLE_FACTS_MAX_FACTS_PER_ROLE = 2
ROLE_FACT_ORDER = [
    "all_roles", "principal", "vice_principal", "subject_head",
    "panel_chair", "teacher", "eo_admin", "supplier",
]
ROLE_FACT_LABELS = {
    "all_roles": "所有角色",
    "principal": "校長",
    "vice_principal": "副校長",
    "subject_head": "科主任",
    "panel_chair": "主任",
    "teacher": "教師",
    "eo_admin": "EO",
    "supplier": "供應商",
}

POST_REVIEW_PROCUREMENT_KEYWORDS = ["採購", "招標", "報價", "供應商", "承辦商", "投標"]
POST_REVIEW_CURRICULUM_KEYWORDS = [
    "課程", "學與教", "學習", "教學", "展覽", "講座", "教材", "資源",
    "國家安全教育", "價值觀教育", "小學人文科", "中國歷史", "公民與社會發展科",
]
POST_REVIEW_FINANCE_KEYWORDS = [
    "津貼", "撥款", "資助", "經費", "申請", "財務", "報銷", "結餘",
    "收支", "發還", "資助學校", "學校發展津貼",
]
POST_REVIEW_STUDENT_KEYWORDS = [
    "學生", "學生活動", "比賽", "交流", "家長", "家校", "參與", "支援",
    "訓育", "輔導", "SEN", "校外活動", "健康", "網絡安全",
]

ORDERED_TERM_RULES = [
    {
        "priority": 1,
        "from": "買設備",
        "to": "採購設備",
        "reason": "以正式採購用語取代口語化表述",
    },
    {
        "priority": 2,
        "from": "報價／投標",
        "to": "報價／招標",
        "reason": "統一 supplier 用語，避免投標/招標混用",
    },
    {
        "priority": 3,
        "from": "承辦商",
        "to": "供應商／承辦商",
        "reason": "對外角色描述更完整",
    },
    {
        "priority": 4,
        "from": "跟進學校安排",
        "to": "按學校採購程序提交文件及回覆要求",
        "reason": "把含糊動作改成可執行表述",
    },
    {
        "priority": 5,
        "from": "學與教資源",
        "to": "學與教資源／課程相關材料",
        "reason": "統一 curriculum 類通告用語，突出課程應用場景",
    },
]

KNOWLEDGE_RECOMMENDED_LINKS = [
    {
        "label": "學校財務管理（供應商視角）",
        "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/about-fin-management/index.html",
        "why": "補充學校採購、利益衝突及供應商溝通的標準參考",
    },
    {
        "label": "廉政公署採購參考資料",
        "url": "https://www.icac.org.hk/icac/pb/tc/reference.html",
        "why": "補充防貪及採購誠信要求",
    },
]

CURRICULUM_RECOMMENDED_LINKS = [
    {
        "label": "課程發展指引",
        "url": "https://www.edb.gov.hk/tc/curriculum-development/renewal/guides.html",
        "why": "補充課程架構、學習領域與學與教資源的官方參考",
    },
    {
        "label": "學校表現指標 (KPM)",
        "url": "https://www.edb.gov.hk/tc/sch-admin/sch-quality-assurance/performance-indicators/kpm/index.html",
        "why": "補充課程推行、自評與學校層面跟進的參考框架",
    },
]

FINANCE_RECOMMENDED_LINKS = [
    {
        "label": "學校財務管理",
        "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/about-fin-management/index.html",
        "why": "補充撥款運用、財務安排及校內批核的官方參考",
    },
    {
        "label": "學校發展津貼的參考資料",
        "url": "http://www.edb.gov.hk/tc/sch-admin/fin-management/subsidy-info/ref-capacity-enhancement-grant/index.html",
        "why": "補充津貼基本原則、申請/發放安排及會計處理要求",
    },
]

STUDENT_RECOMMENDED_LINKS = [
    {
        "label": "學校活動指引",
        "url": "https://www.edb.gov.hk/tc/sch-admin/admin/about-activities/sch-activities-guidelines/index.html",
        "why": "補充學生活動安排、風險管理及校內行政協調的官方參考",
    },
    {
        "label": "學校行政手冊",
        "url": "https://www.edb.gov.hk/tc/sch-admin/regulations/sch-admin-guide/index.html",
        "why": "補充學生支援、家校溝通及校內程序處理的行政參考",
    },
]

K1_TOPIC_KEYWORDS = {
    "finance": ["採購", "財務", "津貼", "撥款", "資助", "金額", "招標", "報價", "經費"],
    "hr": ["CPD", "培訓", "聘任", "薪酬", "專業發展", "教職員"],
    "curriculum": ["課程", "科目", "評估", "學習", "教學", "課時", "學與教", "教材"],
    "activity": ["活動", "考察", "旅行", "比賽", "境外", "交流", "參觀", "展覽"],
    "student": ["學生", "意外", "安全", "健康", "SEN", "欺凌", "家長", "校外活動"],
    "it": ["資訊科技", "電腦", "設備", "IT", "AI", "網絡", "系統", "平台"],
    "general": ["行政", "安排", "指引", "程序", "通知"],
}

K1_TOPIC_PRIORITY = ["finance", "curriculum", "student", "activity", "hr", "it"]
K1_TOPIC_SUPPLEMENT_MIN_HITS = {
    "finance": 2,
    "hr": 2,
    "curriculum": 2,
    "activity": 2,
    "student": 2,
    "it": 2,
    "general": 2,
}
K1_MAX_TOPICS = 3
K1_MAX_FACTS_PER_TOPIC = 4
K1_MAX_FACTS_TOTAL = 12
K1_MAX_GUIDELINES_PER_TOPIC = 2
K1_MAX_GUIDELINES_TOTAL = 6

ANALYSIS_TO_K1_TOPIC = {
    "finance": "finance",
    "procurement": "finance",
    "hr": "hr",
    "curriculum": "curriculum",
    "activity": "activity",
    "student": "student",
    "safety": "student",
    "it": "it",
    "exam": "curriculum",
}

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

_SUPPLIER_ROLE_OBJ = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "r":               {"type": "boolean"},
        "pts":             {"type": "array", "items": {"type": "string"}},
        "acts":            {"type": "array", "items": {"type": "string"}},
        "is_tender":       {"type": "boolean"},
        "procurement_cat": {"type": "string", "enum": ["IT", "Construction", "Furniture", "Services", "Training", "Stationery", "Other", "none"]},
        "budget_estimate": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        "compliance_ref":  {"type": "array", "items": {"type": "string"}},
        "eligibility":     {"type": "string"},
        "contact_unit":    {"type": "string"},
    },
    "required": [
        "r", "pts", "acts", "is_tender", "procurement_cat",
        "budget_estimate", "compliance_ref", "eligibility", "contact_unit"
    ],
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
                    "principal", "vice_principal", "subject_head", "panel_chair",
                    "teacher", "eo_admin", "supplier",
                ],
                "properties": {
                    "principal":       _ROLE_OBJ,
                    "vice_principal":  _ROLE_OBJ,
                    "subject_head":    _ROLE_OBJ,
                    "panel_chair":     _ROLE_OBJ,
                    "teacher":         _ROLE_OBJ,
                    "eo_admin":        _ROLE_OBJ,
                    "supplier":        _SUPPLIER_ROLE_OBJ,
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

SYSTEM_PROMPT = """你是一個香港教育局（EDB）通告分析專家，服務對象包括學校校長、副校長、科主任、主任、教師、EO 和供應商。
你具備深厚的香港學校管理知識，並能將提供的「經審核知識庫 (Knowledge Base)」與通告內容進行語義對照分析。

你的任務是閱讀 EDB 通告全文，提取結構化資訊，以 JSON 格式輸出分析結果。

━━━ 知識對照分析 (Fact-Checking) ━━━
1. 如提供的「經審核知識庫」含有與當前通告相關的規定（如採購門檻、CPD 時數、撥款用途、廉潔要求），請務必在對應角色的 pts (重點事項) 或 acts (行動) 中體現。
2. 即使通告全文未提及具體金額門檻，若知識庫有相關一般準則，應在 supplier (供應商) 角色中提及。

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
  角色清單：principal, vice_principal, subject_head, panel_chair, teacher, eo_admin, supplier
  (supplier 角色額外包含：is_tender, procurement_cat, budget_estimate, compliance_ref, eligibility, contact_unit)

deadlines（截止日期）：
  apply_deadline      — 申請撥款/服務的截止
  submission_deadline — 提交文件/報告的截止
  awareness_deadline  — 知悉/生效日期
  日期格式：YYYY-MM-DD

actions（具體行動步驟）：
  按時間先後排列，role 欄只用：principal, vice_principal, subject_head, panel_chair, teacher, eo_admin, supplier
  dl 填 YYYY-MM-DD 或 null

diff（版本比較）：
  如通告標題或內容含「(修訂)」「更新」「修改」「updated」「revised」等，分析主要變更
  否則返回 null

━━━ 輸出注意 ━━━
1. 日期格式必須為 YYYY-MM-DD
2. 金額單位為港元（HKD），只填數字不加逗號
3. tags 最多 5 個，用 2-6 字中文描述
4. summary 中文摘要約 120-250 字，以 1-2 段短段落為主：
   - 第 1 段：概述通告主旨、對象或安排重點
   - 第 2 段（如需要）：概述主要要求、期限或重要安排
   - summary 只做通告簡介，不要寫角色工作、行動清單或知識庫延伸說明
   - 可參考知識庫詞彙統一用字，但不得把知識庫一般規則、角色常識、延伸管理建議當成通告內容
   - 只寫通告已明示或可直接從官方摘要/PDF讀出的內容；資訊不足時直接略去，不要描述「未提供什麼」
   - 不得使用「可推斷」「初步判讀」「根據標題可判斷」等方法說明或保留語氣
   - 不得使用「若有……將另行通知」「目前尚未披露」「等待後續公告」等低信息模板句填充摘要
   - 除非通告本身明確逐一分派角色責任，否則不要在 summary 逐個角色展開
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


# =============================================================================
# KNOWLEDGE ENGINE (v3.0.4)
# =============================================================================

class KnowledgeStore:
    def __init__(self, client: "OpenAI", verbose: bool = False):
        self.client  = client
        self.verbose = verbose
        self.log     = logging.getLogger("Knowledge")
        self.data    = {}
        self.facts   = []      # List of strings: "Fact content"
        self.embeds  = []      # List of lists: [0.1, -0.2, ...]
        self.threshold = 0.45  # Project spec threshold
        self.cache_path = CACHE_DIR / ".knowledge_embeds.json"

    def load(self, path_or_url: str):
        self.log.info(f"Loading knowledge from: {path_or_url}")
        try:
            if path_or_url.startswith("http"):
                resp = requests.get(path_or_url, timeout=30)
                resp.raise_for_status()
                self.data = resp.json()
            else:
                with open(path_or_url, encoding="utf-8") as f:
                    self.data = json.load(f)
            
            # Flatten knowledge into facts
            self.facts = []
            for topic_id, topic_data in self.data.items():
                if topic_id.startswith("_"): continue
                for role_id, role_facts in topic_data.items():
                    if role_id.startswith("_"): continue
                    if isinstance(role_facts, list):
                        self.facts.extend(role_facts)
            
            # Uniqify and remove too short ones
            self.facts = sorted(list(set(f for f in self.facts if len(f) > 5)))
            self.log.info(f"  Loaded {len(self.facts)} unique facts")
            
            self._ensure_embeddings()
        except Exception as exc:
            self.log.error(f"  Failed to load knowledge: {exc}")

    def _ensure_embeddings(self):
        """Load from cache or generate for new facts."""
        cached = {}
        if self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    cached = json.load(f)
            except: pass

        self.embeds = []
        to_gen = []
        for f in self.facts:
            if f in cached:
                self.embeds.append(cached[f])
            else:
                to_gen.append(f)
        
        if to_gen:
            self.log.info(f"  Generating embeddings for {len(to_gen)} new facts...")
            # Batch process 100 at a time
            for i in range(0, len(to_gen), 100):
                batch = to_gen[i:i+100]
                res = self.client.embeddings.create(model="text-embedding-3-small", input=batch)
                for item in res.data:
                    cached[to_gen[i + item.index]] = item.embedding
                    # Match order
            
            # Update entire embeds list from refreshed cache
            self.embeds = [cached[f] for f in self.facts]
            
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(cached, f, ensure_ascii=False)
            self.log.info(f"  Knowledge embeddings cached: {self.cache_path}")

    def find_relevant(self, text: str) -> list[str]:
        """Find facts with cosine similarity >= 0.45."""
        if not text or not self.embeds: return []
        
        try:
            res = self.client.embeddings.create(model="text-embedding-3-small", input=text[:2000])
            query_vec = res.data[0].embedding
            
            hits = []
            for i, fact_vec in enumerate(self.embeds):
                # Cosine similarity for normalized vectors = dot product
                sim = sum(a*b for a,b in zip(query_vec, fact_vec))
                if sim >= self.threshold:
                    hits.append((sim, self.facts[i]))
            
            # Sort by similarity descending
            hits.sort(key=lambda x: x[0], reverse=True)
            results = [h[1] for h in hits[:15]] # Cap at 15 facts to avoid prompt bloat
            if self.verbose and results:
                self.log.debug(f"  Found {len(results)} facts (top sim={hits[0][0]:.3f})")
            return results
        except Exception as exc:
            self.log.error(f"  Embedding / search failed: {exc}")
            return []


class K1KnowledgeClient:
    """Fetch K1 public JSON endpoints and return prompt-ready facts/guidelines."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.log = logging.getLogger("K1")
        self.knowledge = None
        self.guidelines = None
        self.topic_keywords = copy.deepcopy(K1_TOPIC_KEYWORDS)

    def _fetch_json(self, url: str) -> Optional[dict]:
        if not HAS_REQUESTS:
            self.log.warning(f"  requests unavailable — skip K1 fetch: {url}")
            return None
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            self.log.warning(f"  K1 fetch failed ({url}): {exc}")
            return None

    def ensure_loaded(self):
        if self.knowledge is None:
            self.knowledge = self._fetch_json(K1_KNOWLEDGE_URL) or {}
            self._refresh_topic_keywords_from_knowledge()
        if self.guidelines is None:
            self.guidelines = self._fetch_json(K1_GUIDELINES_URL) or {}

    def _refresh_topic_keywords_from_knowledge(self):
        if not isinstance(self.knowledge, dict):
            return
        for topic_id, topic_data in self.knowledge.items():
            if topic_id.startswith("_") or not isinstance(topic_data, dict):
                continue
            keywords = topic_data.get("_keywords_zh")
            if isinstance(keywords, list) and keywords:
                self.topic_keywords[topic_id] = [
                    kw for kw in keywords if isinstance(kw, str) and kw.strip()
                ]

    def detect_topics(self, circ: dict) -> list[str]:
        text = " ".join(
            filter(
                None,
                [
                    circ.get("title", ""),
                    circ.get("official", ""),
                    circ.get("pdf_text", "")[:2000],
                    circ.get("summary", ""),
                ],
            )
        )
        keyword_hits = {
            topic: sum(1 for keyword in keywords if keyword and keyword in text)
            for topic, keywords in self.topic_keywords.items()
        }
        topics = []

        for topic in circ.get("topics", []) or []:
            mapped = ANALYSIS_TO_K1_TOPIC.get(topic)
            if mapped and mapped not in topics:
                topics.append(mapped)

        selected = []
        for topic in topics:
            if topic not in selected:
                selected.append(topic)

        supplements = []
        for topic in K1_TOPIC_PRIORITY:
            if topic in selected:
                continue
            if keyword_hits.get(topic, 0) >= K1_TOPIC_SUPPLEMENT_MIN_HITS.get(topic, 2):
                supplements.append((keyword_hits[topic], topic))

        supplements.sort(key=lambda item: (-item[0], K1_TOPIC_PRIORITY.index(item[1])))
        for _, topic in supplements:
            if len(selected) >= K1_MAX_TOPICS:
                break
            selected.append(topic)

        if not selected and keyword_hits.get("general", 0) >= K1_TOPIC_SUPPLEMENT_MIN_HITS["general"]:
            selected.append("general")

        if len(selected) > K1_MAX_TOPICS:
            selected = selected[:K1_MAX_TOPICS]

        return selected

    def fetch_facts(self, topics: list[str]) -> list[str]:
        self.ensure_loaded()
        facts: list[str] = []
        for topic in topics:
            topic_data = (self.knowledge or {}).get(topic)
            if isinstance(topic_data, list):
                topic_facts = self._extract_legacy_facts(topic_data)
            elif isinstance(topic_data, dict):
                topic_facts = self._extract_role_bucket_facts(topic_data)
            else:
                topic_facts = []
            facts.extend(_dedupe_strings(topic_facts)[:K1_MAX_FACTS_PER_TOPIC])
            if len(facts) >= K1_MAX_FACTS_TOTAL:
                break
        return _dedupe_strings(facts)[:K1_MAX_FACTS_TOTAL]

    def _extract_legacy_facts(self, entries: list[dict]) -> list[str]:
        facts = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("review_state") != "approved":
                continue
            roles = entry.get("roles", {})
            if not isinstance(roles, dict):
                continue
            if not any(roles.get(role_key) for role_key in ("all_roles", "subject_head", "panel_chair")):
                continue
            fact = entry.get("fact")
            if isinstance(fact, str) and fact.strip():
                facts.append(fact.strip())
        return facts

    def _extract_role_bucket_facts(self, topic_data: dict) -> list[str]:
        facts = []
        for role_key in ("all_roles", "subject_head", "panel_chair"):
            role_facts = topic_data.get(role_key, [])
            if not isinstance(role_facts, list):
                continue
            for fact in role_facts:
                if isinstance(fact, str) and fact.strip():
                    facts.append(fact.strip())
        return facts

    def fetch_guidelines(self, topics: list[str]) -> list[dict]:
        self.ensure_loaded()
        docs = []
        seen = set()
        for topic in topics:
            topic_docs = []
            for doc in (self.guidelines or {}).get(topic, []) or []:
                if not isinstance(doc, dict):
                    continue
                url = doc.get("url")
                if not url or url in seen:
                    continue
                seen.add(url)
                topic_docs.append(doc)
                if len(topic_docs) >= K1_MAX_GUIDELINES_PER_TOPIC:
                    break
            docs.extend(topic_docs)
            if len(docs) >= K1_MAX_GUIDELINES_TOTAL:
                break
        return docs[:K1_MAX_GUIDELINES_TOTAL]


class RoleFactsClient:
    """Load local role_facts.json and provide prompt-ready role knowledge."""

    def __init__(self, path: Path, verbose: bool = False):
        self.path = Path(path)
        self.verbose = verbose
        self.log = logging.getLogger("RoleFacts")
        self.data = {}
        self._load_attempted = False
        self.topic_keywords = copy.deepcopy(K1_TOPIC_KEYWORDS)

    def ensure_loaded(self):
        if self._load_attempted:
            return
        self._load_attempted = True
        try:
            with open(self.path, encoding="utf-8") as fh:
                self.data = json.load(fh)
            self._refresh_topic_keywords()
            topic_count = len([k for k in self.data if not k.startswith("_")])
            self.log.info(f"  Loaded local role facts: {self.path} ({topic_count} topics)")
        except Exception as exc:
            self.log.warning(f"  Role facts load failed ({self.path}): {exc}")
            self.data = {}

    def _refresh_topic_keywords(self):
        if not isinstance(self.data, dict):
            return
        for topic_id, topic_data in self.data.items():
            if topic_id.startswith("_") or not isinstance(topic_data, dict):
                continue
            keywords = topic_data.get("_keywords_zh")
            if isinstance(keywords, list) and keywords:
                self.topic_keywords[topic_id] = [
                    kw for kw in keywords if isinstance(kw, str) and kw.strip()
                ]

    def detect_topics(self, circ: dict, preferred_topics: list[str] | None = None) -> list[str]:
        self.ensure_loaded()
        if not self.data:
            return []

        valid_topics = {k for k in self.data if not k.startswith("_")}
        selected = []
        for topic in preferred_topics or []:
            if topic in valid_topics and topic not in selected:
                selected.append(topic)

        for topic in circ.get("topics", []) or []:
            mapped = ANALYSIS_TO_K1_TOPIC.get(topic)
            if mapped in valid_topics and mapped not in selected:
                selected.append(mapped)

        text = " ".join(
            filter(
                None,
                [
                    circ.get("title", ""),
                    circ.get("official", ""),
                    circ.get("pdf_text", "")[:2000],
                    circ.get("summary", ""),
                ],
            )
        )
        keyword_hits = {
            topic: sum(1 for keyword in keywords if keyword and keyword in text)
            for topic, keywords in self.topic_keywords.items()
            if topic in valid_topics
        }
        supplements = []
        for topic in K1_TOPIC_PRIORITY:
            if topic not in valid_topics or topic in selected:
                continue
            if keyword_hits.get(topic, 0) >= K1_TOPIC_SUPPLEMENT_MIN_HITS.get(topic, 2):
                supplements.append((keyword_hits[topic], topic))

        supplements.sort(key=lambda item: (-item[0], K1_TOPIC_PRIORITY.index(item[1])))
        for _, topic in supplements:
            if len(selected) >= ROLE_FACTS_MAX_TOPICS:
                break
            selected.append(topic)

        if not selected and "general" in valid_topics:
            selected.append("general")

        return selected[:ROLE_FACTS_MAX_TOPICS]

    def fetch_role_facts(self, topics: list[str]) -> dict[str, list[str]]:
        self.ensure_loaded()
        if not self.data:
            return {}

        grouped = {role_key: [] for role_key in ROLE_FACT_ORDER}
        for topic in topics:
            topic_data = self.data.get(topic)
            if not isinstance(topic_data, dict):
                continue
            for role_key in ROLE_FACT_ORDER:
                facts = topic_data.get(role_key, [])
                if not isinstance(facts, list):
                    continue
                grouped[role_key].extend(
                    fact.strip() for fact in facts if isinstance(fact, str) and fact.strip()
                )

        trimmed = {}
        for role_key in ROLE_FACT_ORDER:
            deduped = _dedupe_strings(grouped[role_key])[:ROLE_FACTS_MAX_FACTS_PER_ROLE]
            if deduped:
                trimmed[role_key] = deduped
        return trimmed


class LLMAnalyzer:
    """Wraps gpt-5-nano Structured Output analysis."""

    def __init__(self, client: "OpenAI", model: str = LLM_MODEL_DEFAULT, verbose: bool = False, knowledge_engine: KnowledgeStore = None, k1_client: K1KnowledgeClient = None, role_facts_client: RoleFactsClient = None):
        self.client  = client
        self.model   = model
        self.verbose = verbose
        self.log     = logging.getLogger("LLM")
        self.kn      = knowledge_engine
        self.k1      = k1_client
        self.role_facts = role_facts_client

    def analyze(self, circ: dict) -> Optional[dict]:
        """
        Analyze one circular. Returns structured dict or None on error.
        Uses temperature=1 (FIXED) and json_schema response_format.
        """
        # Semantic search for relevant knowledge
        relevant_facts = []
        if self.kn:
            # Match circular title + official text
            search_text = f"{circ.get('title', '')} {circ.get('official', '')}"
            relevant_facts = self.kn.find_relevant(search_text)
            circ["relevant_facts"] = relevant_facts  # Store for provenance

        k1_topics = []
        k1_facts = []
        k1_guidelines = []
        role_fact_topics = []
        role_facts = {}
        if self.k1:
            k1_topics = self.k1.detect_topics(circ)
            try:
                k1_facts = self.k1.fetch_facts(k1_topics)
                k1_guidelines = self.k1.fetch_guidelines(k1_topics)
            except Exception as exc:
                self.log.warning(f"  K1 enrichment skipped: {exc}")
                k1_topics, k1_facts, k1_guidelines = [], [], []
        if self.role_facts:
            try:
                role_fact_topics = self.role_facts.detect_topics(circ, preferred_topics=k1_topics)
                role_facts = self.role_facts.fetch_role_facts(role_fact_topics)
            except Exception as exc:
                self.log.warning(f"  Role-facts enrichment skipped: {exc}")
                role_fact_topics, role_facts = [], {}
        circ["k1_topics"] = k1_topics
        circ["k1_facts"] = k1_facts
        circ["k1_guidelines"] = k1_guidelines
        circ["role_fact_topics"] = role_fact_topics
        circ["role_facts"] = role_facts

        prompt = self._build_prompt(circ, relevant_facts, k1_facts, k1_guidelines, role_facts)

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
            # Re-detect K1 topics using LLM-derived topics for better accuracy
            if self.k1:
                enriched = {**circ, "topics": result.get("topics", [])}
                k1_topics_post = self.k1.detect_topics(enriched)
                if k1_topics_post:
                    try:
                        circ["k1_topics"]     = k1_topics_post
                        circ["k1_facts"]      = self.k1.fetch_facts(k1_topics_post)
                        circ["k1_guidelines"] = self.k1.fetch_guidelines(k1_topics_post)
                    except Exception as exc:
                        self.log.warning(f"  K1 post-LLM re-detect failed: {exc}")
            if self.role_facts:
                enriched = {**circ, "topics": result.get("topics", [])}
                try:
                    role_fact_topics_post = self.role_facts.detect_topics(
                        enriched,
                        preferred_topics=circ.get("k1_topics", []),
                    )
                    circ["role_fact_topics"] = role_fact_topics_post
                    circ["role_facts"] = self.role_facts.fetch_role_facts(role_fact_topics_post)
                except Exception as exc:
                    self.log.warning(f"  Role-facts post-LLM re-detect failed: {exc}")
            return result
        except json.JSONDecodeError as exc:
            self.log.error(f"  LLM returned invalid JSON: {exc}")
            return None
        except Exception as exc:
            self.log.error(f"  LLM API error: {exc}")
            return None

    def _build_prompt(self, circ: dict, facts: list[str] = None, k1_facts: list[str] = None, k1_guidelines: list[dict] = None, role_facts: dict[str, list[str]] = None) -> str:
        """Build user prompt for LLM."""
        lines = [
            f"通告號：{circ.get('number', '?')}",
            f"標題：{circ.get('title', '?')}",
            f"發佈日期：{circ.get('date', '?')}",
            f"通告類型：{circ.get('type', 'EDBCM')}",
            "",
            "【摘要寫作要求】",
            "- summary 只作通告簡介，約 120-250 字，以 1-2 段中文短段落撰寫。",
            "- 第一段只交代通告主旨、對象與核心安排。",
            "- 第二段只在有需要時交代主要要求、期限或重要安排。",
            "- 不要把知識庫一般規則、角色百科、延伸管理建議寫進 summary。",
            "- 可以借用知識庫詞彙去統一用字，但不可把知識庫內容寫成通告內容。",
            "- 只寫通告已明示或可直接從官方摘要/PDF讀出的內容；資訊不足時直接略去，不要描述『未提供什麼』。",
            "- 除非通告本身明確逐一分派角色責任，否則不要在 summary 逐個角色展開。",
            "- 不要在 summary 寫角色工作、行動清單或跟進分工；這些內容留給 actions 與 roles。",
            "- 不要寫「可推斷」「初步判讀」「根據標題可判斷」等自我說明語氣。",
            "- 不要寫「若有……將另行通知」「目前尚未披露」「等待後續公告」等低信息模板句。",
            "",
        ]
        if facts:
            lines += ["【經審核知識庫 (相關事實對照)】", "\n".join(f"- {f}" for f in facts), ""]
        if k1_facts:
            lines += ["【相關政策事實】", "\n".join(f"- {fact}" for fact in k1_facts), ""]
        if k1_guidelines:
            doc_lines = []
            for doc in k1_guidelines:
                title = doc.get("title") or doc.get("titleShort") or "未命名文件"
                year = doc.get("year")
                suffix = f"（{year}）" if year and year not in title else ""
                doc_lines.append(f"- {title}{suffix}: {doc.get('url', '')}")
            lines += ["【相關指引文件】", "\n".join(doc_lines), ""]
        if role_facts:
            role_lines = []
            for role_key in ROLE_FACT_ORDER:
                role_entries = role_facts.get(role_key, [])
                if not role_entries:
                    continue
                role_lines.append(f"- {ROLE_FACT_LABELS[role_key]}：")
                role_lines.extend(f"  - {fact}" for fact in role_entries)
            if role_lines:
                lines += ["【EDB學校管理知識中心角色事實】", "\n".join(role_lines), ""]
        
        if circ.get("official"):
            lines += ["【官方摘要 / 網頁文字】", circ["official"], ""]
        if circ.get("pdf_text"):
            lines += ["【通告全文（PDF 提取）】", circ["pdf_text"]]
        elif not circ.get("official"):
            lines.append("【資料限制】僅可按已知標題、日期與可得資料整理摘要；不要補充未明示的背景常識或角色百科。")
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
        "roles": {
            **{r: {"r": False, "pts": [], "acts": []}
               for r in ["principal", "vice_principal", "subject_head", "panel_chair", "teacher", "eo_admin"]},
            "supplier": {
                "r": False, "pts": [], "acts": [],
                "is_tender": False, "procurement_cat": "none",
                "budget_estimate": None, "compliance_ref": [],
                "eligibility": "", "contact_unit": ""
            }
        },
        "deadlines": [],
        "actions": [],
        "diff": None,
    }


def _dedupe_strings(items: list[str]) -> list[str]:
    seen = set()
    output = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def _merge_role_obj(base: dict | None, incoming: dict | None) -> dict:
    merged = copy.deepcopy(base or {"r": False, "pts": [], "acts": []})
    if not isinstance(incoming, dict):
        return merged
    merged["r"] = bool(merged.get("r") or incoming.get("r"))
    merged["pts"] = _dedupe_strings((merged.get("pts", []) or []) + (incoming.get("pts", []) or []))
    merged["acts"] = _dedupe_strings((merged.get("acts", []) or []) + (incoming.get("acts", []) or []))
    return merged


def _normalize_roles_payload(circ: dict) -> dict:
    """Normalize legacy and new role payloads to the current 7-role contract."""
    normalized = copy.deepcopy(circ)
    defaults = _empty_analysis()["roles"]
    original_roles = normalized.get("roles", {})
    roles = copy.deepcopy(defaults)

    if isinstance(original_roles, dict):
        for role_name in ["principal", "vice_principal", "subject_head", "panel_chair", "teacher", "eo_admin", "supplier"]:
            if role_name not in original_roles:
                continue
            if role_name == "supplier":
                merged_supplier = copy.deepcopy(roles["supplier"])
                if isinstance(original_roles[role_name], dict):
                    merged_supplier.update(original_roles[role_name])
                roles["supplier"] = merged_supplier
            else:
                roles[role_name] = _merge_role_obj(roles[role_name], original_roles[role_name])

        if "department_head" in original_roles:
            roles["panel_chair"] = _merge_role_obj(roles["panel_chair"], original_roles["department_head"])

    normalized["roles"] = roles

    for action in normalized.get("actions", []) or []:
        if action.get("role") == "department_head":
            action["role"] = "panel_chair"

    for deadline in normalized.get("deadlines", []) or []:
        if isinstance(deadline.get("roles"), list):
            deadline["roles"] = [
                "panel_chair" if role == "department_head" else role
                for role in deadline["roles"]
            ]
            deadline["roles"] = list(dict.fromkeys(deadline["roles"]))

    return normalized


def _replace_terms(text: str, applied: list[dict]) -> str:
    if not text:
        return text
    result = text
    for rule in ORDERED_TERM_RULES:
        source = rule["from"]
        target = rule["to"]
        changed = False

        if source in target:
            suffix = target[len(source):]
            if suffix:
                duplicate_pattern = re.compile(
                    re.escape(source) + f"(?:{re.escape(suffix)})+"
                )
                normalized = duplicate_pattern.sub(target, result)
                if normalized != result:
                    result = normalized
                    changed = True

                source_pattern = re.compile(
                    re.escape(source) + f"(?!{re.escape(suffix)})"
                )
                replaced = source_pattern.sub(target, result)
                if replaced != result:
                    result = replaced
                    changed = True
            elif source in result:
                replaced = result.replace(source, target)
                if replaced != result:
                    result = replaced
                    changed = True
        elif source in result:
            replaced = result.replace(source, target)
            if replaced != result:
                result = replaced
                changed = True

        if changed:
            applied.append(rule)
    return result


def _unique_applied_rules(applied: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for rule in sorted(applied, key=lambda item: item["priority"]):
        key = (rule["from"], rule["to"])
        if key in seen:
            continue
        seen.add(key)
        output.append(rule)
    return output


def _merge_link_lists(*groups: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for group in groups:
        for item in group:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            merged.append(item)
    return merged


def _dedupe_summary_phrases(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"(供應商／)+供應商／承辦商", "供應商／承辦商", text)
    text = re.sub(r"(供應商／承辦商)(?:／承辦商)+", "供應商／承辦商", text)
    text = re.sub(r"(供應商／承辦商)(?:／供應商)+", "供應商／承辦商", text)
    return text


SUMMARY_BANNED_PHRASES = [
    "若有截止日期、配套安排或其他實施要點，將於後續通知。",
    "如有截止日、配套安排將另行通知。",
    "第二段內容摘要需以官方全文公布為準，後續的執行要求、時間表及配套措施將於正式發布時提供，學校需依指引落實相關安排。",
]

SUMMARY_BANNED_MARKERS = [
    "第二段內容摘要",
    "根據標題可推測",
    "根據可得的知識庫",
    "根據經審核知識庫",
    "依照經審核知識庫",
    "知識庫",
    "若有",
    "如有",
    "目前尚未",
    "未披露",
    "未提供",
    "未包含",
    "未有",
    "未見",
    "以正式發布的公告全文為準",
    "此通告未逐一分派角色責任",
    "等待教育局後續公告",
    "請校方留意日後更新",
    "截至現時",
]

SUMMARY_ROLE_LABEL_MARKERS = [
    "校長",
    "副校長",
    "科主任",
    "主任",
    "教師",
    "EO",
    "EOAdmin",
    "供應商",
]

SUMMARY_ROLE_ACTION_MARKERS = [
    "須",
    "需",
    "負責",
    "協助",
    "跟進",
    "提交",
    "處理",
    "規劃",
    "監督",
    "提供",
    "確保",
    "參與",
    "發出",
    "存檔",
    "審批",
    "核對",
]


def _strip_summary_filler(text: str) -> str:
    if not text:
        return text
    cleaned = text
    for phrase in SUMMARY_BANNED_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    cleaned = cleaned.replace("根據標題可推測，", "")
    cleaned = cleaned.replace("根據標題可判斷，", "")
    cleaned = cleaned.replace("可推斷，", "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _filter_summary_sentences(sentences: list[str]) -> list[str]:
    filtered = []
    for sentence in sentences:
        if any(marker in sentence for marker in SUMMARY_BANNED_MARKERS):
            continue
        role_label_hits = sum(1 for marker in SUMMARY_ROLE_LABEL_MARKERS if marker in sentence)
        has_role_action_shape = (
            role_label_hits >= 1
            and any(marker in sentence for marker in SUMMARY_ROLE_ACTION_MARKERS)
        )
        if has_role_action_shape:
            continue
        sentence = sentence.strip()
        sentence = re.sub(r"[；，、：]+$", "。", sentence)
        if sentence:
            filtered.append(sentence)
    return filtered


SUMMARY_ROLE_PRIORITY = [
    "principal",
    "vice_principal",
    "subject_head",
    "panel_chair",
    "teacher",
    "eo_admin",
    "supplier",
]

SUMMARY_ROLE_LABELS = {
    "principal": "校長",
    "vice_principal": "副校長",
    "subject_head": "科主任",
    "panel_chair": "主任",
    "teacher": "教師",
    "eo_admin": "EO",
    "supplier": "供應商",
}


def _synthesize_sparse_actions(reviewed: dict) -> list[dict]:
    """Promote role-level action points into top-level actions for sparse circulars."""
    if reviewed.get("actions"):
        return reviewed.get("actions", [])

    roles = reviewed.get("roles") or {}
    summary = reviewed.get("summary") or ""
    source_text = " ".join([
        reviewed.get("title", ""),
        reviewed.get("official", ""),
        reviewed.get("pdf_text", "")[:1200],
    ]).strip()
    summary_paragraphs = [p.strip() for p in summary.split("\n\n") if p.strip()]

    sparse_case = (not source_text) or len(source_text) < 220 or len(summary_paragraphs) <= 2
    if not sparse_case:
        return reviewed.get("actions", [])

    synthesized = []
    seen = set()
    for role_key in SUMMARY_ROLE_PRIORITY:
        role = roles.get(role_key)
        if not isinstance(role, dict) or not role.get("r"):
            continue
        for text in (role.get("acts") or []):
            action_text = (text or "").strip()
            if not action_text or action_text in seen:
                continue
            seen.add(action_text)
            synthesized.append({
                "text": action_text,
                "role": role_key,
                "dl": None,
                "note": "",
            })
            break
        if len(synthesized) >= 3:
            break
    return synthesized


def _compact_summary_source_text(text: str) -> str:
    if not text:
        return ""
    compact = re.sub(r"\s+", "", text)
    compact = compact.replace("（下稱夏令營）", "")
    compact = compact.replace("下稱夏令營", "")
    return compact


def _build_activity_source_summary(title: str, source_text: str) -> str:
    compact = _compact_summary_source_text(source_text)
    if not compact:
        return ""

    def pick(*patterns: str) -> str:
        for pattern in patterns:
            match = re.search(pattern, compact)
            if match:
                return match.group(0)
        return ""

    para1_bits = []
    organizer = pick(r".{0,40}由北京市教育委員會、香港特別行政區政府教育局及澳門特別行政區政府教育及青年發展局聯合主辦.{0,80}?。")
    if organizer:
        organizer = organizer.replace(f"「{title}」", "本活動").replace(f"{title}", "本活動")
        para1_bits.append(organizer)

    schedule = pick(r"本年的?夏令營將於\d{4}年\d{1,2}月\d{1,2}日至?\d{1,2}日在北京舉行.{0,40}?。")
    if schedule:
        para1_bits.append(schedule)

    para2_bits = []
    quota = pick(r"香港的名額為\d+名學生及\d+名隨團教師。")
    if quota:
        para2_bits.append(quota)

    nomination = pick(r"每所學校可合共提名最多\d+名中四及／或中五級學生及\d+名校內教師（包括校長）參加。")
    if nomination:
        para2_bits.append(nomination)

    voluntary = pick(r"學生參加全屬自願性質。")
    if voluntary:
        para2_bits.append(voluntary)

    deadline = pick(r"請於\d{4}年\d{1,2}月\d{1,2}日.*?或之前.*?申請。", r"請於\d{4}年\d{1,2}月\d{1,2}日.*?或之前將填妥的電子申請表.*?。")
    if deadline:
        deadline = re.sub(r"電郵至[^。]+。", "提交申請，逾期將不獲受理。", deadline)
        deadline = re.sub(r"本局不會接受逾期的申請。?", "逾期將不獲受理。", deadline)
        deadline = re.sub(r"(逾期將不獲受理。)+", "逾期將不獲受理。", deadline)
        para2_bits.append(deadline)

    if not para1_bits and not para2_bits:
        return ""

    para1 = "".join(para1_bits)[:180]
    para2 = "".join(para2_bits)[:180]
    parts = [f"本通告介紹「{title}」的安排。"]
    if para1:
        parts[0] += para1
    if para2:
        parts.append(para2)
    return "\n\n".join(parts[:2]).strip()


def _build_summary_fallback(reviewed: dict) -> str:
    title = (reviewed.get("title") or "").strip()
    if not title:
        return ""

    source_text = " ".join([
        reviewed.get("official", ""),
        reviewed.get("pdf_text", "")[:2400],
    ]).strip()

    if any(token in title for token in ["交流", "夏令營", "參觀", "展覽", "活動"]):
        sourced = _build_activity_source_summary(title, source_text)
        if sourced:
            return sourced

    tags = [tag for tag in (reviewed.get("tags") or []) if tag]
    topics = reviewed.get("topics") or []

    if any(token in title for token in ["交流", "夏令營", "參觀", "展覽", "活動"]) or "activity" in topics:
        if tags:
            detail_tags = "、".join(tags[:3])
            detail = f"內容聚焦{detail_tags}及學校相關安排。"
        else:
            detail = "內容聚焦學生交流、活動安排及學校相關支援要求。"
    elif any(token in title for token in ["課程", "學習領域", "文憑考試", "教學"]) or "curriculum" in topics:
        detail = "內容聚焦課程推行、學校安排及相關要求。"
    elif any(token in title for token in ["津貼", "資助", "撥款", "財務", "採購"]) or "finance" in topics:
        detail = "內容聚焦申請安排、資助用途及相關程序要求。"
    elif "student" in topics or any(token in title for token in ["學生", "安全", "家長"]):
        detail = "內容聚焦學生參與安排及相關支援要求。"
    elif tags:
        detail_tags = "、".join(tags[:2])
        detail = f"內容聚焦{detail_tags}及相關安排。"
    else:
        detail = "內容聚焦相關安排及通告列明的跟進要求。"

    return f"本通告介紹「{title}」的安排。\n\n{detail}"


def _normalize_summary_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    cleaned = re.sub(r"[ \t\r\f\v]+", "", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _strip_summary_filler(cleaned)
    cleaned = _dedupe_summary_phrases(cleaned)
    cleaned = cleaned.replace("本公告", "本通告")
    if not cleaned:
        return ""

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    if len(paragraphs) >= 1:
        kept = paragraphs[:2]
        normalized = []
        for p in kept:
            sents = [s.strip() for s in re.split(r"(?<=[。！？])", p) if s.strip()]
            sents = _filter_summary_sentences(sents)
            if len(paragraphs) == 1 and len(sents) >= 2:
                normalized.append(_dedupe_summary_phrases(sents[0]))
                remainder = "".join(sents[1:]).strip()
                if remainder:
                    normalized.append(_dedupe_summary_phrases(remainder))
                continue
            para = "".join(sents).strip() if sents else ""
            if para:
                normalized.append(_dedupe_summary_phrases(para))
        if normalized:
            return "\n\n".join(normalized[:2])

    sentences = [s.strip() for s in re.split(r"(?<=[。！？])", cleaned) if s.strip()]
    sentences = _filter_summary_sentences(sentences)
    if not sentences:
        return _dedupe_summary_phrases(cleaned)
    if len(sentences) <= 2:
        joined = "\n\n".join(_dedupe_summary_phrases(s) for s in sentences)
        if len(joined) <= 250:
            return joined
        trimmed = []
        total = 0
        for sentence in sentences:
            if trimmed and total + len(sentence) > 250:
                break
            trimmed.append(sentence)
            total += len(sentence)
        return "\n\n".join(_dedupe_summary_phrases(s) for s in trimmed) if trimmed else joined[:250].rstrip("，、；：") + "。"

    groups = [sentences[:1], sentences[1:3]]

    paragraphs = []
    for group in groups:
        para = "".join(group).strip()
        para = _dedupe_summary_phrases(_strip_summary_filler(para))
        if para:
            paragraphs.append(para)

    result = "\n\n".join(paragraphs[:2])
    if len(result) <= 250:
        return result

    trimmed = []
    total = 0
    for sentence in sentences:
        if trimmed and total + len(sentence) > 250:
            break
        trimmed.append(sentence)
        total += len(sentence)
    return "\n\n".join(_dedupe_summary_phrases(s) for s in trimmed[:2]) if trimmed else result[:250].rstrip("，、；：") + "。"


def _apply_post_analysis_review(circ: dict) -> dict:
    """Second-pass deterministic knowledge review after primary analysis."""
    reviewed = _normalize_roles_payload(circ)
    applied_rules: list[dict] = []
    missing_points: list[str] = []
    role_notes: list[str] = []
    added_links: list[dict] = []

    reviewed["summary"] = _normalize_summary_text(_replace_terms(reviewed.get("summary", ""), applied_rules))

    roles = reviewed.get("roles", {})
    topics = reviewed.get("topics", []) or []
    for role_data in roles.values():
        if not isinstance(role_data, dict):
            continue
        role_data["pts"] = [_replace_terms(pt, applied_rules) for pt in role_data.get("pts", [])]
        role_data["acts"] = [_replace_terms(act, applied_rules) for act in role_data.get("acts", [])]
        role_data["pts"] = _dedupe_strings(role_data.get("pts", []))
        role_data["acts"] = _dedupe_strings(role_data.get("acts", []))

    for action in reviewed.get("actions", []):
        action["text"] = _replace_terms(action.get("text", ""), applied_rules)

    supplier = roles.get("supplier")
    source_text = " ".join(
        [
            reviewed.get("title", ""),
            reviewed.get("official", ""),
            reviewed.get("pdf_text", "")[:1200],
            reviewed.get("summary", ""),
        ]
    )
    raw_signal_text = " ".join(
        [
            reviewed.get("title", ""),
            reviewed.get("official", ""),
            reviewed.get("pdf_text", "")[:1200],
        ]
    )
    procurement_keyword_hits = sum(1 for keyword in POST_REVIEW_PROCUREMENT_KEYWORDS if keyword in raw_signal_text)
    has_procurement_signal = (
        ("procurement" in topics and procurement_keyword_hits >= 1)
        or procurement_keyword_hits >= 2
    )
    has_curriculum_signal = (
        "curriculum" in topics
        or any(keyword in raw_signal_text for keyword in POST_REVIEW_CURRICULUM_KEYWORDS)
    )
    finance_keyword_hits = sum(1 for keyword in POST_REVIEW_FINANCE_KEYWORDS if keyword in raw_signal_text)
    has_finance_signal = (
        reviewed.get("grant_info", {}).get("type") in {"applicable", "resource"}
        or ("finance" in topics and finance_keyword_hits >= 1)
        or finance_keyword_hits >= 2
    )

    if isinstance(supplier, dict):
        if has_procurement_signal and not supplier.get("r"):
            supplier["r"] = True
            role_notes.append("偵測到採購/供應商關鍵字，將 supplier 角色標記為相關。")

        if has_procurement_signal and supplier.get("r"):
            if not supplier.get("eligibility"):
                supplier["eligibility"] = "應按學校/招標文件列明的供應商資格、產品規格及提交條件核對。"
                missing_points.append("補回 supplier `eligibility`，提醒需核對招標/報價資格與文件要求。")
            if not supplier.get("contact_unit"):
                supplier["contact_unit"] = "建議以通告或招標文件列明的學校/教育局聯絡單位為準。"
                missing_points.append("補回 supplier `contact_unit`，避免聯絡路徑缺失。")
            if not supplier.get("compliance_ref"):
                supplier["compliance_ref"] = [
                    "避免利益衝突及不當利益往來",
                    "按學校採購程序及招標文件要求提交資料",
                ]
                missing_points.append("補回 supplier `compliance_ref`，加上廉潔及程序要求。")

            supplier["pts"] = _dedupe_strings(supplier.get("pts", []))
            supplier["acts"] = _dedupe_strings(supplier.get("acts", []))
            added_links.extend(KNOWLEDGE_RECOMMENDED_LINKS)

    if has_curriculum_signal:
        curriculum_roles = ["principal", "vice_principal", "subject_head", "panel_chair", "teacher", "eo_admin"]
        curriculum_note = "建議對照課程發展指引及相關學習領域，規劃校本落實、參訪安排或學與教延伸活動。"
        implementation_note = "可按校本課程、學生級別及活動安排，預早協調參與時段、教師分工及學習延伸。"
        school_followup_note = "如屬跨科或全校活動，可配合學校層面的課程規劃、自評或KPM跟進需要。"

        for role_name in curriculum_roles:
            role_data = roles.get(role_name)
            if not isinstance(role_data, dict):
                continue

            if role_name in {"principal", "vice_principal", "subject_head", "panel_chair", "teacher"} and not role_data.get("r"):
                role_data["r"] = True
                role_notes.append(f"偵測到 curriculum 類訊號，將 `{role_name}` 角色標記為相關。")

            if role_data.get("r"):
                role_data.setdefault("pts", [])
                role_data.setdefault("acts", [])

                if curriculum_note not in role_data["pts"]:
                    role_data["pts"].append(curriculum_note)
                if role_name in {"principal", "vice_principal", "eo_admin"} and school_followup_note not in role_data["pts"]:
                    role_data["pts"].append(school_followup_note)
                if role_name in {"subject_head", "panel_chair", "teacher"} and implementation_note not in role_data["acts"]:
                    role_data["acts"].append(implementation_note)

                role_data["pts"] = _dedupe_strings(role_data["pts"])[:3]
                role_data["acts"] = _dedupe_strings(role_data["acts"])[:3]

        missing_points.append("補回 curriculum 類通告的課程落實 / 校本安排提醒。")
        added_links.extend(CURRICULUM_RECOMMENDED_LINKS)

    if has_finance_signal:
        finance_roles = ["principal", "vice_principal", "panel_chair", "eo_admin"]
        finance_overview_note = "留意撥款用途、批核流程、可動用範圍及年度結餘安排，避免偏離通告列明用途。"
        finance_admin_note = "核對申請資格、截止日期、所需證明文件及收支記錄要求，並保留佐證以備查核。"
        finance_followup_note = "按通告要求整理申請／報告文件，跟進發放時序、收支結算及校內存檔安排。"
        finance_planning_note = "如涉及校本計劃或資源申請，應先對應實施目的、預算依據及預期成效。"

        for role_name in finance_roles:
            role_data = roles.get(role_name)
            if not isinstance(role_data, dict):
                continue

            if role_name in {"principal", "vice_principal", "eo_admin"} and not role_data.get("r"):
                role_data["r"] = True
                role_notes.append(f"偵測到 finance 類訊號，將 `{role_name}` 角色標記為相關。")

            if role_data.get("r"):
                role_data.setdefault("pts", [])
                role_data.setdefault("acts", [])

                if role_name in {"principal", "vice_principal"} and finance_overview_note not in role_data["pts"]:
                    role_data["pts"].append(finance_overview_note)
                if role_name == "eo_admin" and finance_admin_note not in role_data["pts"]:
                    role_data["pts"].append(finance_admin_note)
                if role_name in {"panel_chair", "eo_admin"} and finance_followup_note not in role_data["acts"]:
                    role_data["acts"].append(finance_followup_note)
                if role_name == "panel_chair" and finance_planning_note not in role_data["pts"]:
                    role_data["pts"].append(finance_planning_note)

                role_data["pts"] = _dedupe_strings(role_data["pts"])[:3]
                role_data["acts"] = _dedupe_strings(role_data["acts"])[:3]

        missing_points.append("補回 finance 類通告的撥款用途、文件要求及收支存檔提醒。")
        added_links.extend(FINANCE_RECOMMENDED_LINKS)

    has_student_signal = (
        "student" in topics
        or any(keyword in raw_signal_text for keyword in POST_REVIEW_STUDENT_KEYWORDS)
    )

    if has_student_signal:
        student_roles = ["principal", "vice_principal", "subject_head", "panel_chair", "teacher", "eo_admin"]
        student_support_note = "留意學生參與條件、支援安排及活動期間的照顧需要，避免遺漏個別學生的參與支援。"
        parent_notice_note = "如涉及校外活動、比賽或交流安排，宜及早完成家長通知、回條及校內批准流程。"
        implementation_followup_note = "按學生級別、活動安排及支援需要，預早協調人手、分組、風險提示及記錄安排。"
        admin_record_note = "整理學生名單、家長通知、回覆記錄及相關支援文件，並保留校內存檔。"

        for role_name in student_roles:
            role_data = roles.get(role_name)
            if not isinstance(role_data, dict):
                continue

            if role_name in {"vice_principal", "subject_head", "panel_chair", "teacher", "eo_admin"} and not role_data.get("r"):
                role_data["r"] = True
                role_notes.append(f"偵測到 student 類訊號，將 `{role_name}` 角色標記為相關。")

            if role_data.get("r"):
                role_data.setdefault("pts", [])
                role_data.setdefault("acts", [])

                if role_name in {"principal", "vice_principal", "subject_head", "panel_chair"} and student_support_note not in role_data["pts"]:
                    role_data["pts"].append(student_support_note)
                if role_name in {"principal", "vice_principal", "eo_admin"} and parent_notice_note not in role_data["pts"]:
                    role_data["pts"].append(parent_notice_note)
                if role_name in {"subject_head", "panel_chair", "teacher"} and implementation_followup_note not in role_data["acts"]:
                    role_data["acts"].append(implementation_followup_note)
                if role_name == "eo_admin" and admin_record_note not in role_data["acts"]:
                    role_data["acts"].append(admin_record_note)

                role_data["pts"] = _dedupe_strings(role_data["pts"])[:3]
                role_data["acts"] = _dedupe_strings(role_data["acts"])[:3]

        missing_points.append("補回 student 類通告的學生參與支援、家長通知及校內記錄提醒。")
        added_links.extend(STUDENT_RECOMMENDED_LINKS)

    reviewed["knowledge_review"] = {
        "terminology_review": [
            {
                "priority": rule["priority"],
                "from": rule["from"],
                "to": rule["to"],
                "reason": rule["reason"],
            }
            for rule in _unique_applied_rules(applied_rules)
        ],
        "missing_points": missing_points,
        "recommended_links": _merge_link_lists(added_links),
        "role_notes": role_notes,
    }
    reviewed["actions"] = _synthesize_sparse_actions(reviewed)
    if not (reviewed.get("summary") or "").strip():
        reviewed["summary"] = _build_summary_fallback(reviewed)
    return reviewed


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

    # ── Init LLM & Knowledge ──────────────────────────────────────────────────
    client = None
    kn = None
    k1 = None
    role_facts_client = None
    analyzer = None
    if not args.dry_run:
        if not HAS_OPENAI:
            log.error("openai package required (pip install openai)")
            return 1
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            log.error("OPENAI_API_KEY not set. Export it before running.")
            return 1
        
        client = OpenAI(api_key=api_key)
        
        # Load knowledge base (prefer local if exists, else public URL)
        kn_path = Path("dev/knowledge/knowledge.json")
        kn_url = K1_KNOWLEDGE_URL
        kn = KnowledgeStore(client, verbose=args.verbose)
        if kn_path.exists():
            kn.load(str(kn_path))
        else:
            kn.load(kn_url)
        k1 = K1KnowledgeClient(verbose=args.verbose)
        if ROLE_FACTS_PATH.exists():
            role_facts_client = RoleFactsClient(ROLE_FACTS_PATH, verbose=args.verbose)
            
        try:
            analyzer = LLMAnalyzer(
                client,
                model=args.model,
                verbose=args.verbose,
                knowledge_engine=kn,
                k1_client=k1,
                role_facts_client=role_facts_client,
            )
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
            # school-year / custom date range: 0 results is unexpected → fatal
            if getattr(args, 'school_year', False) or date_from_str:
                log.error("No circulars found. Check network access to edb.gov.hk")
                log.error("Tip: Run from Mac Terminal (not the Claude VM)")
                return 1
            # days-N mode: 0 results is valid (weekend / public holiday)
            log.warning("No new circulars in date range (weekend/holiday?). Keeping existing data.")
            # fall through to PHASE 4 with raw=[] — merge fix will preserve existing data

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
                # Carry forward k1 fields from existing record (if previously enriched)
                for k1_key in ("k1_topics", "k1_facts", "k1_guidelines", "role_fact_topics", "role_facts"):
                    if k1_key not in circ:
                        circ[k1_key] = existing[num].get(k1_key, [] if k1_key != "role_facts" else {})
                circ = _normalize_roles_payload(circ)
                circ = _apply_post_analysis_review(circ)
                raw[idx] = circ
                continue

            if not circ.get("pdf_text") and not circ.get("official"):
                log.warning(f"  → No text content — LLM will rely on title only")

            result = analyzer.analyze(circ)
            if result:
                circ.update(result)
                circ = _normalize_roles_payload(circ)
                circ = _apply_post_analysis_review(circ)
                raw[idx] = circ
            else:
                log.warning(f"  → LLM failed — using empty analysis defaults")
                circ.update(_empty_analysis())
                circ = _normalize_roles_payload(circ)

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

    # =========================================================================
    # PHASE 4.5 — K1 BACKFILL
    # Enrich records that have empty k1_topics (analysed before K1 integration,
    # or skipped in incremental mode). Uses LLM-derived circ["topics"] for
    # accurate topic mapping; knowledge/guidelines are cached after first fetch.
    # =========================================================================
    if not args.dry_run and k1:
        k1_backfilled = 0
        for circ in merged_sorted:
            if circ.get("k1_topics"):          # already enriched — skip
                continue
            k1_topics_bf = k1.detect_topics(circ)   # uses circ["topics"] from LLM
            circ["k1_topics"] = k1_topics_bf
            if k1_topics_bf:
                try:
                    circ["k1_facts"]      = k1.fetch_facts(k1_topics_bf)
                    circ["k1_guidelines"] = k1.fetch_guidelines(k1_topics_bf)
                    k1_backfilled += 1
                except Exception as exc:
                    log.warning(f"  K1 backfill {circ.get('number')}: {exc}")
                    circ["k1_facts"]      = []
                    circ["k1_guidelines"] = []
            else:
                circ["k1_facts"]      = []
                circ["k1_guidelines"] = []
        if k1_backfilled:
            log.info(f"  K1 backfill: {k1_backfilled} records enriched")

    if not args.dry_run and role_facts_client:
        role_facts_backfilled = 0
        for circ in merged_sorted:
            if circ.get("role_fact_topics") and circ.get("role_facts"):
                continue
            role_topics_bf = role_facts_client.detect_topics(
                circ,
                preferred_topics=circ.get("k1_topics", []),
            )
            circ["role_fact_topics"] = role_topics_bf
            circ["role_facts"] = role_facts_client.fetch_role_facts(role_topics_bf) if role_topics_bf else {}
            if circ["role_facts"]:
                role_facts_backfilled += 1
        if role_facts_backfilled:
            log.info(f"  Role-facts backfill: {role_facts_backfilled} records enriched")

    output_list = []
    for idx, circ in enumerate(merged_sorted):
        circ = _normalize_roles_payload(circ)
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
            "knowledge_review": circ.get("knowledge_review", None),
            "k1_topics":  circ.get("k1_topics", []),
            "k1_facts":   circ.get("k1_facts", []),
            "k1_guidelines": circ.get("k1_guidelines", []),
            "role_fact_topics": circ.get("role_fact_topics", []),
            "role_facts":  circ.get("role_facts", {}),
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
    print(f"  EDB Circular Scraper + Analyzer  v3.0.36")
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
