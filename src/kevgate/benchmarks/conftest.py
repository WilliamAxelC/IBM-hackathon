"""
S1Gate Benchmark Suite — 20 real-world diffs with automated pass/fail evaluation.

Run with mock mode (no LM Studio required):
  pytest src/kevgate/benchmarks/ --mock

Run against live LM Studio (requires model loaded on localhost:1234):
  pytest src/kevgate/benchmarks/

Results summary is printed at the end showing recall and false-positive rate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock

import pytest

from kevgate.config import S1GateConfig
from kevgate.entropy_scanner import scan_diff
from kevgate.gemini_client import GeminiClient
from kevgate.lmstudio_client import LMStudioClient
from kevgate.policy_engine import GateDecision, evaluate
from kevgate.schema import DecisionPayload

# ---------------------------------------------------------------------------
# Pytest option
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--mock",
        action="store_true",
        default=False,
        help="Run benchmarks with mock LM Studio client (no GPU required).",
    )


# ---------------------------------------------------------------------------
# Mock payloads — returned by the mock client based on diff category
# ---------------------------------------------------------------------------

def _make_risky_payload(summary: str = "Security risk detected.") -> DecisionPayload:
    return DecisionPayload(
        category="security_risk",
        risk_score=85,
        confidence=0.92,
        is_breaking_change=False,
        exposes_unprotected_resource=True,
        unhandled_failure_mode=False,
        summary=summary,
        trigger_agent=True,
    )


def _make_safe_payload(summary: str = "Safe change.") -> DecisionPayload:
    return DecisionPayload(
        category="safe_refactor",
        risk_score=8,
        confidence=0.97,
        is_breaking_change=False,
        exposes_unprotected_resource=False,
        unhandled_failure_mode=False,
        summary=summary,
        trigger_agent=False,
    )


# ---------------------------------------------------------------------------
# Benchmark parametrization
# ---------------------------------------------------------------------------

_BENCHMARKS_DIR = Path(__file__).parent

# True positives: expect BLOCK
TRUE_POSITIVE_DIFFS = sorted(_BENCHMARKS_DIR.glob("true_positives/*.diff"))
# False positives: expect PASS or WARN (not BLOCK)
FALSE_POSITIVE_DIFFS = sorted(_BENCHMARKS_DIR.glob("false_positives/*.diff"))


# ---------------------------------------------------------------------------
# True positive tests — must BLOCK
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("diff_file", TRUE_POSITIVE_DIFFS, ids=[f.stem for f in TRUE_POSITIVE_DIFFS])
@pytest.mark.asyncio
async def test_true_positive_is_blocked(diff_file: Path, request):
    """Each true-positive diff MUST be blocked by the gate (BLOCK decision)."""
    diff_text = diff_file.read_text()
    config = S1GateConfig(
        block_threshold=70,
        warn_threshold=30,
        offline_behavior="fail",
    )

    use_mock = request.config.getoption("--mock", default=False)
    secret_findings = scan_diff(diff_text)

    if use_mock:
        # In mock mode: inject a risky payload directly
        payload = _make_risky_payload(f"Mock: risk detected in {diff_file.stem}")
    elif config.backend == "gemini" and config.gemini_api_key:
        client = GeminiClient(config)
        payload = await client.triage_diff_async(diff_text)
    else:
        async with LMStudioClient(config) as client:
            payload = await client.triage_diff(diff_text)

    decision = evaluate(payload, config, secret_findings_count=len(secret_findings))

    assert decision == GateDecision.BLOCK, (
        f"Expected BLOCK for {diff_file.name} but got {decision.value}. "
        f"risk_score={payload.risk_score}, category={payload.category}, "
        f"summary={payload.summary!r}"
    )


# ---------------------------------------------------------------------------
# False positive tests — must NOT block (PASS or WARN only)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("diff_file", FALSE_POSITIVE_DIFFS, ids=[f.stem for f in FALSE_POSITIVE_DIFFS])
@pytest.mark.asyncio
async def test_false_positive_is_not_blocked(diff_file: Path, request):
    """Each false-positive diff MUST NOT be blocked (only PASS or WARN allowed)."""
    diff_text = diff_file.read_text()
    config = S1GateConfig(
        block_threshold=70,
        warn_threshold=30,
        offline_behavior="fail",
    )

    use_mock = request.config.getoption("--mock", default=False)
    secret_findings = scan_diff(diff_text)

    if use_mock:
        payload = _make_safe_payload(f"Mock: safe change in {diff_file.stem}")
    elif config.backend == "gemini" and config.gemini_api_key:
        client = GeminiClient(config)
        payload = await client.triage_diff_async(diff_text)
    else:
        async with LMStudioClient(config) as client:
            payload = await client.triage_diff(diff_text)

    decision = evaluate(payload, config, secret_findings_count=len(secret_findings))

    assert decision != GateDecision.BLOCK, (
        f"FALSE POSITIVE: {diff_file.name} was incorrectly blocked. "
        f"risk_score={payload.risk_score}, category={payload.category}, "
        f"summary={payload.summary!r}"
    )

