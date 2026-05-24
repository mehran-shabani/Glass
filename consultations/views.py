import time

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClinicalAIRequest
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
from .services.openai_response import parse_structured_output, structured_to_markdown


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
            original_content = response.get("content", "")
            structured_output = parse_structured_output(original_content)
            markdown_content = structured_to_markdown(structured_output)
            extracted_content = markdown_content or original_content

            rec = ClinicalAIRequest.objects.create(
                task_type=d.get("task_type", "clinical_qa"),
                question=d["question"],
                patient_context=d.get("patient_context", ""),
                prompt_sent=prompt,
                raw_response=response.get("raw", {}),
                extracted_content=extracted_content,
                structured_output=structured_output,
                references=response.get("references", []),
                citations=response.get("citations", []),
                usage=response.get("usage", {}),
                detected_schema=response.get("detected_schema", "openai_responses"),
                status="completed",
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )
            return Response(ClinicalAskResponseSerializer(rec).data)
        except ClinicalBadRequestError:
            err, detail, code = "Request failed validation.", "Unable to process request.", status.HTTP_400_BAD_REQUEST
        except ClinicalRateLimitError:
            err, detail, code = "Upstream rate limit reached.", "Service is busy. Please retry shortly.", status.HTTP_429_TOO_MANY_REQUESTS
        except ClinicalTimeoutError:
            err, detail, code = "Upstream timeout.", "Service timed out. Please retry.", status.HTTP_504_GATEWAY_TIMEOUT
        except ClinicalAuthenticationError:
            err, detail, code = "OpenAI authentication failed.", "Service configuration error.", status.HTTP_502_BAD_GATEWAY
        except ClinicalServerError:
            err, detail, code = "Upstream service error.", "Service unavailable. Please retry.", status.HTTP_502_BAD_GATEWAY

        rec = ClinicalAIRequest.objects.create(
            task_type=d.get("task_type", "clinical_qa"),
            question=d.get("question", ""),
            patient_context=d.get("patient_context", ""),
            prompt_sent=prompt,
            raw_response={},
            status="failed",
            error_message=err,
            latency_ms=int((time.perf_counter() - t0) * 1000),
        )
        return Response({"detail": detail, "id": rec.id, "status": "failed"}, status=code)


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
    queryset = ClinicalAIRequest.objects.order_by("-created_at")
    serializer_class = ClinicalRequestSerializer


class ClinicalRequestDetailView(generics.RetrieveAPIView):
    queryset = ClinicalAIRequest.objects.all()
    serializer_class = ClinicalRequestSerializer
