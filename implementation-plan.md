# KevGate: Implementation Plan

> **Status**: Ready for implementation  
> **Source Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)  
> **Hackathon Guide**: [HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)

---

## Critical Architecture Review

Before implementation, the following issues with the current architecture design require resolution:

### ❌ Issue 1: "Non-autoregressive" is marketing fiction for Kev-4B
The architecture repeatedly claims Kev-4B runs as a "non-autoregressive single-forward-pass" model. This is false for any GGUF-served chat model in LM Studio — those are all standard autoregressive transformers. The 30–60ms latency claim is plausible for `Q4_K_M` with `max_tokens: 80` and grammar-constrained JSON decoding, but the architectural framing is misleading. **Fix**: Drop "non-autoregressive" from all descriptions. The actual differentiator is `max_tokens: 80` + JSON grammar constraint, which short-circuits generation early. That's still a valid technical claim.

### ❌ Issue 2: No fallback when LM Studio is not running
The architecture silently assumes LM Studio is always available at `localhost:1234`. A pre-commit hook that hangs or crashes because the local server is down will be worse than no hook at all — developers will `--no-verify` it immediately. **Fix**: The `lmstudio_client.py` must have a timeout (≤500ms), a configurable skip-on-unavailable flag (`KEVGATE_OFFLINE_BEHAVIOR=pass|fail|warn`), and a clear error message.

### ❌ Issue 3: MCP server transport — stdio only for Bob
The architecture says "stdio and sse" but Bob IDE's MCP config uses `command` + `args`, which is stdio. SSE is for HTTP-based remote MCP servers. Mixing the two without clarification creates configuration ambiguity. **Fix**: Implement stdio transport first (covers Bob IDE, Claude Code, Agrav, Kiro). SSE is a stretch goal if time permits.

### ❌ Issue 4: The benchmark suite has no automation
"20 curated test diffs" with manual verification is not a benchmark suite — it's a folder of files. Without an automated test runner (`pytest` or similar), there is no way to measure regression between implementations and no reproducible pass/fail evidence for judges. **Fix**: Each benchmark diff must have a corresponding expected `DecisionPayload` JSON and be runnable via `pytest benchmarks/`.

### ❌ Issue 5: `policy_engine.py` thresholds are hardcoded magic numbers
Risk score 70 as a block threshold is an architectural constant that needs to be configurable. Different repos have different risk tolerances. **Fix**: Policy thresholds must be loaded from a `.kevgate.toml` config file with documented defaults, not embedded in source.

### ✅ What the architecture gets right
- Unified diff as the universal evaluation surface (polyglot, no AST dependency) — solid.
- `DecisionPayload` Pydantic schema with Literal categories and boolean invariants — clean.
- Actor-Critic verification loop via `kevgate_verify_remediation` — novel and directly relevant to LLM hallucination.
- Bobcoin conservation framing — directly addresses the hackathon judging criteria.
- IBM Bob task dispatch via `.bob/tasks/pending_remediation.json` — ties System-1 output directly to Bob IDE Agent mode, which is the strongest judging differentiator.

---

## Top-Level Overview

Build KevGate as a working Python package (`src/kevgate/`) with:
1. A fast local pre-filter (entropy scanner)
2. An LM Studio adapter calling Kev-4B with grammar-constrained JSON output
3. A CLI and git pre-commit hook installer
4. A universal MCP server (stdio) exposing 3 tools to Bob IDE, Claude Code, and other harnesses
5. An automated benchmark suite of 20 diffs with verifiable pass/fail output

IBM Bob IDE is used to build, test, and run the project. Each milestone generates a `bob_sessions/` screenshot.

---

## Sub-Task 1: Project Scaffold & Configuration Layer

**Status**: `[ ] pending`

### Intent
Establish the package layout, dependency manifest, and configuration schema before any logic is written. Getting this right prevents refactoring later and ensures every other sub-task has a clean foundation.

### Expected Outcomes
- `src/kevgate/` package installable via `pip install -e .`
- `pyproject.toml` with all required dependencies pinned
- `.kevgate.toml` schema defined and loadable via Pydantic Settings
- `src/kevgate/schema.py` with `DecisionPayload` fully defined
- `src/kevgate/config.py` loading `.kevgate.toml` with documented defaults

### Todo List
1. Create `pyproject.toml` with build-system (`hatchling`), metadata, and dependencies: `pydantic>=2.0`, `pydantic-settings`, `httpx`, `typer[all]`, `mcp` (Anthropic MCP SDK), `pytest`, `pytest-asyncio`.
2. Create `src/kevgate/__init__.py` (empty, version string only).
3. Create `src/kevgate/schema.py` — implement `DecisionPayload` exactly as in `ARCHITECTURE.md` §5, using Pydantic v2 `model_validator` to enforce that `trigger_agent=True` requires `risk_score >= 70`.
4. Create `src/kevgate/config.py` — implement `KevGateConfig` using `pydantic-settings` loading from `.kevgate.toml`. Fields: `lmstudio_base_url` (default `http://localhost:1234/v1`), `lmstudio_model` (default `kev-4b`), `block_threshold` (default `70`), `warn_threshold` (default `30`), `offline_behavior` (Literal `pass|fail|warn`, default `warn`), `request_timeout_ms` (default `500`).
5. Create `src/kevgate/exceptions.py` — define `LMStudioUnavailableError`, `DecisionParseError`, `GateBlockedError`.
6. Verify `pip install -e .` succeeds and `python -c "from kevgate.schema import DecisionPayload"` works.

### Relevant Context
- Architecture §5 defines the `DecisionPayload` Pydantic schema verbatim
- Issue fixes: hardcoded thresholds → `config.py`; LM Studio unavailability → `offline_behavior` field
- MCP SDK: `pip install mcp` installs the Anthropic reference SDK for Python stdio servers

---

## Sub-Task 2: Fast Pre-Filter — Entropy Scanner & Diff Parser

**Status**: `[ ] pending`

### Intent
Implement the two sub-millisecond pre-processing modules. These run before the LM Studio call and provide immediate, deterministic catches (leaked secrets, lockfile noise) that should never waste LLM inference time.

### Expected Outcomes
- `src/kevgate/entropy_scanner.py`: Shannon entropy function + regex patterns for common secret formats (AWS keys, GH tokens, private keys, `.env` values)
- `src/kevgate/diff_parser.py`: Git diff extraction and chunking — given a raw unified diff string, return a list of `DiffChunk` objects (file path, changed lines, context lines)
- Both modules have unit tests in `tests/test_entropy_scanner.py` and `tests/test_diff_parser.py` that pass via `pytest`

### Todo List
1. Implement `entropy_scanner.py`:
   - `shannon_entropy(data: str) -> float` — standard formula, O(n).
   - `ENTROPY_THRESHOLD = 4.5` (configurable via config) — strings above this are flagged.
   - `SECRET_PATTERNS: list[re.Pattern]` — cover: `AKIA[0-9A-Z]{16}` (AWS key), `ghp_[A-Za-z0-9]{36}` (GitHub PAT), `-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----`, generic `[A-Za-z0-9+/]{40,}=` near assignment operators.
   - `scan_diff(diff: str) -> list[SecretFinding]` — returns findings with line number, pattern name, and entropy score.
2. Implement `diff_parser.py`:
   - `parse_unified_diff(raw_diff: str) -> list[DiffChunk]` — use stdlib `difflib` heuristics or manual parsing of `+++ / --- / @@ / + / -` markers.
   - `DiffChunk` dataclass: `file_path`, `added_lines`, `removed_lines`, `context`.
   - `extract_staged_diff() -> str` — runs `git diff --cached` via `subprocess.run`, returns stdout. Raises `subprocess.CalledProcessError` on failure.
3. Write `tests/test_entropy_scanner.py` — test known AWS key strings (high entropy), plain English comments (low entropy), and `.env` secret patterns.
4. Write `tests/test_diff_parser.py` — test parsing a known unified diff string into expected `DiffChunk` objects.
5. Run `pytest tests/` — all pass.

### Relevant Context
- Architecture §2: "Language-agnostic Shannon Entropy Scanner" is the sub-2ms pre-filter
- Architecture §9: `entropy_scanner.py`, `diff_parser.py` are separate files in the module
- `subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)` is the standard git staged diff command

---

## Sub-Task 3: LM Studio Adapter — Decision Engine

**Status**: `[ ] pending`

### Intent
Implement the HTTP client that calls the locally-running Kev-4B model in LM Studio and parses the constrained JSON response into a `DecisionPayload`. This is the core intelligence layer.

### Expected Outcomes
- `src/kevgate/lmstudio_client.py` with async `triage_diff()` and `verify_remediation()` methods
- Timeout handling: raises `LMStudioUnavailableError` if no response within `config.request_timeout_ms`
- JSON schema-constrained request: `response_format={"type": "json_object"}`, `max_tokens=80`, `temperature=0.0`
- Fallback behavior driven by `config.offline_behavior`
- Unit tests using `httpx` mock transport (no live server required)

### Todo List
1. Implement `lmstudio_client.py`:
   - `LMStudioClient(config: KevGateConfig)` class.
   - `async def triage_diff(diff: str, context: str | None = None) -> DecisionPayload` — builds prompt, calls `/v1/chat/completions`, parses JSON into `DecisionPayload`.
   - `async def verify_remediation(original_diff: str, remediation_patch: str) -> RemediationVerification` — delta evaluation returning `verified`, `previous_score`, `new_score`, `delta`, `message`.
   - Add `RemediationVerification` dataclass to `schema.py`.
   - Implement timeout via `httpx.AsyncClient(timeout=config.request_timeout_ms / 1000)`.
   - On `httpx.ConnectError` or timeout: check `config.offline_behavior` — `pass` returns a synthetic low-risk payload, `fail` raises `LMStudioUnavailableError`, `warn` returns low-risk payload and prints a warning to stderr.
2. Write the system prompt — instruct the model to output only valid JSON matching `DecisionPayload` fields. Provide field descriptions inline. Keep the prompt under 300 tokens.
3. Implement `DecisionPayload` JSON parsing with graceful fallback: if `model_validate_json()` fails, raise `DecisionParseError` with the raw response for debugging.
4. Write `tests/test_lmstudio_client.py` using `httpx.MockTransport` — test: successful parse, timeout behavior (mock slow response), malformed JSON response (expect `DecisionParseError`).
5. Run `pytest tests/` — all pass.

### Relevant Context
- Architecture §7: `temperature=0.0`, `max_tokens=80`, `response_format={"type": "json_object"}`, port `1234`
- Architecture §3: `kevgate_verify_remediation` response schema defined verbatim
- Issue fix: no silent crash on LM Studio unavailability — `offline_behavior` field from Sub-Task 1 controls this

---

## Sub-Task 4: Policy Engine & Gate Decision

**Status**: `[ ] pending`

### Intent
Implement the routing layer that reads a `DecisionPayload`, applies the configured thresholds, and returns an actionable gate decision (`PASS`, `WARN`, `BLOCK`). Also implements the IBM Bob task file generator for blocked commits.

### Expected Outcomes
- `src/kevgate/policy_engine.py` — takes `DecisionPayload` + `KevGateConfig` and returns `GateDecision`
- `GateDecision` enum: `PASS`, `WARN`, `BLOCK`
- On `BLOCK`: generates `.bob/tasks/pending_remediation.json` in the repo root with the full `DecisionPayload` and `remediation_hint`
- Unit tests covering threshold boundary cases

### Todo List
1. Implement `policy_engine.py`:
   - `GateDecision` enum (`PASS`, `WARN`, `BLOCK`).
   - `evaluate(payload: DecisionPayload, config: KevGateConfig) -> GateDecision`:
     - Any `True` Noul (`is_breaking_change`, `exposes_unprotected_resource`, `unhandled_failure_mode`) with `risk_score >= config.block_threshold` → `BLOCK`.
     - `payload.trigger_agent == True` → always `BLOCK`.
     - `risk_score >= config.block_threshold` → `BLOCK`.
     - `risk_score >= config.warn_threshold` → `WARN`.
     - Otherwise → `PASS`.
   - `generate_bob_task(payload: DecisionPayload, repo_root: Path) -> Path` — writes `.bob/tasks/pending_remediation.json`. Schema: `{"task_type": "remediation", "triggered_by": "kevgate", "payload": payload.model_dump(), "instructions": payload.remediation_hint}`.
2. Write `tests/test_policy_engine.py` — test: `risk_score=69` → `WARN`, `risk_score=70` → `BLOCK`, `trigger_agent=True, risk_score=5` → `BLOCK` (invariant), `noul=True, score=71` → `BLOCK`.
3. Run `pytest tests/` — all pass.

### Relevant Context
- Architecture §2: "Risk Score >= 70 OR trigger_agent?" is the gate condition
- Architecture §8: `.bob/tasks/pending_remediation.json` is the IBM Bob task dispatch mechanism
- Issue fix: thresholds come from `config.block_threshold` / `config.warn_threshold`, not hardcoded

---

## Sub-Task 5: CLI & Git Pre-Commit Hook

**Status**: `[ ] pending`

### Intent
Expose KevGate as a developer-facing CLI (`kevgate`) with commands for manual diff checking and automatic git hook installation/removal.

### Expected Outcomes
- `kevgate check` — reads `git diff --cached`, runs the full gate pipeline, prints result with color, exits `0` on PASS/WARN, exits `1` on BLOCK
- `kevgate check --diff <file>` — reads diff from a file (for testing without a git repo)
- `kevgate hook install` — installs `.git/hooks/pre-commit` in the CWD repo
- `kevgate hook uninstall` — removes the pre-commit hook
- `kevgate config show` — prints resolved `KevGateConfig` (for debugging)
- End-to-end test: run `kevgate check --diff benchmarks/true_positives/sqli.diff` exits `1`

### Todo List
1. Implement `cli.py` using `typer`:
   - `app = typer.Typer(name="kevgate")`
   - `check` command: orchestrates `extract_staged_diff()` → `entropy_scanner.scan_diff()` → `LMStudioClient.triage_diff()` → `policy_engine.evaluate()` → print result → `sys.exit`.
   - `hook install` / `hook uninstall` commands delegating to `hook_manager.py`.
   - `config show` command printing `KevGateConfig().model_dump_json(indent=2)`.
2. Implement `hook_manager.py`:
   - `install_hook(repo_root: Path)` — writes `.git/hooks/pre-commit` with `#!/bin/sh\nkevgate check\n`, sets `chmod +x`.
   - `uninstall_hook(repo_root: Path)` — removes or backs up the hook file.
   - Guards: check if a pre-commit hook already exists (not installed by KevGate) and prompt the user before overwriting.
3. Register `kevgate` entry point in `pyproject.toml`: `[project.scripts] kevgate = "kevgate.cli:app"`.
4. Write `tests/test_cli.py` using `typer.testing.CliRunner` — test: `check --diff` with a clean diff (exit 0), a known risky diff (exit 1), `config show` prints valid JSON.
5. Run `pytest tests/` — all pass.

### Relevant Context
- Architecture §9: `cli.py`, `hook_manager.py` are separate files
- Architecture §2: exit code `0` on pass, exit code `1` on block
- `typer.testing.CliRunner` allows CLI testing without subprocess

---

## Sub-Task 6: Universal MCP Server (stdio)

**Status**: `[ ] pending`

### Intent
Expose KevGate's decision engine as a standard MCP server over stdio, allowing IBM Bob IDE, Claude Code, and other MCP-compatible harnesses to call `kevgate_triage_diff`, `kevgate_inspect_file`, and `kevgate_verify_remediation` as structured tool calls.

### Expected Outcomes
- `src/kevgate/mcp_server.py` runnable as `python -m kevgate.mcp_server`
- All 3 tools from Architecture §3 implemented and discoverable via MCP `tools/list`
- `mcp.json` config file generated at repo root for IBM Bob IDE registration
- `.claude/mcp.json` generated for Claude Code registration
- Manual smoke test: Bob IDE can call `kevgate_triage_diff` with a sample diff and receive a `DecisionPayload`

### Todo List
1. Implement `mcp_server.py` using the `mcp` Python SDK (Anthropic reference implementation):
   - `server = Server("kevgate")`
   - Register `kevgate_triage_diff` tool: input schema from Architecture §3, handler calls `LMStudioClient.triage_diff()`, returns `DecisionPayload.model_dump_json()`.
   - Register `kevgate_inspect_file` tool: input `file_path`, handler runs `git diff HEAD -- <file_path>`, then calls `triage_diff`.
   - Register `kevgate_verify_remediation` tool: input schema from Architecture §3, handler calls `LMStudioClient.verify_remediation()`, returns `RemediationVerification.model_dump_json()`.
   - `if __name__ == "__main__": asyncio.run(server.run_stdio_async())`.
2. Write `mcp.json` at repo root:
   ```json
   {
     "mcpServers": {
       "kevgate": {
         "command": "python",
         "args": ["-m", "kevgate.mcp_server"],
         "env": { "KEVGATE_LMSTUDIO_BASE_URL": "http://localhost:1234/v1" }
       }
     }
   }
   ```
3. Write `.claude/mcp.json` at repo root with identical config (Claude Code format).
4. Write `tests/test_mcp_server.py` — use the MCP SDK's in-process test client to call each tool and assert the response schema is valid.
5. Run `pytest tests/` — all pass.
6. Manual Bob IDE smoke test: add KevGate MCP server to Bob IDE settings and verify tool list appears.

### Relevant Context
- Architecture §3 defines all three MCP tool schemas verbatim
- Architecture §4 defines `mcp.json` and `.claude/mcp.json` config blocks verbatim
- Issue fix: stdio only (not SSE) — matches how Bob IDE and Claude Code connect to local MCP servers

---

## Sub-Task 7: Benchmark Suite & Automated Tests

**Status**: `[ ] pending`

### Intent
Create the 20-diff benchmark corpus with expected outputs and an automated `pytest` runner that produces measurable pass/fail evidence. This is required to demonstrate correctness to judges and proves the Actor-Critic loop works end-to-end.

### Expected Outcomes
- `src/kevgate/benchmarks/` directory with 10 true-positive diffs and 10 true-negative diffs
- Each diff has a companion `expected.json` matching the `DecisionPayload` schema
- `pytest benchmarks/` runs all 20 cases against a live LM Studio instance OR a mock client
- A `--mock` flag allows running benchmarks without LM Studio for CI
- Summary table printed at end: recall on positives, false positive rate on negatives

### Todo List
1. Create `src/kevgate/benchmarks/true_positives/` — 10 `.diff` files covering:
   - SQL injection via string interpolation
   - Hardcoded AWS key in Python config
   - Public API endpoint added without auth middleware
   - `eval()` of user input
   - Schema migration dropping a non-null column
   - `os.system()` with unsanitized input
   - Exposed admin route without role check
   - Dependency bump to a known CVE version (synthetic)
   - Pickle deserialization of untrusted data
   - Unprotected S3 bucket policy in Terraform
2. Create `src/kevgate/benchmarks/false_positives/` — 10 `.diff` files covering:
   - Docstring formatting fix
   - Import order sort (isort)
   - New internal utility function (no public API)
   - Fixture data file adding mock records
   - README update
   - Type annotation addition only
   - Adding a unit test
   - Lock file update (should be filtered by pre-filter)
   - Renaming a private variable
   - Adding logging statements
3. Write `expected.json` for each diff: minimum fields `category`, `risk_score >= 70` for true-positives, `risk_score < 30` for false-positives.
4. Implement `benchmarks/run_benchmarks.py` — parametrized `pytest` using `@pytest.mark.parametrize` over all 20 diffs. Uses `--mock` flag to inject a `MockLMStudioClient` that returns expected payloads (tests schema/pipeline, not model quality).
5. Run `pytest benchmarks/ --mock` — 20/20 pass.
6. Document live-run instructions (requires LM Studio running with Kev-4B loaded).

### Relevant Context
- Architecture §9: `benchmarks/true_positives/` and `benchmarks/false_positives/` directories
- Issue fix: manual verification → `pytest` with parametrize
- Mock client allows CI and Bob IDE task runs without requiring GPU hardware

---

## Sub-Task 8: Bob Sessions Evidence & Submission Readiness

**Status**: `[ ] pending`

### Intent
Ensure all mandatory hackathon deliverables are complete: `bob_sessions/` screenshots captured for each milestone, README updated with setup instructions, and submission checklist verified.

### Expected Outcomes
- At least 4 Bob IDE task session screenshots in `bob_sessions/` (one per major milestone)
- `README.md` updated with installation steps, quickstart demo, and architecture diagram link
- `ARCHITECTURE.md` updated to remove the "non-autoregressive" misstatement and reflect the actual implemented system
- All items in `HACKATHON_GUIDE.md` §8 submission checklist verified

### Todo List
1. Use IBM Bob IDE Agent mode to execute each of the 4 prior milestones (scaffold, diff engine, MCP server, benchmarks). Capture session summary screenshots per `HACKATHON_GUIDE.md` §7 naming convention.
2. Save screenshots as:
   - `bob_sessions/kevgate_task01_scaffold_schema_summary.png`
   - `bob_sessions/kevgate_task02_diff_engine_summary.png`
   - `bob_sessions/kevgate_task03_mcp_server_summary.png`
   - `bob_sessions/kevgate_task04_benchmarks_summary.png`
3. Update `README.md`:
   - Add `## Installation` section: `pip install -e .` + LM Studio setup instructions.
   - Add `## Quickstart` section: `kevgate hook install` → make a commit → see gate output.
   - Add `## MCP Integration` section: link to `mcp.json` and `.claude/mcp.json`.
4. Update `ARCHITECTURE.md` §2: replace "Non-autoregressive single-forward-pass" with accurate description: "Single completion call with `max_tokens: 80` and JSON grammar constraint, completing in 30–60ms".
5. Verify `HACKATHON_GUIDE.md` §8 submission checklist — check each item.

### Relevant Context
- `HACKATHON_GUIDE.md` §7 defines exact screenshot naming format and capture steps
- `HACKATHON_GUIDE.md` §8 is the complete submission checklist
- Bob IDE task session summaries are the judge's primary evidence of Bob usage

---

## Dependency Graph

```
Sub-Task 1 (Scaffold)
    └── Sub-Task 2 (Entropy Scanner + Diff Parser)
    └── Sub-Task 3 (LM Studio Adapter)  [depends on Sub-Task 1]
            └── Sub-Task 4 (Policy Engine)  [depends on Sub-Tasks 2 + 3]
                    └── Sub-Task 5 (CLI + Hook)  [depends on Sub-Task 4]
                    └── Sub-Task 6 (MCP Server)  [depends on Sub-Task 4]
                            └── Sub-Task 7 (Benchmarks)  [depends on Sub-Tasks 5 + 6]
                                    └── Sub-Task 8 (Bob Sessions + Submission)
```

Sub-Tasks 2 and 3 can be worked in parallel after Sub-Task 1 is complete.  
Sub-Tasks 5 and 6 can be worked in parallel after Sub-Task 4 is complete.
