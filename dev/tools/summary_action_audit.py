#!/usr/bin/env python3
"""Audit circular summary/action quality without rerunning the LLM.

Purpose:
- provide a fast release gate for summary/action regressions
- scan an existing circulars.json and surface suspicious records
- reduce the need to run a 1+ hour school-year workflow for every copy tweak
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SUMMARY_FILLER_MARKERS = [
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
    "根據標題可推測",
    "根據標題可判斷",
    "可推斷",
    "初步判讀",
    "另行通知",
    "後續通知",
]

ROLE_KEYS = [
    "principal",
    "vice_principal",
    "subject_head",
    "panel_chair",
    "teacher",
    "eo_admin",
    "supplier",
]


def load_circulars(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict):
        return obj.get("circulars", [])
    if isinstance(obj, list):
        return obj
    raise ValueError("Unsupported circulars payload shape")


def summary_paragraphs(summary: str) -> list[str]:
    return [p.strip() for p in (summary or "").split("\n\n") if p.strip()]


def role_action_count(circ: dict[str, Any]) -> int:
    total = 0
    roles = circ.get("roles") or {}
    for key in ROLE_KEYS:
        role = roles.get(key)
        if isinstance(role, dict):
            total += len(role.get("acts") or [])
    return total


def has_filler(summary: str) -> bool:
    return any(marker in (summary or "") for marker in SUMMARY_FILLER_MARKERS)


def repeated_supplier_phrase(summary: str) -> bool:
    text = summary or ""
    return (
        "供應商／供應商" in text
        or "供應商／供應商／承辦商" in text
        or "供應商／供應商／供應商" in text
    )


def classify(circ: dict[str, Any]) -> dict[str, Any]:
    summary = circ.get("summary") or ""
    paragraphs = summary_paragraphs(summary)
    top_actions = circ.get("actions") or []
    role_actions = role_action_count(circ)
    chars = len(summary)
    issues: list[str] = []

    if has_filler(summary):
        issues.append("summary_filler")
    if repeated_supplier_phrase(summary):
        issues.append("summary_repeated_supplier")
    if not top_actions and role_actions > 0:
        issues.append("missing_top_actions")
    if chars < 60:
        issues.append("summary_too_short")
    if chars > 320:
        issues.append("summary_too_long")
    if len(paragraphs) > 3:
        issues.append("summary_too_many_paragraphs")
    if len(paragraphs) == 1 and chars > 120:
        issues.append("summary_single_paragraph")

    return {
        "id": circ.get("id"),
        "number": circ.get("number"),
        "title": circ.get("title"),
        "topics": circ.get("topics") or [],
        "summary_chars": chars,
        "summary_paragraphs": len(paragraphs),
        "top_actions": len(top_actions),
        "role_actions": role_actions,
        "issues": issues,
        "summary_preview": summary.replace("\n", " ")[:180],
    }


def build_report(circulars: list[dict[str, Any]], max_examples: int) -> dict[str, Any]:
    rows = [classify(c) for c in circulars]
    flagged = [r for r in rows if r["issues"]]

    categories = [
        "summary_filler",
        "missing_top_actions",
        "summary_too_short",
        "summary_too_long",
        "summary_single_paragraph",
        "summary_too_many_paragraphs",
        "summary_repeated_supplier",
    ]

    by_issue: dict[str, list[dict[str, Any]]] = {}
    for category in categories:
        hits = [r for r in rows if category in r["issues"]]
        by_issue[category] = hits[:max_examples]

    return {
        "total_circulars": len(circulars),
        "flagged_circulars": len(flagged),
        "issue_counts": {category: len([r for r in rows if category in r["issues"]]) for category in categories},
        "examples": by_issue,
    }


def print_report(report: dict[str, Any]) -> None:
    print("EDB Summary/Action Audit")
    print("=" * 60)
    print(f"Total circulars:   {report['total_circulars']}")
    print(f"Flagged circulars: {report['flagged_circulars']}")
    print("")
    print("Issue counts")
    print("-" * 60)
    for key, value in report["issue_counts"].items():
        print(f"{key:28} {value}")

    for issue, examples in report["examples"].items():
        if not examples:
            continue
        print("")
        print(issue)
        print("-" * 60)
        for item in examples:
            print(
                f"{item['number']} | topics={','.join(item['topics']) or '-'} | "
                f"chars={item['summary_chars']} | paras={item['summary_paragraphs']} | "
                f"top_actions={item['top_actions']} | role_actions={item['role_actions']}"
            )
            print(f"  {item['summary_preview']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit summary/action quality in circulars.json")
    parser.add_argument(
        "--input",
        default="./circulars.json",
        help="Path to circulars.json (default: ./circulars.json)",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=5,
        help="Max examples shown per issue category (default: 5)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON",
    )
    args = parser.parse_args()

    circulars = load_circulars(Path(args.input))
    report = build_report(circulars, args.max_examples)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
