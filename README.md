# Agent-Helssa MVP with Glass API

## Real Glass API test

`.env` example:

```env
GLASS_API_KEY=your_real_key_here
GLASS_API_BASE_URL=https://glass.health/api/external/v2
GLASS_API_VERSION=glass-5.5
GLASS_API_TIMEOUT_SECONDS=120
GLASS_API_AUTH_HEADER=Authorization
GLASS_API_AUTH_SCHEME=Bearer
GLASS_API_DEBUG_RAW_RESPONSE=true
```

Install:

```bash
pip install -r requirements.txt
```

Migrate:

```bash
python manage.py migrate
```

Run:

```bash
python manage.py runserver
```

Check safe config:

```bash
curl http://127.0.0.1:8000/api/glass/config/
```

Direct debug call:

```bash
curl -X POST http://127.0.0.1:8000/api/glass/debug/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "version": "glass-5.5",
    "messages": [
      {
        "role": "user",
        "content": "Return a short clinical-style answer: What are common causes of acute unilateral leg swelling?"
      }
    ],
    "stream": false
  }'
```

Clinical wrapped call:

```bash
curl -X POST http://127.0.0.1:8000/api/glass/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "differential",
    "patient_context": "54M, smoker, recent long flight, unilateral calf swelling and pain, no fever.",
    "question": "Generate prioritized differential diagnosis and recommended diagnostic workup."
  }'
```

CLI direct API test:

```bash
python scripts/test_glass_api.py
```

Expected response:
- The response should be JSON.
- It should contain a markdown-formatted clinical answer.
- It may contain in-text citations.
- It may contain references/citations metadata.
- The app stores `raw_response` and extracts best-effort fields.
- `/api/glass/debug/messages/` is development-only and must not be exposed publicly in production.
