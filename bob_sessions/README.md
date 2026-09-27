# Bob Task Session Summaries (`bob_sessions/`)

> [!CAUTION]
> **MANDATORY SUBMISSION DELIVERABLE**: Every participant/team must upload their Bob IDE task session consumption summary screenshots to this `bob_sessions/` directory. Submissions lacking this folder and screenshots **will not be eligible for judging**.

---

## Overview

In the **IBM Bob 2.0 Hackathon**, the `bob_sessions` folder serves as the official, verifiable proof of IBM Bob IDE usage. 

As stated in the [Hackathon Guide](../docs/HACKATHON_GUIDE.md#upload-bob-task-session-summary) and the [Kickoff Announcement](../docs/KICKOFF_ANNOUNCEMENT.md):
> *"Every participant must upload their Bob IDE task session summary screenshots to a folder called `bob_sessions` in your final code repository. It's a required deliverable and it's your evidence of Bob usage... Do this as you go, not at 11 PM on Sunday!"*

---

## Step-by-Step Instructions: How to Capture Task Summaries

### Step 1: Open Tasks in Bob IDE
In your Bob IDE’s chat interface, click the **Tasks** icon to display the task list.

![Step 1: Tasks Tab](../docs/assets/images/fig20_tasks_tab.png)  
*Figure 20: Selecting Tasks in Bob IDE chat interface*

---

### Step 2: Select the Relevant Project Task & Workspace
Select a task from the list that is relevant to your project submission. The selected task will open in the chat panel.  
- Confirm that you are in the correct project workspace.
- If your submission involves tasks from multiple workspaces, select **All** to view tasks across all relevant workspaces.

![Step 2: Workspace Filter](../docs/assets/images/fig21_workspace_all.png)  
*Figure 21: Workspace filter set to All*

---

### Step 3: Open the Task Session Consumption Summary
Click on the **task header** at the very top of the chat panel. A detailed **task session consumption summary** dropdown will be displayed showing tokens, model usage, tool executions, and Bobcoin consumption.

![Step 3: Task Header](../docs/assets/images/fig22_task_header.png)  
*Figure 22: Clicking the task header to display consumption summary*

---

### Step 4: Capture & Save PNG Screenshot
1. Take a screenshot of the entire task session consumption summary modal.
2. Save the file in **PNG format** for optimal legibility.
3. Save directly into this folder: `bob_sessions/`.

![Step 4: Consumption Summary Screenshot](../docs/assets/images/fig23_consumption_summary_screenshot.png)  
*Figure 23: Example task session consumption summary screenshot*

---

## 🏷️ File Naming Convention

All screenshots in this folder must adhere to the standardized naming structure:

```
<team_name>_task<XX>_<short_task_description>_summary.png
```

### Examples:
- `teamalpha_task01_repo_scaffolding_summary.png`
- `teamalpha_task02_login_flow_summary.png`
- `teamalpha_task03_api_endpoints_summary.png`
- `teamalpha_task04_unit_tests_summary.png`
- `teamalpha_task05_deployment_ci_summary.png`

---

## 📋 Task Session Log Tracker

Use the table below to track all recorded sessions as your team completes development tasks:

| Task # | File Name | Workspace | Description / Feature | Captured By | Bobcoins / Consumption | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| 01 | `s1gate_task01_architecture_audit.png` | IBM-hackathon | Architecture & Security Audit of S1Gate | WilliamAxelC | 156.8k tokens / 14.69 Bobcoins | ✅ Verified |
| 02 | `s1gate_task02_implementation_subtasks.png` | IBM-hackathon | Benchmark validation (72/72 passed) & Sub-tasks execution | WilliamAxelC | Agent Mode execution | ✅ Verified |
| 03 | `s1gate_task03_consumption_summary_modal.png` | IBM-hackathon | **Task Consumption Summary Modal** (Task Id `38a62e...`, Region: `us-east`) | WilliamAxelC | 123.8k tokens / 13.02 Bobcoins | ✅ Verified |
| 04 | `s1gate_task03_budget_remaining_summary.png` | IBM-hackathon | 40 Bobcoins Allocation & Budget remaining (28.34 / 40.00) | WilliamAxelC | Budget Tracker | ✅ Verified |
| 05 | `s1gate_task03_bob_ide_workspace_view.png` | IBM-hackathon | Bob IDE full workspace, 9/9 sub-tasks & git push | WilliamAxelC | 123.8k tokens / 13.02 Bobcoins | ✅ Verified |
| 06 | `s1gate_task03_all_tasks_completed.png` | IBM-hackathon | Completion status view (14 files changed, branch push) | WilliamAxelC | Workflow verification | ✅ Verified |
| 07 | `s1gate_agent_orchestration_menu.png` | IBM-hackathon | Multi-agent orchestration menu (Bob, Bob Shell) | WilliamAxelC | UI inspection | ✅ Verified |
| 08 | `s1gate_benchmark_metrics_graph.png` | IBM-hackathon | S1Gate vs. Naive Baseline: Latency, Accuracy, Confusion Matrix | WilliamAxelC | 20-diff Benchmark Suite | ✅ Verified |
| 09 | `s1gate_error_matrix.png` | IBM-hackathon | **Error Matrix (TP/FP/TN/FN)**: Type I False Alarm vs Type II Breach Escapes | WilliamAxelC | 20 Hard Diffs Challenge | ✅ Verified |

---

## ⚠️ Final Submission Checklist
Before submitting the project repository URL:
- [ ] Ensure `bob_sessions/` contains valid PNG screenshots for **every task** showcased in the submission.
- [ ] Verify that screenshots clearly show task consumption metrics and task headers.
- [ ] Confirm filenames match the `<team_name>_task<XX>_<description>_summary.png` standard.
- [ ] Check that `bob_sessions/` is committed and pushed to remote `main` branch.
