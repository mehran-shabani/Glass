from rest_framework import serializers
from .models import GlassClinicalRequest

class GlassClinicalAskRequestSerializer(serializers.Serializer):
    task_type=serializers.ChoiceField(choices=[c[0] for c in GlassClinicalRequest.TASK_CHOICES],default='clinical_qa',required=False)
    question=serializers.CharField()
    patient_context=serializers.CharField(required=False,allow_blank=True,default='')

class GlassClinicalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=GlassClinicalRequest
        fields='__all__'

class GlassClinicalAskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model=GlassClinicalRequest
        fields=['id','task_type','question','patient_context','status','extracted_content','references','raw_response','error_message','latency_ms','created_at']
