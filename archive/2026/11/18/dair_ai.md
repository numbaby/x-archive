# 🐦 @dair_ai

## 📅 November 18, 2026

> 3 post(s) archived.

---

### 🕐 16:30 UTC · @dair_ai

> // RAG in a Trenchcoat // This NeurIPS 2026 paper shows that a minimal RAG memory matches state-of-the-art agent memory systems on standard benchmarks. (bookmark it) BRIDGE stores chained observation notes, retrieves them with BM25 plus embeddings, and shows them in time order. It uses one LLM call per write or query and about 5-7K tokens per question. It matches the prior best within confidence intervals on LongMemEval-S and BEAM, and beats the best memory baseline on EverMemBench by 5.7-6.3 points. The authors then test what memory lets an agent do. In their probes, the agent must apply a remembered rule or pattern that the question never mentions. No single design wins all probes. LangMem, which extracts atomic facts, wins rule application. BRIDGE wins pattern induction. Fact extraction loses the shape of a demonstrated pattern, while block summaries retrieve the rule, but the agent often does not apply it. Showing the rule more prominently closes most of that gap. Don&apos;t overcomplicate your memory system. Old retrieval methods are still very useful for agents. https://arxiv.org/abs/2611.22179 Chat with Paper: https://academy.dair.ai/papers/rag-in-a-trenchcoat-when-minimal-memory-is-enough-for-agentic-systems-and-when-i-2611.22179

![// RAG in a Trenchcoat // This NeurIPS 2026 paper shows that a minimal RAG memory matches state-of-the-art agent memory systems on standard benchmarks. (bookmark it) BRIDGE stores chained observation ](../../../../assets/images/2026/11/18/2123091409435853190-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2123091409435853190)

---

### 🕐 15:34 UTC · @dair_ai

> Another very interesting paper from Google on self-improving agent harnesses. (bookmark it) They let an optimizer rewrite the harness around a frozen Gemini 3.8 Flash on SWE-bench Lite and compared three approaches. - A prompt rule file lowered held-out accuracy from 5.0% to 2.5%. - A full rewrite of the harness reached 42.5% at 451.6k tokens per task. - Gated edits to one module at a time reached 40.0% at 46.7k tokens per task. The gated version splits the harness into four parts (context, control, tools, and verification). Each round it patches one part, checks the patch on held-out tasks under a token cap, and deploys it only if it passes. The gated harness also transferred to Gemini 4 Argon with no new search, solving 37.5% against 30.0% for the full rewrite. The test set is small (40 held-out issues), so treat the numbers as directional. The paper also lists failure modes to guard against when a harness edits itself, including prompt bloat, benchmark gaming, and evaluator tampering. https://arxiv.org/abs/2611.22299 Chat with Paper: https://academy.dair.ai/papers/harnesses-that-improve-themselves-a-unifying-framework-for-self-improving-agent-2611.22299

![Another very interesting paper from Google on self-improving agent harnesses. (bookmark it) They let an optimizer rewrite the harness around a frozen Gemini 3.8 Flash on SWE-bench Lite and compared th](../../../../assets/images/2026/11/18/2123077276350976396-1.png)

🔗 [View original post](https://x.com/omarsar0/status/2123077276350976396)

---

### 🕐 14:09 UTC · @dair_ai

> For a &quot;software factory&quot; to scale, you need a set of strong primitives. I feel like this auto-approving feature is an interesting primitive worth learning about. https://x.com/i/article/2123051296894717952

🔗 [View original post](https://x.com/omarsar0/status/2123056013582713318)

---
