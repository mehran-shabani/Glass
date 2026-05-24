import pytest
from unittest.mock import patch
from consultations.models import GlassClinicalRequest
from consultations.services.glass_client import GlassAuthenticationError,GlassRateLimitError

@pytest.mark.django_db
def test_ask_valid(client):
    data={'content':'Possible DVT','references':[{'title':'Example guideline','url':'https://example.com'}]}
    with patch('consultations.views.GlassClient.ask_clinical_question',return_value=data):
        r=client.post('/api/glass/ask/',data={'task_type':'differential','question':'q','patient_context':'p'},content_type='application/json')
    assert r.status_code==200
    assert GlassClinicalRequest.objects.count()==1
    assert GlassClinicalRequest.objects.first().extracted_content=='Possible DVT'

@pytest.mark.django_db
def test_missing_question(client):
    r=client.post('/api/glass/ask/',data={'task_type':'differential'},content_type='application/json')
    assert r.status_code==400

@pytest.mark.django_db
def test_auth_error(client,settings):
    settings.GLASS_API_KEY='SECRET'
    with patch('consultations.views.GlassClient.ask_clinical_question',side_effect=GlassAuthenticationError('bad')):
        r=client.post('/api/glass/ask/',data={'task_type':'differential','question':'q'},content_type='application/json')
    assert r.status_code==502
    assert 'SECRET' not in r.content.decode()
    assert 'SECRET' not in (GlassClinicalRequest.objects.first().error_message)

@pytest.mark.django_db
def test_rate_limit(client):
    with patch('consultations.views.GlassClient.ask_clinical_question',side_effect=GlassRateLimitError('rate')):
        r=client.post('/api/glass/ask/',data={'question':'q'},content_type='application/json')
    assert r.status_code==429

@pytest.mark.django_db
def test_history_and_detail(client):
    obj=GlassClinicalRequest.objects.create(task_type='clinical_qa',question='q')
    assert client.get('/api/glass/history/').status_code==200
    d=client.get(f'/api/glass/history/{obj.id}/')
    assert d.status_code==200 and d.json()['id']==obj.id
