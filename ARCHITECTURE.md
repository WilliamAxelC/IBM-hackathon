# S1Gate: Universal System-1 Decision Layer & Pre-Commit Gate for Agentic Coding Harnesses

> **Document Type**: Architecture & Technical Specification  
> **Target Audience**: Core Team, Peer Engineers, and Autonomous AI Agents (IBM Bob, Claude Code, Agrav, Kiro, Codex, DeepSeek Harness)  
> **Repository**: [WilliamAxelC/IBM-hackathon](https://github.com/WilliamAxelC/IBM-hackathon)  
> **Status**: Approved Design / Active Development

---

## 1. Executive Summary & Vision

Modern AI coding agents (such as **IBM Bob**, **Claude Code**, **Agrav / Antigravity**, **Kiro**, **Codex**, and **DeepSeek Harness**) excel at deep, multi-file code synthesis and refactoring (**System-2 Deliberative Reasoning**). However, deploying these generative models directly on every routine developer event (like a `git commit` hook or PR triage) creates two fatal operational bottlenecks:

1. **Flow-State Latency**: Autoregressive LLM generation takes 5–30 seconds per evaluation, causing developers to immediately disable git hooks with `--no-verify`.
2. **Token & Quota Burn**: 80–90% of commits are routine clean changes (formatting, docs, isolated internal edits). Running heavy LLMs on every micro-commit rapidly exhausts token allowances and hackathon quotas (such as IBM Bob's strict 40 Bobcoins limit).

**S1Gate** introduces a **Universal System-1 Decision Layer** positioned immediately in front of the agentic harnesses. 

### Dual-Backend Strategy (MVP & Offline)
* **Cloud MVP (Default)**: Powered by **Google Gemini 2.0 Flash Lite** (via free-tier API key in `.env`). Delivers sub-150ms triage, native strict JSON Schema decoding (`response_schema`), and zero local hardware setup requirements.
* **Local Offline GPU**: Connects to **LM Studio** (`http://localhost:1234/v1`) running on local consumer GPUs (such as an AMD Radeon RX 6600 XT with Qwen2.5-Coder-3B or Kev-4B) for 100% air-gapped, zero-network environments.

### The Decision Funnel
- **Clean Commits (<30 Risk Score)**: Instantly greenlit (<150ms, 0 tokens / 0 Bobcoins burned).
- **High-Risk Regressions / Security Vulnerabilities (≥70 Risk Score)**: Hard-blocked at the gate and packaged into a structured **Remediation Intent Protocol (RIP)**.
- **Universal Protocol**: Exposed as a standard **Model Context Protocol (MCP) server**, allowing **any** agentic harness (Bob, Claude Code, Agrav, Kiro, Codex, DeepSeek) to consume S1Gate for both pre-commit gating and self-verifying **Actor-Critic loops**.

---

## 2. Dual-Process Architecture: System 1 vs. System 2

```
                       [ Developer: git commit / PR Diff ]
                                       │
                                       ▼
             ┌───────────────────────────────────────────────────┐
             │             S1Gate Git Interceptor                │
             │       (.git/hooks/pre-commit or CLI tool)         │
             └─────────────────────────┬─────────────────────────┘
                                       │  Raw Unified Diff
                                       ▼
             ┌───────────────────────────────────────────────────┐
             │       Fast Universal Pre-Filter (<2ms)            │
             │       • Excludes lockfiles & build artifacts      │
             │       • Language-agnostic Shannon Entropy Scanner │
             │         (Instantly flags leaked secrets & keys)   │
             └─────────────────────────┬─────────────────────────┘
                                       │
                                       ▼
             ┌───────────────────────────────────────────────────┐
             │            System 1: Decision Engine              │
             │  • Backend A (Default MVP): Gemini 2.0 Flash Lite │
             │    (Free API via .env, sub-150ms, strict JSON)    │
             │  • Backend B (Offline GPU): LM Studio             │
             │    (localhost:1234, Qwen2.5-Coder / Kev-4B)       │
             └─────────────────────────┬─────────────────────────┘
                                       │
                                       ▼
             ┌───────────────────────────────────────────────────┐
             │    Typed Decision Output (Jev/Kev Primitives)     │
             │    • Choice: category triage                      │
             │    • Score:  0-100 risk score                     │
             │    • Nouls:  boolean semantic invariant flags     │
             └─────────────────────────┬─────────────────────────┘
                                       │
                           Risk Score >= 70 OR trigger_agent?
                                      / \
                             NO      /   \      YES
                            ────────       ────────
                           │                       │
                           ▼                       ▼
                 [ Fast Pass Path ]       [ Block & Dispatch Path ]
                 • Exit code: 0           • Exit code: 1 (Commit aborted)
                 • Latency: <150ms        • Structured Remediation Intent
                 • 0 Bobcoins burned      • Dispatched via Universal MCP
                                                   │
                                                   ▼
            ┌─────────────────────────────────────────────────────────────┐
            │        Universal MCP Interface (`s1gate-mcp`)               │
            │   JSON-RPC standard compatible across all agent harnesses   │
            └──────────────┬───────────────────────────────┬──────────────┘
                           │                               │
              ┌────────────┼────────────┐     ┌────────────┼────────────┐
              ▼            ▼            ▼     ▼            ▼            ▼
          [IBM Bob]  [Claude Code]   [Agrav] [Kiro]     [Codex]   [DeepSeek]
```

---

## 3. Environment & Security Configuration (`.env`)

For the MVP, S1Gate authenticates against Google AI Studio using an API key loaded from `.env`:

```env
# .env (NEVER COMMITTED)
S1GATE_BACKEND=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Local LM Studio fallback (Optional)
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=qwen2.5-coder-3b-instruct
```

> [!CAUTION]
> **Zero-Leakage Security Policy**:
> 1. `.env` and `*.env` are explicitly registered in [`.gitignore`](.gitignore).
> 2. The repo provides a sanitized template at [`.env.example`](.env.example).
> 3. S1Gate's pre-commit hook automatically scans for uncommitted `.env` files and hard-blocks any commit that attempts to stage environment secrets.

---

## 4. Universal MCP Interface Specification

S1Gate exposes standard tools through the **Model Context Protocol (MCP)** specification over `stdio` and `sse`. Any agent harness supporting MCP can register S1Gate in its configuration.

### Exposed MCP Tools

#### Tool 1: `s1gate_triage_diff`
Evaluates a unified git diff against the decision model and returns the full typed decision payload.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "diff": { "type": "string", "description": "Unified git diff text" },
      "context": { "type": "string", "description": "Optional commit message or PR description" }
    },
    "required": ["diff"]
  }
  ```
- **Response**: Full `DecisionPayload` JSON.

#### Tool 2: `s1gate_inspect_file`
Evaluates a specific file's uncommitted or staged changes against universal semantic invariants.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "file_path": { "type": "string", "description": "Path to file relative to repo root" }
    },
    "required": ["file_path"]
  }
  ```

#### Tool 3: `s1gate_verify_remediation` (Actor-Critic Loop)
Takes the original problematic diff and the agent's proposed remediation patch, executing a delta evaluation to verify whether the vulnerability or contract break was resolved.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "original_diff": { "type": "string", "description": "The diff that failed triage" },
      "remediation_patch": { "type": "string", "description": "The patch generated by the agent" }
    },
    "required": ["original_diff", "remediation_patch"]
  }
  ```
- **Response**:
  ```json
  {
    "verified": true,
    "previous_score": 88,
    "new_score": 6,
    "delta": -82,
    "message": "Vulnerability successfully eliminated. Patch safe to commit."
  }
  ```

---

## 5. Cross-Harness Interoperability Matrix

S1Gate is intentionally **harness-agnostic**. The core gate and decision logic run independently of the consuming agent.

| Agentic Harness | Connection Mechanism | Primary Workflow Role |
| :--- | :--- | :--- |
| **IBM Bob IDE** | Native MCP via `mcp.json` + Task Payload | Runs Agent Mode refactoring; captures task consumption summaries for `bob_sessions/` deliverable. |
| **Claude Code** | Native MCP via `.claude/mcp.json` or CLI tool | Interactive terminal agent invoking `s1gate_verify_remediation` during file edits. |
| **Agrav (Antigravity)** | Eager/Lazy MCP server in CLI settings | Pre-execution guardrail and automated remediation agent. |
| **Kiro** | MCP Server integration / Tool dispatch | Autonomous loop gating and tool call validation. |
| **Codex / OpenHands** | MCP stdio container connector | Headless CI gating and automated PR fix dispatch. |
| **DeepSeek Harness** | REST API bridge / Local MCP client | Cost-effective System-2 code generation following System-1 triage. |
| **Git Pre-Commit** | Standalone Python / Rust executable | Non-IDE developers running terminal git commands. |

### Harness Configuration Examples

#### 1. IBM Bob IDE (`mcp.json`)
```json
{
  "mcpServers": {
    "s1gate": {
      "command": "python",
      "args": ["-m", "kevgate.mcp_server"],
      "env": {
        "S1GATE_BACKEND": "gemini"
      }
    }
  }
}
```

#### 2. Claude Code (`.claude/mcp.json`)
```json
{
  "mcpServers": {
    "s1gate": {
      "command": "s1gate-mcp",
      "args": []
    }
  }
}
```

---

## 6. Universal State & Decision Schema

To maintain complete polyglot support (Python, Go, Rust, TypeScript, Terraform, Docker, YAML), S1Gate does **not** rely on language-specific AST parsers. It evaluates the universal **Unified Diff** format.

### Typed Output Primitives (Pydantic Specification)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class DecisionPayload(BaseModel):
    # Choice Primitive (Categorical Action)
    category: Literal[
        "safe_refactor",       # Formatting, comments, isolated non-breaking rename
        "benign_feature",      # New functionality preserving existing contracts
        "contract_break",      # Modified/deleted public API, schema, or endpoint
        "security_risk",       # Taint sink, unvalidated input, permission bypass
        "dependency_shift"     # Lockfile or package manifest mutation
    ]
    
    # Score Primitive (0 - 100 Risk Rating)
    risk_score: int = Field(ge=0, le=100, description="Calibrated risk and blast radius score")
    confidence: float = Field(ge=0.0, le=1.0, description="Mathematical confidence probability")
    
    # Noul Primitives (Strict Boolean Invariants)
    is_breaking_change: bool = Field(description="Alters external API or data contract")
    exposes_unprotected_resource: bool = Field(description="Bypasses auth or injects untrusted data")
    unhandled_failure_mode: bool = Field(description="Introduces I/O side-effect without error handling")
    
    # Remediation Intent Protocol (RIP)
    summary: str = Field(description="One-sentence description of finding")
    target_file: Optional[str] = None
    target_lines: Optional[str] = None
    remediation_hint: Optional[str] = None
    trigger_agent: bool = Field(description="Definitive decision to invoke System-2 Agent")
```

---

## 7. The Actor-Critic Verification Loop

A major vulnerability of generative AI coding assistants is **hallucinated or incomplete patches**. S1Gate solves this by acting as an impartial **Critic**:

```sequence
Developer->>Git: git commit
Git->>S1Gate: Execute pre-commit hook (git diff --cached)
S1Gate->>Decision Engine: Single forward pass on diff
Decision Engine-->>S1Gate: Score: 92 (SQL Injection in auth.py)
S1Gate-->>Git: Exit 1 (Commit Blocked)
S1Gate->>Agent Harness: Dispatch Remediation Intent Payload
Agent Harness->>Agent Harness: Generate patch (parameterized query)
Agent Harness->>S1Gate: Tool Call: s1gate_verify_remediation(original, patch)
S1Gate->>Decision Engine: Re-evaluate patch delta
Decision Engine-->>S1Gate: Score: 4 (Clean, vulnerability eliminated)
S1Gate-->>Agent Harness: Verification: PASS (Delta -88)
Agent Harness->>Git: git commit (Patch Approved & Logged)
```

---

## 8. Backends: Cloud API & Local Hardware

### Backend A: Gemini 2.0 Flash Lite (MVP Default)
- **Model**: `gemini-2.0-flash-lite`
- **Latency**: ~100–150ms
- **Cost**: $0.00 (Google AI Studio Free Tier: 1,500 requests/day, 15 RPM)
- **Decoding**: Strict JSON Schema constrained decoding (`response_mime_type="application/json"`)
- **Key Storage**: `.env` (gitignored)

### Backend B: LM Studio (Local GPU / Air-Gapped)
- **Target Hardware**: AMD Radeon RX 6600 XT (8 GB VRAM) / NVIDIA RTX
- **Model**: `Qwen2.5-Coder-3B-Instruct` or `Kev-4B` (GGUF format, `Q8_0` or `Q6_K`)
- **Server**: `http://localhost:1234/v1`
- **Sampling**: `temperature=0.0`, `max_tokens=80`, `response_format={"type": "json_object"}`

---

## 9. Hackathon Eligibility Alignment (IBM Bob 2.0)

While S1Gate is architected to be completely universal, it directly fulfills the **IBM Bob 2.0 Hackathon criteria**:

1. **Showcases IBM Bob IDE as a Core Component**:
   When S1Gate blocks a commit, it generates a native IBM Bob task specification (`.bob/tasks/pending_remediation.json`). Bob IDE's Agent mode consumes the task, executes the multi-file refactoring, and logs the session.
2. **Solves the 40 Bobcoins Constraint**:
   By using S1Gate's free System-1 discriminator to filter out the 85% of clean commits, **Bobcoins are conserved 100% for high-value, complex code generation tasks in Bob IDE**.
3. **Generates Required `bob_sessions/` Deliverable**:
   Every time Bob IDE performs a remediation triggered by S1Gate, the session summary screenshot is saved to [`bob_sessions/`](bob_sessions/README.md) as official evidence for judging.

---

## 10. Implementation Roadmap & File Layout

```
IBM-hackathon/
├── ARCHITECTURE.md                  # This document
├── README.md                        # Project landing & quickstart
├── HACKATHON_GUIDE.md               # Hackathon rules, deadlines, judging criteria
├── .env.example                     # Environment template (API keys)
├── .gitignore                       # Ensures .env is never committed
├── bob_sessions/                    # Mandatory hackathon deliverable folder
│   └── README.md
├── docs/                            # Guides and rules
│   ├── HACKATHON_GUIDE.md
│   └── KICKOFF_ANNOUNCEMENT.md
└── src/
    └── kevgate/                     # Core engine (S1Gate)
        ├── __init__.py
        ├── cli.py                   # Terminal CLI (`s1gate check`, `s1gate hook install`)
        ├── diff_parser.py           # Git diff extraction & chunking
        ├── entropy_scanner.py       # 1ms Shannon entropy & regex secret filter
        ├── lmstudio_client.py       # HTTP client connecting to local LM Studio / Gemini API
        ├── schema.py                # Pydantic decision models & Jev primitives
        ├── policy_engine.py         # Asymmetric risk thresholding & gating decisions
        ├── mcp_server.py            # Universal MCP Server (stdio & SSE)
        ├── hook_manager.py          # Git pre-commit installer and configuration
        └── benchmarks/              # 20 real-world curated test diffs for verification
            ├── true_positives/      # SQLi, exposed secrets, breaking schema
            └── false_positives/     # Tricky safe diffs, mock fixtures, formatting
```

---

## 9. Team & Branch Contributions

| Branch | Author | Work Covered |
| :--- | :--- | :--- |
| `main` | WilliamAxelC | Initial scaffold: KevGate concept, LM Studio client, entropy scanner, diff parser, policy engine, MCP server (stdio), CLI, git hook manager, ARCHITECTURE.md |
| `william-dev` | WilliamAxelC | S1Gate rebrand, Gemini dual-backend, SSE remote MCP server, Docker deployment, benchmark harness (40 diffs), error matrix, Bob IDE session evidence |
| `raja-dev` | Raja | README installation polish (`uv sync`), team section, demo video script ([`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)), submission checklist completion, ARCHITECTURE contribution log |

### How to Reproduce the Full Environment

```bash
# Clone & switch to raja-dev (includes all william-dev work)
git clone https://github.com/WilliamAxelC/IBM-hackathon.git
cd IBM-hackathon
git checkout raja-dev

# One-command install (Python + all deps locked via uv.lock)
uv sync

# Verify all 64 tests pass
uv run pytest tests/ -v

# Run S1Gate on a risky diff
uv run s1gate check --diff src/kevgate/benchmarks/true_positives/01_sql_injection.diff
```
