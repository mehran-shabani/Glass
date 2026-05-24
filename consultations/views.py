import time

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GlassClinicalRequest
from .serializers import (
    ClinicalAskRequestSerializer,
    ClinicalAskResponseSerializer,
    ClinicalRequestSerializer,
)
from .services.openai_client import (
    ClinicalAuthenticationError,
    ClinicalBadRequestError,
    ClinicalOpenAIClient,
    ClinicalRateLimitError,
    ClinicalServerError,
    ClinicalTimeoutError,
)
from .services.prompt_builder import build_clinical_prompt


class ClinicalAskView(APIView):
    def post(self, request):
        s = ClinicalAskRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        t0 = time.perf_counter()
        prompt = build_clinical_prompt(d["question"], d.get("patient_context", ""), d.get("task_type", "clinical_qa"))

        try:
            response = ClinicalOpenAIClient().generate_clinical_response(
                messages=[{"role": "user", "content": prompt}],
                task_type=d.get("task_type", "clinical_qa"),
                model=d.get("model") or None,
                temperature=d.get("temperature"),
                max_output_tokens=d.get("max_output_tokens"),
                structured=d.get("structured"),
            )
            rec = GlassClinicalRequest.objects.create(
                task_type=d.get("task_type", "clinical_qa"),
                question=d["question"],
                patient_context=d.get("patient_context", ""),
                prompt_sent=prompt,
                raw_response=response.get("raw", {}),
                extracted_content=response.get("content", ""),
                references=response.get("references", []),
                citations=response.get("citations", []),
                usage=response.get("usage", {}),
                detected_schema=response.get("detected_schema", "openai_responses"),
                status="completed",
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )
            return Response(ClinicalAskResponseSerializer(rec).data)
        except ClinicalBadRequestError as e:
            err, code = str(e), status.HTTP_400_BAD_REQUEST
        except ClinicalRateLimitError as e:
            err, code = str(e), status.HTTP_429_TOO_MANY_REQUESTS
        except ClinicalTimeoutError as e:
            err, code = str(e), status.HTTP_504_GATEWAY_TIMEOUT
        except ClinicalAuthenticationError:
            err, code = "OpenAI authentication failed. Check OPENAI_API_KEY.", status.HTTP_502_BAD_GATEWAY
        except ClinicalServerError as e:
            err, code = str(e), status.HTTP_502_BAD_GATEWAY

        rec = GlassClinicalRequest.objects.create(
            task_type=d.get("task_type", "clinical_qa"),
            question=d.get("question", ""),
            patient_context=d.get("patient_context", ""),
            prompt_sent=prompt,
            raw_response={},
            status="failed",
            error_message=err,
            latency_ms=int((time.perf_counter() - t0) * 1000),
        )
        return Response({"detail": err, "id": rec.id, "status": "failed"}, status=code)


class ClinicalConfigView(APIView):
    def get(self, request):
        return Response(
            {
                "api_key_configured": bool(settings.OPENAI_API_KEY),
                "base_url": settings.OPENAI_BASE_URL,
                "default_model": settings.OPENAI_MODEL,
                "timeout_seconds": settings.OPENAI_TIMEOUT_SECONDS,
                "temperature": settings.OPENAI_TEMPERATURE,
                "max_output_tokens": settings.OPENAI_MAX_OUTPUT_TOKENS,
                "app_name": settings.CLINICAL_APP_NAME,
                "default_language": settings.CLINICAL_DEFAULT_LANGUAGE,
                "structured_output": settings.CLINICAL_STRUCTURED_OUTPUT,
                "safe_mode": settings.CLINICAL_SAFE_MODE,
            }
        )


class ClinicalRequestListView(generics.ListAPIView):
    queryset = GlassClinicalRequest.objects.order_by("-created_at")
    serializer_class = ClinicalRequestSerializer


class ClinicalRequestDetailView(generics.RetrieveAPIView):
    queryset = GlassClinicalRequest.objects.all()
    serializer_class = ClinicalRequestSerializer
