from django.db import models


class Consultation(models.Model):
    question = models.TextField()
    answer = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class GlassClinicalRequest(models.Model):
    # NOTE: patient_context may contain PHI. Production deployment must encrypt/redact/audit this field.
    TASK_CHOICES = [
        ("clinical_qa", "Clinical Q&A"),
        ("differential", "Differential Diagnosis"),
        ("treatment_plan", "Treatment Plan"),
        ("summarization", "Patient Summarization"),
        ("documentation", "Documentation"),
        ("triage", "Triage"),
        ("raw_prompt", "Raw Prompt"),
    ]
    task_type = models.CharField(max_length=50, choices=TASK_CHOICES, default="clinical_qa")
    question = models.TextField()
    patient_context = models.TextField(blank=True, default="")
    prompt_sent = models.TextField(blank=True, default="")
    raw_response = models.JSONField(default=dict, blank=True)
    extracted_content = models.TextField(blank=True, default="")
    references = models.JSONField(default=list, blank=True)
    citations = models.JSONField(default=list, blank=True)
    usage = models.JSONField(default=dict, blank=True)
    detected_schema = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=30, default="completed")
    error_message = models.TextField(blank=True, default="")
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
