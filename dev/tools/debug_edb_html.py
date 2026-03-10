#!/usr/bin/env python3
"""
debug_edb_html.py
=================
診斷工具：抓取 EDB 通告列表頁面的實際 HTML，存為本地檔案以便分析。

執行方式：
  python3 debug_edb_html.py

輸出：
  debug_edb_GET.html   — GET 初始頁面（含 ViewState）
  debug_edb_POST.html  — POST 搜尋結果頁面
  debug_edb_info.txt   — 關鍵診斷資訊（表單字段、表格結構）
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

URL = "https://applications.edb.gov.hk/circular/circular.aspx?langno=2"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8",
}

def main():
    s = requests.Session()
    s.headers.update(HEADERS)

    # ── Step 1: GET ──────────────────────────────────────────────────────────
    print("Step 1: GET initial page...")
    r = s.get(URL, timeout=30)
    r.encoding = r.apparent_encoding or "utf-8"
    print(f"  Status: {r.status_code}  Size: {len(r.text):,} chars")

    with open("debug_edb_GET.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("  Saved → debug_edb_GET.html")

    soup_get = BeautifulSoup(r.text, "html.parser")

    # ── Extract ALL form fields (for diagnosis) ───────────────────────────
    info_lines = ["=" * 60, "EDB HTML DIAGNOSIS", "=" * 60, ""]

    info_lines.append("── ALL HIDDEN INPUTS ──")
    for inp in soup_get.find_all("input"):
        itype = inp.get("type", "text")
        iname = inp.get("name", "(no name)")
        ival  = inp.get("value", "")[:80]
        if itype == "hidden":
            info_lines.append(f"  HIDDEN  name={iname!r}  val={ival!r}")
        else:
            info_lines.append(f"  {itype.upper():8} name={iname!r}")

    info_lines.append("")
    info_lines.append("── ALL SELECT FIELDS ──")
    for sel in soup_get.find_all("select"):
        sname = sel.get("name", "(no name)")
        opts  = [(o.get("value",""), o.get_text(strip=True)) for o in sel.find_all("option")]
        info_lines.append(f"  SELECT  name={sname!r}")
        for v, t in opts[:10]:
            info_lines.append(f"    option value={v!r}  text={t!r}")

    # ── Extract ViewState ─────────────────────────────────────────────────
    vs = {}
    for name in ["__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION",
                 "__EVENTTARGET", "__EVENTARGUMENT"]:
        el = soup_get.find("input", {"name": name})
        if el:
            vs[name] = el.get("value", "")

    info_lines.append("")
    info_lines.append("── VIEWSTATE FIELDS FOUND ──")
    for k, v in vs.items():
        info_lines.append(f"  {k}: {len(v)} chars  (first 40: {v[:40]!r})")

    # ── Step 2: POST ─────────────────────────────────────────────────────
    print("\nStep 2: POST search (past 30 days)...")
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
    today  = datetime.now().strftime("%d/%m/%Y")
    print(f"  Date range: {cutoff} – {today}")

    post_data = {
        **vs,
        "__EVENTTARGET":  "",
        "__EVENTARGUMENT": "",
        "ctl00$currentSection": "2",
        "ctl00$MainContentPlaceHolder$lbltab_circular": "通告",
        "ctl00$MainContentPlaceHolder$ddlSchoolType2":  "",
        "ctl00$MainContentPlaceHolder$ddlCircularType": "",
        "ctl00$MainContentPlaceHolder$txtPeriodFrom":   cutoff,
        "ctl00$MainContentPlaceHolder$txtPeriodTo":     today,
        "ctl00$MainContentPlaceHolder$btnSearch2":      "搜尋",
    }

    r2 = s.post(URL, data=post_data, timeout=30)
    r2.encoding = r2.apparent_encoding or "utf-8"
    print(f"  Status: {r2.status_code}  Size: {len(r2.text):,} chars")

    with open("debug_edb_POST.html", "w", encoding="utf-8") as f:
        f.write(r2.text)
    print("  Saved → debug_edb_POST.html")

    soup_post = BeautifulSoup(r2.text, "html.parser")

    # ── Analyze POST response ─────────────────────────────────────────────
    info_lines.append("")
    info_lines.append("── ALL TABLES IN POST RESPONSE ──")
    for i, tbl in enumerate(soup_post.find_all("table")):
        rows = tbl.find_all("tr")
        cells0 = rows[0].find_all(["th", "td"]) if rows else []
        tbl_text = tbl.get_text()[:200].replace("\n", " ")
        has_edb  = bool(re.search(r"EDB(?:CM|CL)\d{3}", tbl_text))
        info_lines.append(
            f"  Table[{i}]: {len(rows)} rows × {len(cells0)} cols  "
            f"EDB#={has_edb}  preview={tbl_text[:80]!r}"
        )

    info_lines.append("")
    info_lines.append("── EDB CIRCULAR NUMBERS FOUND IN POST RESPONSE ──")
    matches = re.findall(r"EDB(?:CM|CL)\d{3}/\d{4}", r2.text)
    if matches:
        for m in sorted(set(matches)):
            info_lines.append(f"  {m}")
    else:
        info_lines.append("  (none found — search may not have executed)")

    info_lines.append("")
    info_lines.append("── KEYWORDS IN PAGE (for debugging) ──")
    page_lower = r2.text.lower()
    for kw in ["gridview", "datagrid", "repeater", "listview",
                "no record", "no circular", "沒有", "找不到", "error"]:
        if kw in page_lower:
            info_lines.append(f"  FOUND keyword: {kw!r}")

    # ── Check if POST returned same page as GET (no search triggered) ──
    if len(r2.text) == len(r.text):
        info_lines.append("")
        info_lines.append("⚠️  POST response same size as GET — search may NOT have been triggered")
        info_lines.append("   Possible cause: wrong button field name or form field names")

    # ── Write info file ───────────────────────────────────────────────────
    info_txt = "\n".join(info_lines)
    with open("debug_edb_info.txt", "w", encoding="utf-8") as f:
        f.write(info_txt)
    print("\n  Saved → debug_edb_info.txt")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(info_txt[info_txt.find("── ALL TABLES"):])
    print("=" * 60)
    print("\n✅ Done. Please share debug_edb_info.txt for analysis.")

if __name__ == "__main__":
    main()
