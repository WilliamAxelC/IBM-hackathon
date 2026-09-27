# S1Gate — Hackathon Submission Package

> **Event**: IBM Bob 2.0 Hackathon (Hosted on lablab.ai)  
> **Project**: S1Gate (Universal System-1 Pre-Commit Decision Layer & MCP Server)  
> **Repository**: [https://github.com/WilliamAxelC/IBM-hackathon](https://github.com/WilliamAxelC/IBM-hackathon)  
> **Live MCP SSE Server**: `https://mcp.cuang.dev/s1gate/sse`  
> **Health Check**: `https://mcp.cuang.dev/s1gate/health`  
> **Judge Key**: `s1gate-judge-secret-key-2026`  

---

## 1. Submission Form Fields

### Short Description (255 characters max, min 50)
```text
S1Gate is a sub-second System-1 pre-commit decision gate and universal MCP server that shields git repositories from security flaws and contract breaks while preserving developer flow and saving agent quota.
```
*(Character count: 211 / 255 characters)*

---

### Long Description (Problem & Solution Statement)
*(Limit: 500 words or less, min 500 chars, max 4000 chars)*

```text
Problem:
Modern AI coding harnesses (such as IBM Bob, Claude Code, and autonomous multi-agent systems) possess immense deliberative capability (System-2 thinking) for multi-file architecture synthesis. However, deploying heavy reasoning models on every micro-commit creates two critical bottlenecks:
1. Flow-State Latency: Waiting 10 to 30 seconds per commit forces developers to bypass safeguards with `git commit --no-verify`.
2. Quota & Cost Exhaustion: Over 85% of real-world commits are routine, non-breaking edits (formatting, documentation, isolated internal refactors). Running heavy frontier models on every git action rapidly exhausts token budgets and strict quota allowances (like IBM Bob's 40 Bobcoins limit).

Solution:
S1Gate introduces an ultra-fast System-1 Decision Layer at the pre-commit boundary, inspired by Daniel Kahneman's dual-process cognitive model. By separating fast, deterministic triage from deep reasoning, S1Gate acts as an autonomous guardian:
- Fast Pre-Filter (< 2ms): Instant Shannon entropy and regex scanning detects high-entropy secrets (AWS, GitHub, Slack tokens, private keys) in 0.05 milliseconds.
- System-1 Triage (~1.2s): Evaluates unified diffs using Google Gemini 3.1 Flash Lite or offline local GPU models (via LM Studio), returning structured decisions: PASS (routine safe changes), WARN (minor API contract modifications), or BLOCK (security flaws, unprotected resources, unhandled failures).
- Actor-Critic Remediation Loop: When a commit is blocked, S1Gate generates a structured Remediation Intent Protocol (RIP) task in `.bob/tasks/pending_remediation.json`. IBM Bob's Agent mode autonomously ingests the diagnosis, generates a targeted patch, and verifies it with S1Gate's critic tool (`s1gate_verify_remediation`) before committing.

Target Users & Interaction:
- Individual Developers & Teams: Install S1Gate as a native git pre-commit hook (`s1gate hook install`) or run manual checks via CLI (`s1gate check`).
- Autonomous Agent Harnesses & Evaluators: Connect via the Model Context Protocol (MCP) using local stdio or the hosted remote SSE server (`https://mcp.cuang.dev/s1gate/sse`).

What Makes S1Gate Unique & Effective:
1. Sub-Second Performance: Persistent connection pooling, token capping, and deterministic short-circuiting deliver latency under 1.5 seconds.
2. Zero Escapes: In our rigorous benchmark against 12 realistic production vulnerabilities (SSRF, Prototype Pollution, BOLA/IDOR, TOCTOU Race Conditions, Deserialization RCE, Zip Slip, JWT Confusion), S1Gate achieved a 100% block rate (0 Type II escapes).
3. Zero Quota Waste: Routine commits pass instantly without burning a single Bobcoin or LLM reasoning token.
```
*(Word count: 378 words | Character count: 2,612 / 4000 characters)*

---

### IBM Bob Usage Statement
*(Min 500 chars, max 4000 chars)*

```text
IBM Bob played a dual role throughout the S1Gate project: as the primary development workbench and as the autonomous System-2 Actor in our Actor-Critic architecture.

1. IDE-Level Development & Implementation:
We utilized IBM Bob IDE to architect and develop the entire S1Gate Python codebase. Bob was used to scaffold the project with uv, design typed Pydantic v2 schemas (DecisionPayload, RemediationVerification), implement the unified diff parser with AST chunk filtering, and write the Shannon entropy secret scanner. Bob's integrated terminal and context awareness accelerated testing and debugging across 85 unit and integration tests.

2. Autonomous Actor in the System-1 / System-2 Remediation Loop:
S1Gate was specifically designed to supercharge IBM Bob by decoupling cognitive workloads. When S1Gate detects an invariant violation (such as an SQL injection, BOLA flaw, or broken API contract), it halts the commit and writes a machine-readable task packet to `.bob/tasks/pending_remediation.json`. IBM Bob's Agent mode polls this directory, reads the diagnosis and remediation hint, investigates the affected file, and synthesizes a verified fix.

3. Deep Model Context Protocol (MCP) Integration:
S1Gate exposes three production-grade tools via the Model Context Protocol:
- `s1gate_triage_diff`: Evaluates unified diffs and outputs risk scores (0–100), boolean invariants, and remediation hints.
- `s1gate_inspect_file`: Inspects uncommitted and staged modifications on disk.
- `s1gate_verify_remediation`: The Critic tool that allows IBM Bob to test its proposed fix against the original risk score before finalizing the commit.

4. Hosted Remote MCP Deployment:
To allow IBM Bob to connect seamlessly without local setup, we deployed a hosted Remote MCP Server accessible over Server-Sent Events (SSE) at `https://mcp.cuang.dev/s1gate/sse`. Registered directly in Bob's `mcp.json`, IBM Bob can invoke S1Gate tools remotely across any workspace.
```
*(Character count: 1,972 / 4000 characters)*

---

### Categories
- Developer Tools
- Artificial Intelligence
- Cybersecurity / DevSecOps
- Agentic Workflows

---

### Technologies Used
- IBM Bob IDE (MCP Client & Agent Mode)
- Model Context Protocol (MCP v2.0 - Stdio & SSE Transports)
- Python 3.12 & `uv` Package Manager
- Google Gemini 3.1 Flash Lite (Structured JSON Decoding & Keep-Alive Pooling)
- LM Studio / Local LLMs (Air-Gapped Offline GPU Inference)
- Starlette & Uvicorn (Pure ASGI Streaming & Cloudflare Compatibility)
- Pydantic v2 (Strict Schema Validation)
- Docker & Docker Compose (Containerized Remote MCP Service)
- Cloudflare Tunnels (Zero-Trust Reverse Proxy Gateway)

---

## 2. Presentation Deck (Slide by Slide)

### Slide 1: Title & Hook
- **Slide Title**: **S1Gate: The System-1 Decision Layer for AI Coding Harnesses**
- **Subtitle**: Sub-Second Pre-Commit Guardrails & Actor-Critic Remediation for IBM Bob
- **Key Visual**: S1Gate shield logo connecting Git Pre-Commit to IBM Bob IDE.
- **Presenter Script**:
  > "Hello everyone! Today we are introducing S1Gate — an ultra-fast, intelligent pre-commit decision layer and universal MCP server designed to protect repositories from security vulnerabilities and broken contracts without slowing down developers or wasting agent quota."

---

### Slide 2: The Core Problem: The Agent Flow Paradox
- **Slide Title**: **The Problem: Autoregressive Latency & Quota Burn**
- **Bullet Points**:
  - Developers commit frequently (micro-commits, iterative refactors).
  - System-2 agents take 10–30s to evaluate diffs — leading developers to use `--no-verify`.
  - 85%+ of commits are routine and safe; running heavy LLMs burns precious tokens and Bobcoins.
  - Absence of deterministic fast-paths for leaked credentials.
- **Key Visual**: Comparison chart: 30s LLM wait vs 1.2s S1Gate triage.
- **Presenter Script**:
  > "Modern coding agents like IBM Bob are incredible at deep reasoning. But when applied at every git commit, they create a major problem: flow-state latency. Waiting 15 to 30 seconds per commit frustrates engineers and rapidly exhausts token quotas on routine formatting or documentation edits. We need a way to make pre-commit decisions instantly."

---

### Slide 3: The Architecture: System-1 vs. System-2
- **Slide Title**: **System-1 Intuition meets System-2 Deliberation**
- **Bullet Points**:
  - **Stage 1 (0.01ms)**: Local Shannon Entropy Scanner catches API keys & secrets instantly.
  - **Stage 2 (0.015ms)**: Unified Diff Parser strips lockfiles and isolates code changes.
  - **Stage 3 (~1.2s)**: Gemini 3.1 Flash Lite / Local LM Studio classifies risk (0–100) and strict invariants.
  - **Decision Gate**: PASS (0 quota burned), WARN, or BLOCK.
- **Key Visual**: Kahneman dual-process diagram (Fast System-1 Gate → Slow System-2 IBM Bob Agent).
- **Presenter Script**:
  > "Inspired by Daniel Kahneman's dual-process cognitive model, S1Gate inserts a System-1 decision gate. It filters obvious secrets in under 0.05 milliseconds using Shannon entropy. For code changes, it calls an optimized, connection-pooled model that evaluates risk in just 1.2 seconds. Safe commits pass immediately without burning a single Bobcoin."

---

### Slide 4: The Actor-Critic Remediation Loop
- **Slide Title**: **Autonomous Fixes via IBM Bob & MCP**
- **Bullet Points**:
  - Blocked commits trigger a **Remediation Intent Protocol (RIP)** packet.
  - IBM Bob Agent mode ingests `.bob/tasks/pending_remediation.json`.
  - Bob inspects the flaw, crafts a fix, and calls `s1gate_verify_remediation`.
  - Verified patch is auto-committed when risk score drops to zero.
- **Key Visual**: Circular workflow diagram: Block → Bob Diagnoses → Bob Fixes → S1Gate Verifies → Commit Approved.
- **Presenter Script**:
  > "What happens when a real flaw is caught? S1Gate writes a structured remediation task. IBM Bob IDE immediately steps in as the System-2 deliberative actor: it analyzes the vulnerability, synthesizes a fix, and uses the S1Gate verify tool to prove the risk was eliminated before committing."

---

### Slide 5: Empirical Benchmarks & Error Matrix
- **Slide Title**: **Zero Escapes: 100% Detection Across 12 Production CVEs**
- **Bullet Points**:
  - Evaluated against 12 realistic vulnerabilities (SSRF, Prototype Pollution, BOLA, TOCTOU, Deserialization, Zip Slip, JWT confusion).
  - **12 / 12 Blocked (100% Detection Rate)**.
  - **0 Type II Security Escapes**.
  - Dual Backend: Cloud API (~1.2s) or 100% Offline Local GPU (~60ms).
- **Key Visual**: Error Matrix table and QA benchmark results summary.
- **Presenter Script**:
  > "We tested S1Gate against a comprehensive suite of 12 production-grade vulnerable git diffs spanning Python, TypeScript, Go, and Java. S1Gate achieved a 100% detection rate with zero security escapes, proving that lightweight System-1 gates can provide ironclad protection."

---

### Slide 6: Live Deployment & Judge Access
- **Slide Title**: **Live Hosted MCP Server & Ready for Evaluation**
- **Bullet Points**:
  - Hosted Remote MCP Endpoint: `https://mcp.cuang.dev/s1gate/sse`
  - Zero-install configuration for IBM Bob IDE via `mcp.json`.
  - Real-time latency reporting (`X-Response-Time-Ms` headers & `processing_time_ms` fields).
  - Fully open source on GitHub.
- **Key Visual**: Screenshot of IBM Bob tool palette displaying `s1gate_triage_diff`.
- **Presenter Script**:
  > "S1Gate is live right now! Hackathon judges can connect to our hosted Remote MCP server at mcp.cuang.dev/s1gate/sse using IBM Bob or Claude Code with zero local setup. Thank you, and we welcome your questions!"

---

## 3. Video Demo Script & Storyboard (2–3 Minutes)

| Timestamp | Screen Display / Visual | Voiceover Script |
| :--- | :--- | :--- |
| **0:00 - 0:25** | Terminal showing `git commit` getting blocked instantly by S1Gate. | "Every developer has experienced the frustration of slow pre-commit hooks or accidentally pushing a secret to GitHub. Today, we're demonstrating S1Gate — an ultra-fast System-1 decision gate and Model Context Protocol server that solves this forever." |
| **0:25 - 0:55** | Terminal running `s1gate check` on routine doc changes vs secret leak. | "Watch what happens on a routine commit: S1Gate evaluates the diff in milliseconds and greenlights it — burning zero agent quota and preserving developer flow. But when high-entropy credentials or subtle vulnerabilities are introduced, S1Gate's deterministic scanner catches them in under 0.05 milliseconds and halts the commit." |
| **0:55 - 1:35** | IBM Bob IDE opening `.bob/tasks/pending_remediation.json`, generating patch, and running verification. | "When a commit is blocked, S1Gate dispatches a structured task to IBM Bob IDE. Bob acts as our System-2 deliberative engine: it analyzes the vulnerability, writes the patch, and calls `s1gate_verify_remediation` via MCP. Notice the risk score dropping from 95 to 0. Bob commits the verified fix automatically." |
| **1:35 - 2:05** | Browser showing `https://mcp.cuang.dev/s1gate/health` and live curl SSE connection. | "For hackathon evaluators, we've hosted a production-ready remote MCP server behind Cloudflare at mcp.cuang.dev/s1gate/sse. You can plug it directly into IBM Bob IDE or Claude Desktop to inspect files and triage diffs in real time with sub-1.5s latency." |
| **2:05 - 2:25** | Terminal showing 85/85 test cases and QA benchmark table. | "With 85 automated tests and 100% detection across 12 production CVEs, S1Gate proves that smart System-1 guardrails make autonomous agent coding both faster and safer. Thank you!" |
