from __future__ import annotations


def build_clinical_prompt(question: str, patient_context: str = "", task_type: str = "clinical_qa") -> str:
    if task_type == "raw_prompt":
        return question

    return f"""You are assisting a licensed clinician. This is clinician-facing clinical decision support, not direct patient advice.

Patient context:
{patient_context}

Clinical task type:
{task_type}

Clinical question:
{question}

Return a structured, evidence-based answer with:
1. Bottom line
2. Key clinical reasoning
3. Differential diagnosis if relevant
4. Recommended next steps
5. Red flags / urgent actions
6. Missing data and limitations
7. References/citations if available from the API

Important safety note:
The output is a draft for clinician review and must not replace clinical judgment, local guidelines, examination, or emergency care.
"""
