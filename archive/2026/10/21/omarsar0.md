# 🐦 @omarsar0

## 📅 October 21, 2026

> 2 post(s) archived.

---

### 🕐 14:27 UTC · @omarsar0

> I&apos;ve seen effective use of object-oriented design with agents before. You might find this NVIDIA paper interesting too: https://academy.dair.ai/papers/nooa

![I&apos;ve seen effective use of object-oriented design with agents before. You might find this NVIDIA paper interesting too: https://academy.dair.ai/papers/nooa](../../../../assets/images/2026/10/21/2112913670544171298-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2112913670544171298)

---

### 🕐 14:17 UTC · @omarsar0

> Build specialized harnesses, folks. This is a banger paper from Google Cloud AI Research on self-evolving agent harnesses. (bookmark it) They introduce OO-Harness, which raises AutomationBench from 61.6% to 77.4% with the same Gemini 3.5 Flash executor. It also beats Meta-Harness on all three benchmarks they test. More details below. Instead of evolving one global harness for every task, an evolution agent builds a class hierarchy of specialized harnesses from execution records. The design has three parts. &gt; Subclasses inherit the base harness and override only the methods a task cluster needs &gt; Design lessons record which changes helped and which ones failed &gt; A router reads the task and the base run, then picks a subclass or keeps the base result On Workspace-Bench, the score goes from 25.5% to 39.5%, and on Toolathlon-GYM strict pass goes from 31.2% to 37.5%. Spending extra inference on best-of-K sampling or self-refinement does not reliably help. Inheritance also improves results. On Workspace-Bench, harnesses built as subclasses score 4.96 points higher than the same evolved code copied into flat classes. https://arxiv.org/abs/2610.28380 Chat with Paper: https://academy.dair.ai/papers/object-oriented-harness-evolving-agent-harnesses-through-object-oriented-design-2610.28380

![Build specialized harnesses, folks. This is a banger paper from Google Cloud AI Research on self-evolving agent harnesses. (bookmark it) They introduce OO-Harness, which raises AutomationBench from 61](../../../../assets/images/2026/10/21/2112911038098317422-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2112911038098317422)

---
