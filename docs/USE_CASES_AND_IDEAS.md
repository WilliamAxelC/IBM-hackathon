# IBM Bob 2.0 Hackathon: Challenge Tracks & Implementation Guide

> **Theme**: *Build with purpose using IBM Bob 2.0*  
> **Goal**: Create a working prototype that measurably accelerates and improves a high-friction developer workflow.  
> **Primary References**: [HACKATHON_GUIDE.md](HACKATHON_GUIDE.md) | [KICKOFF_ANNOUNCEMENT.md](KICKOFF_ANNOUNCEMENT.md)

---

## 🎯 The Core Brief

Traditional developer tooling often isolates code autocomplete from higher-level development workflows. The goal of this hackathon is to go beyond simple code generation and build an end-to-end working prototype that tackles real friction points across the software lifecycle.

### Key Success Factors
- **Measurable Impact**: Demonstrate concrete before-and-after improvements (e.g., hours reduced to minutes, reduction in error rates, automated toil).
- **Core Bob IDE Integration**: Showcase IBM Bob IDE features (Agent mode, subagents, parallel tasks, custom modes, MCP) as the central driver.
- **Workflow Completeness**: Solve an entire workflow step (discovery, analysis, generation, validation, and commit/PR), rather than a single prompt response.

---

## 🧭 The 5 Suggested Tracks & Architectural Blueprints

### Track 1: Smart Developer Onboarding Assistant
*“From zero to productive in 15 minutes instead of 2 weeks.”*
- **The Problem**: New team members spend days wading through fragmented documentation, setting up complex local dev environments, and trying to comprehend service architectures.
- **Solution Concept**: An intelligent onboarding copilot built in Bob IDE that ingests repository code, dependencies, and environment configs to produce interactive guided tours, setup validators, and curated starter issues.
- **Bob 2.0 Features to Leverage**:
  - `/init` and `AGENTS.md` for project context modeling.
  - Context mentions (`@codebase`, `@problems`) to map inter-module dependencies.
  - Mermaid diagram generation for UML class, sequence, and system diagrams.
- **Optional Watsonx Integration**: watsonx Orchestrate to automate credential provisioning and Slack/Teams onboarding greetings.

---

### Track 2: Intelligent Code Review and Quality Coach
*“Elevate code quality before the PR even opens.”*
- **The Problem**: Human code reviews are bottlenecked, inconsistent, and often miss subtle security vulnerabilities or architectural regressions until production.
- **Solution Concept**: An automated pre-PR coaching workflow inside Bob IDE that inspects diffs, evaluates adherence to team standards, runs actor-critic security checks (OWASP ASVS), and generates concise review summaries with actionable inline fixes.
- **Bob 2.0 Features to Leverage**:
  - Built-in **Review Workflow** and inline code diffs.
  - **Actor-Critic security loops**: Bob proposes code -> Critic subagent checks against security rules -> Bob refactors before check-in.
  - Custom rules (`.bob/rules/`) enforcing team conventions.
  - SARIF and OSCAL report generation for security auditing.
- **Optional Watsonx Integration**: watsonx.ai to prioritize findings by risk severity; watsonx Orchestrate to manage approval workflows.

---

### Track 3: Automated Testing and Validation Hub
*“Zero-to-100% meaningful coverage with self-healing tests.”*
- **The Problem**: Writing unit, integration, and end-to-end tests is often deferred due to time pressure, leading to poor test coverage, flaky tests, and regression surprises.
- **Solution Concept**: An agentic test generator and validator that inspects functions, boundary cases, and existing test suites, automatically writes comprehensive unit tests, executes test suites in isolated subagents, and self-corrects broken tests upon failure.
- **Bob 2.0 Features to Leverage**:
  - **Subagents**: Isolated execution environments running tests without polluting parent chat history.
  - **Literate Coding**: Generating parameterized test cases directly from inline specifications.
  - **Auto-Approve policies**: Safe read/write/execute cycles during automated test execution.
- **Optional Watsonx Integration**: watsonx Orchestrate to trigger automated CI test runs and send telemetry to dashboards.

---

### Track 4: Release Readiness and Deployment Assistant
*“Ship on Friday with zero anxiety.”*
- **The Problem**: Preparing a release requires juggling git logs, dependency audits, breaking API changes, deployment runbooks, and release note authoring.
- **Solution Concept**: A release copilot that inspects recent commits, verifies semantic versioning, detects CVEs in dependencies, validates staging environment health, and drafts release notes and changelogs.
- **Bob 2.0 Features to Leverage**:
  - Commit message & PR generation features.
  - Parallel tasks to simultaneously audit dependencies, check migrations, and write release documentation.
  - MCP tools connecting to GitHub APIs, Jira, or cloud deployment endpoints.
- **Optional Watsonx Integration**: watsonx Orchestrate to coordinate deployment gates and manager sign-offs.

---

### Track 5: Legacy Application Modernization Accelerator
*“Upgrading decades of tech debt safely and systematically.”*
- **The Problem**: Enterprises sit on massive legacy codebases (outdated Node versions, deprecated Python 2, monolithic Java/COBOL) where manual refactoring is cost-prohibitive and risky.
- **Solution Concept**: A modernization engine that scans legacy modules, maps dependencies, flags deprecated API usage, and uses Plan & Code modes to incrementally refactor components with regression tests.
- **Bob 2.0 Features to Leverage**:
  - **Plan Mode & Code Mode**: End-to-end architectural planning followed by autonomous file-by-file refactoring.
  - **Rollback**: Automatic workspace checkpointing to safely revert breaking changes.
  - Context window management for parsing large repositories without context overflow.
- **Optional Watsonx Integration**: watsonx.ai for semantic dependency mapping; watsonx Orchestrate for batch modernization pipeline orchestration.

---

## 🛠️ Bob 2.0 Feature Toolkit Reference

| Feature | Best For | How to Access in Bob IDE |
| :--- | :--- | :--- |
| **Agent Mode** | Multi-file autonomous execution & iteration | Select `Agent` from the Modes dropdown |
| **Plan Mode** | Architectural blueprinting before writing code | Select `Plan` from the Modes dropdown |
| **Subagents** | Isolated tasks (e.g. running linters/tests, audits) | Configure in Custom Modes / Subagent settings |
| **Literate Coding** | Inline code generation directly inside the code editor | Trigger via inline editor prompt |
| **Custom Rules** | Enforcing coding styles, security frameworks | Define in `.bob/rules/` or project settings |
| **MCP Servers** | Connecting Bob to external APIs, databases, CI | Configure via Settings → MCP Servers |
| **Context Mentions** | Feeding specific files, problems, or directories | Use `@filename`, `@problems`, `@codebase` |
| **Bob Tips** | Real-time AI code smell and complexity detection | Automatic in editor gutter / lightbulb |

---

## 💡 Bobcoins Conservation Strategy

With **40 Bobcoins per participant**, smart resource management is essential:
1. **Divide Tasks by Member**: If your team has 3 members, that's $3 \times 40 = 120$ Bobcoins. Assign distinct tasks to each member's account.
2. **Use Plan Mode First**: Outline solutions before triggering multi-file code modifications to avoid iterative rework loops.
3. **Refine Prompts Early**: Use the prompt enhancer (sparkles icon) to sharpen queries before hitting enter.
4. **Leverage Local Shell & watsonx**: Use local tools or free-tier watsonx services when Bobcoins approach the 100% mark.
