import pytest
from unittest.mock import patch

from consultations.models import GlassClinicalRequest
from consultations.services.glass_client import GlassAuthenticationError, GlassRateLimitError
from consultations.services.glass_response import extract_glass_response


def test_extract_response_schemas():
    a = extract_glass_response({"content": "x", "references": [1], "usage": {"a": 1}})
    assert a["content"] == "x" and a["references"] == [1] and a["usage"] == {"a": 1}
    b = extract_glass_response({"clinical_response": "y", "citations": [2]})
    assert b["content"] == "y" and b["citations"] == [2]
    c = extract_glass_response({"message": {"content": "z"}})
    assert c["content"] == "z"
    d = extract_glass_response({"choices": [{"message": {"content": "w"}}]})
    assert d["content"] == "w"
    e = extract_glass_response({"foo": "bar"})
    assert e["detected_schema"] == "unknown_raw_json"


@pytest.mark.django_db
def test_config_never_returns_api_key(client, settings):
    settings.GLASS_API_KEY = "SECRET_KEY"
    r = client.get('/api/glass/config/')
    assert r.status_code == 200
    data = r.json()
    assert data["api_key_configured"] is True
    assert "SECRET_KEY" not in r.content.decode()


@pytest.mark.django_db
def test_debug_messages_endpoint(client):
    with patch('consultations.views.GlassClient.send_messages', return_value={"content": "hello", "references": []}):
        r = client.post('/api/glass/debug/messages/', data={"messages": [{"role": "user", "content": "hi"}], "stream": False}, content_type='application/json')
    assert r.status_code == 200
    assert r.json()["raw_response"]["content"] == "hello"


@pytest.mark.django_db
def test_ask_valid_and_storage(client):
    data = {"content": "Possible DVT", "references": [{"title": "Example"}], "citations": [{"id": 1}], "usage": {"tokens": 10}}
    with patch('consultations.views.GlassClient.send_messages', return_value=data):
        r = client.post('/api/glass/ask/', data={'task_type': 'differential', 'question': 'q', 'patient_context': 'p'}, content_type='application/json')
    assert r.status_code == 200
    rec = GlassClinicalRequest.objects.first()
    assert rec.raw_response["content"] == "Possible DVT"
    assert rec.extracted_content == 'Possible DVT'
    assert rec.references and rec.citations and rec.usage
    assert rec.detected_schema


@pytest.mark.django_db
def test_raw_prompt_sends_direct_question(client):
    with patch('consultations.views.GlassClient.send_messages', return_value={"content": "ok"}) as mocked:
        client.post('/api/glass/ask/', data={'task_type': 'raw_prompt', 'question': 'DIRECT_TEXT', 'patient_context': 'ignored'}, content_type='application/json')
    sent = mocked.call_args.kwargs["messages"][0]["content"]
    assert sent == 'DIRECT_TEXT'


@pytest.mark.django_db
def test_auth_error(client, settings):
    settings.GLASS_API_KEY = 'SECRET'
    with patch('consultations.views.GlassClient.send_messages', side_effect=GlassAuthenticationError('bad')):
        r = client.post('/api/glass/ask/', data={'task_type': 'differential', 'question': 'q'}, content_type='application/json')
    assert r.status_code == 502
    assert 'SECRET' not in r.content.decode()


@pytest.mark.django_db
def test_rate_limit(client):
    with patch('consultations.views.GlassClient.send_messages', side_effect=GlassRateLimitError('rate')):
        r = client.post('/api/glass/ask/', data={'question': 'q'}, content_type='application/json')
    assert r.status_code == 429
