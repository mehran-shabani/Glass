from rest_framework import serializers

from .models import GlassClinicalRequest


class GlassClinicalAskRequestSerializer(serializers.Serializer):
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
    debug = serializers.BooleanField(required=False, default=False)
    version = serializers.CharField(required=False, allow_blank=True, default="")
    stream = serializers.BooleanField(required=False, default=False)


class GlassDebugMessagesSerializer(serializers.Serializer):
    version = serializers.CharField(required=False, allow_blank=True, default="")
    messages = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    stream = serializers.BooleanField(required=False, default=False)


class GlassClinicalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlassClinicalRequest
        fields = "__all__"


class GlassClinicalAskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlassClinicalRequest
        fields = [
            "id",
            "task_type",
            "question",
            "patient_context",
            "status",
            "extracted_content",
            "references",
            "citations",
            "usage",
            "detected_schema",
            "raw_response",
            "error_message",
            "latency_ms",
            "created_at",
        ]
