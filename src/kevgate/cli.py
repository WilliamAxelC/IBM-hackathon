"""
KevGate CLI — terminal interface for diff triage and git hook management.

Commands:
  kevgate check              Evaluate the current staged diff.
  kevgate check --diff FILE  Evaluate a diff from a file.
  kevgate hook install       Install the git pre-commit hook.
  kevgate hook uninstall     Remove the git pre-commit hook.
  kevgate config show        Print the resolved KevGate configuration.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer

from kevgate.config import KevGateConfig
from kevgate.diff_parser import (
    chunks_to_condensed_diff,
    extract_staged_diff,
    filter_triageable,
    parse_unified_diff,
)
from kevgate.entropy_scanner import scan_diff
from kevgate.exceptions import LMStudioUnavailableError
from kevgate.hook_manager import install_hook, uninstall_hook
from kevgate.lmstudio_client import LMStudioClient
from kevgate.policy_engine import GateDecision, evaluate, format_gate_result, generate_bob_task

app = typer.Typer(
    name="kevgate",
    help="Universal System-1 pre-commit gate and MCP server for agentic coding harnesses.",
    add_completion=False,
)
hook_app = typer.Typer(help="Git pre-commit hook management.")
app.add_typer(hook_app, name="hook")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

@app.command()
def check(
    diff_file: Optional[Path] = typer.Option(
        None,
        "--diff",
        "-d",
        help="Read diff from a file instead of `git diff --cached`.",
        exists=True,
        readable=True,
        metavar="FILE",
    ),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output."),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Optional commit message or PR description."
    ),
) -> None:
    """
    Evaluate the staged diff (or a diff file) through the KevGate decision pipeline.

    Exits with code 0 on PASS/WARN, code 1 on BLOCK.
    """
    config = KevGateConfig()

    # --- 1. Read diff ---
    if diff_file is not None:
        raw_diff = diff_file.read_text()
    else:
        try:
            raw_diff = extract_staged_diff()
        except Exception as exc:
            typer.echo(f"[kevgate] ERROR: Could not read staged diff: {exc}", err=True)
            raise typer.Exit(code=1)

    if not raw_diff.strip():
        typer.echo("[kevgate] No staged changes detected. Nothing to check.")
        raise typer.Exit(code=0)

    # --- 2. Pre-filter: entropy scanner ---
    secret_findings = scan_diff(raw_diff, entropy_threshold=config.entropy_threshold)

    # --- 3. Parse and filter diff chunks ---
    chunks = parse_unified_diff(raw_diff)
    triageable = filter_triageable(chunks)

    if not triageable and not secret_findings:
        typer.echo("[kevgate] Only lockfiles/artifacts in diff — skipping LLM triage. ✓ PASS")
        raise typer.Exit(code=0)

    # --- 4. LM Studio triage ---
    condensed = chunks_to_condensed_diff(triageable) if triageable else raw_diff[:4000]

    async def _run_triage():
        async with LMStudioClient(config) as client:
            return await client.triage_diff(condensed, context=context)

    try:
        payload = asyncio.run(_run_triage())
    except LMStudioUnavailableError as exc:
        # offline_behavior='fail' re-raises; 'pass'/'warn' returns safe payload
        typer.echo(f"[kevgate] {exc}", err=True)
        raise typer.Exit(code=1)

    # --- 5. Policy evaluation ---
    decision = evaluate(payload, config, secret_findings_count=len(secret_findings))

    # --- 6. Output ---
    use_color = not no_color and sys.stdout.isatty()
    typer.echo(format_gate_result(decision, payload, len(secret_findings), use_color=use_color))

    # --- 7. On BLOCK: write Bob task and exit 1 ---
    if decision == GateDecision.BLOCK:
        try:
            task_file = generate_bob_task(payload)
            typer.echo(f"[kevgate] Bob task written → {task_file}", err=True)
        except Exception as exc:
            typer.echo(f"[kevgate] Warning: Could not write Bob task: {exc}", err=True)
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# hook
# ---------------------------------------------------------------------------

@hook_app.command("install")
def hook_install(
    repo: Optional[Path] = typer.Option(
        None, "--repo", help="Path to the git repository root (default: cwd)."
    ),
) -> None:
    """Install the KevGate pre-commit hook into the current git repository."""
    try:
        hook_file = install_hook(repo_root=repo)
        typer.echo(f"[kevgate] Pre-commit hook installed → {hook_file}")
    except FileExistsError as exc:
        typer.echo(f"[kevgate] ERROR: {exc}", err=True)
        raise typer.Exit(code=1)
    except FileNotFoundError as exc:
        typer.echo(f"[kevgate] ERROR: {exc}", err=True)
        raise typer.Exit(code=1)


@hook_app.command("uninstall")
def hook_uninstall(
    repo: Optional[Path] = typer.Option(
        None, "--repo", help="Path to the git repository root (default: cwd)."
    ),
) -> None:
    """Remove the KevGate pre-commit hook from the current git repository."""
    try:
        removed = uninstall_hook(repo_root=repo)
        if removed:
            typer.echo("[kevgate] Pre-commit hook removed.")
        else:
            typer.echo("[kevgate] No KevGate hook found.")
    except PermissionError as exc:
        typer.echo(f"[kevgate] ERROR: {exc}", err=True)
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

@app.command()
def config() -> None:
    """Print the resolved KevGate configuration (useful for debugging)."""
    cfg = KevGateConfig()
    typer.echo(cfg.model_dump_json(indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
