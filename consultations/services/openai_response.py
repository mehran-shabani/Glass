from __future__ import annotations

import json
from typing import Any


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def extract_openai_response(raw: dict) -> dict:
    content = ""
    references = []
    citations = []
    usage = {}
    schema = "unknown_raw_json"

    if raw.get("content") is not None:
        content = raw.get("content")
        schema = "content/references/usage"
    elif raw.get("response") is not None:
        content = raw.get("response")
        schema = "response"
    elif raw.get("answer") is not None:
        content = raw.get("answer")
        schema = "answer"
    elif raw.get("clinical_response") is not None:
        content = raw.get("clinical_response")
        schema = "clinical_response"
    elif isinstance(raw.get("message"), dict) and raw["message"].get("content") is not None:
        content = raw["message"]["content"]
        schema = "message.content"
    elif raw.get("output_text") is not None:
        content = raw.get("output_text")
        schema = "output_text"
    elif isinstance(raw.get("choices"), list) and raw["choices"] and isinstance(raw["choices"][0], dict):
        content = (raw["choices"][0].get("message") or {}).get("content", "")
        if content:
            schema = "choices.message.content"
    elif isinstance(raw.get("data"), dict) and raw["data"].get("content") is not None:
        content = raw["data"]["content"]
        schema = "data.content"
    elif isinstance(raw.get("data"), dict) and raw["data"].get("response") is not None:
        content = raw["data"]["response"]
        schema = "data.response"
    elif isinstance(raw.get("result"), dict) and raw["result"].get("content") is not None:
        content = raw["result"]["content"]
        schema = "result.content"
    elif isinstance(raw.get("result"), dict) and raw["result"].get("response") is not None:
        content = raw["result"]["response"]
        schema = "result.response"

    for key in ("references", "citations", "sources"):
        if isinstance(raw.get(key), list):
            references = raw.get(key) or []
            break
    if not references and isinstance(raw.get("metadata"), dict):
        references = raw["metadata"].get("references") or raw["metadata"].get("citations") or []
    if not references and isinstance(raw.get("data"), dict):
        references = raw["data"].get("references") or []
    if not references and isinstance(raw.get("result"), dict):
        references = raw["result"].get("references") or []

    citations = raw.get("citations") if isinstance(raw.get("citations"), list) else references

    if isinstance(raw.get("usage"), dict):
        usage = raw.get("usage") or {}
    elif isinstance(raw.get("metadata"), dict) and isinstance(raw["metadata"].get("usage"), dict):
        usage = raw["metadata"].get("usage") or {}
    elif isinstance(raw.get("data"), dict) and isinstance(raw["data"].get("usage"), dict):
        usage = raw["data"].get("usage") or {}
    elif isinstance(raw.get("result"), dict) and isinstance(raw["result"].get("usage"), dict):
        usage = raw["result"].get("usage") or {}

    if not content:
        content = pretty_json(raw)
        schema = "unknown_raw_json"

    return {
        "content": content,
        "references": references if isinstance(references, list) else [],
        "citations": citations if isinstance(citations, list) else [],
        "usage": usage if isinstance(usage, dict) else {},
        "detected_schema": schema,
        "raw": raw,
    }
