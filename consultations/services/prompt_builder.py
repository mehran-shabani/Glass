from __future__ import annotations

SUPPORTED_TASK_TYPES = {
    "clinical_qa",
    "draft_ddx",
    "draft_assessment_plan",
    "draft_hpi",
    "draft_clinic_note",
    "draft_patient_handout",
    "raw_prompt",
}

DEFAULT_FOOTER = (
    "Draft for clinician review. Verify with examination, local protocols, and current guidelines."
)


def build_system_instructions(language: str = "fa") -> str:
    """Build global system instructions for clinician-facing clinical support."""
    normalized_language = (language or "fa").strip().lower()

    return f"""You are a clinical decision support assistant for licensed clinicians.

Core safety and quality rules:
- You must not replace clinician judgment.
- You must not provide a definitive diagnosis without sufficient data.
- Clearly separate known facts from assumptions/inferences.
- Explicitly mention missing or uncertain data.
- Highlight emergency red flags and time-sensitive risks.
- Provide practical, clinically useful next steps.
- Never fabricate citations or references.
- If citations are unavailable, explicitly state: evidence retrieval is not available.
- Recommend checking local protocols and current guidelines.
- Do not hallucinate exam, imaging, or laboratory findings.
- If patient context is incomplete, explicitly state what is missing.
- If emergency red flags are present, prioritize urgent evaluation.
- Keep outputs structured and useful for real physicians.

Language policy:
- Default output language is Persian (fa), unless the user requests another language.
- Requested/default language for this task: {normalized_language}.

Hard requirement:
- End every output with this exact line:
\"{DEFAULT_FOOTER}\"
"""


def _task_format_instructions(task_type: str) -> str:
    task_map = {
        "clinical_qa": """Output format:
- پاسخ کوتاه / Bottom line
- استدلال بالینی
- نکات عملی برای پزشک
- Red flags
- Missing data
- Suggested next steps
- Evidence note""",
        "draft_ddx": """Output format:
- Problem representation
- Most likely diagnoses
- Cannot-miss diagnoses
- Expanded differential
- Key discriminating features
- Suggested workup
- Red flags
- What data would change the ranking""",
        "draft_assessment_plan": """Output format:
- Problem representation
- Assessment
- Differential by priority
- Diagnostic plan
- Treatment plan
- Patient education
- Follow-up
- Safety net / return precautions""",
        "draft_hpi": """Output format:
- Chief complaint
- Chronology
- Location / quality / severity if relevant
- Associated symptoms
- Pertinent positives
- Pertinent negatives
- Risk factors
- Prior treatment
- Clinician review checklist""",
        "draft_clinic_note": """Output format:
- CC
- HPI
- Relevant history
- Medications/allergies if provided
- Exam if provided
- Assessment
- Plan
- Follow-up
- Safety note""",
        "draft_patient_handout": """Output format:
Use patient-friendly language.
- Plain-language overview
- What this may mean
- What to do at home
- Medications / treatment instructions if provided
- Warning signs
- Follow-up
- FAQ""",
    }
    return task_map[task_type]


def build_task_prompt(
    task_type: str,
    question: str,
    patient_context: str = "",
) -> str:
    """Build a task-scoped prompt with structure and safety rules."""
    normalized_task_type = (task_type or "clinical_qa").strip()
    if normalized_task_type not in SUPPORTED_TASK_TYPES:
        raise ValueError(
            f"Unsupported task_type '{normalized_task_type}'. Supported values: "
            f"{', '.join(sorted(SUPPORTED_TASK_TYPES))}"
        )

    cleaned_question = (question or "").strip()
    cleaned_context = (patient_context or "").strip()

    if normalized_task_type == "raw_prompt":
        return (
            f"Task type: raw_prompt\n\n"
            f"Use the clinical question exactly as provided below.\n"
            f"Still enforce clinical safety constraints and include the required footer.\n\n"
            f"Clinical question:\n{cleaned_question}\n\n"
            f"Patient context:\n{cleaned_context or 'Not provided.'}\n\n"
            f"Safety requirements:\n"
            f"- Do not hallucinate findings.\n"
            f"- If context is incomplete, list missing critical data.\n"
            f"- If red flags are present, prioritize urgent evaluation.\n"
            f"- End with exact footer: \"{DEFAULT_FOOTER}\""
        )

    format_instructions = _task_format_instructions(normalized_task_type)

    return f"""Task type: {normalized_task_type}

{format_instructions}

Clinical question:
{cleaned_question}

Patient context:
{cleaned_context or 'Not provided.'}

Prompt rules:
- Do not hallucinate missing exam/lab/imaging findings.
- If patient_context is incomplete, explicitly state what is missing.
- If emergency red flags are present, prioritize urgent evaluation.
- Keep outputs practical and useful for real physicians.
- Separate known facts from assumptions.
- Avoid definitive diagnosis without enough data.
- Include an Evidence note; if citations are unavailable, state: evidence retrieval is not available.
- End with exact footer: "{DEFAULT_FOOTER}""".strip()


def build_clinical_prompt(question: str, patient_context: str = "", task_type: str = "clinical_qa") -> str:
    """Backward-compatible wrapper; prefer build_task_prompt."""
    return build_task_prompt(task_type=task_type, question=question, patient_context=patient_context)
