# 🐦 @dair_ai

## 📅 October 30, 2026

> 3 post(s) archived.

---

### 🕐 14:42 UTC · @dair_ai

> Great report from NVIDIA. They report that Nemotron 3.5 Super reaches 51.78% on SWE-bench Pro. That beats Nemotron 3 Ultra with about 4.6x fewer active parameters. Super has 120B parameters with 12B active, and it handles text, images, and video. Lightning is a 30B text model with 3B active. The technical report covers every stage of training. Super gets mid-training on agentic software engineering, then supervised fine-tuning, RL, and multi-teacher on-policy distillation. Serving numbers are also included. The stack reaches up to 4,856 output tokens/s/GPU on GB200 while holding at least 50 tokens/s/user. NVFP4 quantization recovers 99.62% median accuracy relative to BF16. https://arxiv.org/abs/2610.38095 Chat with Paper: https://academy.dair.ai/papers/nemotron-3-5-super-and-lightning-open-efficient-mixture-of-experts-hybrid-mamba-2610.38095

![Great report from NVIDIA. They report that Nemotron 3.5 Super reaches 51.78% on SWE-bench Pro. That beats Nemotron 3 Ultra with about 4.6x fewer active parameters. Super has 120B parameters with 12B a](../../../../assets/images/2026/10/30/2116178819271032975-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2116178819271032975)

---

### 🕐 02:00 UTC · @dair_ai

> Self-improving harnesses are one of the most discussed ideas in AI right now. (bookmark it) This work proposes a new harness, RuHarness, that beats the strongest harness-evolution baseline by 4.5 points on held-out tasks with Qwen3.5-35B-A3B, and by 5.3 points with GLM-4.7-Flash. The work targets a gap in current methods. They evolve the harness but keep the criteria that guide each edit fixed, so the criteria stop matching the agent&apos;s weaknesses after a few rounds. RuHarness evolves the rubric along with the harness. Each round, it finds behavioral criteria in the trajectories, re-scores them, and directs harness edits at the most relevant unresolved weakness. Criteria that stop firing go dormant and return if the weakness reappears. If your harness evolution stops improving after a few rounds, update the critic too. https://arxiv.org/abs/2610.36826 Chat with Paper: https://academy.dair.ai/papers/when-the-critic-falls-behind-co-evolving-rubrics-and-harnesses-for-continual-age-2610.36826

![Self-improving harnesses are one of the most discussed ideas in AI right now. (bookmark it) This work proposes a new harness, RuHarness, that beats the strongest harness-evolution baseline by 4.5 poin](../../../../assets/images/2026/10/30/2115987068761628740-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2115987068761628740)

---

### 🕐 01:33 UTC · @dair_ai

> Learn to build evals, folks! You&apos;re not really doing recursive self-improvement (RSI) if you are not doing evals. And don&apos;t tell me your agents are generating the evals for you. They are pretty bad at it. I have found it really interesting and useful to give agents a concrete way to measure results and stay on track with a long-term goal. It&apos;s easier to hill climb when things are clearly measured and well defined. Probably one of the most important skills anyone in the space can have today. It doesn&apos;t matter how many agents and intelligence you throw at a problem; you are not going too far without proper evals.

🔗 [View original post](https://x.com/omarsar0/status/2115980498975551690)

---
