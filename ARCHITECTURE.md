# KevGate: Universal System-1 Decision Layer & Pre-Commit Gate for Agentic Coding Harnesses

> **Document Type**: Architecture & Technical Specification  
> **Target Audience**: Core Team, Peer Engineers, and Autonomous AI Agents (IBM Bob, Claude Code, Agrav, Kiro, Codex, DeepSeek Harness)  
> **Repository**: [WilliamAxelC/IBM-hackathon](https://github.com/WilliamAxelC/IBM-hackathon)  
> **Status**: Approved Design / Active Development

---

## 1. Executive Summary & Vision

Modern AI coding agents (such as **IBM Bob**, **Claude Code**, **Agrav / Antigravity**, **Kiro**, **Codex**, and **DeepSeek Harness**) excel at deep, multi-file code synthesis and refactoring (**System-2 Deliberative Reasoning**). However, deploying these generative models directly on every routine developer event (like a `git commit` hook or PR triage) creates two fatal operational bottlenecks:

1. **Flow-State Latency**: Autoregressive LLM generation takes 5–30 seconds per evaluation, causing developers to immediately disable git hooks with `--no-verify`.
2. **Token & Quota Burn**: 80–90% of commits are routine clean changes (formatting, docs, isolated internal edits). Running heavy LLMs on every micro-commit rapidly exhausts token allowances and hackathon quotas (such as IBM Bob's 40 Bobcoins limit).

**KevGate** introduces a **Universal System-1 Decision Layer** positioned immediately in front of the agentic harnesses. Powered by a local non-autoregressive decision model (**Kev-4B** served via LM Studio / llama.cpp), KevGate evaluates unified git diffs in **~30–60ms** using candidate logit readout and schema-constrained decoding.

- **Clean Commits (<30 Risk Score)**: Instantly greenlit (<80ms, 0 tokens / 0 Bobcoins burned).
- **High-Risk Regressions / Security Vulnerabilities (≥70 Risk Score)**: Hard-blocked at the gate and packaged into a structured **Remediation Intent Protocol (RIP)**.
- **Universal Protocol**: Exposed as a standard **Model Context Protocol (MCP) server**, allowing **any** agentic harness (Bob, Claude Code, Agrav, Kiro, Codex, DeepSeek) to consume KevGate for both pre-commit gating and self-verifying **Actor-Critic loops**.

---

## 2. Dual-Process Architecture: System 1 vs. System 2

```
                       [ Developer: git commit / PR Diff ]
                                       │
                                       ▼
             ┌───────────────────────────────────────────────────┐
             │            KevGate Git Interceptor                │
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
             │    System 1: Local Decision Engine (Kev-4B)       │
             │    • Served via LM Studio (localhost:1234)        │
             │    • Single completion with max_tokens: 80        │
             │    • Grammar-constrained JSON schema decoding     │
             │    • Latency: ~30-60ms on local GPU / CPU         │
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
                 • Latency: <80ms         • Structured Remediation Intent
                 • 0 Tokens burned        • Dispatched via Universal MCP
                                                   │
                                                   ▼
            ┌─────────────────────────────────────────────────────────────┐
            │        Universal MCP Interface (`kevgate-mcp`)              │
            │   JSON-RPC standard compatible across all agent harnesses   │
            └──────────────┬───────────────────────────────┬──────────────┘
                           │                               │
              ┌────────────┼────────────┐     ┌────────────┼────────────┐
              ▼            ▼            ▼     ▼            ▼            ▼
          [IBM Bob]  [Claude Code]   [Agrav] [Kiro]     [Codex]   [DeepSeek]
```

---

## 3. Universal MCP Interface Specification

KevGate exposes standard tools through the **Model Context Protocol (MCP)** specification over `stdio` and `sse`. Any agent harness supporting MCP can register KevGate in its configuration.

### Exposed MCP Tools

#### Tool 1: `kevgate_triage_diff`
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

#### Tool 2: `kevgate_inspect_file`
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

#### Tool 3: `kevgate_verify_remediation` (Actor-Critic Loop)
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

## 4. Cross-Harness Interoperability Matrix

KevGate is intentionally **harness-agnostic**. The core gate and decision logic run independently of the consuming agent.

| Agentic Harness | Connection Mechanism | Primary Workflow Role |
| :--- | :--- | :--- |
| **IBM Bob IDE** | Native MCP via `mcp.json` + Task Payload | Runs Agent Mode refactoring; captures task consumption summaries for `bob_sessions/` deliverable. |
| **Claude Code** | Native MCP via `.claude/mcp.json` or CLI tool | Interactive terminal agent invoking `kevgate_verify_remediation` during file edits. |
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
    "kevgate": {
      "command": "python",
      "args": ["-m", "kevgate.mcp_server"],
      "env": {
        "LMSTUDIO_BASE_URL": "http://localhost:1234/v1"
      }
    }
  }
}
```

#### 2. Claude Code (`.claude/mcp.json`)
```json
{
  "mcpServers": {
    "kevgate": {
      "command": "kevgate-mcp",
      "args": []
    }
  }
}
```

---

## 5. Universal State & Decision Schema

To maintain complete polyglot support (Python, Go, Rust, TypeScript, Terraform, Docker, YAML), KevGate does **not** rely on language-specific AST parsers. It evaluates the universal **Unified Diff** format.

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

## 6. The Actor-Critic Verification Loop

A major vulnerability of generative AI coding assistants is **hallucinated or incomplete patches**. KevGate solves this by acting as an impartial **Critic**:

```sequence
Developer->>Git: git commit
Git->>KevGate: Execute pre-commit hook (git diff --cached)
KevGate->>LM Studio: Single forward pass on diff
LM Studio-->>KevGate: Score: 92 (SQL Injection in auth.py)
KevGate-->>Git: Exit 1 (Commit Blocked)
KevGate->>Agent Harness: Dispatch Remediation Intent Payload
Agent Harness->>Agent Harness: Generate patch (parameterized query)
Agent Harness->>KevGate: Tool Call: kevgate_verify_remediation(original, patch)
KevGate->>LM Studio: Re-evaluate patch delta
LM Studio-->>KevGate: Score: 4 (Clean, vulnerability eliminated)
KevGate-->>Agent Harness: Verification: PASS (Delta -88)
Agent Harness->>Git: git commit (Patch Approved & Logged)
```

---

## 7. LM Studio & Hardware Runtime Configuration

### Target Hardware: AMD Radeon RX 6600 XT (8 GB VRAM)
- **Model Checkpoint**: `Kev-4B` (GGUF format, `Q4_K_M` or `Q8_0`).
- **Memory Footprint**:
  - `Q4_K_M`: **~2.5 GB VRAM** (leaves >5 GB free for system, IDE, browser).
  - `Q8_0`: **~4.2 GB VRAM** (maximum precision within 8 GB envelope).
- **Inference Acceleration**:
  - LM Studio automatically enables hardware acceleration via **Vulkan** or **ROCm** on RDNA 2 GPUs.
  - Short generation loop: `max_tokens: 80` with grammar-constrained JSON schema decoding means generation terminates after the decision payload is emitted, completing in **30ms–60ms**.

### LM Studio Server Settings
- **Port**: `1234` (`http://localhost:1234/v1`)
- **Sampling Parameters**:
  - `temperature`: `0.0` (deterministic)
  - `max_tokens`: `80`
  - `response_format`: `{"type": "json_object"}`

---

## 8. Hackathon Eligibility Alignment (IBM Bob 2.0)

While KevGate is architected to be completely universal, it directly fulfills the **IBM Bob 2.0 Hackathon criteria**:

1. **Showcases IBM Bob IDE as a Core Component**:
   When KevGate blocks a commit, it generates a native IBM Bob task specification (`.bob/tasks/pending_remediation.json`). Bob IDE's Agent mode consumes the task, executes the multi-file refactoring, and logs the session.
2. **Solves the 40 Bobcoins Constraint**:
   By using KevGate's local System-1 model to filter out the 85% of clean commits, **Bobcoins are conserved 100% for high-value, complex code generation tasks in Bob IDE**.
3. **Generates Required `bob_sessions/` Deliverable**:
   Every time Bob IDE performs a remediation triggered by KevGate, the session summary screenshot is saved to [`bob_sessions/`](bob_sessions/README.md) as official evidence for judging.

---

## 9. Implementation Roadmap & File Layout

```
IBM-hackathon/
├── ARCHITECTURE.md                  # This document
├── README.md                        # Project landing & quickstart
├── bob_sessions/                    # Mandatory hackathon deliverable folder
│   └── README.md
├── docs/                            # Guides and rules
│   ├── HACKATHON_GUIDE.md
│   └── KICKOFF_ANNOUNCEMENT.md
└── src/
    └── kevgate/
        ├── __init__.py
        ├── cli.py                   # Terminal CLI (`kevgate check`, `kevgate hook install`)
        ├── diff_parser.py           # Git diff extraction & chunking
        ├── entropy_scanner.py       # 1ms Shannon entropy & regex secret filter
        ├── lmstudio_client.py       # HTTP client connecting to local Kev-4B in LM Studio
        ├── schema.py                # Pydantic decision models & Jev primitives
        ├── policy_engine.py         # Asymmetric risk thresholding & gating decisions
        ├── mcp_server.py            # Universal MCP Server (stdio & SSE)
        ├── hook_manager.py          # Git pre-commit installer and configuration
        └── benchmarks/              # 20 real-world curated test diffs for verification
            ├── true_positives/      # SQLi, exposed secrets, breaking schema
            └── false_positives/     # Tricky safe diffs, mock fixtures, formatting
```

### 48-Hour Execution Milestones

- [ ] **Milestone 1: Core Engine & LM Studio Adapter**
  - Implement `entropy_scanner.py`, `diff_parser.py`, and `lmstudio_client.py`.
  - Validate schema-constrained JSON output against local Kev-4B in LM Studio.
- [ ] **Milestone 2: CLI & Git Pre-Commit Hook**
  - Implement `cli.py` and `hook_manager.py`.
  - Verify instant pass (<80ms) on clean commits and blocking on risky diffs.
- [ ] **Milestone 3: Universal MCP Server**
  - Implement `mcp_server.py` exposing `kevgate_triage_diff` and `kevgate_verify_remediation`.
  - Connect and test with **IBM Bob IDE** (`mcp.json`) and **Claude Code** (`.claude/mcp.json`).
- [ ] **Milestone 4: Actor-Critic Verification & Benchmark Suite**
  - Run the 20-diff benchmark suite proving 0% false positives on safe code and 100% recall on critical flaws.
  - Record task session summary screenshots for `bob_sessions/`.
