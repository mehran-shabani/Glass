import pytest
from unittest.mock import patch

from consultations.models import GlassClinicalRequest
from consultations.services.openai_response import extract_openai_response


def test_extract_response_schemas():
    a = extract_openai_response({"content": "x", "references": [1], "usage": {"a": 1}})
    assert a["content"] == "x" and a["references"] == [1] and a["usage"] == {"a": 1}


@pytest.mark.django_db
def test_config_never_returns_api_key(client, settings):
    settings.OPENAI_API_KEY = "SECRET_KEY"
    r = client.get('/api/clinical/config/')
    assert r.status_code == 200
    assert "SECRET_KEY" not in r.content.decode()


@pytest.mark.django_db
def test_ask_valid_and_storage(client):
    data = {"content": "Possible DVT", "raw": {"id": "resp_1"}, "references": [{"title": "Example"}], "citations": [{"id": 1}], "usage": {"tokens": 10}, "detected_schema": "openai_responses"}
    with patch('consultations.views.ClinicalOpenAIClient') as mock_client:
        mock_client.return_value.generate_clinical_response.return_value = data
        r = client.post('/api/clinical/ask/', data={'task_type': 'differential', 'question': 'q', 'patient_context': 'p'}, content_type='application/json')
    assert r.status_code == 200
    rec = GlassClinicalRequest.objects.first()
    assert rec.raw_response["id"] == "resp_1"
    assert rec.extracted_content == 'Possible DVT'
