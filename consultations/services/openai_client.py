from __future__ import annotations

from typing import Any

from django.conf import settings
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)


class ClinicalAIError(Exception): ...


class ClinicalAuthenticationError(ClinicalAIError): ...


class ClinicalBadRequestError(ClinicalAIError): ...


class ClinicalRateLimitError(ClinicalAIError): ...


class ClinicalTimeoutError(ClinicalAIError): ...


class ClinicalServerError(ClinicalAIError): ...


class ClinicalOpenAIClient:
    def __init__(self):
        self.api_key = getattr(settings, "OPENAI_API_KEY", "")
        self.base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.timeout = getattr(settings, "OPENAI_TIMEOUT_SECONDS", 120)

        if not self.api_key:
            raise ClinicalAuthenticationError("Missing OPENAI_API_KEY.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def generate_clinical_response(
        self,
        messages: list[dict],
        task_type: str,
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        structured: bool | None = None,
    ) -> dict:
        selected_model = model or getattr(settings, "OPENAI_MODEL", "gpt-4.1")
        selected_temperature = (
            temperature if temperature is not None else getattr(settings, "OPENAI_TEMPERATURE", None)
        )
        selected_max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else getattr(settings, "OPENAI_MAX_OUTPUT_TOKENS", None)
        )
        system_instructions = self._build_system_instructions(task_type=task_type, structured=structured)

        payload: dict[str, Any] = {
            "model": selected_model,
            "instructions": system_instructions,
            "input": messages,
        }
        if selected_temperature is not None:
            payload["temperature"] = selected_temperature
        if selected_max_output_tokens is not None:
            payload["max_output_tokens"] = selected_max_output_tokens

        try:
            response = self.client.responses.create(**payload)
        except BadRequestError as e:
            if payload.get("temperature") is not None and self._is_unsupported_temperature_error(e):
                payload.pop("temperature", None)
                try:
                    response = self.client.responses.create(**payload)
                except Exception as retry_error:  # noqa: BLE001
                    raise self._map_openai_error(retry_error) from retry_error
            else:
                raise self._map_openai_error(e) from e
        except Exception as e:  # noqa: BLE001
            raise self._map_openai_error(e) from e

        raw = self._safe_raw_response(response)
        return {
            "content": self._extract_content(response),
            "raw": raw,
            "usage": self._safe_usage(raw),
            "model": self._safe_value(raw, "model") or selected_model,
            "task_type": task_type,
            "detected_schema": "openai_responses",
            "finish_reason": self._extract_finish_reason(raw),
            "citations": [],
            "references": [],
        }

    def _build_system_instructions(self, task_type: str, structured: bool | None) -> str:
        base = f"You are a clinical AI assistant. Task type: {task_type}."
        if structured:
            return f"{base} Return concise, structured clinical output."
        return base

    def _is_unsupported_temperature_error(self, err: BadRequestError) -> bool:
        msg = str(err).lower()
        return "temperature" in msg and any(k in msg for k in ("unsupported", "not supported", "unknown"))

    def _extract_content(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text:
            return output_text

        chunks: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if isinstance(text, str) and text:
                    chunks.append(text)
                    continue
                if isinstance(content, dict):
                    text = content.get("text")
                    if isinstance(text, str) and text:
                        chunks.append(text)
        return "\n".join(chunks).strip()

    def _safe_raw_response(self, response: Any) -> dict[str, Any]:
        model_dump = getattr(response, "model_dump", None)
        if callable(model_dump):
            try:
                dumped = model_dump()
                if isinstance(dumped, dict):
                    return dumped
            except Exception:  # noqa: BLE001
                pass

        if isinstance(response, dict):
            return response

        raw: dict[str, Any] = {}
        for attr in ("id", "model", "output", "output_text", "usage", "status", "created"):
            value = getattr(response, attr, None)
            if value is not None:
                raw[attr] = value
        return raw

    def _extract_finish_reason(self, raw: dict[str, Any]) -> str:
        output = raw.get("output")
        if not isinstance(output, list):
            return ""
        for item in output:
            if isinstance(item, dict):
                reason = item.get("finish_reason")
                if isinstance(reason, str):
                    return reason
        return ""

    def _safe_usage(self, raw: dict[str, Any]) -> dict[str, Any]:
        usage = raw.get("usage", {})
        return usage if isinstance(usage, dict) else {}

    def _safe_value(self, raw: dict[str, Any], key: str) -> Any:
        value = raw.get(key)
        return value if isinstance(value, (str, int, float, bool, dict, list)) else None

    def _map_openai_error(self, err: Exception) -> ClinicalAIError:
        if isinstance(err, AuthenticationError):
            return ClinicalAuthenticationError("OpenAI authentication failed.")
        if isinstance(err, RateLimitError):
            return ClinicalRateLimitError("OpenAI rate limit reached.")
        if isinstance(err, (APITimeoutError, TimeoutError)):
            return ClinicalTimeoutError("OpenAI request timed out.")
        if isinstance(err, BadRequestError):
            return ClinicalBadRequestError("OpenAI bad request.")
        if isinstance(err, (InternalServerError, APIConnectionError)):
            return ClinicalServerError("OpenAI server error.")
        if isinstance(err, APIStatusError):
            status_code = getattr(err, "status_code", None)
            if status_code in (401, 403):
                return ClinicalAuthenticationError("OpenAI authentication failed.")
            if status_code == 429:
                return ClinicalRateLimitError("OpenAI rate limit reached.")
            if status_code == 400:
                return ClinicalBadRequestError("OpenAI bad request.")
            if status_code in (500, 502, 503, 504):
                return ClinicalServerError("OpenAI server error.")
            return ClinicalAIError("OpenAI request failed.")
        if isinstance(err, APIError):
            return ClinicalAIError("OpenAI API error.")
        return ClinicalAIError("OpenAI request failed.")
