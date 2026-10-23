# 🐦 @dair_ai

## 📅 October 23, 2026

> 2 post(s) archived.

---

### 🕐 14:28 UTC · @dair_ai

> Great application of small language models by Meta. They find that an 8B model picks tools better than a 402B model when trained for the job. This work focuses on tool selection for agents with more than ten thousand tools. At that scale, tool descriptions won&apos;t fit in context, and a retriever can only rank candidates without knowing which tools the instruction actually needs. Many systems hand this step to a proprietary LLM. They train Qwen3 models on a Plan, Retrieve, Select workflow. The model splits the instruction into substeps, the retriever returns candidates for each one, and the model commits one tool per substep. Training is SFT on about 20K curated ToolBench instructions, then RL with a reward that scores how many gold tools are covered and at what rank. On ToolBench G3, the 8B model goes from 36.2% after SFT to 41.5% after RL, above prompted Llama-4-Maverick. The trained selector also works with different retrievers and on tool corpora from new domains. https://arxiv.org/abs/2610.31483 Chat with Paper: https://academy.dair.ai/papers/training-small-language-models-for-transferable-tool-selection-2610.31483

![Great application of small language models by Meta. They find that an 8B model picks tools better than a 402B model when trained for the job. This work focuses on tool selection for agents with more t](../../../../assets/images/2026/10/23/2113638581818556920-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2113638581818556920)

---

### 🕐 14:16 UTC · @dair_ai

> RAG is so back! This work shows that plain RAG over raw chat history beats complex agentic memory systems on most long-term memory benchmarks. (bookmark it) They tested Raw-RAG, which is just dense retrieval plus reranking over the raw conversation, feeding a reader LLM. Across LoCoMo, LongMemEval, MEME and MemoryAgentBench, it ranks first in six of seven benchmark and model settings, ahead of the strongest agentic memory system by 0.13 to 5.53 points. Ingestion on BEAM-1M takes 0.3 hours, against 3.2 to 27 hours for systems like Mem0, MemOS and Memora. Why does it hold up? Raw history keeps more of the evidence a question needs, including the relations and dependency paths behind an answer. Rewriting history into memory entries tends to drop those important bits. Even with complete access to the transformed memory stores, models answer less accurately than with raw evidence. Before adding a memory layer to your agent, at least run this baseline on your own data. https://arxiv.org/abs/2610.30755 Chat with Paper: https://academy.dair.ai/papers/is-complex-agentic-memory-always-needed-naive-rag-is-stronger-than-we-thought-2610.30755

![RAG is so back! This work shows that plain RAG over raw chat history beats complex agentic memory systems on most long-term memory benchmarks. (bookmark it) They tested Raw-RAG, which is just dense re](../../../../assets/images/2026/10/23/2113635562578178147-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2113635562578178147)

---
