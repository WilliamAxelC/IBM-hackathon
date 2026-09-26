# IBM Bob 2.0 Hackathon Solution

> **Event**: IBM Bob 2.0 Hackathon (Hosted on lablab.ai)  
> **Theme**: *Build with purpose using IBM Bob 2.0*  
> **Repository**: [WilliamAxelC/IBM-hackathon](https://github.com/WilliamAxelC/IBM-hackathon)

---

## 📖 Project Documentation & Resources

All official rules, guides, and architectural blueprints have been converted and indexed locally for the project:

- 📘 [**Builder's Hackathon Guide**](HACKATHON_GUIDE.md): The essential builder's guide covering deadlines, prize distribution ($12k), the 3 fatal disqualification rules, Bobcoin conservation, required video pitch, and judging criteria.
- 🏛️ [**System Architecture & Technical Specification**](ARCHITECTURE.md): Universal System-1 decision gate, LM Studio / Kev-4B integration, cross-harness MCP protocol (Bob, Claude Code, Agrav, Kiro, Codex, DeepSeek), and Actor-Critic verification loop.
- 📚 [**Official IBM Bob Guide (Offline Archive)**](docs/HACKATHON_GUIDE.md): Complete verbatim offline copy of the official IBM Bob 2.0 tutorial covering Bob IDE installation, UI walkthroughs, modes, and exercises.
- 📢 [**Kickoff Announcement & Critical Rules**](docs/KICKOFF_ANNOUNCEMENT.md): The official kickoff announcement detailing deadlines, prize breakdown ($12,000 pool), Bobcoins budgeting, and the 3 eligibility rules.
- 💡 [**Challenge Tracks & Implementation Guide**](docs/USE_CASES_AND_IDEAS.md): Detailed architectural breakdowns of the 5 recommended developer workflow use cases (Onboarding, Code Review, Testing, Release Readiness, Legacy Modernization).
- 📸 [**Bob Task Session Screenshots (`bob_sessions/`)**](bob_sessions/README.md): **Mandatory judging deliverable directory**. Contains PNG screenshots of Bob IDE task session consumption summaries.

---

## ⚠️ 3 Critical Rules for Judging Eligibility

Before final submission, ensure complete adherence to these rules:

1. **Bob IDE as a Core Component**:
   The solution may use any stack or framework, but **IBM Bob IDE must be showcased as a core component** (Bob Shell is optional).
2. **Mandatory `bob_sessions/` Folder**:
   Every participant must capture and upload their **Bob IDE task session consumption summaries** (PNG format) inside the [`bob_sessions/`](bob_sessions/) directory as verifiable evidence of Bob usage.
   - Format: `<team_name>_task<XX>_<description>_summary.png`
   - Capture these throughout development, not at the last minute!
3. **Data Compliance**:
   Bring your own datasets. **Zero tolerance** for client data, company confidential data, personal information (PI/PII), or social media data. Public web data must allow commercial use.

---

## 🪙 Bobcoins Budgeting

- Each hackathon account receives **40 Bobcoins**.
- When usage hits **100%**, no further coins are provided.
- **Team Strategy**:
  - Distribute tasks across team members to maximize available coins.
  - Monitor coins in Bob IDE under **Settings → General** or in the [Admin Dashboard](https://bob.ibm.com/admin/subscription).
  - Ensure the active instance is set to **`ibm-coding-challenge-uat` (region: `us-east`)** to avoid burning personal coins.
  - If depleted, optional watsonx tools (watsonx.ai, watsonx Orchestrate) remain available.

---

## 📁 Repository Structure

```
.
├── README.md                           # Main project overview & eligibility checklist
├── HACKATHON_GUIDE.md                  # Comprehensive builder's guide (rules, coins, judging, video)
├── ARCHITECTURE.md                     # Technical architecture of KevGate universal MCP
├── bob_sessions/                       # [REQUIRED DELIVERABLE] Bob IDE task session summary screenshots
│   ├── .gitkeep
│   └── README.md                       # Screenshot guidelines, naming format & task tracker
└── docs/                               # Project documentation & references
    ├── HACKATHON_GUIDE.md              # Complete offline copy of IBM Bob 2.0 Hackathon Guide
    ├── KICKOFF_ANNOUNCEMENT.md         # Kickoff email, rules, checklist & prize breakdown
    ├── USE_CASES_AND_IDEAS.md          # 5 workflow tracks, architectural blueprints & Bob toolkit
    └── assets/                         # Guide diagrams, UI screenshots & reference assets
        └── images/                     # 22 extracted figures from the official guide
```

---

## 🚀 Getting Started

1. **Create IBMid**: Register with the hackathon email address at [IBM Account Signup](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776).
2. **Install Bob IDE**: Ensure version is `v2.0.2` or later (v1.0.3 and v2.0.0 sunset on September 30, 2026).
3. **Connect Account**: Look for invite email (`ibm-hackathon-xxxx`) and switch active instance to `ibm-coding-challenge-uat` (region: `us-east`) in Bob IDE Settings.
4. **Log Sessions**: For every task completed in Bob IDE, save a session consumption screenshot into [`bob_sessions/`](bob_sessions/).
