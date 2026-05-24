import time

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GlassClinicalRequest
from .serializers import (
    GlassClinicalAskRequestSerializer,
    GlassClinicalAskResponseSerializer,
    GlassClinicalRequestSerializer,
    GlassDebugMessagesSerializer,
)
from .services.glass_client import (
    GlassAuthenticationError,
    GlassBadRequestError,
    GlassClient,
    GlassClientError,
    GlassRateLimitError,
    GlassServerError,
    GlassTimeoutError,
)
from .services.glass_response import extract_glass_response
from .services.prompt_builder import build_clinical_prompt


class ChatView(APIView):
    def post(self, request):
        return Response({"message": "legacy chat ok"})


class GlassClinicalAskView(APIView):
    def post(self, request):
        s = GlassClinicalAskRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        t0 = time.perf_counter()
        prompt = build_clinical_prompt(d["question"], d.get("patient_context", ""), d.get("task_type", "clinical_qa"))

        try:
            raw = GlassClient().send_messages(
                messages=[{"role": "user", "content": prompt}],
                version=d.get("version") or None,
                stream=d.get("stream", False),
            )
            parsed = extract_glass_response(raw)
            rec = GlassClinicalRequest.objects.create(
                task_type=d.get("task_type", "clinical_qa"),
                question=d["question"],
                patient_context=d.get("patient_context", ""),
                prompt_sent=prompt,
                raw_response=parsed["raw"],
                extracted_content=parsed["content"],
                references=parsed["references"],
                citations=parsed["citations"],
                usage=parsed["usage"],
                detected_schema=parsed["detected_schema"],
                status="completed",
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )
            return Response(GlassClinicalAskResponseSerializer(rec).data)
        except GlassBadRequestError as e:
            err, code = str(e), status.HTTP_400_BAD_REQUEST
        except GlassRateLimitError as e:
            err, code = str(e), status.HTTP_429_TOO_MANY_REQUESTS
        except GlassTimeoutError as e:
            err, code = str(e), status.HTTP_504_GATEWAY_TIMEOUT
        except GlassAuthenticationError:
            err, code = "Glass API authentication failed. Check GLASS_API_KEY and auth header.", status.HTTP_502_BAD_GATEWAY
        except (GlassServerError, GlassClientError) as e:
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


class GlassDebugMessagesView(APIView):
    # Development-only schema discovery endpoint. Do not expose publicly in production.
    def post(self, request):
        s = GlassDebugMessagesSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        raw = GlassClient().send_messages(d["messages"], version=d.get("version") or None, stream=d.get("stream", False))
        parsed = extract_glass_response(raw)
        return Response(
            {
                "status": "ok",
                "detected_schema": parsed["detected_schema"],
                "extracted_content": parsed["content"],
                "references": parsed["references"],
                "citations": parsed["citations"],
                "usage": parsed["usage"],
                "raw_response": parsed["raw"],
            }
        )


class GlassConfigView(APIView):
    def get(self, request):
        return Response(
            {
                "base_url": settings.GLASS_API_BASE_URL,
                "version": settings.GLASS_API_VERSION,
                "timeout_seconds": settings.GLASS_API_TIMEOUT_SECONDS,
                "auth_header": settings.GLASS_API_AUTH_HEADER,
                "auth_scheme": settings.GLASS_API_AUTH_SCHEME,
                "api_key_configured": bool(settings.GLASS_API_KEY),
            }
        )


class GlassClinicalRequestListView(generics.ListAPIView):
    queryset = GlassClinicalRequest.objects.order_by("-created_at")
    serializer_class = GlassClinicalRequestSerializer


class GlassClinicalRequestDetailView(generics.RetrieveAPIView):
    queryset = GlassClinicalRequest.objects.all()
    serializer_class = GlassClinicalRequestSerializer
