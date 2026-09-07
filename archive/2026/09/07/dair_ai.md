# 🐦 @dair_ai

## 📅 September 07, 2026

> 2 post(s) archived.

---

### 🕐 08:00 UTC · @dair_ai

> // Evaluating and Improving LLM Self-Modeling // Really interesting paper. Can a model answer questions about its own behavior? The questions are deliberately verifiable, such as whether a particular prompt edit would change the model&apos;s final answer. This framing avoids the usual trap where introspection claims cannot be checked by anyone. Current models show real but limited skill on a new benchmark covering diverse self-modeling question types, and they make consistent errors on simple counterfactuals about themselves. A scalable synthetic-data pipeline plus reinforcement learning raises the aggregate score across three open-source model families, with some transfer to held-out tasks. The authors then decline the interpretation their own result invites. They note the gains may not come from privileged access to the model&apos;s internal decision process, so a better self-modeling score is not evidence of introspection. Useful if you want agents that predict their own failures well enough to route or escalate, since that capability can now be measured without settling what produces it. Paper: https://academy.dair.ai/papers/evaluating-and-improving-llm-self-modeling-2608.30980

![// Evaluating and Improving LLM Self-Modeling // Really interesting paper. Can a model answer questions about its own behavior? The questions are deliberately verifiable, such as whether a particular ](../../../../assets/images/2026/09/07/2096871139184451647-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2096871139184451647)

---

### 🕐 02:08 UTC · @dair_ai

> Fascinating paper from Anthropic and colleagues. They study whether models can tell when they are being tested. It turns out that capable models can tell when they are being tested rather than deployed. They claim that this fact weakens every conclusion a safety evaluation supports, and it gets worse as models get better. Two techniques make simulated evaluations harder to distinguish from real deployment. Critique refinement spends extra inference-time compute on each simulator action, generating several candidates, asking an instance of the target model how to make them more realistic, and continuing with the most deployment-like one. DISH, the Deployment-Imitating SWE-Agent Harness, wraps the target in a real agent harness so the simulated coding environment matches production. Why does it matter? Your harness is a signal the model reads. If evaluations run in a different scaffold than production, the model can condition on that difference, which makes scaffold parity a safety property rather than an engineering detail. Paper: https://academy.dair.ai/papers/improving-evaluation-realism-with-inference-time-compute-and-deployment-scaffold-2609.02302

![Fascinating paper from Anthropic and colleagues. They study whether models can tell when they are being tested. It turns out that capable models can tell when they are being tested rather than deploye](../../../../assets/images/2026/09/07/2096782512119001119-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2096782512119001119)

---
