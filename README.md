# Agent-Helssa MVP with OpenAI Clinical API

## OpenAI API test

`.env` example:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1
OPENAI_TIMEOUT_SECONDS=120
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_OUTPUT_TOKENS=1200
```

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Clinical UI:

```bash
curl http://127.0.0.1:8000/clinical/
```

Clinical config:

```bash
curl http://127.0.0.1:8000/api/clinical/config/
```

Clinical ask:

```bash
curl -X POST http://127.0.0.1:8000/api/clinical/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "differential",
    "patient_context": "54M, smoker, recent long flight, unilateral calf swelling and pain, no fever.",
    "question": "Generate prioritized differential diagnosis and recommended diagnostic workup."
  }'
```

History endpoints:

- `GET /api/clinical/history/`
- `GET /api/clinical/history/<id>/`

CLI direct API test:

```bash
python scripts/test_openai_api.py
```
