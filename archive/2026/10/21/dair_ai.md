# 🐦 @dair_ai

## 📅 October 21, 2026

> 6 post(s) archived.

---

### 🕐 22:28 UTC · @dair_ai

> Recommended reading and a super-interesting benchmark for measuring continual learning capabilities through memory. Agent memory is largely unsolved. As agents advance in capabilities like long-horizon work, it&apos;s unclear which models or harnesses work best, or which memory systems and types to use. Opus 5.5 at the top is not a surprise. But it&apos;s exciting that open-weight models like GLM-5.3 perform so well on memory generation. My big question is how this (better memory systems and persistent agent capabilities) translates into more performant, efficient RSI agents and harnesses. Introducing FrontierMemory: a new way to evaluate agent memory through downstream task performance. While existing memory benchmarks focus on recall (saturated via agentic search), FrontierMemory focuses on how agents learn from experience.

![Recommended reading and a super-interesting benchmark for measuring continual learning capabilities through memory. Agent memory is largely unsolved. As agents advance in capabilities like long-horizo](../../../../assets/images/2026/10/21/2113034713774363040-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2113034713774363040)

---

### 🕐 18:04 UTC · @dair_ai

> We love papers that go deeper down the stack. This is a good example that shifts from agentic context engineering to agentic cache engineering. They also apply recursive self-improvement to cache policies to further reduce cost by 7.1% over expert design. Specifically, this work focuses on KV cache management in long-running agents. When an agent summarizes or trims its history, the prefix change invalidates the cache after it, and the retained context must be prefilled again. Cache engineering gives the agent two operations on its own KV cache. One removes entries from future attention, and the other shifts the positions of the keys that remain. The trajectory text stays unchanged. This essentially provides a programmable interface for agents to define and refine their own cache engineering strategies. A rolling drop of old tool responses scores 1.7 points higher and costs 27.7% less than threshold-triggered summarization. Their AKV serving engine adds up to 1.2x throughput and 1.5x faster P95 latency. https://arxiv.org/abs/2610.28577 Chat with Paper: https://academy.dair.ai/papers/cache-engineering-for-agents-2610.28577

![We love papers that go deeper down the stack. This is a good example that shifts from agentic context engineering to agentic cache engineering. They also apply recursive self-improvement to cache poli](../../../../assets/images/2026/10/21/2112968165680640143-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2112968165680640143)

---

### 🕐 14:31 UTC · @dair_ai

> Banger paper on evolving agent interfaces. Pay close attention to this new trend if you build with agents. Like optimizing harnesses, it&apos;s remarkable what you can achieve with agents that have access to better interfaces. Computer-use agents usually act through interfaces that people design by hand, so an agent may type a spreadsheet cell by cell when one line of code would do. Simular&apos;s Agent S4 has a meta-agent that builds those interfaces instead. It reads the task agent&apos;s trajectories, with no success labels, and writes new tools and notes on when to use them. With the evolved interfaces, an open 27B model reaches 21.3% on OSWorld V2, 3.8 times that of the same model with hand-built interfaces. That is above GPT-5.5 (13.0%) and Claude Opus 4.8 (20.6%), at about 4.3% and 1.5% of their cost. Population-based selection keeps the interface repositories that do best on validation tasks the meta-agent never sees, so the changes carry over to new tasks. On ScienceBoard, the evolved interfaces raise success from 41.4% to 58.6% with the same model. The code is open source. https://arxiv.org/abs/2610.28601 Chat with Paper: https://academy.dair.ai/papers/evolving-agent-interfaces-2610.28601

![Banger paper on evolving agent interfaces. Pay close attention to this new trend if you build with agents. Like optimizing harnesses, it&apos;s remarkable what you can achieve with agents that have ac](../../../../assets/images/2026/10/21/2112914561590546695-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2112914561590546695)

---

### 🕐 14:21 UTC · @dair_ai

> Brilliant paper from Google on leveraging object-oriented design for self-evolving agent harnesses. Build specialized harnesses, folks. This is a banger paper from Google Cloud AI Research on self-evolving agent harnesses. (bookmark it) They introduce OO-Harness, which raises AutomationBench from 61.6% to 77.4% with the same Gemini 3.5 Flash executor. It also beats Meta-Harness…

🔗 [View original post](https://x.com/dair_ai/status/2112912142722855336)

---

### 🕐 02:15 UTC · @dair_ai

> Great work from Microsoft and colleagues. This one is on the hot new topic of co-evolving the harness and the model. (bookmark it) They raise Qwen3.5-35B-A3B&apos;s average resolve rate on three coding benchmarks from 57.8% to 64.8% by alternating the two. In each round, the policy reads its own failures and proposes harness changes. Then it is trained with RL under the harness it picked. Tasks that stay hard during training become the search set for the next harness round. The joint gain is larger than the harness-only gain and the policy-only gain added together. Each optimized part also keeps its improvement when paired with the other&apos;s original version. Using Opus 4.8 as the harness proposer in the same loop adds more on top, which makes this a practical way to transfer a frontier model&apos;s harness judgment into a smaller policy. https://arxiv.org/abs/2610.22791 Chat with Paper: https://academy.dair.ai/papers/self-evolving-coding-agents-via-harness-policy-optimization-2610.22791

![Great work from Microsoft and colleagues. This one is on the hot new topic of co-evolving the harness and the model. (bookmark it) They raise Qwen3.5-35B-A3B&apos;s average resolve rate on three codin](../../../../assets/images/2026/10/21/2112729341306220739-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2112729341306220739)

---

### 🕐 02:10 UTC · @dair_ai

> Highly recommended read from Google DeepMind and colleagues. There is a lot of interest in self-evolving agents, but they&apos;re hard to get right. This work highlights how important and difficult memory and retrieval are in agents. The big question in this paper is whether self-evolving agents keep learning without forgetting. They tested ReasoningBank, GEPA, and Meta-Harness on four task streams that drift in topic, workflow, or domain, built from BIRD, BFCL, and ScienceWorld. The weights stay frozen, and the agents adapt by rewriting prompts, memory, and skills. Self-evolution improves overall scores on most streams. But more adaptation consistently means agents forget more. Methods that rewrite a shared prompt or workspace make global edits, so they interfere with unseen tasks and overwrite older knowledge when the stream shifts. Memory retrieval keeps updates more local, but it still pulls in memories from other domains and collides when similar queries need different workflows. Static benchmarks hide both problems, so test self-evolving agents on a stream that changes over time. https://arxiv.org/abs/2610.25858 Chat with Paper: https://academy.dair.ai/papers/are-self-evolving-agents-continual-learners-2610.25858

![Highly recommended read from Google DeepMind and colleagues. There is a lot of interest in self-evolving agents, but they&apos;re hard to get right. This work highlights how important and difficult me](../../../../assets/images/2026/10/21/2112728082042015769-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2112728082042015769)

---
