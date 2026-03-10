#!/usr/bin/env python3
"""
parse_form.py
=============
讀取 debug_edb_GET.html，顯示完整表單結構 + 所有按鈕名稱。
幫助診斷 POST 搜尋為何沒有執行。

執行方式：python3 parse_form.py
"""
from bs4 import BeautifulSoup
from pathlib import Path

html = Path("debug_edb_GET.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

print("=" * 70)
print("FORM STRUCTURE IN debug_edb_GET.html")
print("=" * 70)

for fi, form in enumerate(soup.find_all("form")):
    print(f"\n── FORM[{fi}] ──")
    print(f"  id     = {form.get('id','')!r}")
    print(f"  name   = {form.get('name','')!r}")
    print(f"  action = {form.get('action','')!r}")
    print(f"  method = {form.get('method','')!r}")

    print("\n  ALL INPUTS:")
    for inp in form.find_all("input"):
        itype = inp.get("type","text")
        iname = inp.get("name","")
        ival  = inp.get("value","")
        iid   = inp.get("id","")
        if itype == "hidden":
            print(f"    [hidden]  name={iname!r:55s}  val={ival[:50]!r}")
        elif itype in ("submit","button","image"):
            print(f"    [BUTTON]  name={iname!r:55s}  value={ival!r}  id={iid!r}")
        elif itype == "text":
            print(f"    [text  ]  name={iname!r:55s}  id={iid!r}")
        else:
            print(f"    [{itype:7}]  name={iname!r:55s}  id={iid!r}")

    print("\n  ALL SELECT / DROPDOWNS:")
    for sel in form.find_all("select"):
        sname = sel.get("name","")
        sid   = sel.get("id","")
        opts  = [(o.get("value",""), o.get_text(strip=True)) for o in sel.find_all("option")]
        print(f"    [select]  name={sname!r}  id={sid!r}")
        for v,t in opts[:8]:
            print(f"              option val={v!r:6}  text={t!r}")

    print("\n  ALL BUTTONS (button tag):")
    for btn in form.find_all("button"):
        print(f"    type={btn.get('type','')!r}  name={btn.get('name','')!r}  "
              f"id={btn.get('id','')!r}  text={btn.get_text(strip=True)[:40]!r}")

print("\n" + "=" * 70)
print("JAVASCRIPT HINTS (search-related functions in page):")
print("=" * 70)
import re
scripts = soup.find_all("script")
for sc in scripts:
    text = sc.get_text()
    for line in text.splitlines():
        if any(kw in line.lower() for kw in ["search", "btnSearch", "dopostback",
                                              "click", "submit", "circular"]):
            stripped = line.strip()
            if stripped:
                print(f"  {stripped[:120]}")
