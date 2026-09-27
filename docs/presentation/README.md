# S1Gate Presentation & Pitch Deck

This directory contains the official presentation slides, pitch deck PDF, and full demonstration video for **S1Gate** created for the **IBM Bob 2.0 Hackathon** on [lablab.ai](https://lablab.ai).

---

## Deliverables

| Asset | Format | Location | Description |
| :--- | :--- | :--- | :--- |
| **Presentation Deck** | PDF | [`s1gate_presentation.pdf`](./s1gate_presentation.pdf) | 6-page 16:9 full-color presentation deck |
| **Pitch Video** | MP4 | [`s1gate_presentation.mp4`](./s1gate_presentation.mp4) | 1080p Full HD video synchronized with voiceover (1:49 duration) |
| **Master Audio** | WAV | [`Generated Audio September 27, 2026 - 8_24PM.wav`](./Generated%20Audio%20September%2027%2C%202026%20-%208_24PM.wav) | High-fidelity neural TTS master audio track |
| **Submission Details** | Markdown | [`../SUBMISSION_PACKAGE.md`](../SUBMISSION_PACKAGE.md) | Short/long descriptions, IBM Bob statement, tech list |
| **Slide Images** | PNG | [`images/`](./images/) | 1920x1080 high-res PNG renders for each slide |

---

## Slide Outline & Video Timestamps (1:49 Total Runtime)

### Slide 1: Introduction & Title (0:00 – 0:16)
- **Title**: S1Gate: Universal System-1 Pre-Commit Decision Layer & Remote MCP Server
- **Badges**: Sub-second latency (~1.2s), 100% CVE Catch Rate, Actor-Critic Remediation Loop, Hosted Remote SSE MCP
- **Visual**: S1Gate Shield & IBM Bob Hackathon branding.

### Slide 2: The Flow Paradox & Quota Burn (0:16 – 0:38)
- **The Bottleneck**: System-2 heavy LLM reasoning takes 15–30 seconds per micro-commit.
- **The Consequence**: Developers bypass safeguards with `git commit --no-verify`.
- **The Waste**: 85%+ of commits are routine edits that exhaust strict token quotas and Bobcoins.
- **Visual**: Side-by-side comparison of 30s LLM wait vs 1.2s S1Gate triage.

### Slide 3: Cognitive Architecture: Dual-Process Model (0:38 – 0:58)
- **Fast Intuition vs Deep Deliberation**:
  - *Stage 1 (< 0.05 ms)*: Shannon Entropy Scanner catches API keys and secrets instantly.
  - *Stage 2 (< 0.02 ms)*: AST Diff Parser strips lockfiles and isolates code changes.
  - *Stage 3 (~1.2 s)*: Gemini 3.1 Flash Lite / Local LM Studio classifies risk and strict invariants.
  - *Stage 4*: Tri-State Policy Gate (PASS / WARN / BLOCK).

### Slide 4: Actor-Critic Remediation Loop (0:58 – 1:19)
- **Autonomous Repair**:
  - S1Gate blocks vulnerable commit and dispatches `.bob/tasks/pending_remediation.json`.
  - IBM Bob Agent investigates via `s1gate_inspect_file`.
  - Bob synthesizes a surgical patch (System-2).
  - S1Gate Critic verifies via `s1gate_verify_remediation`. Risk score drops to 0. Auto-committed!

### Slide 5: Empirical Benchmarks & Error Matrix (1:19 – 1:36)
- **100% Detection Rate (12 / 12 CVEs Blocked)**:
  - SSRF (CWE-918), Prototype Pollution (CWE-1321), BOLA/IDOR (CWE-639), TOCTOU Race Condition (CWE-362), Insecure Deserialization (CWE-502), Buried Secrets (CWE-798).
  - Zero Type II escapes.
  - 85/85 Passing Unit & Integration Tests.

### Slide 6: Live Deployment & Judge Evaluation (1:36 – 1:49)
- **Remote MCP SSE Endpoint**: `https://mcp.cuang.dev/s1gate/sse`
- **Health Check**: `https://mcp.cuang.dev/s1gate/health`
- **Judge API Key**: `s1gate-judge-secret-key-2026`
- **Configuration**: Ready-to-paste `mcp.json` snippet for zero-install connection.

---

## Voiceover Narration Script

```text
Every developer has experienced the frustration of slow pre-commit hooks, or accidentally leaking a secret token to GitHub. Today, we are presenting S-one-Gate: an ultra-fast System-1 decision layer and universal Model Context Protocol server built for IBM Bob.

Modern coding agents possess incredible deep reasoning, known as System-2 thinking. But when applied at every micro-commit, waiting fifteen to thirty seconds ruins developer flow. Engineers bypass hooks with no-verify, and routine edits rapidly exhaust strict token quotas and Bobcoins. We need pre-commit decisions instantly.

Inspired by Daniel Kahneman's dual-process cognitive model, S-one-Gate inserts an ultra-fast System-1 gate. Obvious secrets and private keys are halted in under zero point zero five milliseconds using local Shannon entropy. Safe documentation and refactoring diffs pass in one point two seconds, burning zero agent quota and zero Bobcoins.

When a real flaw is caught, S-one-Gate does not just block: it writes a structured Remediation Intent Protocol task packet. IBM Bob IDE immediately steps in as the System-2 deliberative actor. Bob analyzes the vulnerability, synthesizes a surgical fix, and invokes the S-one-Gate verify tool over M-C-P. Once the risk score drops to zero, the commit is automatically cleared.

We evaluated S-one-Gate against twelve realistic production vulnerabilities spanning Python, TypeScript, Go, and Java. S-one-Gate achieved a one hundred percent detection rate with zero security escapes, verified across eighty-five automated unit and integration tests.

Best of all, S-one-Gate is live right now! Judges can connect to our hosted Remote M-C-P server at mcp dot cuang dot dev slash s-one-gate slash S-S-E using IBM Bob IDE with zero local setup. Thank you, and we welcome your evaluation!
```
