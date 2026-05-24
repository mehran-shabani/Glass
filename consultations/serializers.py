from django.conf import settings
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
    temperature = serializers.FloatField(required=False)
    max_output_tokens = serializers.IntegerField(required=False, min_value=1)
    structured = serializers.BooleanField(required=False, default=True)
    debug = serializers.BooleanField(required=False, default=False)


class ClinicalAIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalAIRequest
        fields = [
            "id",
            "task_type",
            "question",
            "patient_context",
            "status",
            "extracted_content",
            "structured_output",
            "citations",
            "references",
            "usage",
            "latency_ms",
            "created_at",
            "updated_at",
        ]


class ClinicalAskResponseSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="detected_schema", read_only=True)
    raw_response = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAIRequest
        fields = [
            "id",
            "task_type",
            "model",
            "status",
            "extracted_content",
            "structured_output",
            "citations",
            "references",
            "usage",
            "latency_ms",
            "created_at",
            "raw_response",
        ]

    def get_raw_response(self, obj):
        include_raw = bool(self.context.get("include_raw_response")) and bool(settings.DEBUG)
        if not include_raw:
            return None
        return obj.raw_response

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("raw_response") is None:
            data.pop("raw_response", None)
        return data
