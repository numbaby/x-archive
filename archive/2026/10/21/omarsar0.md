# 🐦 @omarsar0

## 📅 October 21, 2026

> 3 post(s) archived.

---

### 🕐 15:39 UTC · @omarsar0

> Beyond agent harnesses, I believe agent interfaces are an important direction for the development of self-evolving agents. This is connected to the idea of building for agents. You can pack so much into a good harness and interface that agents understand well. Think about the efficiencies you get. Costs you can reduce. More importantly, this lets agents work more effectively and reliably with interfaces that make sense for the task at hand. With Artifacts, we&apos;ve already seen huge gains in productivity. It&apos;s a more natural interface for humans and agents to collaborate. We&apos;ll discover more of these interfaces over time, and agents will be able to build them on the fly, iterate on them, and evolve as needs arise. Excited about this emerging trend. Banger paper on evolving agent interfaces. Pay close attention to this new trend if you build with agents. Like optimizing harnesses, it&apos;s remarkable what you can achieve with agents that have access to better interfaces. Computer-use agents usually act through interfaces that pe…

🔗 [View original post](https://x.com/omarsar0/status/2112931809142939998)

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
