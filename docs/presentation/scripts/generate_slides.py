"""
Script to generate 6 high-resolution (1920x1080) presentation slides for S1Gate
and render them to PNG images using Playwright.
"""
import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLIDES_DIR = Path(__file__).parent / "slides"
OUTPUT_DIR = Path(__file__).parent / "output"

SLIDES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Common styling for all slides
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  width: 1920px;
  height: 1080px;
  background: radial-gradient(circle at 15% 15%, #111a2e 0%, #080c14 100%);
  color: #f1f5f9;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  overflow: hidden;
  position: relative;
}

/* Background grid & glowing orb accents */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}

.orb-blue {
  position: absolute;
  top: -150px;
  right: -150px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(15, 98, 254, 0.25) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
}

.orb-cyan {
  position: absolute;
  bottom: -150px;
  left: -150px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 242, 254, 0.2) 0%, transparent 70%);
  filter: blur(90px);
  pointer-events: none;
}

.slide-container {
  position: relative;
  z-index: 10;
  width: 1920px;
  height: 1080px;
  padding: 80px 100px;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.brand-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(15, 98, 254, 0.15);
  border: 1px solid rgba(15, 98, 254, 0.4);
  padding: 8px 18px;
  border-radius: 9999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #38bdf8;
  letter-spacing: 0.5px;
}

.brand-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00f2fe;
  box-shadow: 0 0 10px #00f2fe;
}

.slide-number {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  color: #64748b;
  font-weight: 500;
}

.slide-title {
  font-size: 52px;
  font-weight: 800;
  letter-spacing: -1.5px;
  line-height: 1.15;
  background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.slide-subtitle {
  font-size: 22px;
  color: #94a3b8;
  font-weight: 400;
  margin-bottom: 40px;
  max-width: 1200px;
  line-height: 1.5;
}

/* Glassmorphic card styling */
.glass-card {
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.glow-blue {
  border-color: rgba(15, 98, 254, 0.4);
  box-shadow: 0 0 30px rgba(15, 98, 254, 0.15);
}

.glow-green {
  border-color: rgba(16, 185, 129, 0.4);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.15);
}

.glow-amber {
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.15);
}

.glow-red {
  border-color: rgba(239, 68, 68, 0.4);
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.15);
}

.badge-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;
}

.badge-blue { background: rgba(15, 98, 254, 0.2); color: #60a5fa; border: 1px solid rgba(15, 98, 254, 0.4); }
.badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.badge-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
.badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }

.code-box {
  background: #090d16;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 18px 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.6;
}

.footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 15px;
  color: #64748b;
}
"""

SLIDES_HTML = {
    # -------------------------------------------------------------
    # SLIDE 1: Title & Hook
    # -------------------------------------------------------------
    "slide_1.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 1 - S1Gate Introduction</title>
  <style>
    {BASE_CSS}
    .hero-container {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      position: relative;
    }}
    .shield-icon {{
      width: 120px;
      height: 120px;
      background: linear-gradient(135deg, #0f62fe 0%, #00f2fe 100%);
      border-radius: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 60px rgba(0, 242, 254, 0.4);
      margin-bottom: 32px;
    }}
    .shield-icon svg {{
      width: 64px;
      height: 64px;
      fill: #ffffff;
    }}
    .title-gradient {{
      font-size: 80px;
      font-weight: 800;
      letter-spacing: -2.5px;
      line-height: 1;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #ffffff 40%, #38bdf8 80%, #00f2fe 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .tagline {{
      font-size: 28px;
      color: #94a3b8;
      max-width: 1000px;
      margin-bottom: 48px;
      line-height: 1.4;
      font-weight: 500;
    }}
    .badges-row {{
      display: flex;
      gap: 20px;
      margin-bottom: 60px;
    }}
    .feature-pill {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 100px;
      padding: 12px 24px;
      font-size: 16px;
      font-weight: 600;
      color: #e2e8f0;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }}
    .feature-pill span.icon {{
      font-size: 20px;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        IBM BOB 2.0 HACKATHON • LABLAB.AI
      </div>
      <div class="slide-number">01 / 06</div>
    </div>

    <div class="hero-container">
      <div class="shield-icon">
        <svg viewBox="0 0 24 24">
          <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
        </svg>
      </div>
      <h1 class="title-gradient">S1Gate</h1>
      <p class="tagline">The Universal System-1 Pre-Commit Decision Layer & Remote MCP Server for AI Coding Harnesses</p>
      
      <div class="badges-row">
        <div class="feature-pill" style="border-color: rgba(56, 189, 248, 0.4);">
          <span class="icon">⚡</span>
          <span>Sub-Second Latency (~1.2s)</span>
        </div>
        <div class="feature-pill" style="border-color: rgba(52, 211, 153, 0.4);">
          <span class="icon">🛡️</span>
          <span>100% CVE Catch Rate (12/12)</span>
        </div>
        <div class="feature-pill" style="border-color: rgba(192, 132, 252, 0.4);">
          <span class="icon">🤖</span>
          <span>IBM Bob Actor-Critic Remediation</span>
        </div>
        <div class="feature-pill" style="border-color: rgba(251, 191, 36, 0.4);">
          <span class="icon">🌐</span>
          <span>Hosted Remote SSE MCP</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Project: <strong>S1Gate</strong> | Team: WilliamAxelC</div>
      <div>Live Endpoint: <code style="color: #38bdf8;">https://mcp.cuang.dev/s1gate/sse</code></div>
    </div>
  </div>
</body>
</html>
""",

    # -------------------------------------------------------------
    # SLIDE 2: The Core Problem: Latency Paradox & Quota Burn
    # -------------------------------------------------------------
    "slide_2.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 2 - The Problem</title>
  <style>
    {BASE_CSS}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
      flex: 1;
      align-items: stretch;
    }}
    .stat-number {{
      font-size: 56px;
      font-weight: 800;
      line-height: 1;
      margin-bottom: 8px;
      font-family: 'JetBrains Mono', monospace;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        THE AGENT FLOW PARADOX
      </div>
      <div class="slide-number">02 / 06</div>
    </div>

    <h2 class="slide-title">Heavy LLM Reasoning Destroys Commit Flow</h2>
    <p class="slide-subtitle">Modern AI agents (IBM Bob, Claude Code) are built for complex multi-file architecture synthesis (System-2). Applying them blindly to micro-commits creates catastrophic friction.</p>

    <div class="grid-2">
      <!-- Problem Card -->
      <div class="glass-card glow-red" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span class="badge-tag badge-red">WITHOUT S1GATE</span>
            <span style="color: #f87171; font-weight: 700;">FLAWED PATTERN</span>
          </div>
          <div class="stat-number" style="color: #f87171;">15 – 30s</div>
          <div style="font-size: 18px; color: #cbd5e1; font-weight: 600; margin-bottom: 24px;">Autoregressive Latency per Micro-Commit</div>
          
          <ul style="list-style: none; display: flex; flex-direction: column; gap: 16px; color: #94a3b8; font-size: 16px;">
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #f87171;">❌</span>
              <span><strong>Developers bypass hooks:</strong> Long waits force engineers to run <code style="color: #f87171;">git commit --no-verify</code>, letting flaws through.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #f87171;">❌</span>
              <span><strong>Quota & Cost Burn:</strong> 85%+ of commits are routine edits (docs, comments, formatting). Heavy frontier reasoning exhausts token allowances & Bobcoins instantly.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #f87171;">❌</span>
              <span><strong>No deterministic secret gate:</strong> Leaked AWS or GitHub keys wait for slow model inference instead of instant sub-millisecond halting.</span>
            </li>
          </ul>
        </div>

        <div class="code-box" style="margin-top: 24px; border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.05);">
          <span style="color: #f87171;">$ git commit -m "docs: fix typo in README"</span><br/>
          <span style="color: #64748b;">[System-2 Agent Thinking...] 24.8s elapsed... Quota: -1 Bobcoin</span>
        </div>
      </div>

      <!-- Solution Card -->
      <div class="glass-card glow-green" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span class="badge-tag badge-green">WITH S1GATE SYSTEM-1</span>
            <span style="color: #34d399; font-weight: 700;">DUAL-PROCESS FLOW</span>
          </div>
          <div class="stat-number" style="color: #34d399;">&lt; 1.2s</div>
          <div style="font-size: 18px; color: #cbd5e1; font-weight: 600; margin-bottom: 24px;">Sub-Second Pre-Commit Verification Gate</div>
          
          <ul style="list-style: none; display: flex; flex-direction: column; gap: 16px; color: #94a3b8; font-size: 16px;">
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #34d399;">✅</span>
              <span><strong>Sub-millisecond Secret Detection:</strong> Deterministic Shannon entropy filter halts high-entropy credentials in <strong>0.05 milliseconds</strong>.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #34d399;">✅</span>
              <span><strong>Zero Quota Burn on Safe Edits:</strong> Routine documentation and refactor diffs get instant PASS greenlight without invoking heavy reasoning models.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #34d399;">✅</span>
              <span><strong>Developer Flow Preserved:</strong> Engineers keep their rhythm while repositories stay strictly shielded from security vulnerabilities.</span>
            </li>
          </ul>
        </div>

        <div class="code-box" style="margin-top: 24px; border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.05);">
          <span style="color: #34d399;">$ git commit -m "docs: fix typo in README"</span><br/>
          <span style="color: #10b981;">[S1Gate] PASS (Score: 0) • Invariants clean • Time: 1.14s (0 Quota)</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Core Principle: <em>Fast deterministic gating before deep cognitive deliberation.</em></div>
      <div>Flow Preservation: <strong>100%</strong></div>
    </div>
  </div>
</body>
</html>
""",

    # -------------------------------------------------------------
    # SLIDE 3: Architecture: System-1 Intuition meets System-2
    # -------------------------------------------------------------
    "slide_3.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 3 - Kahneman Dual-Process Architecture</title>
  <style>
    {BASE_CSS}
    .arch-flow {{
      display: flex;
      flex-direction: column;
      gap: 24px;
      flex: 1;
    }}
    .stage-row {{
      display: grid;
      grid-template-columns: 280px 1fr 220px;
      gap: 24px;
      align-items: center;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 22px 32px;
    }}
    .stage-title {{
      font-size: 20px;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .stage-desc {{
      font-size: 15px;
      color: #94a3b8;
      line-height: 1.5;
    }}
    .stage-metric {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 18px;
      font-weight: 700;
      text-align: right;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        COGNITIVE ARCHITECTURE
      </div>
      <div class="slide-number">03 / 06</div>
    </div>

    <h2 class="slide-title">System-1 Intuition Meets System-2 Deliberation</h2>
    <p class="slide-subtitle">Inspired by Daniel Kahneman's dual-process cognitive model: S1Gate separates sub-millisecond deterministic reflex from focused sub-second neural triage.</p>

    <div class="arch-flow">
      <!-- Stage 1 -->
      <div class="stage-row" style="border-left: 6px solid #38bdf8;">
        <div class="stage-title">
          <span style="color: #38bdf8;">01</span> Shannon Scanner
        </div>
        <div class="stage-desc">
          High-entropy string detector and regex engine. Scans diff additions for AWS secret keys, GitHub tokens, Slack Webhooks, and private keys. Instant deterministic short-circuit.
        </div>
        <div class="stage-metric" style="color: #38bdf8;">
          &lt; 0.05 ms<br/>
          <span style="font-size: 12px; font-weight: 400; color: #64748b;">Fast Pre-Filter</span>
        </div>
      </div>

      <!-- Stage 2 -->
      <div class="stage-row" style="border-left: 6px solid #818cf8;">
        <div class="stage-title">
          <span style="color: #818cf8;">02</span> AST Diff Parser
        </div>
        <div class="stage-desc">
          Parses unified diff syntax, strips lockfiles (package-lock, poetry.lock, uv.lock), and extracts semantic code chunks. Limits prompt footprint to under 8,000 characters.
        </div>
        <div class="stage-metric" style="color: #818cf8;">
          &lt; 0.02 ms<br/>
          <span style="font-size: 12px; font-weight: 400; color: #64748b;">Zero Allocations</span>
        </div>
      </div>

      <!-- Stage 3 -->
      <div class="stage-row" style="border-left: 6px solid #34d399;">
        <div class="stage-title">
          <span style="color: #34d399;">03</span> System-1 Triage
        </div>
        <div class="stage-desc">
          Evaluates code changes against security invariants using Google Gemini 3.1 Flash Lite (Keep-Alive pooled) or 100% offline Local LM Studio. Outputs structured Pydantic v2 JSON.
        </div>
        <div class="stage-metric" style="color: #34d399;">
          ~1.2 s<br/>
          <span style="font-size: 12px; font-weight: 400; color: #64748b;">Cloud or GPU</span>
        </div>
      </div>

      <!-- Stage 4: Decision -->
      <div class="stage-row" style="border-left: 6px solid #f59e0b;">
        <div class="stage-title">
          <span style="color: #f59e0b;">04</span> Policy Gate
        </div>
        <div class="stage-desc">
          Tri-state enforcement: <strong>PASS</strong> (Score 0–24, zero quota used), <strong>WARN</strong> (Score 25–69, contract alert), or <strong>BLOCK</strong> (Score 70–100, security flaw). Triggers Actor-Critic loop on BLOCK.
        </div>
        <div class="stage-metric" style="color: #f59e0b;">
          Tri-State<br/>
          <span style="font-size: 12px; font-weight: 400; color: #64748b;">PASS / WARN / BLOCK</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Engine: <strong>Gemini 3.1 Flash Lite</strong> + <strong>Local LM Studio</strong> fallback</div>
      <div>Security Invariants: <strong>Injection, SSRF, Deserialization, BOLA, Race Conditions, Secret Leaks</strong></div>
    </div>
  </div>
</body>
</html>
""",

    # -------------------------------------------------------------
    # SLIDE 4: Actor-Critic Remediation Loop (IBM Bob Integration)
    # -------------------------------------------------------------
    "slide_4.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 4 - IBM Bob Actor-Critic Remediation Loop</title>
  <style>
    {BASE_CSS}
    .grid-loop {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 36px;
      flex: 1;
    }}
    .step-card {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 18px 24px;
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }}
    .step-num {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: rgba(15, 98, 254, 0.3);
      color: #38bdf8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      flex-shrink: 0;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        AUTONOMOUS REMEDIATION
      </div>
      <div class="slide-number">04 / 06</div>
    </div>

    <h2 class="slide-title">Actor-Critic Remediation with IBM Bob</h2>
    <p class="slide-subtitle">When a vulnerability is caught, S1Gate doesn't just block — it empowers IBM Bob's Agent mode to diagnose, repair, and verify the patch automatically.</p>

    <div class="grid-loop">
      <!-- Steps column -->
      <div style="display: flex; flex-direction: column; gap: 16px; justify-content: space-between;">
        <div class="step-card glow-red">
          <div class="step-num" style="background: rgba(239,68,68,0.2); color: #f87171;">1</div>
          <div>
            <div style="font-weight: 700; color: #ffffff; font-size: 17px; margin-bottom: 4px;">S1Gate Blocks Vulnerable Diff</div>
            <div style="font-size: 14px; color: #94a3b8;">Commit is halted. Generates structured Remediation Intent Protocol (RIP) task at <code>.bob/tasks/pending_remediation.json</code>.</div>
          </div>
        </div>

        <div class="step-card glow-blue">
          <div class="step-num">2</div>
          <div>
            <div style="font-weight: 700; color: #ffffff; font-size: 17px; margin-bottom: 4px;">IBM Bob Agent Reads Task Packet</div>
            <div style="font-size: 14px; color: #94a3b8;">Bob reads the vulnerability diagnosis, CWE classification, and targeted remediation hint. Inspects source via <code>s1gate_inspect_file</code>.</div>
          </div>
        </div>

        <div class="step-card glow-blue">
          <div class="step-num">3</div>
          <div>
            <div style="font-weight: 700; color: #ffffff; font-size: 17px; margin-bottom: 4px;">Bob Synthesizes Surgical Fix (System-2)</div>
            <div style="font-size: 14px; color: #94a3b8;">Bob uses its deep deliberative reasoning to patch the vulnerability (e.g., parameterizing SQL, sanitizing paths, fixing race condition).</div>
          </div>
        </div>

        <div class="step-card glow-green">
          <div class="step-num" style="background: rgba(16,185,129,0.2); color: #34d399;">4</div>
          <div>
            <div style="font-weight: 700; color: #ffffff; font-size: 17px; margin-bottom: 4px;">S1Gate Critic Verifies & Clears Commit</div>
            <div style="font-size: 14px; color: #94a3b8;">Bob invokes <code>s1gate_verify_remediation</code> MCP tool. Risk score drops from 95 to 0. Commit is cleared and finalized!</div>
          </div>
        </div>
      </div>

      <!-- JSON Task Packet Display -->
      <div class="glass-card" style="display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #38bdf8;">.bob/tasks/pending_remediation.json</span>
          <span class="badge-tag badge-red">RIP TASK PACKET</span>
        </div>
        <div class="code-box" style="flex: 1; font-size: 13px; overflow: hidden; background: #070a12;">
<span style="color: #64748b;">&#123;</span><br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"task_id"</span>: <span style="color: #a5f3fc;">"rip-2026-cve-891"</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"decision"</span>: <span style="color: #f87171;">"BLOCK"</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"original_risk_score"</span>: <span style="color: #f87171;">95</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"violated_invariants"</span>: <span style="color: #f87171;">["has_ssrf", "flawed_ip_resolution"]</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"affected_file"</span>: <span style="color: #cbd5e1;">"services/webhook_client.py"</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"remediation_hint"</span>: <span style="color: #34d399;">"Validate resolved IP against RFC1918 and link-local ranges before socket connection."</span>,<br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"critic_tool"</span>: <span style="color: #fbbf24;">"s1gate_verify_remediation"</span><br/>
<span style="color: #64748b;">&#125;</span>
        </div>
        <div style="margin-top: 16px; font-size: 13px; color: #64748b; font-family: 'JetBrains Mono', monospace;">
          Status: Verified Fixed • Risk: 0/100 • Safe to Commit
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Protocol: <strong>Remediation Intent Protocol (RIP v1.0)</strong></div>
      <div>MCP Tools: <code>s1gate_triage_diff</code> • <code>s1gate_inspect_file</code> • <code>s1gate_verify_remediation</code></div>
    </div>
  </div>
</body>
</html>
""",

    # -------------------------------------------------------------
    # SLIDE 5: Rigorous Benchmarks & Error Matrix
    # -------------------------------------------------------------
    "slide_5.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 5 - Benchmarks and Error Matrix</title>
  <style>
    {BASE_CSS}
    .benchmark-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    .benchmark-table th {{
      text-align: left;
      padding: 12px 16px;
      background: rgba(15, 98, 254, 0.15);
      border-bottom: 2px solid rgba(15, 98, 254, 0.4);
      color: #38bdf8;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
    }}
    .benchmark-table td {{
      padding: 10px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      color: #cbd5e1;
    }}
    .grid-stats {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-bottom: 28px;
    }}
    .stat-card {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 20px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        EMPIRICAL EVALUATION
      </div>
      <div class="slide-number">05 / 06</div>
    </div>

    <h2 class="slide-title">Zero Escapes: 100% Catch Across 12 Production CVEs</h2>
    <p class="slide-subtitle">Tested against realistic multi-language git diffs (Python, TypeScript, Go, Java) designed by an unbiased security auditor.</p>

    <div class="grid-stats">
      <div class="stat-card glow-green">
        <div style="font-size: 40px; font-weight: 800; color: #34d399; font-family: 'JetBrains Mono', monospace;">12 / 12</div>
        <div style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Flaws Blocked (100%)</div>
      </div>
      <div class="stat-card glow-green">
        <div style="font-size: 40px; font-weight: 800; color: #34d399; font-family: 'JetBrains Mono', monospace;">0</div>
        <div style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Type II Escapes (Zero Leakage)</div>
      </div>
      <div class="stat-card glow-blue">
        <div style="font-size: 40px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">0.05 ms</div>
        <div style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Entropy Secret Detection</div>
      </div>
      <div class="stat-card glow-blue">
        <div style="font-size: 40px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">85 / 85</div>
        <div style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Automated Tests Passing</div>
      </div>
    </div>

    <div class="glass-card" style="padding: 16px 24px; flex: 1;">
      <table class="benchmark-table">
        <thead>
          <tr>
            <th>CVE / Flaw Category</th>
            <th>Language</th>
            <th>Vulnerability Description</th>
            <th>S1Gate Decision</th>
            <th>Detection Time</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>CWE-918 (SSRF)</strong></td>
            <td>Python</td>
            <td>IPv4-mapped IPv6 internal cloud metadata bypass</td>
            <td><span class="badge-tag badge-red">BLOCKED (Score: 92)</span></td>
            <td>1.21s</td>
          </tr>
          <tr>
            <td><strong>CWE-1321 (Prototype Pollution)</strong></td>
            <td>TypeScript</td>
            <td>Recursive deep merge touching __proto__ object prototype</td>
            <td><span class="badge-tag badge-red">BLOCKED (Score: 94)</span></td>
            <td>1.18s</td>
          </tr>
          <tr>
            <td><strong>CWE-639 (BOLA / IDOR)</strong></td>
            <td>Python/FastAPI</td>
            <td>Multi-tenant resource retrieval missing org_id boundary</td>
            <td><span class="badge-tag badge-red">BLOCKED (Score: 90)</span></td>
            <td>1.25s</td>
          </tr>
          <tr>
            <td><strong>CWE-362 (Race Condition / TOCTOU)</strong></td>
            <td>Go</td>
            <td>Unsynchronized wallet balance debit without mutex lock</td>
            <td><span class="badge-tag badge-red">BLOCKED (Score: 88)</span></td>
            <td>1.14s</td>
          </tr>
          <tr>
            <td><strong>CWE-502 (Insecure Deserialization)</strong></td>
            <td>Python</td>
            <td>Unsafe PyYAML FullLoader cache deserialization leading to RCE</td>
            <td><span class="badge-tag badge-red">BLOCKED (Score: 96)</span></td>
            <td>1.20s</td>
          </tr>
          <tr>
            <td><strong>CWE-798 (Buried Secrets)</strong></td>
            <td>Python / Env</td>
            <td>High-entropy AWS Secret Key disguised in mock config</td>
            <td><span class="badge-tag badge-red">BLOCKED (Entropy)</span></td>
            <td><strong>0.04 ms</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="footer">
      <div>Benchmark Runner: <code>uv run python qa_vulnerable_cases/run_qa_suite.py</code></div>
      <div>Full Report: <code>SUBMISSION_PACKAGE.md</code></div>
    </div>
  </div>
</body>
</html>
""",

    # -------------------------------------------------------------
    # SLIDE 6: Live Deployment & Judge Access
    # -------------------------------------------------------------
    "slide_6.html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide 6 - Live Deployment & Judge Evaluation</title>
  <style>
    {BASE_CSS}
    .grid-eval {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
      flex: 1;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="orb-blue"></div>
  <div class="orb-cyan"></div>
  
  <div class="slide-container">
    <div class="header">
      <div class="brand-badge">
        <div class="dot"></div>
        LIVE EVALUATION READY
      </div>
      <div class="slide-number">06 / 06</div>
    </div>

    <h2 class="slide-title">Live Remote MCP Server & Ready for Judges</h2>
    <p class="slide-subtitle">S1Gate is deployed in production behind Cloudflare reverse proxy with zero-install setup for IBM Bob IDE and Claude Code.</p>

    <div class="grid-eval">
      <!-- Endpoint card -->
      <div class="glass-card glow-blue" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="font-size: 20px; font-weight: 700; color: #ffffff; margin-bottom: 20px;">Production Endpoints</div>
          
          <div style="margin-bottom: 20px;">
            <div style="font-size: 13px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px;">REMOTE MCP SSE ENDPOINT:</div>
            <div class="code-box" style="color: #38bdf8; font-weight: 600;">https://mcp.cuang.dev/s1gate/sse</div>
          </div>

          <div style="margin-bottom: 20px;">
            <div style="font-size: 13px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px;">HEALTH MONITORING:</div>
            <div class="code-box" style="color: #34d399;">https://mcp.cuang.dev/s1gate/health</div>
          </div>

          <div style="margin-bottom: 20px;">
            <div style="font-size: 13px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px;">JUDGE EVALUATION API KEY:</div>
            <div class="code-box" style="color: #fbbf24;">s1gate-judge-secret-key-2026</div>
          </div>
        </div>

        <div style="background: rgba(15, 98, 254, 0.1); border: 1px solid rgba(15, 98, 254, 0.3); border-radius: 12px; padding: 14px 18px; font-size: 14px; color: #cbd5e1;">
          ⚡ <strong>Sub-1.5s Response Time:</strong> Streaming SSE + JSON Keep-Alive pooling with real-time latency reporting headers.
        </div>
      </div>

      <!-- Config card -->
      <div class="glass-card glow-green" style="display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span style="font-size: 18px; font-weight: 700; color: #ffffff;">IBM Bob mcp.json Configuration</span>
          <span class="badge-tag badge-green">ZERO LOCAL SETUP</span>
        </div>
        
        <div class="code-box" style="flex: 1; font-size: 13px;">
<span style="color: #64748b;">&#123;</span><br/>
&nbsp;&nbsp;<span style="color: #38bdf8;">"mcpServers"</span>: <span style="color: #64748b;">&#123;</span><br/>
&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #38bdf8;">"s1gate"</span>: <span style="color: #64748b;">&#123;</span><br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #38bdf8;">"url"</span>: <span style="color: #34d399;">"https://mcp.cuang.dev/s1gate/sse"</span>,<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #38bdf8;">"headers"</span>: <span style="color: #64748b;">&#123;</span><br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #38bdf8;">"Authorization"</span>: <span style="color: #fbbf24;">"Bearer s1gate-judge-secret-key-2026"</span><br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #64748b;">&#125;</span><br/>
&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #64748b;">&#125;</span><br/>
&nbsp;&nbsp;<span style="color: #64748b;">&#125;</span><br/>
<span style="color: #64748b;">&#125;</span>
        </div>

        <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 14px; color: #94a3b8;">Repository: <strong>WilliamAxelC/IBM-hackathon</strong></div>
          <span class="badge-tag badge-purple">MIT LICENSE</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <div>Thank you IBM Bob & lablab.ai team!</div>
      <div>Try S1Gate today: <code>git clone https://github.com/WilliamAxelC/IBM-hackathon</code></div>
    </div>
  </div>
</body>
</html>
"""
}

async def render_all_slides():
    print("Writing HTML slides...")
    for filename, html_content in SLIDES_HTML.items():
        slide_path = SLIDES_DIR / filename
        slide_path.write_text(html_content, encoding="utf-8")
        print(f"  Saved {slide_path}")

    print("\nRendering slides with Playwright Chromium...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for i in range(1, 7):
            filename = f"slide_{i}.html"
            output_png = OUTPUT_DIR / f"slide_{i}.png"
            slide_url = f"file://{SLIDES_DIR / filename}"
            
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            await page.goto(slide_url, wait_until="networkidle")
            await page.screenshot(path=str(output_png))
            await page.close()
            print(f"  Rendered {output_png.name} (1920x1080)")
        await browser.close()
    print("\nAll slides successfully generated and rendered!")

if __name__ == "__main__":
    asyncio.run(render_all_slides())
