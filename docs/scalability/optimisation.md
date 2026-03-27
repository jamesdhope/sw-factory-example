# The Optimized Granularity Model (OGM)

![Software Factory Optimization Space](/Users/jamesdhope/.gemini/antigravity/brain/0447f5fa-79c2-4fcc-9ba5-e2d855ddbf7f/software_factory_optimization_graph_1774601963264.png)

## 📊 Decoding the Optimization Space

Each line in the graph above represents a critical force acting on your factory's bottom line:

### **📈 Bootstrap Tax (Blue Line)**
- **Behavior**: Linear (N * B).
- **Logic**: Every time you add a worker, you pay a fixed "entry tax" for system prompts and context loading. If you have 50 workers, you pay this 50 times.

### **📉 Risk Penalty (Red Curve)**
- **Behavior**: Exponential Decay.
- **Logic**: This is the "hidden cost" of complexity. When tasks are few (N is small), they are massive and hard for the AI to get right. As you split tasks (N increases), they become simpler, and the likelihood of needing a costly "Retry" drops toward zero.

### **🏗️ Overhead (Orange Line)**
- **Behavior**: Constant (S + P + I).
- **Logic**: The cost of generating the Spec, Planning the tasks, and the Final Merge. This stays mostly flat regardless of how many workers you use.

### **✅ Total Cost (Green Curve)**
- **Behavior**: U-Shaped (The Parabola of Profit).
- **Logic**: This is the sum of all forces. At the far left, you fail too often (High Risk). At the far right, you spend too much on startup tax (High Overhead). The **Sweet Spot** is the bottom of this curve.

## 🧩 The Variables

| Symbol | Concept | Value Range | Impact |
| :--- | :--- | :--- | :--- |
| **B** | **Bootstrap Tax** | ~3,100 | Fixed cost per worker. Favors **low N**. |
| **W** | **Work Unit** | 1k - 15k | Useful output tokens. Favors **high N**. |
| **P** | **Prob. Success** | 0.4 - 0.99 | Likelihood of non-failure. Favors **high N**. |
| **C** | **Context Load** | 5k - 30k | Amount of data loaded. Favors **low N**. |

## 📐 The Universal Balancing Act

The factory reaches peak efficiency where **Marginal Bootstrapping Cost** equals **Marginal Failure Savings**.

### **1. The Decay of Success (P)**
As your Work Unit (W) and Context (C) increase, your Success Probability (P) decays. 
- For W < 5k: P is approx 0.98
- For W > 15k: P is approx 0.40 (The agent starts making structural errors).

### **2. The Expected Project Cost (E)**
The total "real" cost of your project is:

**Expected Cost = Overhead + Sum of [ (Instance Tax + Work) / Prob. Success ]**

## 🏁 The Optimal Strategy

To maximize ROI, the **Orchestrator** must generate a `tasks.json` that satisfies these constraints:

1. **Avoid the "Management Sink"**: (Number of Tasks * Bootstrap Tax) should not exceed 50% of Total Tokens.
2. **The 10k Rule**: Keep W_i + C_i < 20,000 tokens. This keeps P in the high 90s.
3. **The Delta Threshold**: If adding one more task (N+1) increases the total project tokens by less than the cost of a likely failure in a larger task, do the split.

### **The Gold Standard Calculation**
For a 50,000 token code-base:
- **Standard (7 workers)**: Estimated Prob. Success = 0.95 -> Total: **~65k tokens**.
- **Aggressive (2 workers)**: Estimated Prob. Success = 0.50 -> Total: **~110k tokens** (due to multiple retries).
- **Over-Granular (20 workers)**: Estimated Prob. Success = 0.99 -> Total: **~105k tokens** (due to 60k in bootstrapping tax).

> [!TIP]
> **The Takeaway**: Complexity is the enemy of economics. The factory's job is to "shred" complexity into small, high-probability chunks (P approx 1) while minimizing the number of times it has to pay the "Goose-OS Entry Tax."
