from consultations.services.openai_response import parse_structured_output


def test_parse_structured_output_handles_valid_json():
    payload = '{"summary": "ok", "sections": []}'
    parsed = parse_structured_output(payload)
    assert parsed == {"summary": "ok", "sections": []}


def test_parse_structured_output_handles_markdown_fenced_json():
    payload = """```json
{"summary": "ok"}
```"""
    parsed = parse_structured_output(payload)
    assert parsed == {"summary": "ok"}


def test_parse_structured_output_returns_empty_for_invalid_json():
    parsed = parse_structured_output("{invalid")
    assert parsed == {}
