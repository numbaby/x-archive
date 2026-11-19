# 🐦 @dair_ai

## 📅 November 19, 2026

> 4 post(s) archived.

---

### 🕐 20:45 UTC · @dair_ai

> Great paper from MIT and NVIDIA. I think this is an important step toward personalized, accessible RSI. The best recipe changes with every model and precision, so experts usually redesign it by hand. QDA hands that loop to an agent that builds and tests candidates over many rounds. They show that QDA beats the strongest public recipes by 0.9, 1.4 and 2.2 points at W4A16, W4A8 and W3A16, using 64 GPU-hours per search. Evaluation speed is what makes this work. Scoring one quantized reasoning model normally takes tens of GPU-hours. QDA scores each candidate in minutes by measuring its output KL divergence from the original model on reasoning traces the agent never sees. Promising candidates then get long generations to catch repetition loops. A shared library of public PTQ methods lets the agent combine them without porting each codebase by hand. On the 320B MoE GLM-5.3-Flash at NVFP4 W4A4, QDA recovered 98.3% of FP8 accuracy, against 96.9% for the best vendor checkpoint. Every checkpoint runs on existing serving kernels with no inference overhead. https://arxiv.org/abs/2611.23388 Chat with Paper: https://academy.dair.ai/papers/qda-closed-loop-llm-quantization-design-with-agents-2611.23388

![Great paper from MIT and NVIDIA. I think this is an important step toward personalized, accessible RSI. The best recipe changes with every model and precision, so experts usually redesign it by hand. ](../../../../assets/images/2026/11/19/2123517934974955558-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2123517934974955558)

---

### 🕐 20:20 UTC · @dair_ai

> Self-improving agents are one of the most discussed ideas in AI right now. (bookmark it) This update gate for a personal health assistant rejected 20 of 21 risky self-proposed updates. Researchers built Safe Personal RSI for the Kicker assistant. The agent can only change its own instructions. Model weights and runtime code stay fixed. Each proposed update is tested against the current instructions on 29 executable email, calendar, health, and marketplace cases. Separate probes test authorization reuse, memory, and tool-output injection. Failing cases are repeated, and changes are temporarily undone to find which edit caused the failure. If no version passes, the current instructions stay. One admitted repair for GPT-5.6 Luna cut attack violations from 10.7% to 0% and raised safe task completion from 89.7% to 100%. Under stronger attacks, a repair moved from Qwen2.5-7B to Qwen3-14B, cutting violations from 69.0% to 17.9%. https://arxiv.org/abs/2611.23651 Chat with Paper: https://academy.dair.ai/papers/safe-personal-rsi-evaluating-and-repairing-personal-agent-updates-2611.23651

![Self-improving agents are one of the most discussed ideas in AI right now. (bookmark it) This update gate for a personal health assistant rejected 20 of 21 risky self-proposed updates. Researchers bui](../../../../assets/images/2026/11/19/2123511637584036078-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2123511637584036078)

---

### 🕐 14:31 UTC · @dair_ai

> Great paper from Meta on ML engineering agents, tested with a large-scale A/B test on production search rankers. (bookmark it) They also show how important the harness design is. The agents propose a model change, implement it, train it, and evaluate it. Engineers keep control of the objective, the search direction, and the final review. In one campaign, the system completed 1,097 experiments and accepted 325 of them. That is a 29.6% acceptance rate, against 15.6% in an earlier campaign with a different objective. The best model raised search volume by 0.23% in the live test. They share that three problems made this hard. Each experiment takes hours, offline metrics often disagree with online impact, and gains flatten after the early wins. The team answered with parallel training runs, an objective calibrated to online impact, and careful context engineering. Several accepted changes were architectures the team had never tried. The authors also report that a stronger model was not enough on its own. The loop around it mattered just as much. If you plan to put agents on your training pipeline, calibrate the objective first. https://arxiv.org/abs/2611.23910 Chat with Paper: https://academy.dair.ai/papers/mle-agents-autonomous-ml-engineering-in-large-scale-recommendation-systems-2611.23910

![Great paper from Meta on ML engineering agents, tested with a large-scale A/B test on production search rankers. (bookmark it) They also show how important the harness design is. The agents propose a ](../../../../assets/images/2026/11/19/2123423809839698400-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2123423809839698400)

---

### 🕐 14:18 UTC · @dair_ai

> Banger paper from Google on self-improving agent harnesses. (bookmark it) It addresses common issues in self-improving agent harnesses like local overfitting, catastrophic forgetting, and memory pollution. They propose GUARD, which keeps the base model frozen and lets the agent edit its own prompts, skills, tool rules, and memory. An edit is accepted only when its gains outweigh the behaviors it breaks. - On 43 hosted SDK tasks, GUARD reached 80.80% accuracy, 8.89 points over the starting harness (p = 0.008). - It beat Meta-Harness by 6.28 points and used 54.5% fewer tokens per task. - On procedural memory tasks, it led update correctness at 90.1% with zero memory pollution. Aggressive rewriters scored similarly and tripled pollution. How does it know what broke? Each task is split into self-checks before execution. Every round grades trajectories against them, pins rules the agent already handles, and ranks newly broken behaviors first. At test time, one frozen harness runs in a single pass. https://arxiv.org/abs/2611.23476 Chat with Paper: https://academy.dair.ai/papers/guard-stabilizing-recursive-self-improvement-with-regret-guidance-2611.23476

![Banger paper from Google on self-improving agent harnesses. (bookmark it) It addresses common issues in self-improving agent harnesses like local overfitting, catastrophic forgetting, and memory pollu](../../../../assets/images/2026/11/19/2123420538030957015-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2123420538030957015)

---
