#!/usr/bin/env python3
"""
parse_structure.py
==================
讀取 debug_edb_POST.html，找出每個 EDB 通告號碼的 DOM 位置，
揭示實際 HTML 結構（div / ul / table / span / a）。

執行方式：python3 parse_structure.py
"""
from bs4 import BeautifulSoup
from pathlib import Path
import re

html = Path("debug_edb_POST.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

CIRC_RE = re.compile(r"EDB(?:CM|CL)\d{3}/\d{4}")

print("=" * 70)
print("EDB CIRCULAR NUMBER — DOM CONTEXT")
print("=" * 70)

# Find every element containing a circular number
found_els = []
for el in soup.find_all(string=CIRC_RE):
    parent = el.parent
    found_els.append(parent)

print(f"\nFound {len(found_els)} elements containing circular numbers\n")

for i, el in enumerate(found_els[:5]):   # Show first 5 in detail
    num = CIRC_RE.search(el.get_text()).group(0)
    print(f"── [{i+1}] {num} ──")
    print(f"  tag       : <{el.name}>")
    print(f"  classes   : {el.get('class', [])}")
    print(f"  id        : {el.get('id', '')}")
    print(f"  text      : {el.get_text(strip=True)[:80]!r}")

    # Walk up the DOM tree to show ancestry
    ancestors = []
    p = el.parent
    for _ in range(6):
        if p is None or p.name == "[document]":
            break
        ancestors.append(
            f"<{p.name} class={p.get('class',[])} id={p.get('id','')!r}>"
        )
        p = p.parent
    print(f"  ancestors : {' > '.join(ancestors[:4])}")

    # Show siblings (same-level elements = other columns in the row)
    siblings = el.parent.parent.find_all(recursive=False) if el.parent.parent else []
    print(f"  siblings  : {len(siblings)} elements in parent")
    for j, sib in enumerate(siblings[:6]):
        sib_text = sib.get_text(strip=True)[:60]
        print(f"    [{j}] <{sib.name}> {sib_text!r}")
    print()

# ── Show all <a> links near circular numbers ─────────────────────────
print("=" * 70)
print("ALL LINKS CONTAINING EDB CIRCULAR NUMBERS")
print("=" * 70)
for a in soup.find_all("a"):
    txt = a.get_text(strip=True)
    href = a.get("href", "")
    if CIRC_RE.search(txt) or CIRC_RE.search(href):
        print(f"  <a href={href!r:60s}>  text={txt[:60]!r}")

# ── Show the repeating container structure ────────────────────────────
print("\n" + "=" * 70)
print("REPEATING CONTAINER DETECTION")
print("=" * 70)
# Find parent of first circular element
if found_els:
    # Go up until we find a repeating structure
    sample = found_els[0]
    for _ in range(8):
        p = sample.parent
        if p is None:
            break
        # Count siblings with same tag
        same_tag_siblings = p.parent.find_all(p.name, recursive=False) if p.parent else []
        if len(same_tag_siblings) >= 3:
            print(f"  Repeating container: <{p.name}> "
                  f"class={p.get('class',[])} "
                  f"id={p.get('id','')!r}")
            print(f"  Count: {len(same_tag_siblings)} siblings with same tag")
            print(f"  First item text: {p.get_text(strip=True)[:120]!r}")
            print(f"  Parent: <{p.parent.name}> class={p.parent.get('class',[])} "
                  f"id={p.parent.get('id','')!r}")
            break
        sample = p

print("\n✅ Done.")
