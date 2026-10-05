# 🐦 @dair_ai

## 📅 October 05, 2026

> 2 post(s) archived.

---

### 🕐 02:00 UTC · @dair_ai

> Great overview of context compression in LLM Agents And one interesting, unexpected finding. If your compaction policy is tuned to cut tokens, it may be making your agent run slower. Great study from UT Austin on context compression in coding agents. They ran nearly 35,000 agent runs on SWE-bench Verified and Terminal-Bench and varied three decisions separately. These are how context is compressed, when compression triggers, and how much is removed. On Terminal-Bench with Qwen, policies that use about a third of the tokens can take 20% to 80% longer than keeping full context. Step-triggered policies cut the most tokens per step but need 10% to 27% more model calls. Threshold-triggered policies cut tokens by 22% to 55% with call counts close to full context. Results also differ by model. A policy that works well for Qwen drops Devstral to 38.7% and makes it slower, so measure latency and cost per model before choosing one. Paper: https://arxiv.org/abs/2609.32961 Chat with Paper: https://academy.dair.ai/papers/beyond-token-savings-a-systematic-study-of-context-compression-in-llm-agents-2609.32961

![Great overview of context compression in LLM Agents And one interesting, unexpected finding. If your compaction policy is tuned to cut tokens, it may be making your agent run slower. Great study from ](../../../../assets/images/2026/10/05/2106927371366596692-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2106927371366596692)

---

### 🕐 00:23 UTC · @dair_ai

> Huge release from EverMind AI. Raven is an open-source multi-agent system that builds a separate harness for each model and domain, evolves those harnesses from their failures, and coordinates them through a host agent. The host agent splits a goal into a task graph and sends each part to a model-harness pair for research, code, design, or on-call work. Harness components are diagnosed, mutated, and recombined, and a candidate replaces the current harness only after passing a statistical check. With DeepSeek-V4-Flash, the research harness scores 69.3% on BrowseComp and 60.0% on Humanity&apos;s Last Exam, against at most 62.4% and 43.3% for two other harnesses on the same model. Its curated skill library raises SkillsBench Pass@1 from 9.2% with no skills to 22.6%. Paper: https://arxiv.org/abs/2609.33439 Chat with Paper: https://academy.dair.ai/papers/raven-the-harness-of-harnesses-for-composable-agentic-intelligence-2609.33439

![Huge release from EverMind AI. Raven is an open-source multi-agent system that builds a separate harness for each model and domain, evolves those harnesses from their failures, and coordinates them th](../../../../assets/images/2026/10/05/2106902948173529447-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2106902948173529447)

---
