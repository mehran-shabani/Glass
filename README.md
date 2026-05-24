# Agent-Helssa MVP with Glass API

## Glass API setup
Set env vars:
- GLASS_API_KEY=your_key_here
- GLASS_API_BASE_URL=https://glass.health/api/external/v2
- GLASS_API_VERSION=glass-5.5
- GLASS_API_TIMEOUT_SECONDS=120

## Run
```bash
python manage.py migrate
python manage.py runserver
```

## API example
```bash
curl -X POST http://127.0.0.1:8000/api/glass/ask/ -H "Content-Type: application/json" -d '{
  "task_type": "differential",
  "patient_context": "54M, smoker, recent long flight, unilateral calf swelling and pain, no fever.",
  "question": "Generate prioritized differential diagnosis and recommended diagnostic workup."
}'
```

Notes:
- API key remains server-side.
- Not patient-facing advice.
- Raw response is stored because Glass response schema may evolve.
