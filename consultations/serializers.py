from rest_framework import serializers

from .models import GlassClinicalRequest


class ClinicalAskRequestSerializer(serializers.Serializer):
    TASK_CHOICES = [
        "clinical_qa",
        "differential",
        "treatment_plan",
        "summarization",
        "documentation",
        "triage",
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
        model = GlassClinicalRequest
        fields = "__all__"


class ClinicalAskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlassClinicalRequest
        fields = ["id", "task_type", "question", "patient_context", "status", "extracted_content", "references", "citations", "usage", "detected_schema", "raw_response", "error_message", "latency_ms", "created_at"]
