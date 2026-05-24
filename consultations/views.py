import json,time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics,status
from .models import GlassClinicalRequest
from .serializers import GlassClinicalAskRequestSerializer,GlassClinicalAskResponseSerializer,GlassClinicalRequestSerializer
from .services.glass_client import GlassClient,GlassAuthenticationError,GlassBadRequestError,GlassRateLimitError,GlassServerError,GlassTimeoutError,GlassClientError,PROMPT_TEMPLATE

def extract_glass_content(raw_response:dict)->tuple[str,list]:
    content=raw_response.get('content') or raw_response.get('message',{}).get('content')
    if not content and raw_response.get('choices'):
        content=((raw_response.get('choices') or [{}])[0].get('message') or {}).get('content')
    content=content or raw_response.get('output_text') or json.dumps(raw_response,ensure_ascii=False,indent=2)
    refs=raw_response.get('references') if isinstance(raw_response.get('references'),list) else raw_response.get('citations') if isinstance(raw_response.get('citations'),list) else []
    return content,refs

class ChatView(APIView):
    def post(self,request): return Response({'message':'legacy chat ok'})

class GlassClinicalAskView(APIView):
    def post(self,request):
        s=GlassClinicalAskRequestSerializer(data=request.data); s.is_valid(raise_exception=True)
        d=s.validated_data; t0=time.perf_counter(); prompt=PROMPT_TEMPLATE.format(patient_context=d.get('patient_context') or '(none provided)',task_type=d.get('task_type','clinical_qa'),question=d['question'])
        err=''; code=status.HTTP_502_BAD_GATEWAY
        try:
            raw=GlassClient().ask_clinical_question(d['question'],d.get('patient_context',''),d.get('task_type','clinical_qa'))
            content,refs=extract_glass_content(raw)
            rec=GlassClinicalRequest.objects.create(task_type=d.get('task_type','clinical_qa'),question=d['question'],patient_context=d.get('patient_context',''),prompt_sent=prompt,raw_response=raw,extracted_content=content,references=refs,status='completed',latency_ms=int((time.perf_counter()-t0)*1000))
            return Response(GlassClinicalAskResponseSerializer(rec).data)
        except GlassBadRequestError as e: err=str(e); code=status.HTTP_400_BAD_REQUEST
        except GlassRateLimitError as e: err=str(e); code=status.HTTP_429_TOO_MANY_REQUESTS
        except GlassTimeoutError as e: err=str(e); code=status.HTTP_504_GATEWAY_TIMEOUT
        except GlassAuthenticationError: err='Glass API authentication failed. Check GLASS_API_KEY and auth header.'; code=status.HTTP_502_BAD_GATEWAY
        except GlassServerError as e: err=str(e); code=status.HTTP_502_BAD_GATEWAY
        except GlassClientError as e: err=str(e); code=status.HTTP_502_BAD_GATEWAY
        rec=GlassClinicalRequest.objects.create(task_type=d.get('task_type','clinical_qa'),question=d['question'],patient_context=d.get('patient_context',''),prompt_sent=prompt,status='failed',error_message=err,latency_ms=int((time.perf_counter()-t0)*1000))
        return Response({'detail':err,'id':rec.id,'status':'failed'},status=code)

class GlassClinicalRequestListView(generics.ListAPIView):
    queryset=GlassClinicalRequest.objects.order_by('-created_at')
    serializer_class=GlassClinicalRequestSerializer

class GlassClinicalRequestDetailView(generics.RetrieveAPIView):
    queryset=GlassClinicalRequest.objects.all()
    serializer_class=GlassClinicalRequestSerializer
