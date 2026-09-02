# 🐦 @dair_ai

## 📅 September 02, 2026

> 2 post(s) archived.

---

### 🕐 02:16 UTC · @dair_ai

> Finally, a good paper testing if graph memory actually beats flat retrieval for long-term agents. (bookmark this one) Researchers extract each conversational turn into typed nodes and attributed edges, answer from a two-hop subgraph, and hold the candidate-generation budget fixed at five retrieval roots. On LongMemEval the graph gets token F1 0.42 against 0.47 for a flat vector baseline, and a paired bootstrap over 500 questions puts the gap at -0.050 (95% CI -0.085 to -0.016). The damage concentrates on questions that require recalling a specific prior assistant turn, where judged correctness falls from 0.911 to 0.607. Splitting a turn into entities discards the surface form those questions depend on. The forgetting module fares much better. One pruning pass over a persistent 27,021-node graph, scored on recency, access frequency, degree centrality and age, removes 9.8% of nodes and 9.5% of stored bytes with token F1 unchanged. Paper: https://arxiv.org/abs/2608.28978 Chat with Paper: https://academy.dair.ai/papers/selective-forgetting-a-graph-based-memory-framework-for-long-term-llm-agents-2608.28978

![Finally, a good paper testing if graph memory actually beats flat retrieval for long-term agents. (bookmark this one) Researchers extract each conversational turn into typed nodes and attributed edges](../../../../assets/images/2026/09/02/2094972586358927466-1.png)

🔗 [View original post](https://x.com/omarsar0/status/2094972586358927466)

---

### 🕐 01:00 UTC · @dair_ai

> // Agent Zero Memory // This work separates three things that agent memory systems usually collapse into one. If you build agents with long-term memory, this memory design is a worth a read. Here is how it works: Agent Zero Memory runs an episodic events timeline, an entity-event knowledge graph, and a curated documentary memory of durable facts side by side over the same history. A retrieval turn passes through an intent gate, then a source router, then three concurrent agentic searches, one per system. Every stored item carries its origin, timestamp and evidence pointer, and answers run under a citation lock, so a reply may cite only evidence its reader actually opened. When the evidence is missing the system abstains. It reaches 95.60% on LongMemEval and 93.60% on LoCoMo, both new highs. The cost result is the more useful one for AI builders. Across eight backbone models accuracy moves by 3.4 points while per-query cost moves about 30x, with near state of the art quality available at up to 20x lower cost per query. Memory design is driving the quality here. Paper: https://arxiv.org/abs/2608.29606 Chat with Paper: https://academy.dair.ai/papers/agent-zero-memory-provenance-aware-long-term-memory-for-llm-agents-2608.29606

![// Agent Zero Memory // This work separates three things that agent memory systems usually collapse into one. If you build agents with long-term memory, this memory design is a worth a read. Here is h](../../../../assets/images/2026/09/02/2094953486047977860-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2094953486047977860)

---
