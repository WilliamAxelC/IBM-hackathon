"""
LM Studio HTTP adapter — calls the local Kev-4B model for diff triage.

Uses the OpenAI-compatible `/v1/chat/completions` endpoint exposed by
LM Studio with grammar-constrained JSON decoding (`response_format`).
"""

from __future__ import annotations

import json
import sys
from typing import Any

import httpx
from pydantic import ValidationError

from kevgate.config import KevGateConfig
from kevgate.exceptions import DecisionParseError, LMStudioUnavailableError
from kevgate.schema import DecisionPayload, RemediationVerification

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_TRIAGE_SYSTEM_PROMPT = """\
You are KevGate, a security-focused code review classifier. Analyze the provided git diff and return a JSON object with exactly these fields:

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

_TRIAGE_USER_TEMPLATE = """\
Diff to analyze:
```
{diff}
```
{context_block}"""

_VERIFY_SYSTEM_PROMPT = """\
You are KevGate, verifying whether a remediation patch resolves the original risk. Return a JSON object:

{
  "verified": boolean,
  "previous_score": integer 0-100,
  "new_score": integer 0-100,
  "delta": integer (new_score - previous_score),
  "message": "one sentence verdict"
}

Return ONLY the JSON object."""

_VERIFY_USER_TEMPLATE = """\
Original problematic diff:
```
{original_diff}
```

Proposed remediation patch:
```
{remediation_patch}
```

Original risk score: {previous_score}
Does the remediation resolve the risk?"""


# ---------------------------------------------------------------------------
# Synthetic pass payload — used when offline_behavior='pass' or 'warn'
# ---------------------------------------------------------------------------

_OFFLINE_PASS_PAYLOAD = DecisionPayload(
    category="safe_refactor",
    risk_score=0,
    confidence=0.0,
    is_breaking_change=False,
    exposes_unprotected_resource=False,
    unhandled_failure_mode=False,
    summary="KevGate offline — LM Studio unavailable, commit allowed per offline_behavior setting.",
    target_file=None,
    target_lines=None,
    remediation_hint=None,
    trigger_agent=False,
)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class LMStudioClient:
    """Async HTTP client for the LM Studio OpenAI-compatible inference API."""

    def __init__(self, config: KevGateConfig | None = None) -> None:
        self._config = config or KevGateConfig()
        timeout = self._config.request_timeout_ms / 1000.0
        self._client = httpx.AsyncClient(
            base_url=self._config.lmstudio_base_url,
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "LMStudioClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _complete(self, system: str, user: str) -> str:
        """
        Send a chat completion request and return the raw response content.

        Raises:
            LMStudioUnavailableError: On connection error or timeout.
        """
        payload = {
            "model": self._config.lmstudio_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "max_tokens": 200,
            "response_format": {"type": "json_object"},
        }
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
            raise LMStudioUnavailableError(
                url=self._config.lmstudio_base_url,
                timeout_ms=self._config.request_timeout_ms,
            ) from exc

    def _handle_unavailable(self, exc: LMStudioUnavailableError) -> DecisionPayload:
        """Apply offline_behavior policy and return or re-raise."""
        behavior = self._config.offline_behavior
        if behavior == "fail":
            raise exc
        if behavior == "warn":
            print(
                f"[kevgate] WARNING: {exc} — allowing commit (offline_behavior=warn)",
                file=sys.stderr,
            )
        # 'pass' or 'warn' → return synthetic safe payload
        return _OFFLINE_PASS_PAYLOAD

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def triage_diff(
        self,
        diff: str,
        context: str | None = None,
    ) -> DecisionPayload:
        """
        Evaluate a unified diff and return a typed DecisionPayload.

        Args:
            diff: Unified diff text to analyze.
            context: Optional commit message or PR description for extra context.

        Returns:
            DecisionPayload with risk classification and remediation hints.

        Raises:
            LMStudioUnavailableError: If offline_behavior='fail' and LM Studio is down.
            DecisionParseError: If the model returns malformed JSON.
        """
        context_block = f"\nAdditional context: {context}" if context else ""
        user_prompt = _TRIAGE_USER_TEMPLATE.format(diff=diff[:4000], context_block=context_block)

        try:
            raw = await self._complete(_TRIAGE_SYSTEM_PROMPT, user_prompt)
        except LMStudioUnavailableError as exc:
            return self._handle_unavailable(exc)

        try:
            return DecisionPayload.model_validate_json(raw)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise DecisionParseError(raw_response=raw, cause=exc) from exc

    async def verify_remediation(
        self,
        original_diff: str,
        remediation_patch: str,
        previous_score: int | None = None,
    ) -> RemediationVerification:
        """
        Verify whether a remediation patch resolves the risk in the original diff.

        Args:
            original_diff: The diff that was blocked by the gate.
            remediation_patch: The agent-generated fix patch.
            previous_score: Known original risk score (for prompt context).

        Returns:
            RemediationVerification with verified flag and score delta.

        Raises:
            LMStudioUnavailableError: If offline_behavior='fail' and LM Studio is down.
            DecisionParseError: If the model returns malformed JSON.
        """
        user_prompt = _VERIFY_USER_TEMPLATE.format(
            original_diff=original_diff[:3000],
            remediation_patch=remediation_patch[:3000],
            previous_score=previous_score if previous_score is not None else "unknown",
        )

        try:
            raw = await self._complete(_VERIFY_SYSTEM_PROMPT, user_prompt)
        except LMStudioUnavailableError as exc:
            if self._config.offline_behavior == "fail":
                raise
            # Offline: return unverified result
            score = previous_score or 50
            return RemediationVerification(
                verified=False,
                previous_score=score,
                new_score=score,
                delta=0,
                message="KevGate offline — could not verify remediation.",
            )

        try:
            return RemediationVerification.model_validate_json(raw)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise DecisionParseError(raw_response=raw, cause=exc) from exc
