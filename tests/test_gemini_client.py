"""Tests for gemini_client.py — uses httpx mock transport."""

from __future__ import annotations

import json
import pytest
import httpx

from kevgate.config import S1GateConfig
from kevgate.exceptions import DecisionParseError, GeminiUnavailableError
from kevgate.gemini_client import GeminiClient
from kevgate.schema import DecisionPayload, RemediationVerification


VALID_DECISION_JSON = json.dumps({
    "category": "security_risk",
    "risk_score": 90,
    "confidence": 0.98,
    "is_breaking_change": False,
    "exposes_unprotected_resource": True,
    "unhandled_failure_mode": False,
    "summary": "SQL injection vulnerability detected.",
    "target_file": "src/auth.py",
    "target_lines": "12-14",
    "remediation_hint": "Use parameterized queries.",
    "trigger_agent": True,
})

VALID_GEMINI_API_BODY = {
    "candidates": [
        {
            "content": {
                "parts": [{"text": VALID_DECISION_JSON}]
            }
        }
    ]
}

VALID_VERIFY_JSON = json.dumps({
    "verified": True,
    "previous_score": 90,
    "new_score": 5,
    "delta": -85,
    "message": "Remediation verified clean.",
})

VALID_GEMINI_VERIFY_BODY = {
    "candidates": [
        {
            "content": {
                "parts": [{"text": VALID_VERIFY_JSON}]
            }
        }
    ]
}


def _mock_gemini_response(body_dict: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=body_dict)


class TestGeminiClient:
    def test_init_defaults(self):
        cfg = S1GateConfig(gemini_api_key="test-key")
        client = GeminiClient(cfg)
        assert client.api_key == "test-key"
        assert "gemini-2.0-flash-lite" in client.base_url

    def test_triage_diff_sync_success(self):
        transport = httpx.MockTransport(
            lambda req: _mock_gemini_response(VALID_GEMINI_API_BODY)
        )
        mock_http = httpx.Client(transport=transport)
        cfg = S1GateConfig(gemini_api_key="test-key")
        client = GeminiClient(cfg, client=mock_http)
        result = client.triage_diff("+ diff")

        assert isinstance(result, DecisionPayload)
        assert result.risk_score == 90
        assert result.category == "security_risk"
        assert result.trigger_agent is True

    @pytest.mark.asyncio
    async def test_triage_diff_async_success(self):
        transport = httpx.MockTransport(
            lambda req: _mock_gemini_response(VALID_GEMINI_API_BODY)
        )
        mock_async_http = httpx.AsyncClient(transport=transport)
        cfg = S1GateConfig(gemini_api_key="test-key")
        client = GeminiClient(cfg, async_client=mock_async_http)
        result = await client.triage_diff_async("+ diff")

        assert isinstance(result, DecisionPayload)
        assert result.risk_score == 90
        assert result.category == "security_risk"

    def test_missing_api_key_fail(self):
        cfg = S1GateConfig(gemini_api_key="", offline_behavior="fail")
        client = GeminiClient(cfg)
        with pytest.raises(GeminiUnavailableError):
            client.triage_diff("+ diff")

    def test_missing_api_key_pass(self):
        cfg = S1GateConfig(gemini_api_key="", offline_behavior="pass")
        client = GeminiClient(cfg)
        result = client.triage_diff("+ diff")
        assert result.risk_score == 0
        assert result.trigger_agent is False

    def test_malformed_response_raises_decision_parse_error(self):
        malformed_body = {
            "candidates": [{"content": {"parts": [{"text": "not-json"}]}}]
        }
        transport = httpx.MockTransport(
            lambda req: _mock_gemini_response(malformed_body)
        )
        mock_http = httpx.Client(transport=transport)
        cfg = S1GateConfig(gemini_api_key="test-key")
        client = GeminiClient(cfg, client=mock_http)
        with pytest.raises(DecisionParseError):
            client.triage_diff("+ diff")

    def test_verify_remediation_sync_success(self):
        transport = httpx.MockTransport(
            lambda req: _mock_gemini_response(VALID_GEMINI_VERIFY_BODY)
        )
        mock_http = httpx.Client(transport=transport)
        cfg = S1GateConfig(gemini_api_key="test-key")
        client = GeminiClient(cfg, client=mock_http)
        result = client.verify_remediation("+ old", "+ fixed", previous_score=90)

        assert isinstance(result, RemediationVerification)
        assert result.verified is True
        assert result.new_score == 5
        assert result.delta == -85
