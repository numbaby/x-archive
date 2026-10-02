# 🐦 @dair_ai

## 📅 October 02, 2026

> 2 post(s) archived.

---

### 🕐 07:00 UTC · @dair_ai

> New paper from Microsoft on compressing agent context at test time. If your agent gets worse as its interaction history grows, this method is worth a look. FOCUS asks which past interactions the agent&apos;s next decisions actually depend on. It keeps those units of the history and drops the others. It needs no training data or fine-tuning, so it works as a separate layer in front of closed-API models. On tool-calling, QA, web and multi-turn dialogue benchmarks, it cuts peak context by up to 48% and raises task success by up to 8.9 points compared with running on the full history. Paper: https://academy.dair.ai/papers/focus-training-free-decision-preserving-context-compression-for-llm-agents-2609.37590

![New paper from Microsoft on compressing agent context at test time. If your agent gets worse as its interaction history grows, this method is worth a look. FOCUS asks which past interactions the agent](../../../../assets/images/2026/10/02/2105915729812050342-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2105915729812050342)

---

### 🕐 01:30 UTC · @dair_ai

> Super interesting paper from Meta Superintelligence Labs on controlling long agent runs. They use the same workers and same budget, and ProgramBench goes from 63.7% to 71.5% with GPT-5.5 when a dedicated controller decides what work to run next. Codex scores 58.0%. Here is how it works: The controller keeps a short summary of the run and leaves full worker outputs in memory. Each cycle it updates that summary, proposes next steps, estimates what each one is worth under the remaining budget, and sends the chosen work to workers with the earlier outputs they need. On ProofBench, ARC-AGI-2 and LongCoT-mini it adds 3.6 to 4.2 points over direct control, averaged over three frontier models. Paper: https://academy.dair.ai/papers/thinking-before-thinking-scaling-agentic-inference-through-meta-reasoning-2609.38147

![Super interesting paper from Meta Superintelligence Labs on controlling long agent runs. They use the same workers and same budget, and ProgramBench goes from 63.7% to 71.5% with GPT-5.5 when a dedica](../../../../assets/images/2026/10/02/2105832649868837275-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2105832649868837275)

---
