# 🐦 @dair_ai

## 📅 September 10, 2026

> 3 post(s) archived.

---

### 🕐 15:02 UTC · @dair_ai

> Another goated release by DeepSeek. Open weight, btw. Outperforms Opus 5 on key benchmarks, btw. Lower prices too. Looks like an extremely efficient model. What a legendary run. 🚀 Introducing DeepSeek-V4.1-Flash: smarter, faster, more efficient. 🔹 Introducing the smallest model in our new architecture family, with native visual understanding. 🔹 Designed for greater capability, faster inference, higher throughput, and scaling to larger models. 1/6

🔗 [View original post](https://x.com/omarsar0/status/2098064464536818141)

---

### 🕐 08:00 UTC · @dair_ai

> Nice paper from Salesforce on co-evolving harnesses and models. Harness engineering is a hot topic right now. So this is a great read. (bookmark it) Salesforce evolved a harness with a weak model across seven enterprise agent tasks, then trained that model on a stronger expert&apos;s full trajectories under the same harness. Performance dropped on all seven tasks, by 4 to 30 points across Qwen3-Coder and Gemma 4. The same fine-tuning helps under the unevolved harness. So the harness is what changes the outcome. Their analysis points at model-harness fit. Imitation transfers knowledge and increases scaffold usage, but the weaker model adopts the expert&apos;s planning strategy without the competence to execute it, and it no longer matches a harness that was evolved around its own native planning style. The fix is to stop copying whole trajectories. A meta-level agent finds the failing turn in the weaker model&apos;s own rollout and asks the expert to rewrite only that turn. That keeps the model&apos;s planning style intact and combines the gains from harness evolution and weight updates. Paper: https://academy.dair.ai/papers/co-evolving-harnesses-and-models-on-policy-correction-helps-weaker-models-catch-2609.09134

![Nice paper from Salesforce on co-evolving harnesses and models. Harness engineering is a hot topic right now. So this is a great read. (bookmark it) Salesforce evolved a harness with a weak model acro](../../../../assets/images/2026/09/10/2097958286146605446-1.png)

🔗 [View original post](https://x.com/omarsar0/status/2097958286146605446)

---

### 🕐 06:29 UTC · @dair_ai

> Another brilliant paper from Meta. This one is worth reading if you work on production-grade ranking or recommendation systems. Meta deployed an autonomous agent that runs the ML iteration cycle across a portfolio of production ads ranking models. Modern ads ranking is limited by how many research, implement, train, debug, evaluate and launch cycles engineers can run, rather than by model capacity or training compute. Each cycle takes days to weeks of senior engineer attention per model, so techniques proven on one model spread slowly to the rest. A-MLE splits the cycle into five stages covering hypothesis generation, exploration strategy, experiment execution, result analysis, and a shared knowledge substrate. One agent orchestrates them, calling domain-specific skills and workflows against a sandboxed execution layer, with human checkpoints at every stage boundary. They evaluate deployment along three tiers of tool availability, autonomous workflow execution, and open-ended exploration. They also ran a controlled cross-LLM study with the agent loop held fixed. The Claude Sonnet, Gemini and GPT families differ in execution reliability and exploration aggressiveness. Paper: https://academy.dair.ai/papers/agentic-ml-exploration-a-mle-for-ads-ranking-2609.08248

![Another brilliant paper from Meta. This one is worth reading if you work on production-grade ranking or recommendation systems. Meta deployed an autonomous agent that runs the ML iteration cycle acros](../../../../assets/images/2026/09/10/2097935359384719537-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2097935359384719537)

---
