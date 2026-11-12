# 🐦 @dair_ai

## 📅 November 12, 2026

> 1 post(s) archived.

---

### 🕐 14:37 UTC · @dair_ai

> Super interesting work on agent memory. (this is a must-read) It discusses whether agents can manage their own memory. If so, what would that self-organized memory look like? This is the closest implementation that I have seen to my own memory system. I mostly use linked documents with my agents, and it has been working extremely well. It works well because frontier models have gotten better at persisting external knowledge. The problem: Memory systems usually fix the schema in advance, with set record types and rules for how to group them. The solution: SoMem gives the agent ordinary linked documents instead. The agent decides what to summarize, which topics to create, and when to revise them. Every summary links back to the original interaction as evidence, and the runtime builds time, relation, and recency views on top. At question time, the agent chooses what to search and follows links to the source when it needs to check. SoMem beat the strongest baseline by 2.66 points on LoCoMo, 3.10 on BEAM-100K, and 2.00 on LongMemEval-S. Memory built by one model also worked when read by another. If your agent already reads and writes files, try letting it organize memory as linked notes before adding a vector store. https://arxiv.org/abs/2611.11929 Chat with Paper: https://academy.dair.ai/papers/can-llm-agents-organize-their-own-memory-2611.11929

![Super interesting work on agent memory. (this is a must-read) It discusses whether agents can manage their own memory. If so, what would that self-organized memory look like? This is the closest imple](../../../../assets/images/2026/11/12/2120888604402815485-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2120888604402815485)

---
