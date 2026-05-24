# Helssa Clinical AI MVP

A Django + DRF physician-facing clinical AI assistant using OpenAI SDK.

## MVP features
1. Clinical Q&A
2. Draft DDx
3. Draft Assessment & Plan
4. Draft HPI
5. Draft Clinic Note
6. Draft Patient Handout

## Safety disclaimer
This tool is clinical decision support only. It is not a medical device, not a replacement for clinician judgment, examination, emergency care, local protocols, or current guidelines.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`:
```env
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1
```

## Run
```bash
python manage.py migrate
python manage.py runserver
```

Open:

`http://127.0.0.1:8000/clinical/`

## API examples
- `GET /api/clinical/config/`
- `POST /api/clinical/ask/`

Example curl:
```bash
curl -X POST http://127.0.0.1:8000/api/clinical/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "draft_ddx",
    "question": "Adult patient with acute unilateral leg swelling",
    "patient_context": "No fever. Recent long travel. Calf tenderness.",
    "structured": true
  }'
```

## Testing
```bash
pytest
```

## Manual OpenAI smoke test
```bash
python scripts/test_openai_api.py
```

## Production checklist
- DEBUG=false
- secure SECRET_KEY
- rotate API keys
- HTTPS
- authentication
- role-based access
- PHI encryption at rest
- audit logs
- rate limiting
- consent workflow
- retention/deletion policy
- clinical validation
- local guideline adaptation
- monitoring and error tracking

No active workflow depends on Glass Health API.
