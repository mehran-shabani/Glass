from unittest.mock import patch

import pytest

from consultations.models import ClinicalAIRequest
from consultations.services.openai_client import (
    ClinicalAuthenticationError,
    ClinicalRateLimitError,
)


@pytest.mark.django_db
def test_ask_clinical_qa_returns_200_with_mocked_client(client):
    mocked = {
        "content": "Mocked clinical answer.",
        "raw": {"id": "resp_1"},
        "references": [],
        "citations": [],
        "usage": {"total_tokens": 10},
        "model": "gpt-4.1",
    }
    with patch("consultations.views.ClinicalOpenAIClient") as mock_client:
        mock_client.return_value.generate_clinical_response.return_value = mocked
        response = client.post(
            "/api/clinical/ask/",
            data={"task_type": "clinical_qa", "question": "q", "patient_context": "p"},
            content_type="application/json",
        )

    assert response.status_code == 200


@pytest.mark.django_db
def test_ask_stores_clinical_ai_request_record(client):
    mocked = {
        "content": "Possible DVT",
        "raw": {"id": "resp_2"},
        "references": [{"title": "Ref"}],
        "citations": [{"id": 1}],
        "usage": {"total_tokens": 8},
        "model": "gpt-4.1",
    }
    with patch("consultations.views.ClinicalOpenAIClient") as mock_client:
        mock_client.return_value.generate_clinical_response.return_value = mocked
        response = client.post(
            "/api/clinical/ask/",
            data={"task_type": "clinical_qa", "question": "leg swelling", "patient_context": "recent travel"},
            content_type="application/json",
        )

    assert response.status_code == 200
    record = ClinicalAIRequest.objects.get()
    assert record.task_type == "clinical_qa"
    assert record.raw_response["id"] == "resp_2"


@pytest.mark.django_db
def test_authentication_error_returns_401_without_secret_leak(client, settings):
    settings.OPENAI_API_KEY = "VERY_SECRET_KEY"
    with patch("consultations.views.ClinicalOpenAIClient") as mock_client:
        mock_client.return_value.generate_clinical_response.side_effect = ClinicalAuthenticationError("bad key")
        response = client.post(
            "/api/clinical/ask/",
            data={"task_type": "clinical_qa", "question": "q"},
            content_type="application/json",
        )

    assert response.status_code == 401
    payload = response.json()
    assert "VERY_SECRET_KEY" not in str(payload)
    assert "API key" not in str(payload)


@pytest.mark.django_db
def test_rate_limit_error_returns_429(client):
    with patch("consultations.views.ClinicalOpenAIClient") as mock_client:
        mock_client.return_value.generate_clinical_response.side_effect = ClinicalRateLimitError("limit")
        response = client.post(
            "/api/clinical/ask/",
            data={"task_type": "clinical_qa", "question": "q"},
            content_type="application/json",
        )

    assert response.status_code == 429
