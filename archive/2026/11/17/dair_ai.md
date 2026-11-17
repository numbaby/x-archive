# 🐦 @dair_ai

## 📅 November 17, 2026

> 2 post(s) archived.

---

### 🕐 14:50 UTC · @dair_ai

> Great practical paper from Google on building efficient agent skills. For cheaper agents, learn a skill for accuracy first, then prune it for length. This has also worked well in our own experiments. Skill optimizers usually add a new rule after every failure. The skill grows, the agent reads more tokens every turn, and long loops start to time out. EfficientSkill runs two phases. The first repairs failures with no length penalty until the skill reaches a target accuracy. The second prunes instructions and moves reusable code into workspace utilities, while accuracy has to stay close to that target. Pruning from the empty seed stalls, so the order matters. Across four models on MATH-500, ALFWorld, and SpreadsheetBench, output tokens fall on 11 of 12 configurations, up to 80% of the time. Accuracy also rises on every benchmark, including +14.3 points with Gemini 3.8 Flash and +17.5 points with Grok 4.1 Fast on SpreadsheetBench. Serving cost drops 25% to 67%. https://arxiv.org/abs/2611.19823 Chat with Paper: https://academy.dair.ai/papers/efficientskill-learning-skills-for-token-efficient-multi-turn-agents-2611.19823

![Great practical paper from Google on building efficient agent skills. For cheaper agents, learn a skill for accuracy first, then prune it for length. This has also worked well in our own experiments. ](../../../../assets/images/2026/11/17/2122703815992602992-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2122703815992602992)

---

### 🕐 14:39 UTC · @dair_ai

> Banger paper from Google on RSI. (bookmark it) They propose an approach for continual recursive self-improvement at the harness level. They also propose their own self-improving memory system for the harness optimizer. This clearly highlights the importance of traces and having a functional, adaptive, and structured persistent memory system in your harness. They show that a harness optimizer improves 9 of 10 continued runs when it remembers why it made each past edit. They discuss that a common problem shows up when you change the model or the benchmark. An Opus-evolved harness started at 68.41 on Gemini, below the 73.89 of the plain seed harness. Self-Improvement Memory groups past edits by the harness problem they addressed. For each edit, it stores the rationale, predicted outcome, observed outcome, and evaluation context. The proposer and the selector both read it before making new changes. Across four domains, including Terminal-Bench 2.1 to Terminal-Bench 4, SIM beats continuing from the harness alone in six cross-dataset and four Opus-to-Gemini settings. Across ten coding runs, it adds 2.36 points on average (p=0.003). If you evolve harnesses automatically, store the reasons and results of each edit next to the code. https://arxiv.org/abs/2611.18856 Chat with Paper: https://academy.dair.ai/papers/self-improvement-memory-enables-continual-recursive-self-improvement-2611.18856

![Banger paper from Google on RSI. (bookmark it) They propose an approach for continual recursive self-improvement at the harness level. They also propose their own self-improving memory system for the ](../../../../assets/images/2026/11/17/2122701047118635485-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2122701047118635485)

---
