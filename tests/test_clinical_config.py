import pytest


@pytest.mark.django_db
def test_config_never_returns_api_key(client, settings):
    settings.OPENAI_API_KEY = "SUPER_SECRET"
    response = client.get('/api/clinical/config/')

    assert response.status_code == 200
    body = response.json()
    assert "SUPER_SECRET" not in response.content.decode()
    assert "OPENAI_API_KEY" not in body


@pytest.mark.django_db
def test_config_reports_api_key_configured_flag(client, settings):
    settings.OPENAI_API_KEY = ""
    response = client.get('/api/clinical/config/')
    assert response.status_code == 200
    assert response.json()["api_key_configured"] is False

    settings.OPENAI_API_KEY = "present"
    response = client.get('/api/clinical/config/')
    assert response.status_code == 200
    assert response.json()["api_key_configured"] is True
