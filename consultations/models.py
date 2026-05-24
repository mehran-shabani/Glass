from django.db import models


class Consultation(models.Model):
    question = models.TextField()
    answer = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class ClinicalAIRequest(models.Model):
    # IMPORTANT: patient_context may contain PHI. Production deployment must implement:
    # - encryption at rest
    # - authentication
    # - role-based access control
    # - audit logs
    # - retention/deletion policy
    # - HTTPS
    # - consent workflow
    # - rate limiting
    #
    # Do not print patient_context in console logs.
    # Do not expose raw PHI in errors.
    TASK_CHOICES = [
        ("clinical_qa", "Clinical Q&A"),
        ("draft_ddx", "Draft DDx"),
        ("draft_assessment_plan", "Draft Assessment & Plan"),
        ("draft_hpi", "Draft HPI"),
        ("draft_clinic_note", "Draft Clinic Note"),
        ("draft_patient_handout", "Draft Patient Handout"),
        ("raw_prompt", "Raw Prompt"),
    ]
    task_type = models.CharField(max_length=50, choices=TASK_CHOICES, default="clinical_qa")
    question = models.TextField()
    patient_context = models.TextField(blank=True, default="")
    prompt_sent = models.TextField(blank=True, default="")
    raw_response = models.JSONField(default=dict, blank=True)
    extracted_content = models.TextField(blank=True, default="")
    structured_output = models.JSONField(default=dict, blank=True)
    citations = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    usage = models.JSONField(default=dict, blank=True)
    detected_schema = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    error_message = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
