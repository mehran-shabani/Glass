from __future__ import annotations

from typing import Optional

import requests
from django.conf import settings

from .prompt_builder import build_clinical_prompt


class GlassClientError(Exception): ...


class GlassAuthenticationError(GlassClientError): ...


class GlassBadRequestError(GlassClientError): ...


class GlassRateLimitError(GlassClientError): ...


class GlassServerError(GlassClientError): ...


class GlassTimeoutError(GlassClientError): ...


class GlassClient:
    def _auth_headers(self) -> dict:
        header_name = getattr(settings, "GLASS_API_AUTH_HEADER", "Authorization")
        scheme = getattr(settings, "GLASS_API_AUTH_SCHEME", "Bearer")
        return {
            header_name: f"{scheme} {settings.GLASS_API_KEY}",
            "Content-Type": "application/json",
        }

    def send_messages(
        self,
        messages: list[dict],
        version: Optional[str] = None,
        stream: bool = False,
    ) -> dict:
        if not settings.GLASS_API_KEY:
            raise GlassAuthenticationError("Missing GLASS_API_KEY.")

        url = f"{settings.GLASS_API_BASE_URL.rstrip('/')}/messages"
        payload = {"version": version or settings.GLASS_API_VERSION, "messages": messages}
        if stream:
            payload["stream"] = True

        try:
            resp = requests.post(
                url,
                headers=self._auth_headers(),
                json=payload,
                timeout=settings.GLASS_API_TIMEOUT_SECONDS,
            )
        except requests.Timeout as e:
            raise GlassTimeoutError("Glass API request timed out.") from e
        except requests.RequestException as e:
            raise GlassClientError(f"Glass API request failed: {e}") from e

        if not (200 <= resp.status_code < 300):
            body = (resp.text or "")[:1000]
            if resp.status_code == 400:
                raise GlassBadRequestError(body)
            if resp.status_code in (401, 403):
                raise GlassAuthenticationError(body)
            if resp.status_code == 429:
                raise GlassRateLimitError(body)
            if resp.status_code in (500, 502, 503, 504):
                raise GlassServerError(body)
            raise GlassClientError(body)

        try:
            return resp.json()
        except ValueError as e:
            content_type = resp.headers.get("Content-Type", "")
            body = (resp.text or "")[:1000]
            raise GlassClientError(
                f"Glass API returned non-JSON response. status={resp.status_code} content_type={content_type} body_preview={body}"
            ) from e

    def ask_clinical_question(
        self,
        question: str,
        patient_context: str = "",
        task_type: str = "clinical_qa",
    ) -> dict:
        prompt = build_clinical_prompt(question, patient_context, task_type)
        return self.send_messages(messages=[{"role": "user", "content": prompt}])
