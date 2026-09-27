"""
S1Gate MCP Server — Universal stdio MCP interface (MCP SDK v2).

Exposes three tools to any MCP-compatible agent harness (IBM Bob IDE,
Claude Code, Agrav, Kiro, Codex, DeepSeek):

  s1gate_triage_diff          Evaluate a unified diff.
  s1gate_inspect_file         Evaluate staged changes in a specific file.
  s1gate_verify_remediation   Actor-Critic: verify an agent's fix patch.

Run as:
  python -m kevgate.mcp_server

Or register in Bob IDE mcp.json:
  { "command": "python", "args": ["-m", "kevgate.mcp_server"] }
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

from mcp.server.mcpserver import MCPServer

from kevgate.config import S1GateConfig
from kevgate.diff_parser import (
    chunks_to_condensed_diff,
    extract_file_diff,
    filter_triageable,
    parse_unified_diff,
)
from kevgate.entropy_scanner import scan_diff
from kevgate.exceptions import (
    DecisionParseError,
    GeminiUnavailableError,
    LMStudioUnavailableError,
    S1GateError,
)
from kevgate.gemini_client import GeminiClient
from kevgate.lmstudio_client import LMStudioClient
from kevgate.policy_engine import GateDecision, evaluate, format_gate_result, generate_bob_task
from kevgate.schema import DecisionPayload

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

_config = S1GateConfig()
server = MCPServer(
    name=_config.mcp_server_name,
    version="0.1.0",
)

# Persistent client instances for keep-alive connection reuse
_persistent_gemini_client: Optional[GeminiClient] = None


def _get_gemini_client(config: S1GateConfig) -> GeminiClient:
    global _persistent_gemini_client
    if _persistent_gemini_client is None:
        _persistent_gemini_client = GeminiClient(config)
    return _persistent_gemini_client


# ---------------------------------------------------------------------------
# Helper: run triage against configured backend
# ---------------------------------------------------------------------------

async def _triage(diff: str, context: Optional[str] = None):
    t0 = time.perf_counter()
    config = S1GateConfig()
    secret_findings = scan_diff(diff, entropy_threshold=config.entropy_threshold)
    chunks = parse_unified_diff(diff)
    triageable = filter_triageable(chunks)

    # FAST PATH 1: Instant short-circuit on high-entropy secrets / credentials (< 0.05ms)
    if secret_findings:
        target_f = chunks[0].file_b if chunks else None
        first_s = secret_findings[0]
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        payload = DecisionPayload(
            category="security_risk",
            risk_score=95,
            confidence=0.99,
            is_breaking_change=False,
            exposes_unprotected_resource=True,
            unhandled_failure_mode=False,
            summary=f"Critical credential/secret leak detected ({first_s.pattern_name} with entropy {first_s.entropy_score:.2f}).",
            target_file=target_f,
            target_lines=str(first_s.line_number),
            remediation_hint=f"Revoke credential immediately and remove {first_s.pattern_name} from git history.",
            trigger_agent=True,
            processing_time_ms=elapsed,
        )
        decision = GateDecision.BLOCK
        try:
            generate_bob_task(payload)
        except Exception:
            pass
        return payload, decision, secret_findings

    # FAST PATH 2: Instant pass if only non-code / lockfiles / metadata changed (< 0.05ms)
    if chunks and not triageable:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        payload = DecisionPayload(
            category="safe_refactor",
            risk_score=0,
            confidence=1.0,
            is_breaking_change=False,
            exposes_unprotected_resource=False,
            unhandled_failure_mode=False,
            summary="No triageable code changes detected in diff.",
            target_file=None,
            target_lines=None,
            remediation_hint=None,
            trigger_agent=False,
            processing_time_ms=elapsed,
        )
        decision = GateDecision.PASS
        return payload, decision, secret_findings

    condensed = chunks_to_condensed_diff(triageable) if triageable else diff[:4000]

    if config.backend == "gemini":
        client = _get_gemini_client(config)
        payload = await client.triage_diff_async(condensed, context=context)
    else:
        async with LMStudioClient(config) as client:
            payload = await client.triage_diff(condensed, context=context)

    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    payload.processing_time_ms = elapsed
    decision = evaluate(payload, config, secret_findings_count=len(secret_findings))

    if decision.value == "BLOCK":
        try:
            generate_bob_task(payload)
        except Exception:
            pass  # Non-fatal

    return payload, decision, secret_findings


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@server.tool(
    name="s1gate_triage_diff",
    description=(
        "Evaluate a unified git diff through S1Gate's System-1 decision engine. "
        "Returns a risk classification, score (0-100), boolean security invariants, "
        "remediation hints, and processing time in milliseconds. Use before committing or as part of an Actor-Critic loop."
    ),
)
async def s1gate_triage_diff(diff: str, context: Optional[str] = None) -> str:
    """
    Args:
        diff: Unified git diff text (output of `git diff --cached` or similar).
        context: Optional commit message or PR description for additional context.
    """
    t0 = time.perf_counter()
    try:
        payload, decision, secret_findings = await _triage(diff, context=context)
    except S1GateError as exc:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({"error": str(exc), "processing_time_ms": elapsed})

    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    if payload.processing_time_ms is None:
        payload.processing_time_ms = elapsed

    result = {
        "decision": decision.value,
        "processing_time_ms": payload.processing_time_ms,
        "payload": payload.model_dump(),
        "secret_findings_count": len(secret_findings),
        "summary": format_gate_result(
            decision,
            payload,
            len(secret_findings),
            use_color=False,
            processing_time_ms=payload.processing_time_ms,
        ),
    }
    return json.dumps(result, indent=2)


@server.tool(
    name="s1gate_inspect_file",
    description=(
        "Evaluate staged or uncommitted changes in a specific file. "
        "Automatically extracts the diff from the current git repository "
        "and runs it through the S1Gate decision engine."
    ),
)
async def s1gate_inspect_file(file_path: str) -> str:
    """
    Args:
        file_path: Path to the file relative to the repository root.
    """
    t0 = time.perf_counter()
    try:
        diff = extract_file_diff(file_path)
    except Exception as exc:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({"error": f"Could not extract diff for {file_path}: {exc}", "processing_time_ms": elapsed})

    if not diff.strip():
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "decision": "PASS",
            "processing_time_ms": elapsed,
            "message": f"No changes detected in {file_path}.",
        })

    return await s1gate_triage_diff(diff, context=f"File inspection: {file_path}")


@server.tool(
    name="s1gate_verify_remediation",
    description=(
        "Actor-Critic verification loop: checks whether an agent's remediation patch "
        "resolves the risk identified in the original blocked diff. "
        "Returns verified status, score delta, verdict message, and processing time. "
        "Use after generating a fix to confirm the vulnerability was eliminated."
    ),
)
async def s1gate_verify_remediation(
    original_diff: str,
    remediation_patch: str,
    previous_score: Optional[int] = None,
) -> str:
    """
    Args:
        original_diff: The diff that was blocked by S1Gate.
        remediation_patch: The patch generated by the agent to fix the issue.
        previous_score: Risk score of the original diff (optional, for context).
    """
    t0 = time.perf_counter()
    config = S1GateConfig()
    score = previous_score or 70
    try:
        if config.backend == "gemini":
            client = _get_gemini_client(config)
            result = await client.verify_remediation_async(
                original_diff=original_diff,
                remediation_patch=remediation_patch,
                previous_score=score,
            )
        else:
            async with LMStudioClient(config) as client:
                result = await client.verify_remediation(
                    original_diff=original_diff,
                    remediation_patch=remediation_patch,
                    previous_score=score,
                )
    except S1GateError as exc:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({"error": str(exc), "processing_time_ms": elapsed})

    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    result.processing_time_ms = elapsed
    data = result.model_dump()
    data["processing_time_ms"] = elapsed
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
