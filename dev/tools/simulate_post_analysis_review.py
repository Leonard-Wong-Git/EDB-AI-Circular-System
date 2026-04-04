#!/usr/bin/env python3
"""Simulate a post-analysis knowledge review layer for one circular.

This is a deterministic prototype to validate the product direction:
1. terminology normalization (ordered)
2. missing-point enrichment
3. link enrichment
4. role-drift stabilization
"""

from __future__ import annotations

import copy
import json
from typing import Any


SAMPLE_CIRCULAR = {
    "number": "EDBCM999/2026",
    "title": "學校採購資訊科技設備及相關服務安排",
    "official": (
        "學校須按既定程序進行採購，邀請承辦商提交報價或投標文件，"
        "並留意利益衝突、供應商溝通及招標文件要求。"
    ),
}


PRIMARY_ANALYSIS = {
    "summary": "這份通告講述學校購買IT設備時要留意報價程序，供應商可跟進學校安排。",
    "roles": {
        "principal": {"r": True, "pts": ["要監督學校買設備流程"], "acts": ["檢視採購安排"]},
        "vice_principal": {"r": False, "pts": [], "acts": []},
        "department_head": {"r": True, "pts": ["需要和行政同事協調購買"], "acts": ["預備需求清單"]},
        "teacher": {"r": False, "pts": [], "acts": []},
        "eo_admin": {"r": True, "pts": ["報價和文件處理"], "acts": ["整理報價文件"]},
        "supplier": {
            "r": True,
            "pts": [
                "供應商要留意學校的報價要求",
                "如涉及投標，需按文件提交內容",
            ],
            "acts": [
                "跟進學校的報價／投標時間表",
                "按要求遞交產品資料",
            ],
            "is_tender": True,
            "procurement_cat": "IT",
            "budget_estimate": None,
            "compliance_ref": [],
            "eligibility": "",
            "contact_unit": "",
        },
    },
    "actions": [
        {"text": "整理採購需求與報價文件", "role": "eo_admin", "dl": None, "note": ""},
        {"text": "供應商預備投標資料", "role": "supplier", "dl": None, "note": ""},
    ],
}


ORDERED_TERMS = [
    {
        "priority": 1,
        "from": "買設備",
        "to": "採購設備",
        "reason": "以採購用語取代口語化表述",
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
        "reason": "將含糊動作改成可執行表述",
    },
]


KNOWLEDGE_LINKS = {
    "finance_supplier": {
        "label": "學校財務管理（供應商視角）",
        "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/about-fin-management/index.html",
        "why": "補充學校採購、利益衝突及供應商溝通的標準參考",
    },
    "icac_procurement": {
        "label": "廉政公署採購參考資料",
        "url": "https://www.icac.org.hk/icac/pb/tc/reference.html",
        "why": "補充防貪及採購誠信要求",
    },
}


def replace_text(text: str, replacements: list[dict[str, Any]], applied: list[dict[str, Any]]) -> str:
    if not text:
        return text
    output = text
    for rule in replacements:
        if rule["from"] in output:
            output = output.replace(rule["from"], rule["to"])
            applied.append(rule)
    return output


def normalize_terms(review_input: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result = copy.deepcopy(review_input)
    applied: list[dict[str, Any]] = []

    result["summary"] = replace_text(result["summary"], ORDERED_TERMS, applied)

    for role_data in result["roles"].values():
        role_data["pts"] = [replace_text(pt, ORDERED_TERMS, applied) for pt in role_data["pts"]]
        role_data["acts"] = [replace_text(act, ORDERED_TERMS, applied) for act in role_data["acts"]]

    for action in result["actions"]:
        action["text"] = replace_text(action["text"], ORDERED_TERMS, applied)

    # de-dup applied rules while preserving priority order
    seen = set()
    unique_applied = []
    for rule in sorted(applied, key=lambda item: item["priority"]):
        key = (rule["from"], rule["to"])
        if key not in seen:
            seen.add(key)
            unique_applied.append(rule)

    return result, unique_applied


def enrich_supplier(review_input: dict[str, Any], circular: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(review_input)
    supplier = result["roles"]["supplier"]
    title_official = f"{circular['title']} {circular['official']}"
    text = title_official + " " + result["summary"] + " " + " ".join(supplier["pts"] + supplier["acts"])

    missing_points = []
    recommended_links = []
    role_notes = []

    procurement_keywords = ["採購", "招標", "報價", "供應商", "承辦商"]
    if any(keyword in text for keyword in procurement_keywords) and not supplier["r"]:
        supplier["r"] = True
        role_notes.append("偵測到採購/供應商關鍵字，將 supplier 角色標記為相關。")

    if supplier["r"]:
        if not supplier["eligibility"]:
            supplier["eligibility"] = "應按學校/招標文件列明的供應商資格、產品規格及提交條件核對。"
            missing_points.append("補回 supplier `eligibility`，提醒需核對招標/報價資格與文件要求。")
        if not supplier["contact_unit"]:
            supplier["contact_unit"] = "建議以通告或招標文件列明的學校/教育局聯絡單位為準。"
            missing_points.append("補回 supplier `contact_unit`，避免聯絡路徑缺失。")
        if not supplier["compliance_ref"]:
            supplier["compliance_ref"] = [
                "避免利益衝突及不當利益往來",
                "按學校採購程序及招標文件要求提交資料",
            ]
            missing_points.append("補回 supplier `compliance_ref`，加上廉潔及程序要求。")

        recommended_links.extend(
            [
                KNOWLEDGE_LINKS["finance_supplier"],
                KNOWLEDGE_LINKS["icac_procurement"],
            ]
        )

    result["knowledge_review"] = {
        "missing_points": missing_points,
        "recommended_links": recommended_links,
        "role_notes": role_notes,
    }
    return result


def build_report(before: dict[str, Any], after: dict[str, Any], applied_terms: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "simulation_goal": "Validate a post-analysis knowledge review layer after primary circular analysis.",
        "before": before,
        "after": after,
        "terminology_review": [
            {
                "priority": rule["priority"],
                "from": rule["from"],
                "to": rule["to"],
                "reason": rule["reason"],
            }
            for rule in applied_terms
        ],
        "feasibility_assessment": {
            "viable": True,
            "why": [
                "術語統一可以用 deterministic ordered rules 先做，風險低。",
                "補漏與補連結可以先限定在 specific fields，不直接重寫整份分析。",
                "角色飄移可先用 keyword + knowledge hints 做守門，再決定是否交由第二輪 LLM review。",
            ],
            "next_step": "If this shape looks right, wire the same review stage into edb_scraper.py after LLMAnalyzer.analyze().",
        },
    }


def main() -> None:
    normalized, applied_terms = normalize_terms(PRIMARY_ANALYSIS)
    enriched = enrich_supplier(normalized, SAMPLE_CIRCULAR)
    report = build_report(PRIMARY_ANALYSIS, enriched, applied_terms)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
