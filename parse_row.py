#!/usr/bin/env python3
"""
parse_row.py
============
顯示第一條 EDB 通告的完整 row 結構（所有 cells + 所有 links + 日期格式）。
執行方式：python3 parse_row.py
"""
from bs4 import BeautifulSoup
from pathlib import Path
import re

html = Path("debug_edb_POST.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

# Find first row with circularResultRow cells
target_row = None
for tr in soup.find_all("tr"):
    if tr.find("td", class_="circularResultRow"):
        target_row = tr
        break

if not target_row:
    print("❌ No circularResultRow found")
    exit()

print("=" * 70)
print("FIRST CIRCULAR ROW — FULL BREAKDOWN")
print("=" * 70)

cells = target_row.find_all("td")
print(f"\nTotal <td> cells in row: {len(cells)}")

for ci, cell in enumerate(cells):
    print(f"\n── Cell[{ci}] ──")
    print(f"  classes : {cell.get('class', [])}")
    print(f"  text    : {cell.get_text(strip=True)[:120]!r}")

    # All divs
    for di, div in enumerate(cell.find_all("div", recursive=False)):
        print(f"  div[{di}] class={div.get('class',[])} text={div.get_text(strip=True)[:80]!r}")
        for ddi, ddiv in enumerate(div.find_all("div", recursive=False)):
            print(f"    subdiv[{ddi}] class={ddiv.get('class',[])} text={ddiv.get_text(strip=True)[:80]!r}")

    # All links in this cell
    links = cell.find_all("a")
    if links:
        print(f"  links ({len(links)}):")
        for a in links:
            print(f"    href={a.get('href','')!r}  text={a.get_text(strip=True)[:60]!r}")
    else:
        print(f"  links: (none)")

    # Any onclick or data attributes
    for el in cell.find_all(True):
        onclick = el.get("onclick", "")
        if onclick:
            print(f"  onclick on <{el.name}>: {onclick[:120]!r}")

print("\n" + "=" * 70)
print("ALL ROWS — DATE + CIRCULAR NUMBER + LINK SUMMARY")
print("=" * 70)

count = 0
for tr in soup.find_all("tr"):
    remark = tr.find("div", class_="circulars_result_remark")
    if not remark:
        continue
    num_m = re.search(r"EDB(?:CM|CL)\d{3}/\d{4}", remark.get_text())
    if not num_m:
        continue
    num = num_m.group(0)

    cells = tr.find_all("td")
    date = cells[0].get_text(strip=True) if cells else "?"

    # Links in whole row
    row_links = [(a.get("href",""), a.get_text(strip=True)[:30]) for a in tr.find_all("a")]
    # onclicks in whole row
    onclicks = [el.get("onclick","")[:80] for el in tr.find_all(True) if el.get("onclick")]

    print(f"\n  {num}  date={date!r}")
    if row_links:
        for href, txt in row_links:
            print(f"    link: href={href!r}  text={txt!r}")
    if onclicks:
        for oc in onclicks:
            print(f"    onclick: {oc!r}")
    if not row_links and not onclicks:
        print(f"    (no links or onclicks)")
    count += 1

print(f"\nTotal circulars: {count}")
print("\n✅ Done.")
