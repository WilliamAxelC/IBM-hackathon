"""
Policy engine — translates a DecisionPayload into a gate decision.

Applies configurable thresholds and invariant checks, then optionally
generates an IBM Bob task file for blocked commits.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Optional

from kevgate.config import KevGateConfig
from kevgate.schema import DecisionPayload


class GateDecision(str, Enum):
    """Result of the policy engine evaluation."""

    PASS = "PASS"
    """Commit is safe. Exit code 0."""

    WARN = "WARN"
    """Commit is borderline. Warning printed, exit code 0."""

    BLOCK = "BLOCK"
    """Commit is blocked. Remediation dispatched. Exit code 1."""


def evaluate(
    payload: DecisionPayload,
    config: KevGateConfig | None = None,
    secret_findings_count: int = 0,
) -> GateDecision:
    """
    Evaluate a DecisionPayload against the configured risk thresholds.

    Decision logic (in priority order):
    1. Any secret findings from the entropy pre-filter → BLOCK immediately.
    2. trigger_agent=True → always BLOCK regardless of score.
    3. Any Noul invariant is True AND risk_score >= block_threshold → BLOCK.
    4. risk_score >= block_threshold → BLOCK.
    5. risk_score >= warn_threshold → WARN.
    6. Otherwise → PASS.

    Args:
        payload: Typed decision output from the LM Studio adapter.
        config: KevGate configuration. Loads from environment if None.
        secret_findings_count: Number of secrets found by the entropy pre-filter.

    Returns:
        GateDecision enum value.
    """
    cfg = config or KevGateConfig()

    # Rule 1: Pre-filter caught secrets
    if secret_findings_count > 0:
        return GateDecision.BLOCK

    # Rule 2: Model explicitly requested agent dispatch
    if payload.trigger_agent:
        return GateDecision.BLOCK

    # Rule 3: Critical Noul + high risk score
    any_noul = (
        payload.is_breaking_change
        or payload.exposes_unprotected_resource
        or payload.unhandled_failure_mode
    )
    if any_noul and payload.risk_score >= cfg.block_threshold:
        return GateDecision.BLOCK

    # Rule 4: Score threshold
    if payload.risk_score >= cfg.block_threshold:
        return GateDecision.BLOCK

    # Rule 5: Warn zone
    if payload.risk_score >= cfg.warn_threshold:
        return GateDecision.WARN

    return GateDecision.PASS


def generate_bob_task(
    payload: DecisionPayload,
    repo_root: Path | None = None,
) -> Path:
    """
    Write a pending remediation task file for IBM Bob IDE Agent mode.

    The file is written to `.bob/tasks/pending_remediation.json` under
    the repo root. Bob IDE's Agent mode polls this directory for task
    specifications to execute autonomously.

    Args:
        payload: The DecisionPayload that triggered the BLOCK.
        repo_root: Path to the repository root. Defaults to cwd.

    Returns:
        Path to the written task file.
    """
    root = repo_root or Path.cwd()
    tasks_dir = root / ".bob" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    task_file = tasks_dir / "pending_remediation.json"

    task = {
        "task_type": "remediation",
        "triggered_by": "kevgate",
        "version": "1.0",
        "payload": payload.model_dump(),
        "instructions": (
            payload.remediation_hint
            or f"Investigate and fix the following issue: {payload.summary}"
        ),
        "verification_tool": "kevgate_verify_remediation",
        "metadata": {
            "risk_score": payload.risk_score,
            "category": payload.category,
            "target_file": payload.target_file,
            "target_lines": payload.target_lines,
        },
    }

    task_file.write_text(json.dumps(task, indent=2))
    return task_file


def format_gate_result(
    decision: GateDecision,
    payload: DecisionPayload,
    secret_findings_count: int = 0,
    use_color: bool = True,
) -> str:
    """
    Format the gate result as a human-readable string for CLI output.
    """
    colors = {
        GateDecision.PASS: "\033[92m",   # green
        GateDecision.WARN: "\033[93m",   # yellow
        GateDecision.BLOCK: "\033[91m",  # red
    }
    reset = "\033[0m"

    color = colors[decision] if use_color else ""
    end = reset if use_color else ""

    lines = [
        f"{color}╔══ S1Gate ─ {decision.value} ══╗{end}",
        f"  Category   : {payload.category}",
        f"  Risk Score : {payload.risk_score}/100  (confidence: {payload.confidence:.0%})",
        f"  Summary    : {payload.summary}",
    ]

    if secret_findings_count > 0:
        lines.append(f"{color}  ⚠ Secrets  : {secret_findings_count} potential secret(s) detected in diff{end}")

    if payload.target_file:
        target = payload.target_file
        if payload.target_lines:
            target += f":{payload.target_lines}"
        lines.append(f"  Target     : {target}")

    if payload.remediation_hint and decision == GateDecision.BLOCK:
        lines.append(f"  Fix        : {payload.remediation_hint}")

    if decision == GateDecision.BLOCK:
        lines.append(f"{color}  → Commit blocked. Bob task written to .bob/tasks/pending_remediation.json{end}")
    elif decision == GateDecision.WARN:
        lines.append(f"{color}  → Commit allowed with warning.{end}")
    else:
        lines.append(f"{color}  → Commit approved.{end}")

    return "\n".join(lines)
