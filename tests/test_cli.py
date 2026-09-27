"""Tests for cli.py — uses typer CliRunner (no subprocess, no live server)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from kevgate.cli import app
from kevgate.policy_engine import GateDecision
from kevgate.schema import DecisionPayload

# Patch target for the default Gemini backend used in CLI
_GEMINI_TRIAGE_PATH = "kevgate.cli.GeminiClient"

runner = CliRunner()


def make_safe_payload() -> DecisionPayload:
    return DecisionPayload(
        category="safe_refactor",
        risk_score=5,
        confidence=0.98,
        is_breaking_change=False,
        exposes_unprotected_resource=False,
        unhandled_failure_mode=False,
        summary="Minor comment update.",
        trigger_agent=False,
    )


def make_risky_payload() -> DecisionPayload:
    return DecisionPayload(
        category="security_risk",
        risk_score=88,
        confidence=0.95,
        is_breaking_change=False,
        exposes_unprotected_resource=True,
        unhandled_failure_mode=False,
        summary="SQL injection via string interpolation.",
        target_file="src/auth.py",
        target_lines="12-14",
        remediation_hint="Use parameterized queries.",
        trigger_agent=True,
    )


CLEAN_DIFF = """\
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-# Old Title
+# New Title
"""

RISKY_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,3 +1,3 @@
-    query = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
+    query = db.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""


class TestCheckCommand:
    def test_clean_diff_exits_0(self, tmp_path: Path):
        diff_file = tmp_path / "clean.diff"
        diff_file.write_text(CLEAN_DIFF)

        with patch(_GEMINI_TRIAGE_PATH) as MockGemini:
            instance = MagicMock()
            instance.triage_diff_async = AsyncMock(return_value=make_safe_payload())
            MockGemini.return_value = instance

            result = runner.invoke(app, ["check", "--diff", str(diff_file), "--no-color"])

        assert result.exit_code == 0, result.output
        assert "PASS" in result.output

    def test_risky_diff_exits_1(self, tmp_path: Path):
        diff_file = tmp_path / "risky.diff"
        diff_file.write_text(RISKY_DIFF)

        with patch(_GEMINI_TRIAGE_PATH) as MockGemini, \
             patch("kevgate.cli.generate_bob_task"):
            instance = MagicMock()
            instance.triage_diff_async = AsyncMock(return_value=make_risky_payload())
            MockGemini.return_value = instance

            result = runner.invoke(app, ["check", "--diff", str(diff_file), "--no-color"])

        assert result.exit_code == 1, result.output
        assert "BLOCK" in result.output

    def test_empty_diff_exits_0_with_no_changes_message(self, tmp_path: Path):
        diff_file = tmp_path / "empty.diff"
        diff_file.write_text("")

        result = runner.invoke(app, ["check", "--diff", str(diff_file)])
        assert result.exit_code == 0
        assert "No staged changes" in result.output

    def test_lockfile_only_diff_skips_llm(self, tmp_path: Path):
        lockfile_diff = """\
diff --git a/package-lock.json b/package-lock.json
--- a/package-lock.json
+++ b/package-lock.json
@@ -1 +1 @@
-  "version": "1.0.0",
+  "version": "1.0.1",
"""
        diff_file = tmp_path / "lockfile.diff"
        diff_file.write_text(lockfile_diff)

        with patch(_GEMINI_TRIAGE_PATH) as MockGemini:
            result = runner.invoke(app, ["check", "--diff", str(diff_file)])

        # LLM backend should NOT be called for lockfile-only diffs
        MockGemini.assert_not_called()
        assert result.exit_code == 0


class TestConfigCommand:
    def test_config_outputs_valid_json(self):
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "lmstudio_base_url" in data
        assert "block_threshold" in data
        assert "offline_behavior" in data


class TestMcpCommand:
    def test_mcp_help(self):
        result = runner.invoke(app, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "stdio" in result.output
        assert "sse" in result.output

    def test_mcp_stdio_invocation(self):
        with patch("kevgate.mcp_server.server.run_stdio_async", new_callable=AsyncMock) as mock_stdio:
            result = runner.invoke(app, ["mcp", "--transport", "stdio"])
            assert result.exit_code == 0
            mock_stdio.assert_called_once()

    def test_mcp_invalid_transport(self):
        result = runner.invoke(app, ["mcp", "--transport", "invalid-transport"])
        assert result.exit_code == 1
        assert "Unsupported transport" in result.output


class TestServeCommand:
    def test_serve_help(self):
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output

    def test_serve_invocation(self):
        with patch("uvicorn.run") as mock_uvicorn:
            result = runner.invoke(app, ["serve", "--port", "9999", "--api-key", "test-key"])
            assert result.exit_code == 0
            mock_uvicorn.assert_called_once()
            args, kwargs = mock_uvicorn.call_args
            assert kwargs.get("port") == 9999

