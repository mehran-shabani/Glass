from consultations.services.prompt_builder import build_task_prompt


def test_draft_ddx_prompt_contains_required_sections():
    prompt = build_task_prompt("draft_ddx", "q", "ctx")
    assert "Most likely diagnoses" in prompt
    assert "Cannot-miss diagnoses" in prompt
    assert "Suggested workup" in prompt


def test_draft_assessment_plan_prompt_contains_required_sections():
    prompt = build_task_prompt("draft_assessment_plan", "q", "ctx")
    assert "Assessment" in prompt
    assert "Diagnostic plan" in prompt
    assert "Treatment plan" in prompt
    assert "Follow-up" in prompt


def test_draft_hpi_prompt_contains_required_sections():
    prompt = build_task_prompt("draft_hpi", "q", "ctx")
    assert "Chief complaint" in prompt
    assert "Chronology" in prompt
    assert "Pertinent positives" in prompt
    assert "Pertinent negatives" in prompt


def test_draft_clinic_note_prompt_contains_required_sections():
    prompt = build_task_prompt("draft_clinic_note", "q", "ctx")
    assert "CC" in prompt
    assert "HPI" in prompt
    assert "Assessment" in prompt
    assert "Plan" in prompt


def test_draft_patient_handout_prompt_contains_required_sections():
    prompt = build_task_prompt("draft_patient_handout", "q", "ctx")
    assert "Plain-language overview" in prompt
    assert "Warning signs" in prompt
    assert "Follow-up" in prompt
