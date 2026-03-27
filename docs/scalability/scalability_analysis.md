# Software Factory: Token Estimation & Scalability Analysis

This report provides a data-driven heuristic for projecting token consumption as you scale the Goose-OS Software Factory.

## 📊 Real-World Baseline (Turing Machine v2)
Based on our verified 7-task build:
- **Total Consumption**: 57,568 tokens
- **Average per Functional Task**: 3,322 tokens
- **Orchestration Overhead**: ~34,000 tokens (Spec, Planning, Integration)

## 🧮 The Scalability Formula

To project the total cost for any build, use this model:


To avoid rendering issues, here is the plain-text formula for any project:

### **T = (S + P + I) + N × (B + W + D)**

| Letter | Component | Est. Value | Definition |
| :--- | :--- | :--- | :--- |
| **T** | **Total Tokens** | | Total cost of the project lifecycle. |
| **S** | **Specification** | ~12,000 | Custom spec generation from your prompt. |
| **P** | **Planning** | ~8,000 | Decomposing the spec into `tasks.json`. |
| **I** | **Integration (Base)**| ~15,000 | The base cost to start the final merge. |
| **N** | **Number of Tasks** | [1 to 50+] | Count of tasks in the project. |
| **B** | **Bootstrap Tax** | ~3,100 | The startup "tax" for every agent spawned. |
| **W** | **Work per Task** | ~5,000 | Actual generation (Code/Content). |
| **D** | **Integration Delta**| ~500 | Extra analysis tokens per task at merge time. |

---

---

### **Why I depends on N**
As you correctly identified, the Integration Agent (**I**) has to do more heavy lifting as **N** grows:
- **Linear Reading**: It must read the `git log` and diffs for **N** separate branches.
- **Context Swelling**: The "Working Set" of files it must analyze to resolve conflicts grows as more modules are added.
- **Merge Matrix**: In the worst-case, conflict resolution complexity scales with the interaction between modules.

---

## 🧾 The 'Goose-OS Bootstrapping Tax'
Each time the factory spawns a new `goose` session, there is a "startup cost" regardless of task complexity. This covers the initial context window loading:

| Component | Est. Tokens | Purpose |
| :--- | :--- | :--- |
| **System Prompt** | 1,500 - 2,000 | Core instructions, tool definitions, and persona. |
| **Env Context** | 500 - 1,000 | Current directory structure (`ls-R`) and git state. |
| **Initial Task** | 500 - 1,000 | The specific task instructions and high-level goal. |
| **Total Start Cost** | **~2,500 - 4,000** | **Base cost for a single-turn `goose` run.** |

> [!TIP]
> **Efficiency Gain**: For very small tasks (under 10 lines of code), the bootstrapping tax can account for >90% of the total cost. To maximize value, group related sub-tasks into a single worker session to pay the "tax" only once.

## 🚀 Scaling Projections

| Project Size | Tasks | Estimated Tokens | Est. Cost (GPT-4o) |
| :--- | :--- | :--- | :--- |
| **Small Utility** | 3 | 30k - 40k | < $0.50 |
| **Standard Module** | 7 | 55k - 70k | ~$0.75 |
| **Complex App** | 15 | 120k - 150k | ~$1.50 |
| **Enterprise Suite**| 50 | 400k - 500k | ~$5.00 |

## ⚖️ The Inflection Point: Finding the "Sweet Spot"

The mission of any factory run is to balance **Granularity** (tasks per worker) with **Efficiency** (tokens per project).

### **The "Too Small" Trap (N < 3)**
- **Risk**: Each task is too large. The worker must hold 5,000+ lines of code in its active memory.
- **Consequence**: High failure rate, missing requirements, and "hallucinated" code as the context window fills up.

### **The "Too Many" Trap (N > 12)**
- **Risk**: You pay the **Bootstrap Tax (B)** too many times.
- **Consequence**: The combined cost of starting 15 agents and having the Integrator (**I**) analyze 15 branches creates a massive token spike without a proportional increase in code quality.

### **The Optimal Inflection Point: N = 5 to 10**
Data suggests the "Sweet Spot" for `goose-os` is **5-10 workers**. 
- **Why?**: This range keeps the **Work Tokens (W)** per agent below the 10k threshold (ideal for logic retention) while keeping the **Integration Delta (D)** manageable for the final merge agent.

## 🎯 The Optimization KPI: Functional Token Efficiency (FTE)

To measure and optimize your factory's performance, use the **FTE** metric:

### **FTE = (Sum of Work Tokens) / Total Tokens**

*Where Work Tokens are the useful output and Total Tokens is the entire lifecycle cost.*

### **Target Goal: FTE > 0.60 (60%)**
- **Low Efficiency (< 40%)**: You are over-granulated. You are paying too much "Bootstrap Tax" (B) for too little output. **Fix**: Consolidate tasks.
- **High Efficiency (> 75%)**: You are under-granulated. Your tasks are likely too large, increasing the risk of "Context Drift" or agent errors. **Fix**: Split tasks.
- **The "Sweet Spot" (50% - 70%)**: This indicates a healthy balance where the agent has enough context to be smart, but not enough to be overwhelmed.

### **How to use FTE as a Quality Gate:**
1.  **Audit `status.json`**: After every build, check the ratio of `task tokens` to `total tokens`.
2.  **Adjust `tasks.json` Generator**: If FTE is consistently low, prompt the **Planning Agent** to be more aggressive in grouping small refactors into single tasks.
