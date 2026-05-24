import time

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClinicalAIRequest
from .serializers import (
    ClinicalAIRequestSerializer,
    ClinicalAskRequestSerializer,
    ClinicalAskResponseSerializer,
)
from .services.openai_client import (
    ClinicalAIError,
    ClinicalAuthenticationError,
    ClinicalBadRequestError,
    ClinicalOpenAIClient,
    ClinicalRateLimitError,
    ClinicalServerError,
    ClinicalTimeoutError,
)
from .services.openai_response import parse_structured_output, structured_to_markdown
from .services.prompt_builder import build_task_prompt


class ClinicalAskView(APIView):
    def post(self, request):
        s = ClinicalAskRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        prompt = build_task_prompt(
            task_type=d.get("task_type", "clinical_qa"),
            question=d["question"],
            patient_context=d.get("patient_context", ""),
        )
        t0 = time.perf_counter()

        rec = ClinicalAIRequest.objects.create(
            task_type=d.get("task_type", "clinical_qa"),
            question=d["question"],
            patient_context=d.get("patient_context", ""),
            prompt_sent=prompt,
            status="pending",
        )

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
            structured_output = parse_structured_output(original_content) if d.get("structured", True) else {}
            extracted_content = structured_to_markdown(structured_output) or original_content

            rec.raw_response = response.get("raw", {})
            rec.extracted_content = extracted_content
            rec.structured_output = structured_output
            rec.references = response.get("references", [])
            rec.citations = response.get("citations", [])
            rec.usage = response.get("usage", {})
            rec.detected_schema = response.get("model", "")
            rec.status = "completed"
            rec.latency_ms = int((time.perf_counter() - t0) * 1000)
            rec.save()

            out = ClinicalAskResponseSerializer(
                rec,
                context={"include_raw_response": bool(d.get("debug", False))},
            )
            return Response(out.data)
        except ClinicalAuthenticationError:
            err, detail, code = "OpenAI authentication failed.", "Missing or invalid API credentials.", status.HTTP_401_UNAUTHORIZED
        except ClinicalRateLimitError:
            err, detail, code = "Upstream rate limit reached.", "Service is busy. Please retry shortly.", status.HTTP_429_TOO_MANY_REQUESTS
        except ClinicalBadRequestError:
            err, detail, code = "Request failed validation.", "Unable to process request.", status.HTTP_400_BAD_REQUEST
        except ClinicalTimeoutError:
            err, detail, code = "Upstream timeout.", "Service timed out. Please retry.", status.HTTP_504_GATEWAY_TIMEOUT
        except ClinicalServerError:
            err, detail, code = "Upstream service error.", "Service unavailable. Please retry.", status.HTTP_502_BAD_GATEWAY
        except ClinicalAIError:
            err, detail, code = "Unknown upstream error.", "Unknown server error.", status.HTTP_500_INTERNAL_SERVER_ERROR
        except Exception:
            err, detail, code = "Unknown server error.", "Unknown server error.", status.HTTP_500_INTERNAL_SERVER_ERROR

        rec.raw_response = {}
        rec.status = "failed"
        rec.error_message = err
        rec.latency_ms = int((time.perf_counter() - t0) * 1000)
        rec.save(update_fields=["raw_response", "status", "error_message", "latency_ms", "updated_at"])
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
                "structured_output": settings.CLINICAL_STRUCTURED_OUTPUT,
            }
        )


class ClinicalHistoryListView(generics.ListAPIView):
    queryset = ClinicalAIRequest.objects.order_by("-created_at")
    serializer_class = ClinicalAIRequestSerializer


class ClinicalHistoryDetailView(generics.RetrieveAPIView):
    queryset = ClinicalAIRequest.objects.all()
    serializer_class = ClinicalAIRequestSerializer


class ClinicalDebugMessagesView(APIView):
    def get(self, request):
        if not settings.DEBUG:
            return Response({"detail": "Debug endpoint disabled."}, status=status.HTTP_403_FORBIDDEN)
        data = ClinicalAIRequest.objects.order_by("-created_at")[:50]
        return Response(ClinicalAIRequestSerializer(data, many=True).data)
