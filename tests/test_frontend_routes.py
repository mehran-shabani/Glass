from pathlib import Path


def test_frontend_js_uses_clinical_ask_route_only():
    content = Path("webapp/static/webapp/clinical_chat.js").read_text(encoding="utf-8")
    assert "/api/clinical/ask/" in content
    assert "/api/glass/ask/" not in content
