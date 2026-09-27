"""Tests for policy_engine.py"""

import json
import pytest
from pathlib import Path

from kevgate.config import S1GateConfig
from kevgate.policy_engine import GateDecision, evaluate, generate_bob_task, format_gate_result
from kevgate.schema import DecisionPayload


def make_payload(**overrides) -> DecisionPayload:
    defaults = dict(
        category="safe_refactor",
        risk_score=0,
        confidence=0.9,
        is_breaking_change=False,
        exposes_unprotected_resource=False,
        unhandled_failure_mode=False,
        summary="Test finding.",
        target_file=None,
        target_lines=None,
        remediation_hint=None,
        trigger_agent=False,
    )
    defaults.update(overrides)
    return DecisionPayload(**defaults)


def make_config(**overrides) -> S1GateConfig:
    defaults = dict(
        lmstudio_base_url="http://localhost:1234/v1",
        block_threshold=70,
        warn_threshold=30,
    )
    defaults.update(overrides)
    return S1GateConfig(**defaults)


class TestEvaluate:
    def test_score_zero_is_pass(self):
        payload = make_payload(risk_score=0)
        assert evaluate(payload, make_config()) == GateDecision.PASS

    def test_score_29_is_pass(self):
        payload = make_payload(risk_score=29)
        assert evaluate(payload, make_config()) == GateDecision.PASS

    def test_score_30_is_warn(self):
        payload = make_payload(risk_score=30)
        assert evaluate(payload, make_config()) == GateDecision.WARN

    def test_score_69_is_warn(self):
        payload = make_payload(risk_score=69)
        assert evaluate(payload, make_config()) == GateDecision.WARN

    def test_score_70_is_block(self):
        payload = make_payload(risk_score=70)
        assert evaluate(payload, make_config()) == GateDecision.BLOCK

    def test_score_100_is_block(self):
        payload = make_payload(risk_score=100)
        assert evaluate(payload, make_config()) == GateDecision.BLOCK

    def test_trigger_agent_true_always_blocks(self):
        # Even with low score, trigger_agent=True forces BLOCK
        payload = make_payload(risk_score=5, trigger_agent=True)
        assert evaluate(payload, make_config()) == GateDecision.BLOCK

    def test_noul_breaking_change_at_threshold_blocks(self):
        payload = make_payload(risk_score=70, is_breaking_change=True)
        assert evaluate(payload, make_config()) == GateDecision.BLOCK

    def test_noul_below_threshold_does_not_block_alone(self):
        # Noul + score below block_threshold → WARN (score 50 >= warn_threshold 30)
        payload = make_payload(risk_score=50, is_breaking_change=True)
        assert evaluate(payload, make_config()) == GateDecision.WARN

    def test_secret_findings_force_block_regardless_of_score(self):
        payload = make_payload(risk_score=0)
        assert evaluate(payload, make_config(), secret_findings_count=1) == GateDecision.BLOCK

    def test_custom_thresholds_respected(self):
        config = make_config(block_threshold=50, warn_threshold=20)
        payload = make_payload(risk_score=49)
        assert evaluate(payload, config) == GateDecision.WARN

        payload_blocked = make_payload(risk_score=50)
        assert evaluate(payload_blocked, config) == GateDecision.BLOCK


class TestGenerateBobTask:
    def test_task_file_created(self, tmp_path: Path):
        payload = make_payload(
            risk_score=85,
            category="security_risk",
            summary="SQL injection found.",
            remediation_hint="Use parameterized queries.",
        )
        task_file = generate_bob_task(payload, repo_root=tmp_path)
        assert task_file.exists()

    def test_task_file_valid_json(self, tmp_path: Path):
        payload = make_payload(risk_score=85, summary="Test.")
        task_file = generate_bob_task(payload, repo_root=tmp_path)
        data = json.loads(task_file.read_text())
        assert data["task_type"] == "remediation"
        assert data["triggered_by"] == "s1gate"
        assert data["payload"]["risk_score"] == 85

    def test_task_file_path(self, tmp_path: Path):
        payload = make_payload(risk_score=85, summary="Test.")
        task_file = generate_bob_task(payload, repo_root=tmp_path)
        assert task_file == tmp_path / ".bob" / "tasks" / "pending_remediation.json"


class TestFormatGateResult:
    def test_pass_output_contains_pass(self):
        payload = make_payload(risk_score=5, summary="Clean formatting change.")
        result = format_gate_result(GateDecision.PASS, payload, use_color=False)
        assert "PASS" in result

    def test_block_output_contains_block(self):
        payload = make_payload(risk_score=85, summary="SQL injection.")
        result = format_gate_result(GateDecision.BLOCK, payload, use_color=False)
        assert "BLOCK" in result
        assert ".bob/tasks" in result

    def test_warn_output_contains_warn(self):
        payload = make_payload(risk_score=45, summary="New endpoint.")
        result = format_gate_result(GateDecision.WARN, payload, use_color=False)
        assert "WARN" in result
