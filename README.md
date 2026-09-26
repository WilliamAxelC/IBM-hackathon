# KevGate — Universal System-1 Decision Layer for Agentic Coding Harnesses

> **Event**: IBM Bob 2.0 Hackathon (Hosted on lablab.ai)  
> **Repository**: [WilliamAxelC/IBM-hackathon](https://github.com/WilliamAxelC/IBM-hackathon)  
> **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) | **Bob Sessions**: [bob_sessions/](bob_sessions/)

---

## What is KevGate?

Modern AI coding agents (IBM Bob, Claude Code, Agrav, Kiro, Codex) excel at deep multi-file code synthesis but create two bottlenecks when used on every `git commit`:

1. **Latency**: LLM generation takes 5–30s per evaluation — developers disable hooks with `--no-verify`.
2. **Token burn**: 80–90% of commits are safe formatting or doc changes. Running heavy models on every micro-commit exhausts quotas (IBM Bob's 40 Bobcoins limit).

**KevGate** inserts a fast local decision layer in front of those agents. A small model (Kev-4B served via LM Studio) evaluates the unified diff in **~30–60ms** and returns a structured risk classification:

- **PASS** (score < 30): Instantly greenlit. Zero tokens burned.
- **WARN** (score 30–69): Advisory printed. Commit allowed.
- **BLOCK** (score ≥ 70): Commit aborted. A structured [Remediation Intent Protocol](#actor-critic-loop) is dispatched to IBM Bob IDE as a task file.

---

## Architecture

```
git commit → KevGate pre-filter → Kev-4B (LM Studio) → Policy Engine
                                                              │
                                              ┌───────────────┴───────────────┐
                                           PASS/WARN                        BLOCK
                                           exit 0                           exit 1 + Bob task
                                                                                │
                                                              Universal MCP → IBM Bob / Claude Code / Kiro
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full technical specification.

---

## Installation

**Requirements**: Python 3.11+, [LM Studio](https://lmstudio.ai/) with a model loaded on `localhost:1234`

```bash
# Clone the repo
git clone https://github.com/WilliamAxelC/IBM-hackathon.git
cd IBM-hackathon

# Create virtual environment and install
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### LM Studio Setup

1. Download and install [LM Studio](https://lmstudio.ai/).
2. Load any instruction-following model (e.g. Kev-4B, Qwen2.5-Coder, Phi-4-mini).
3. Start the local server on port `1234` (default).
4. Set the model name in `.kevgate.toml`:
   ```toml
   lmstudio_model = "your-model-name-as-shown-in-lmstudio"
   ```

---

## Quickstart

### 1. Manual diff check

```bash
# Check the current staged diff
kevgate check

# Check a diff file directly (no git repo needed)
kevgate check --diff src/kevgate/benchmarks/true_positives/01_sql_injection.diff
```

### 2. Install the git pre-commit hook

```bash
kevgate hook install
# → Installs .git/hooks/pre-commit
# Every subsequent git commit will run through KevGate automatically.

kevgate hook uninstall
# → Removes the hook
```

### 3. View resolved configuration

```bash
kevgate config
```

---

## MCP Integration (IBM Bob IDE / Claude Code)

KevGate exposes three tools via the [Model Context Protocol](https://modelcontextprotocol.io/):

| Tool | Purpose |
|---|---|
| `kevgate_triage_diff` | Evaluate a unified diff, get risk classification |
| `kevgate_inspect_file` | Evaluate staged changes in a specific file |
| `kevgate_verify_remediation` | Actor-Critic: verify an agent's fix patch |

### IBM Bob IDE (`mcp.json`)

The [`mcp.json`](mcp.json) at the repo root is pre-configured. In Bob IDE:

1. Open **Settings → MCP Servers**.
2. Click **Add from file** and select `mcp.json`.
3. KevGate tools appear in Bob's tool list immediately.

### Claude Code (`.claude/mcp.json`)

The [`.claude/mcp.json`](.claude/mcp.json) is pre-configured for Claude Code.

---

## Actor-Critic Loop

When a commit is blocked, KevGate writes `.bob/tasks/pending_remediation.json`. Bob IDE's Agent mode picks this up and:

1. Reads the `remediation_hint` from the task file.
2. Generates a fix patch.
3. Calls `kevgate_verify_remediation(original_diff, patch)` to verify the fix resolved the risk.
4. Commits the verified patch.

```
Blocked commit → Bob reads .bob/tasks/pending_remediation.json
                → Bob generates fix
                → kevgate_verify_remediation(original, fix) → score: 92 → 4
                → Verified: PASS → git commit
```

---

## Running Tests

```bash
# Unit tests (no LM Studio required)
pytest tests/ -v

# Benchmark suite — mock mode (no LM Studio required)
pytest src/kevgate/benchmarks/ --mock -v

# Benchmark suite — live mode (requires LM Studio running)
pytest src/kevgate/benchmarks/ -v
```

---

## Project Structure

```
IBM-hackathon/
├── ARCHITECTURE.md                     # Full technical specification
├── HACKATHON_GUIDE.md                  # Hackathon rules, deadlines, judging criteria
├── mcp.json                            # IBM Bob IDE MCP registration
├── .claude/mcp.json                    # Claude Code MCP registration
├── .kevgate.toml                       # Configuration file (edit model name here)
├── pyproject.toml                      # Python package definition
├── bob_sessions/                       # [REQUIRED] Bob IDE task session screenshots
└── src/kevgate/
    ├── schema.py                       # DecisionPayload + RemediationVerification types
    ├── config.py                       # KevGateConfig (pydantic-settings, .kevgate.toml)
    ├── exceptions.py                   # Typed exception hierarchy
    ├── entropy_scanner.py              # Shannon entropy + secret regex pre-filter
    ├── diff_parser.py                  # Unified diff parser, lockfile detection
    ├── lmstudio_client.py              # HTTP adapter for LM Studio API
    ├── policy_engine.py                # Risk threshold evaluation + Bob task generator
    ├── cli.py                          # kevgate CLI (check, hook install/uninstall, config)
    ├── hook_manager.py                 # Git pre-commit hook installer
    ├── mcp_server.py                   # Universal MCP server (stdio)
    └── benchmarks/
        ├── true_positives/             # 10 risky diffs (SQLi, secrets, auth bypass, ...)
        └── false_positives/            # 10 safe diffs (formatting, docs, tests, ...)
```

---

## ⚠️ Hackathon Eligibility

- IBM Bob IDE session screenshots: [`bob_sessions/`](bob_sessions/)
- Architecture document: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- No proprietary or PII data used — all benchmark diffs are synthetic.
