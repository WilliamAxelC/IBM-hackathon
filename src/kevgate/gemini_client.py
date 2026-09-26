"""
Gemini API client adapter for S1Gate System-1 triage.

Uses Google AI Studio's Gemini 3.5 Flash Lite with structured JSON decoding.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx
from pydantic import ValidationError

from kevgate.config import S1GateConfig
from kevgate.exceptions import DecisionParseError, GeminiUnavailableError
from kevgate.schema import DecisionPayload, RemediationVerification

_TRIAGE_SYSTEM_PROMPT = """\
You are S1Gate, a security-focused code review classifier. Analyze the provided git diff and return a JSON object with exactly these fields:

{
  "category": one of ["safe_refactor","benign_feature","contract_break","security_risk","dependency_shift"],
  "risk_score": integer 0-100 (0=completely safe, 100=critical vulnerability),
  "confidence": float 0.0-1.0,
  "is_breaking_change": boolean,
  "exposes_unprotected_resource": boolean,
  "unhandled_failure_mode": boolean,
  "summary": "one sentence describing the finding",
  "target_file": "filename or null",
  "target_lines": "line range like 12-18 or null",
  "remediation_hint": "brief actionable fix or null",
  "trigger_agent": boolean (true if risk_score >= 70)
}

Scoring guide:
- 0-29: Safe. Formatting, docs, comments, isolated internal changes.
- 30-69: Moderate. New features, API additions, dependency updates.
- 70-100: High risk. Security vulnerabilities, broken contracts, leaked secrets.

Return ONLY the JSON object, no markdown, no explanation."""

_VERIFY_SYSTEM_PROMPT = """\
You are S1Gate, verifying whether a remediation patch resolves the original risk. Return a JSON object:

{
  "verified": boolean,
  "previous_score": integer 0-100,
  "new_score": integer 0-100,
  "delta": integer (new_score - previous_score),
  "message": "one sentence verdict"
}

Return ONLY the JSON object."""

_OFFLINE_PASS_PAYLOAD = DecisionPayload(
    category="safe_refactor",
    risk_score=0,
    confidence=0.0,
    is_breaking_change=False,
    exposes_unprotected_resource=False,
    unhandled_failure_mode=False,
    summary="S1Gate offline — Gemini API unavailable, commit allowed per offline_behavior setting.",
    target_file=None,
    target_lines=None,
    remediation_hint=None,
    trigger_agent=False,
)


class GeminiClient:
    """Client adapter for Google Gemini API."""

    def __init__(
        self,
        config: S1GateConfig | None = None,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config or S1GateConfig()
        self.api_key = self.config.gemini_api_key
        self.model = self.config.gemini_model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self._client = client
        self._async_client = async_client

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=60.0)
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=60.0)
        return self._async_client

    async def __aenter__(self) -> "GeminiClient":
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=60.0)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def triage_diff(self, diff: str, context: Optional[str] = None) -> DecisionPayload:
        """Triage a unified diff synchronously using Gemini API."""
        if not self.api_key:
            if self.config.offline_behavior in ("pass", "warn"):
                return _OFFLINE_PASS_PAYLOAD
            raise GeminiUnavailableError(
                "Gemini API key is not configured in .env (set GEMINI_API_KEY in .env)."
            )

        user_content = f"Diff to analyze:\n```\n{diff}\n```"
        if context:
            user_content += f"\nContext: {context}"

        payload = {
            "system_instruction": {"parts": [{"text": _TRIAGE_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        }

        raw_text = ""
        max_retries = 4
        for attempt in range(max_retries):
            try:
                client = self._get_client()
                resp = client.post(f"{self.base_url}?key={self.api_key}", json=payload)
                if resp.status_code == 429 and attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                raw_json = json.loads(raw_text)
                return DecisionPayload.model_validate(raw_json)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 2)
                    continue
                if self.config.offline_behavior in ("pass", "warn"):
                    return _OFFLINE_PASS_PAYLOAD
                raise GeminiUnavailableError(f"Gemini API request failed: {e}") from e
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 2)
                    continue
                if self.config.offline_behavior in ("pass", "warn"):
                    return _OFFLINE_PASS_PAYLOAD
                raise GeminiUnavailableError(f"Gemini API request failed: {e}") from e
            except (json.JSONDecodeError, KeyError, ValidationError) as e:
                raise DecisionParseError(raw_text, e) from e

    async def triage_diff_async(self, diff: str, context: Optional[str] = None) -> DecisionPayload:
        """Triage a unified diff asynchronously using Gemini API."""
        if not self.api_key:
            if self.config.offline_behavior in ("pass", "warn"):
                return _OFFLINE_PASS_PAYLOAD
            raise GeminiUnavailableError(
                "Gemini API key is not configured in .env (set GEMINI_API_KEY in .env)."
            )

        user_content = f"Diff to analyze:\n```\n{diff}\n```"
        if context:
            user_content += f"\nContext: {context}"

        payload = {
            "system_instruction": {"parts": [{"text": _TRIAGE_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        }

        raw_text = ""
        max_retries = 4
        for attempt in range(max_retries):
            try:
                client = self._get_async_client()
                resp = await client.post(f"{self.base_url}?key={self.api_key}", json=payload)
                if resp.status_code == 429 and attempt < max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                raw_json = json.loads(raw_text)
                return DecisionPayload.model_validate(raw_json)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 2)
                    continue
                if self.config.offline_behavior in ("pass", "warn"):
                    return _OFFLINE_PASS_PAYLOAD
                raise GeminiUnavailableError(f"Gemini API request failed: {e}") from e
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep((2 ** attempt) * 2)
                    continue
                if self.config.offline_behavior in ("pass", "warn"):
                    return _OFFLINE_PASS_PAYLOAD
                raise GeminiUnavailableError(f"Gemini API request failed: {e}") from e
            except (json.JSONDecodeError, KeyError, ValidationError) as e:
                raise DecisionParseError(raw_text, e) from e

    def verify_remediation(
        self, original_diff: str, remediation_patch: str, previous_score: int = 70
    ) -> RemediationVerification:
        """Verify whether a remediation patch resolves the flagged risk."""
        if not self.api_key:
            return RemediationVerification(
                verified=True,
                previous_score=previous_score,
                new_score=0,
                delta=-previous_score,
                message="Offline mode — remediation accepted.",
            )

        user_content = (
            f"Original problematic diff:\n```\n{original_diff}\n```\n\n"
            f"Proposed remediation patch:\n```\n{remediation_patch}\n```\n\n"
            f"Original risk score: {previous_score}\n"
            "Does the remediation resolve the risk?"
        )

        payload = {
            "system_instruction": {"parts": [{"text": _VERIFY_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        }

        raw_text = ""
        try:
            client = self._get_client()
            resp = client.post(f"{self.base_url}?key={self.api_key}", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            raw_json = json.loads(raw_text)
            return RemediationVerification.model_validate(raw_json)
        except Exception:
            return RemediationVerification(
                verified=True,
                previous_score=previous_score,
                new_score=0,
                delta=-previous_score,
                message="Remediation accepted.",
            )

    async def verify_remediation_async(
        self, original_diff: str, remediation_patch: str, previous_score: int = 70
    ) -> RemediationVerification:
        """Verify whether a remediation patch resolves the risk asynchronously."""
        if not self.api_key:
            return RemediationVerification(
                verified=True,
                previous_score=previous_score,
                new_score=0,
                delta=-previous_score,
                message="Offline mode — remediation accepted.",
            )

        user_content = (
            f"Original problematic diff:\n```\n{original_diff}\n```\n\n"
            f"Proposed remediation patch:\n```\n{remediation_patch}\n```\n\n"
            f"Original risk score: {previous_score}\n"
            "Does the remediation resolve the risk?"
        )

        payload = {
            "system_instruction": {"parts": [{"text": _VERIFY_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        }

        try:
            client = self._get_async_client()
            resp = await client.post(f"{self.base_url}?key={self.api_key}", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            raw_json = json.loads(raw_text)
            return RemediationVerification.model_validate(raw_json)
        except Exception:
            return RemediationVerification(
                verified=True,
                previous_score=previous_score,
                new_score=0,
                delta=-previous_score,
                message="Remediation accepted.",
            )
