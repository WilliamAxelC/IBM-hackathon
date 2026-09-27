# S1Gate — Hackathon Demo Video Script
# IBM Bob 2.0 Hackathon · lablab.ai · Target Duration: 4 minutes

---

## 🎬 Scene 1 — The Problem (0:00 – 0:30)

**[Screen: terminal, rapid git commits flying by]**

> "Every time a developer commits code, AI coding agents like IBM Bob, Claude Code, or Kiro
> could review it for security vulnerabilities. But there's a catch — these agents run heavy
> language models that take 5 to 30 seconds per call and burn expensive API tokens.
>
> IBM Bob gives each hackathon team just 40 Bobcoins. And 80% of commits? Totally safe.
> Formatting fixes. Doc updates. Renaming a variable.
>
> We needed a smarter gate — one that only escalates the dangerous 20%."

---

## 🎬 Scene 2 — The Solution (0:30 – 1:30)

**[Screen: architecture diagram from README.md — the mermaid flowchart]**

> "Meet S1Gate. A System-1 Decision Layer that sits at the pre-commit boundary.
>
> Before IBM Bob ever sees your diff, S1Gate runs two ultra-fast checks:
>
> First — a Shannon entropy scanner. It detects hardcoded secrets, API keys, and
> high-entropy tokens in under 2 milliseconds. No LLM needed.
>
> Second — a structured triage call to Gemini 3.5 Flash Lite, our fast cloud backend,
> or a local GPU model via LM Studio for fully offline execution.
>
> The result is a typed risk score from 0 to 100:
> - Score under 30? PASS — commit greenlit instantly. Zero Bobcoins burned.
> - Score 30 to 69? WARN — advisory only, commit goes through.
> - Score 70 or above? BLOCK — commit aborted. S1Gate writes a remediation task
>   directly into IBM Bob's task queue."

**[Screen: show .bob/tasks/pending_remediation.json being written]**

> "IBM Bob then picks up that task in Agent mode, inspects the vulnerability,
> generates a fix, and calls back into S1Gate via MCP to verify the patch resolved the risk.
> This is the Actor-Critic loop — Bob fixes, S1Gate confirms."

---

## 🎬 Scene 3 — Live Demo (1:30 – 3:30)

### Part A — BLOCK a bad commit (1:30 – 2:30)

**[Screen: terminal in the IBM-hackathon repo]**

```bash
# Stage a diff with a SQL injection vulnerability
git add src/kevgate/benchmarks/true_positives/01_sql_injection.diff

# Run S1Gate manually
uv run s1gate check --diff src/kevgate/benchmarks/true_positives/01_sql_injection.diff
```

**[Screen: S1Gate output — RED BLOCK banner]**

> "Watch S1Gate catch it. Risk score 95 out of 100. Category: security_risk.
> Remediation hint printed right in the terminal.
> If this were a real commit, the hook would have exited with code 1 — the commit is aborted."

---

### Part B — PASS a safe commit (2:30 – 2:50)

```bash
uv run s1gate check --diff src/kevgate/benchmarks/false_positives/05_readme_update.diff
```

**[Screen: S1Gate output — GREEN PASS banner, ~150ms]**

> "A README update. Score 0. PASS in under 150 milliseconds. Zero Bobcoins burned."

---

### Part C — IBM Bob IDE integration via MCP (2:50 – 3:30)

**[Screen: IBM Bob IDE — MCP tools panel showing s1gate_triage_diff, s1gate_verify_remediation]**

> "S1Gate also runs as a universal MCP server. Here in IBM Bob IDE, you can see the three
> S1Gate tools registered in Bob's tool palette.
>
> Bob can call s1gate_triage_diff directly from inside a task — triage a diff without
> ever leaving the IDE. And when Bob generates a fix, it calls s1gate_verify_remediation
> to confirm the risk score dropped before committing."

**[Screen: bob_sessions/ screenshots — task consumption summary showing Bobcoins spent]**

> "These are our Bob IDE session summaries — verifiable proof of IBM Bob usage throughout
> the entire build, captured directly from the IDE's task consumption dashboard."

---

## 🎬 Scene 4 — Benchmarks & Business Impact (3:30 – 4:00)

**[Screen: docs/benchmarks/s1gate_error_matrix.png and s1gate_vs_baseline_comparison.png]**

> "We validated S1Gate against 40 production-grade diffs — including subtle SSRF rebinding,
> JWT algorithm confusion, TOCTOU race conditions, and catastrophic ReDoS patterns.
>
> S1Gate achieved 100% accuracy and — critically — a 0% Type II escape rate.
> No vulnerability slipped through undetected.
>
> Compared to naive direct Gemini prompting, S1Gate's structured pipeline is 10% more accurate
> on the standard suite and eliminates the two missed vulnerabilities the baseline let through.
>
> For enterprise teams running thousands of commits a day, this translates to:
> - 80% reduction in LLM token spend
> - Zero security escapes at the pre-commit boundary
> - Sub-150ms developer experience — no more disabling hooks with --no-verify"

---

## 🎬 Closing (4:00)

**[Screen: GitHub repo landing page]**

> "S1Gate is open source, works with IBM Bob, Claude Code, Kiro, and any MCP-compatible agent,
> and runs on your laptop with a free Gemini API key or a local GPU.
>
> We built it in 48 hours using IBM Bob IDE as the primary development harness.
> Try it today — links in the description."

---

## 📋 Recording Checklist

Before hitting record, confirm:

- [ ] Terminal font size ≥ 18px — legible on small screens
- [ ] S1Gate installed and `uv run s1gate --help` working
- [ ] `.env` configured with a valid Gemini API key (or mock mode for recording)
- [ ] IBM Bob IDE open with `mcp.json` loaded — S1Gate tools visible in tool palette
- [ ] `bob_sessions/` screenshots ready to show on screen
- [ ] Error matrix and comparison graph open in image viewer
- [ ] Total recording: aim for **3:50 – 4:10** (strict 5 min limit with buffer)
- [ ] Upload to YouTube (Unlisted) or Loom and paste URL into Lablab.ai submission form
