#!/usr/bin/env python3
"""
test_llm.py — 對第一條通告單獨測試 LLM，顯示完整錯誤訊息。
執行方式：python3 test_llm.py
"""
import json, os
from openai import OpenAI

# ── Load first circular from circulars.json ──
data   = json.load(open("circulars.json"))
circ   = data["circulars"][0]
number = circ["number"]
title  = circ["title"]
pdf_text = circ.get("pdf_text", "")[:3000]

print(f"Testing: {number} — {title[:50]}")
print(f"PDF text length: {len(pdf_text)} chars")
print()

# ── Minimal prompt (skip full schema, just test connection) ──
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Test 1: Basic call (no structured output)
print("── Test 1: Basic call (no structured output) ──")
try:
    resp = client.chat.completions.create(
        model="gpt-5-nano",
        temperature=1,
        max_completion_tokens=100,
        messages=[
            {"role": "user", "content": f"用一句話總結這個通告：{title}"}
        ],
    )
    print(f"✅ Basic call OK: {resp.choices[0].message.content[:100]}")
except Exception as e:
    print(f"❌ Basic call FAILED: {e}")
    exit(1)

print()

# Test 2: Structured output with minimal schema
print("── Test 2: Structured output (minimal schema) ──")
MINI_SCHEMA = {
    "name": "test",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["summary", "impact"],
        "properties": {
            "summary": {"type": "string"},
            "impact":  {"type": "string", "enum": ["high", "mid", "low"]},
        }
    }
}
try:
    resp2 = client.chat.completions.create(
        model="gpt-5-nano",
        temperature=1,
        max_completion_tokens=8000,   # reasoning model needs more tokens
        response_format={"type": "json_schema", "json_schema": MINI_SCHEMA},
        messages=[
            # gpt-5-nano = reasoning model, use "developer" not "system"
            {"role": "developer", "content": "你是 EDB 通告分析助手，請用繁體中文回答。"},
            {"role": "user",      "content": f"分析此通告：{title}\n\n{pdf_text[:500]}"}
        ],
    )
    result = json.loads(resp2.choices[0].message.content)
    print(f"✅ Structured output OK:")
    print(f"   summary: {result.get('summary','')[:80]}")
    print(f"   impact:  {result.get('impact')}")
except Exception as e:
    print(f"❌ Structured output FAILED: {e}")

print()
print("── Test 3: Check finish_reason of first LLM run ──")
try:
    from edb_scraper import CIRCULAR_SCHEMA, SYSTEM_PROMPT, LLM_TEMPERATURE
    prompt = f"通告號：{number}\n標題：{title}\n\nPDF 內容（節錄）：\n{pdf_text}"
    resp3 = client.chat.completions.create(
        model="gpt-5-nano",
        temperature=LLM_TEMPERATURE,
        max_completion_tokens=16000,  # reasoning model needs large budget
        response_format={"type": "json_schema", "json_schema": CIRCULAR_SCHEMA},
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},  # reasoning model: developer not system
            {"role": "user",      "content": prompt},
        ],
    )
    finish = resp3.choices[0].finish_reason
    raw    = resp3.choices[0].message.content
    print(f"finish_reason: {finish}")
    print(f"raw output length: {len(raw)} chars")
    if raw:
        parsed = json.loads(raw)
        print(f"✅ Full schema OK!")
        print(f"   summary: {parsed.get('summary','')[:100]}")
        print(f"   impact:  {parsed.get('impact')}")
        print(f"   tags:    {parsed.get('tags')}")
    else:
        print("❌ Empty response content")
except Exception as e:
    print(f"❌ Full schema FAILED: {e}")
