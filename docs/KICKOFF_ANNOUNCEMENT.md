# IBM Bob 2.0 Hackathon: Kickoff Announcement & Critical Rules

> **Source**: Official lablab.ai Kickoff Announcement to Hackathon Builders  
> **Original Guide URL**: [IBM Bob 2.0 Hackathon Guide](https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/index.html#a-note-on-using-other-technologies)  
> **Local Guide**: [HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)

---

## Executive Summary & Urgent Deadlines

- **Registration Closes**: Thursday, September 24 · 10:00 PM CEST / 4:00 PM ET (No new participants after this window).
- **Duration**: 48 Hours.
- **Total Prize Pool**: **$12,000**
  - 🥇 1st Place: **$5,000**
  - 🥈 2nd Place: **$3,000**
  - 🥉 3rd Place: **$2,000**
  - 🎁 Participant Rewards: **20 × $100** (awarded for submitting a qualified project + completing post-hackathon feedback).

---

## ⚠️ 3 Requirements That Decide Judging Eligibility

If your submission fails any of these three requirements, **it will not be judged**:

### 1️⃣ Bob IDE is Required (Not Optional)
- You may use any framework, runtime, or technology you like (see [A note on using other technologies](HACKATHON_GUIDE.md#a-note-on-using-other-technologies)).
- However, your solution **must showcase IBM Bob IDE as a core component**.
- **Bob Shell** is available as a command-line tool, but it is **optional**. Bob IDE is mandatory.

### 2️⃣ The `bob_sessions` Folder (The #1 Disqualification Risk)
- Every participant must upload their **Bob IDE task session summary screenshots** to a folder called `bob_sessions/` in the final code repository.
- This folder is your **verifiable evidence of Bob usage**.
- **How to capture screenshots**:
  1. In Bob IDE's chat interface, click **Tasks** to open the task list.
  2. Select a task related to your project submission.
  3. Ensure the workspace filter is set to **All** if using multiple workspaces.
  4. Click the **task header** to display the session consumption summary.
  5. Take a PNG screenshot with clear text.
  6. Name the file clearly: `<team_name>_task<XX>_<description>_summary.png`  
     *Example*: `teamalpha_task01_login_flow_summary.png`
  7. Repeat for every task related to your submission.
  8. Save screenshots directly inside `bob_sessions/`.
> [!CAUTION]
> **Capture screenshots as you build!** Do not wait until 11 PM on Sunday before submission.

### 3️⃣ Bring Your Own Data — Keep It Clean & Compliant
- You must supply your own datasets aligning with your project scope.
- **Strict Compliance Rules**:
  - ❌ **No client data**.
  - ❌ **No company confidential data** (or any data without written owner consent).
  - ❌ **No personal information (PI / PII)**.
  - ❌ **No data scraped/obtained from social media**.
  - ✅ **Public web data is allowed** ONLY IF the site terms explicitly permit commercial use. Keep an audit list of all source URLs and licenses used.

---

## 🪙 Bobcoins Budgeting: 40 Coins Allocation

- Every AI prompt, plan, or task execution burns **Bobcoins**.
- Each hackathon account is credited with exactly **40 Bobcoins**.
- **When you hit 100% usage, no additional Bobcoins are provided.**
- **Strategy & Best Practices**:
  - Distribute tasks across all teammates so your team leverages multiple accounts rather than exhausting one person's 40 coins.
  - Track usage under **Settings → General** in Bob IDE, or via the [Admin Dashboard](https://bob.ibm.com/admin/subscription).
  - Keep prompts clear, concise, and focused to minimize token and coin burn.
  - **Fallback**: If Bobcoins run dry, optional **IBM watsonx** tools (watsonx Orchestrate, watsonx.ai Prompt Lab with Granite models) remain available.

---

## ✅ Pre-Kickoff Checklist (15 Minutes)

1. **Create an IBMid**:
   - Required to authenticate into Bob IDE.
   - Must use the **exact email address** used for hackathon registration.
   - Link: [IBM Account Registration](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776).
2. **Install & Verify Bob IDE Version**:
   - Check installed version: `v1.0.3` and `v2.0.0` stop working on **September 30, 2026**.
   - If on `v1.0.3` → upgrade to latest `v2.0.x`.
   - If on `v2.0.0` → upgrade to `v2.0.2` or later.
   - Install instructions: [Bob IDE Install Docs](https://bob.ibm.com/docs/ide/getting-started/install).
3. **Read the Full Hackathon Guide**:
   - Review [HACKATHON_GUIDE.md](HACKATHON_GUIDE.md) covering setup, modes, subagents, rules, MCP tools, and hands-on exercises.

---

## 📧 Kickoff Day Inbox Action

- At kickoff, look for an invitation email from the IBM Bob team stating:
  `You have been added as a team member to ibm-hackathon-xxxx`
- Check spam/junk folders; search query: `"IBM Bob"`.
- ⚠️ **Switch Account in Bob IDE**:
  If you have an existing personal Bob account, navigate to **Settings → General** and ensure the active team instance is set to:
  `ibm-coding-challenge-uat` (region: `us-east`).
  *Failing to do this will burn personal Bobcoins instead of hackathon-provided coins.*
- *(Note: The "team member" label in the email invite is standard enterprise account terminology and does not dictate hackathon team grouping).*

---

## 🎯 What to Build: The Core Brief & Example Tracks

### The Brief
Create a working prototype that measurably improves a specific **developer workflow** where friction, time, cognitive effort, or defect rates are high:
- **Onboarding**
- **Debugging & Root Cause Analysis**
- **Code Review & Quality Assurance**
- **Automated Testing & Coverage**
- **Application Maintenance & Upgrades**
- **Release Readiness & Deployment**

### Strong Submission Differentiators
Avoid standard autocomplete or simple chatbot solutions. Winning projects leverage:
- **Agent Mode**: Autonomous planning and multi-file code modifications.
- **Subagents**: Isolated context execution for specialized tasks.
- **Parallel Tasks**: Running concurrent development workloads.
- **Document & Context Understanding**: Analyzing repositories, architectural diagrams, and system specs.
- **Measurable Impact**: Quantify time saved, errors prevented, or hours transformed into minutes.

### 5 Guide Example Use Cases
1. 🧭 **Smart Developer Onboarding Assistant**: Analyze unfamiliar repositories, explain architecture, generate setup scripts, and suggest starter issues.
2. 🔍 **Intelligent Code Review Coach**: Spot security and architectural risks, provide contextual fixes, and generate automated review summaries.
3. 🧪 **Automated Testing Hub**: Generate unit/integration tests, detect coverage gaps, and validate code diffs.
4. 🚀 **Release Readiness Assistant**: Analyze dependency updates, summarize regression risks, generate release notes, and check deploy prerequisites.
5. 🏗 **Legacy Modernization Accelerator**: Dissect legacy codebases (e.g. Node 16 -> 22, Java, APIs), suggest modernization paths, and execute refactorings.

---

## 📜 Full Verbatim Kickoff Message (Reference)

```text
Hey builder,

Kickoff is tomorrow. 

The full IBM Bob 2.0 Hackathon Guide is now live, along with the deliverables. It's worth twenty minutes of your evening - there are a few requirements in there that decide whether your project gets judged at all.

Here's what matters most tonight 👇
⏰ FIRST: REGISTRATION CLOSES TONIGHT
Thursday, September 24 · 10:00 PM CEST / 4:00 PM ET

After that, no new participants can enroll or be approved. If a teammate still hasn't registered, this is the moment.

⚠️ THREE THINGS THAT DECIDE ELIGIBILITY
1️⃣ Bob IDE is required - not optional
You can use any framework or technology you like, but to be eligible for judging, your solution must showcase IBM Bob IDE as a core component. Bob Shell is available too, but it's optional.
2️⃣ The bob_sessions folder - this is the one people miss 📸
Every participant must upload their Bob IDE task session summary screenshots to a folder called bob_sessions in your final code repository. It's a required deliverable and it's your evidence of Bob usage.
How: in Bob IDE's chat, open Tasks, select a task, click the task header to see the session consumption summary, and screenshot it. PNG format, named clearly - e.g. teamalpha_task01_login_flow_summary.png. Repeat for every task related to your submission.
Do this as you go, not at 11 PM on Sunday! 
3️⃣ Bring your own data - and keep it clean
You'll need your own datasets. The rules matter: no client data, no company confidential data, no personal information, nothing from social media. Public web data is fine if the terms allow commercial use - keep a list of the sites you use. You're responsible for compliance.
🪙 BOBCOINS: YOU GET 40. THAT'S IT.
Every interaction with Bob's AI capabilities burns Bobcoins, and your hackathon account comes with 40. When you hit 100%, no more are provided - you can keep building, but not with Bob.
So plan it: divide tasks across your teammates so you're using the whole team's allocation, not one person's. Monitor usage in Bob IDE under Settings → General, or in the admin dashboard.
💡 And if you run dry, the optional watsonx tools are still open to you.

✅ DO THIS TONIGHT (15 MINUTES)
1) Create your IBMid - required to sign into Bob, and you don't want to be doing this at kickoff. Use the same email you registered with.
2) Install Bob IDE - and check your version. v1.0.3 and v2.0.0 stop working on September 30. On v1.0.3, upgrade to the latest v2.0.x. On v2.0.0, upgrade to v2.0.2 or later.
3) Read the Guide - setup, best practices, features, and hands-on exercises to warm up on.

📧 TOMORROW: WATCH YOUR INBOX
At the start of the hackathon you'll get an email invite to join the hackathon-provisioned Bob account. Look for one that says you've been added to ibm-hackathon-xxxx.
Check your spam folder - search "IBM Bob" if you can't find it.
⚠️ If you already use Bob personally: make sure you switch to the hackathon account (ibm-coding-challenge-uat, region us-east) in Settings. Otherwise you'll burn through your own Bobcoins instead of the free ones. 💸
(And that "team member" wording in the invite is just how the enterprise account works - it doesn't mean you've been put in a hackathon team.)

🎯 STILL DECIDING WHAT TO BUILD?
The brief: improve a specific developer workflow where time, effort or errors are too high today - onboarding, debugging, code review, testing, maintenance, release and deployment.
The guide's own examples, if you need a starting point:
🧭 Smart developer onboarding assistant - analyse a repo, explain its architecture, generate setup guidance, suggest starter tasks
🔍 Intelligent code review coach - spot risks, explain findings, recommend fixes, summarise reviews
🧪 Automated testing hub - generate unit tests, find coverage gaps, validate changes
🚀 Release readiness assistant - review dependencies, summarise risks, generate release notes
🏗 Legacy modernization accelerator - explain old code, find modernization opportunities, cut migration effort
Go beyond autocomplete: Agent mode, parallel tasks, subagents and document understanding are where the strong submissions live. Show measurable impact - less manual effort, fewer errors, hours turned into minutes.

💰 $12,000 IN PRIZES
🥇 $5,000 · 🥈 $3,000 · 🥉 $2,000
🎁 Plus Participant Rewards: 20 × $100. Twenty participants each receive $100 for doing two things - submitting a qualified project and completing the post-hackathon feedback form.

You don't have to place to get paid. 
48 hours goes fast. Get set up tonight so tomorrow is all building. 
Have questions? Ask them on our Discord Server!

Best of luck,
The lablab Team
```
