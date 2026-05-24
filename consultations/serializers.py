from rest_framework import serializers

from .models import ClinicalAIRequest


class ClinicalAskRequestSerializer(serializers.Serializer):
    TASK_CHOICES = [
        "clinical_qa",
        "draft_ddx",
        "draft_assessment_plan",
        "draft_hpi",
        "draft_clinic_note",
        "draft_patient_handout",
        "raw_prompt",
    ]

    question = serializers.CharField(required=True)
    patient_context = serializers.CharField(required=False, allow_blank=True, default="")
    task_type = serializers.ChoiceField(choices=TASK_CHOICES, default="clinical_qa", required=False)
    model = serializers.CharField(required=False, allow_blank=True, default="")
    structured = serializers.BooleanField(required=False, default=False)
    temperature = serializers.FloatField(required=False)
    max_output_tokens = serializers.IntegerField(required=False, min_value=1)


class ClinicalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalAIRequest
        fields = "__all__"


class ClinicalAskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalAIRequest
        fields = ["id", "task_type", "question", "patient_context", "status", "extracted_content", "structured_output", "references", "citations", "usage", "detected_schema", "raw_response", "error_message", "latency_ms", "created_at"]
