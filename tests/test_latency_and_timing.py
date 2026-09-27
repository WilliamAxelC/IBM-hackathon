"""
Tests for latency tracking, processing time reporting, and performance optimizations.
"""

from __future__ import annotations

import json
import pytest
import httpx

from kevgate.config import S1GateConfig
from kevgate.gemini_client import GeminiClient
from kevgate.mcp_server import s1gate_triage_diff, s1gate_inspect_file, s1gate_verify_remediation
from kevgate.schema import DecisionPayload, RemediationVerification
from kevgate.policy_engine import GateDecision, format_gate_result


def test_schema_processing_time():
    """Verify processing_time_ms is properly serialized and deserialized."""
    payload = DecisionPayload(
        category="safe_refactor",
        risk_score=10,
        confidence=0.9,
        is_breaking_change=False,
        exposes_unprotected_resource=False,
        unhandled_failure_mode=False,
        summary="Safe refactor.",
        trigger_agent=False,
        processing_time_ms=12.34,
    )
    assert payload.processing_time_ms == 12.34
    data = payload.model_dump()
    assert data["processing_time_ms"] == 12.34

    verify = RemediationVerification(
        verified=True,
        previous_score=80,
        new_score=10,
        delta=-70,
        message="Fixed clean.",
        processing_time_ms=56.78,
    )
    assert verify.processing_time_ms == 56.78
    assert verify.model_dump()["processing_time_ms"] == 56.78


def test_format_gate_result_displays_latency():
    """Verify format_gate_result displays latency."""
    payload = DecisionPayload(
        category="safe_refactor",
        risk_score=5,
        confidence=0.95,
        is_breaking_change=False,
        exposes_unprotected_resource=False,
        unhandled_failure_mode=False,
        summary="Clean changes.",
        trigger_agent=False,
        processing_time_ms=45.6,
    )
    res = format_gate_result(GateDecision.PASS, payload, use_color=False)
    assert "latency: 45.6ms" in res


@pytest.mark.asyncio
async def test_mcp_triage_diff_reports_processing_time():
    """Verify s1gate_triage_diff returns processing_time_ms in JSON."""
    diff = """--- a/docs/README.md
+++ b/docs/README.md
@@ -1,1 +1,1 @@
-Old readme
+New readme
"""
    raw_res = await s1gate_triage_diff(diff)
    res = json.loads(raw_res)
    assert "processing_time_ms" in res
    assert isinstance(res["processing_time_ms"], (int, float))
    assert res["processing_time_ms"] >= 0
    assert res["decision"] == "PASS"


@pytest.mark.asyncio
async def test_mcp_secret_fast_path_latency():
    """Verify that committing a critical secret triggers instant short-circuit (< 20ms)."""
    diff = """--- a/config.py
+++ b/config.py
@@ -1,1 +1,1 @@
+AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
"""
    raw_res = await s1gate_triage_diff(diff)
    res = json.loads(raw_res)
    assert res["decision"] == "BLOCK"
    assert "processing_time_ms" in res
    # Fast path should finish in under 20ms
    assert res["processing_time_ms"] < 20.0
    assert res["secret_findings_count"] >= 1
    assert "Critical credential/secret leak detected" in res["payload"]["summary"]


@pytest.mark.asyncio
async def test_mcp_inspect_file_reports_processing_time():
    """Verify s1gate_inspect_file returns processing_time_ms."""
    raw_res = await s1gate_inspect_file("non_existent_file_xyz.py")
    res = json.loads(raw_res)
    assert "processing_time_ms" in res
    assert res["decision"] == "PASS"


@pytest.mark.asyncio
async def test_mcp_verify_remediation_reports_processing_time():
    """Verify s1gate_verify_remediation returns processing_time_ms."""
    # When offline or missing API key
    raw_res = await s1gate_verify_remediation("+ old", "+ fixed", previous_score=80)
    res = json.loads(raw_res)
    assert "processing_time_ms" in res
    assert res["verified"] is True
