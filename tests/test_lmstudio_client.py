"""Tests for lmstudio_client.py — uses httpx mock transport (no live server required)."""

from __future__ import annotations

import json
import pytest
import httpx

from kevgate.config import KevGateConfig
from kevgate.exceptions import DecisionParseError, LMStudioUnavailableError
from kevgate.lmstudio_client import LMStudioClient
from kevgate.schema import DecisionPayload, RemediationVerification


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(offline_behavior: str = "fail", timeout_ms: int = 500) -> KevGateConfig:
    return KevGateConfig(
        lmstudio_base_url="http://mock-lmstudio",
        lmstudio_model="test-model",
        offline_behavior=offline_behavior,
        request_timeout_ms=timeout_ms,
    )


def _mock_completion_response(content: str) -> httpx.Response:
    body = {
        "choices": [{"message": {"content": content}}]
    }
    return httpx.Response(200, json=body)


VALID_PAYLOAD_JSON = json.dumps({
    "category": "security_risk",
    "risk_score": 88,
    "confidence": 0.95,
    "is_breaking_change": False,
    "exposes_unprotected_resource": True,
    "unhandled_failure_mode": False,
    "summary": "SQL injection via string interpolation in login query.",
    "target_file": "src/auth.py",
    "target_lines": "12-14",
    "remediation_hint": "Use parameterized queries: cursor.execute(query, (username,))",
    "trigger_agent": True,
})

VALID_VERIFICATION_JSON = json.dumps({
    "verified": True,
    "previous_score": 88,
    "new_score": 5,
    "delta": -83,
    "message": "SQL injection resolved via parameterized query.",
})


# ---------------------------------------------------------------------------
# Tests: triage_diff
# ---------------------------------------------------------------------------

class TestTriageDiff:
    @pytest.mark.asyncio
    async def test_successful_triage_returns_decision_payload(self):
        transport = httpx.MockTransport(
            lambda req: _mock_completion_response(VALID_PAYLOAD_JSON)
        )
        config = _make_config()
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            result = await client.triage_diff("+ some_diff_content")

        assert isinstance(result, DecisionPayload)
        assert result.risk_score == 88
        assert result.category == "security_risk"
        assert result.trigger_agent is True

    @pytest.mark.asyncio
    async def test_connection_error_raises_unavailable_when_fail(self):
        def raise_connect(req: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(raise_connect)
        config = _make_config(offline_behavior="fail")
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            with pytest.raises(LMStudioUnavailableError):
                await client.triage_diff("+ some diff")

    @pytest.mark.asyncio
    async def test_offline_pass_returns_safe_payload(self):
        def raise_connect(req: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(raise_connect)
        config = _make_config(offline_behavior="pass")
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            result = await client.triage_diff("+ some diff")

        assert result.risk_score == 0
        assert result.trigger_agent is False

    @pytest.mark.asyncio
    async def test_malformed_json_raises_parse_error(self):
        transport = httpx.MockTransport(
            lambda req: _mock_completion_response("not valid json at all {{{")
        )
        config = _make_config()
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            with pytest.raises(DecisionParseError):
                await client.triage_diff("+ some diff")

    @pytest.mark.asyncio
    async def test_missing_fields_raises_parse_error(self):
        incomplete = json.dumps({"risk_score": 50})
        transport = httpx.MockTransport(
            lambda req: _mock_completion_response(incomplete)
        )
        config = _make_config()
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            with pytest.raises(DecisionParseError):
                await client.triage_diff("+ some diff")


# ---------------------------------------------------------------------------
# Tests: verify_remediation
# ---------------------------------------------------------------------------

class TestVerifyRemediation:
    @pytest.mark.asyncio
    async def test_successful_verification(self):
        transport = httpx.MockTransport(
            lambda req: _mock_completion_response(VALID_VERIFICATION_JSON)
        )
        config = _make_config()
        async with LMStudioClient(config) as client:
            client._client = httpx.AsyncClient(
                base_url="http://mock-lmstudio",
                transport=transport,
            )
            result = await client.verify_remediation(
                original_diff="+ bad code",
                remediation_patch="+ fixed code",
                previous_score=88,
            )

        assert isinstance(result, RemediationVerification)
        assert result.verified is True
        assert result.new_score == 5
        assert result.delta == -83
