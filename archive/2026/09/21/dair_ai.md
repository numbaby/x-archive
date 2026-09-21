# 🐦 @dair_ai

## 📅 September 21, 2026

> 2 post(s) archived.

---

### 🕐 13:59 UTC · @dair_ai

> StepFun’s new Step 5 Preview model is impressive! Had a chance to test it early. I&apos;ve been testing it as a coding agent. It’s on the Pareto frontier for cost vs. capability. It is a very capable model, comparable to GLM 5.3, Kimi K3, and others, and it comes at a very competitive price. It’s worth trying in your favorite coding agent. I tested it in a minimal harness to see how it compares with GLM 5.3. Here are my results. Overall, it is very effective and feels like a model I could use for a whole range of coding tasks. One behavior that stood out is that it knows when to stop, which makes it very effective at long-horizon tasks compared with other models in this class. I gave it and GLM 5.3 two real tasks in the same repo, at the same commit. First, a bug where numeric filters silently returned zero rows for decimals and negatives. Then a feature that needed new routes, permission gating, and a refactor of the background task supervisor. Both models got both tasks right. Every held-out test passed with no regressions, and neither one weakened an existing test to get there. Step 5 Preview finished, checked its work, and declared itself done. Both times. GLM 5.3 wrote correct code both times and then kept going until the step limit ended the run. Neither model got a follow-up prompt or a retry. Both had zero fix rounds, so the first delivery was the final delivery on both tasks. On the bug, Step 5 Preview wrote the shorter patch, the same approach the Datasette maintainer used in the real commit. It also added its own tests without being asked. Based on this, I would reach for it on unattended agent runs where a clear completion signal matters more than speed, on bug fixes in unfamiliar codebases, and on long-context work. On long context, I gave it a separate test earlier in the week. I generated about 368K tokens of fake incident tickets and hid five clues inside them that together explain an outage. When I asked for the root cause, it found all five clues and connected them correctly in about 90 seconds. Thanks to the StepFun team for partnering on this post. Media

🔗 [View original post](https://x.com/omarsar0/status/2102035017262149640)

---

### 🕐 00:46 UTC · @dair_ai

> Impressive paper on building recursive self-improving agent harnesses. It&apos;s rich with great insights on building effective agent harnesses. If you maintain an agent harness, this paper names three defects in how harnesses get improved and the fixes. First, evolving a harness against the evaluation benchmark makes reusable improvements impossible to tell apart from benchmark fitting. Instead, ModularRSI evolves on tasks disjoint from the benchmark. Second, updating from a single trajectory confuses a systematic harness deficiency with one task&apos;s reasoning details, which produces changes that fail on unseen tasks. ModularRSI contrasts successful against failed trajectories for the same task, then aggregates across tasks to find recurring behavioral deficiencies. Third, a monolithic harness makes it hard to localize a recurring problem, and optimizing the whole thing entangles unrelated mechanisms, so no change can be attributed. ModularRSI splits the evolvable harness into five functional modules that evolve separately. Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection. Paper: https://academy.dair.ai/papers/modularrsi-modular-and-generalizable-recursive-harness-self-improvement-2609.14857

![Impressive paper on building recursive self-improving agent harnesses. It&apos;s rich with great insights on building effective agent harnesses. If you maintain an agent harness, this paper names thre](../../../../assets/images/2026/09/21/2101835306953736396-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2101835306953736396)

---
