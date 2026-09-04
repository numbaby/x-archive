# 🐦 @dair_ai

## 📅 September 04, 2026

> 1 post(s) archived.

---

### 🕐 02:00 UTC · @dair_ai

> Great tips on working with reasoning models. Normally you would append what the model figured out after the document and ask again. It turns out that where you put the reasoning trace changes long-context accuracy by 50 points. Transformers process causally, so a task state discovered late cannot guide the reading that already happened. For causal state update processors, providing the condition first can require exponentially less memory in the worst case than providing it last. Trace as State puts the collected reasoning trace before the long-context block on a fresh pass, so information derived earlier guides the rereading. The matched control, Trace Append, uses the identical trace after the context. On GraphWalks Parents, DeepSeek V4 Pro Preview goes from 29.2% on the initial pass and 43.0% with Trace Append to 81.8% with Trace as State. GLM-5.2 goes from 66.4% and 83.2% to 100.0%. Trace as State wins in 26 of 27 reported combinations of model, task and metric, with no architecture change required. Paper: https://arxiv.org/abs/2609.02702 Chat with Paper: https://academy.dair.ai/papers/trace-as-state-reasoning-traces-as-conditional-states-for-long-context-transform-2609.02702

![Great tips on working with reasoning models. Normally you would append what the model figured out after the document and ask again. It turns out that where you put the reasoning trace changes long-con](../../../../assets/images/2026/09/04/2095693344689238465-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2095693344689238465)

---
