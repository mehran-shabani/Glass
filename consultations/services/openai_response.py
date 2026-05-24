from __future__ import annotations

import json
from typing import Any


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def _strip_markdown_fences(content: str) -> str:
    text = (content or "").strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if not lines:
        return text
    if lines[-1].strip() != "```":
        return text

    inner = lines[1:-1]
    return "\n".join(inner).strip()


def parse_structured_output(content: str) -> dict:
    try:
        candidate = _strip_markdown_fences(content)
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def structured_to_markdown(data: dict) -> str:
    if not isinstance(data, dict) or not data:
        return ""

    lines: list[str] = []

    summary = data.get("summary")
    if isinstance(summary, str) and summary.strip():
        lines.append("## Summary")
        lines.append(summary.strip())

    sections = data.get("sections")
    if isinstance(sections, list) and sections:
        lines.append("## Sections")
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            title = sec.get("title") if isinstance(sec.get("title"), str) else ""
            content = sec.get("content") if isinstance(sec.get("content"), str) else ""
            if title.strip():
                lines.append(f"### {title.strip()}")
            if content.strip():
                lines.append(content.strip())

    for key, heading in (
        ("red_flags", "Red Flags"),
        ("missing_data", "Missing Data"),
        ("suggested_next_steps", "Suggested Next Steps"),
    ):
        items = data.get(key)
        if isinstance(items, list) and items:
            lines.append(f"## {heading}")
            for item in items:
                if isinstance(item, str) and item.strip():
                    lines.append(f"- {item.strip()}")

    citations = data.get("citations")
    if isinstance(citations, list) and citations:
        lines.append("## Citations")
        for citation in citations:
            if not isinstance(citation, dict):
                continue
            title = citation.get("title") if isinstance(citation.get("title"), str) else "Untitled"
            source = citation.get("source") if isinstance(citation.get("source"), str) else ""
            url = citation.get("url") if isinstance(citation.get("url"), str) else ""

            line = f"- **{title.strip() or 'Untitled'}**"
            extras = [part.strip() for part in (source, url) if isinstance(part, str) and part.strip()]
            if extras:
                line += f" — {' | '.join(extras)}"
            lines.append(line)

    safety_note = data.get("safety_note")
    if isinstance(safety_note, str) and safety_note.strip():
        lines.append("## Safety Note")
        lines.append(safety_note.strip())

    return "\n\n".join(lines).strip()


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
