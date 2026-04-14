#!/usr/bin/env python3
"""
test_k1_smoke.py — K1 backend semantic smoke test for EDB Circular AI Analysis System.

Goals:
1. Verify local K1-related contract files are readable and aligned
2. Verify topic detection / fact assembly / prompt injection wiring
3. If OPENAI_API_KEY is available, also verify:
   - semantic retrieval via KnowledgeStore (0.45 threshold)
   - end-to-end LLM analyze() output fields

Usage:
  python3 dev/tools/test_k1_smoke.py
  python3 dev/tools/test_k1_smoke.py --numbers EDBCM053/2026 EDBCM048/2026
  python3 dev/tools/test_k1_smoke.py --skip-llm
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, Union


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from edb_scraper import (  # noqa: E402
    K1_KNOWLEDGE_URL,
    KnowledgeStore,
    K1KnowledgeClient,
    LLMAnalyzer,
    ROLE_FACTS_PATH,
    RoleFactsClient,
)

try:  # noqa: E402
    from openai import OpenAI
except Exception:  # pragma: no cover - local optional dep
    OpenAI = None


DEFAULT_NUMBERS = [
    "EDBCM053/2026",
    "EDBCM048/2026",
]


def load_circulars(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("circulars"), list):
        return payload["circulars"]
    if isinstance(payload, list):
        return payload
    raise ValueError(f"Unsupported circular payload shape: {path}")


def get_samples(circulars: list[dict[str, Any]], numbers: list[str]) -> list[dict[str, Any]]:
    by_number = {item.get("number"): item for item in circulars}
    samples = []
    for number in numbers:
        circ = by_number.get(number)
        if circ:
            samples.append(circ)
    if not samples:
        raise ValueError(f"No matching circulars found for: {numbers}")
    return samples


def ensure_openai_client() -> Any:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return None
    return OpenAI(api_key=api_key)


def schema_snapshot(role_facts_path: Path) -> dict[str, Any]:
    data = json.loads(role_facts_path.read_text(encoding="utf-8"))
    topic_keys = [k for k in data.keys() if not k.startswith("_")]
    topic_shape = {}
    for topic in topic_keys:
        node = data.get(topic, {})
        if isinstance(node, dict):
            topic_shape[topic] = sorted([k for k in node.keys() if not k.startswith("_")])
    return {
        "path": str(role_facts_path),
        "meta_version": data.get("_meta", {}).get("version"),
        "topics": topic_keys,
        "topic_shape": topic_shape,
    }


def compact_text(text: str, limit: int = 160) -> str:
    text = (text or "").strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def inspect_sample(
    circ: dict[str, Any],
    k1_client: K1KnowledgeClient,
    role_facts_client: RoleFactsClient,
    analyzer: LLMAnalyzer,
    knowledge_store: Optional[KnowledgeStore],
    run_llm: bool,
) -> dict[str, Any]:
    circ_copy = dict(circ)
    topic_guess = k1_client.detect_topics(circ_copy)
    k1_facts = k1_client.fetch_facts(topic_guess)
    k1_guidelines = k1_client.fetch_guidelines(topic_guess)
    role_topics = role_facts_client.detect_topics(circ_copy, preferred_topics=topic_guess)
    role_facts = role_facts_client.fetch_role_facts(role_topics)
    relevant_facts = []
    if knowledge_store:
        relevant_facts = knowledge_store.find_relevant(
            f"{circ_copy.get('title', '')} {circ_copy.get('official', '')}"
        )
    prompt = analyzer._build_prompt(  # smoke test: prompt assembly verification
        circ_copy,
        relevant_facts,
        k1_facts,
        k1_guidelines,
        role_facts,
    )

    result: dict[str, Any] = {
        "number": circ_copy.get("number"),
        "title": circ_copy.get("title"),
        "k1_topics": topic_guess,
        "k1_facts_count": len(k1_facts),
        "k1_guidelines_count": len(k1_guidelines),
        "role_fact_topics": role_topics,
        "role_fact_role_counts": {k: len(v) for k, v in role_facts.items()},
        "semantic_relevant_facts_count": len(relevant_facts),
        "prompt_has_policy_facts": "【相關政策事實】" in prompt,
        "prompt_has_guidelines": "【相關指引文件】" in prompt,
        "prompt_has_role_facts": "【EDB學校管理知識中心角色事實】" in prompt,
        "prompt_preview": compact_text(prompt, 260),
    }

    if run_llm:
        llm_result = analyzer.analyze(dict(circ_copy))
        result["llm"] = {
            "ok": llm_result is not None,
            "summary": compact_text((llm_result or {}).get("summary", ""), 180),
            "impact": (llm_result or {}).get("impact"),
            "topics": (llm_result or {}).get("topics"),
            "actions_count": len((llm_result or {}).get("actions", []) or []),
        }
    else:
        result["llm"] = {"ok": False, "skipped": True}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "circulars.json"),
        help="Path to circulars.json",
    )
    parser.add_argument(
        "--numbers",
        nargs="*",
        default=DEFAULT_NUMBERS,
        help="Specific circular numbers to inspect",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip OpenAI-powered semantic retrieval and end-to-end analyze()",
    )
    args = parser.parse_args()

    circulars = load_circulars(Path(args.input))
    samples = get_samples(circulars, args.numbers)
    role_facts_path = (PROJECT_ROOT / ROLE_FACTS_PATH).resolve() if not ROLE_FACTS_PATH.is_absolute() else ROLE_FACTS_PATH

    client = None if args.skip_llm else ensure_openai_client()
    can_run_llm = client is not None

    k1_client = K1KnowledgeClient(verbose=False)
    role_facts_client = RoleFactsClient(role_facts_path, verbose=False)
    knowledge_store = None
    if can_run_llm:
        knowledge_store = KnowledgeStore(client, verbose=False)
        knowledge_store.load(K1_KNOWLEDGE_URL)
    analyzer = LLMAnalyzer(
        client=client,
        verbose=False,
        knowledge_engine=knowledge_store,
        k1_client=k1_client,
        role_facts_client=role_facts_client,
    )

    report = {
        "input": str(Path(args.input).resolve()),
        "role_facts": schema_snapshot(role_facts_path),
        "llm_enabled": can_run_llm,
        "semantic_threshold": getattr(knowledge_store, "threshold", 0.45) if knowledge_store else 0.45,
        "samples": [],
    }

    for circ in samples:
        report["samples"].append(
            inspect_sample(
                circ,
                k1_client=k1_client,
                role_facts_client=role_facts_client,
                analyzer=analyzer,
                knowledge_store=knowledge_store,
                run_llm=can_run_llm,
            )
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
