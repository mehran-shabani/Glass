You are working on an existing Django repository named Glass-main.

Goal:
Convert the current Glass Health based project into an OpenAI-powered clinical assistant MVP for physicians.

Important:
We only want the first 6 core features for this MVP:

1. Clinical Q&A
2. Draft DDx
3. Draft Assessment & Plan
4. Draft HPI
5. Draft Clinic Note
6. Draft Patient Handout

Do NOT implement scribing, transcription, discharge summary, AVS, handoff note, task list, or complex web search in this phase.

The project must no longer depend on Glass Health API. Replace Glass-specific code with OpenAI SDK usage.

Use official OpenAI Python SDK.

The OpenAI API key, base URL, model, timeout, temperature, and max output tokens must be configurable from .env.

This is a clinical decision support tool for physicians. Every clinical output must clearly say:
“Draft for clinician review. Verify with examination, local protocols, and current guidelines.”

Do not expose API keys in frontend, API responses, logs, errors, README examples, or tests.

Keep the existing Django/DRF structure as much as possible.
Refactor cleanly.
Make the app runnable and testable.

Acceptance:
- python manage.py migrate works
- python manage.py runserver works
- /clinical/ opens the UI
- /api/clinical/config/ works
- /api/clinical/ask/ works with mocked tests
- pytest passes
- frontend posts to /api/clinical/ask/
- no active workflow depends on Glass Health
