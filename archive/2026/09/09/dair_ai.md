# 🐦 @dair_ai

## 📅 September 09, 2026

> 2 post(s) archived.

---

### 🕐 05:20 UTC · @dair_ai

> Good work on improving memory for long-horizon agents. They separate two things that agent memory papers usually collapse into one. How memories get merged when they are written, and how retrieved content gets assembled into the prompt. The setting is a tight prompt budget of 2k to 5k tokens, where full-context prompting is off the table because of latency, cost and context limits. RSM-full combines a cosine-gated max-member merge rule on the write side with an atom-aware grouped packer on the read side. At a 4k budget it reaches 83% of full-context quality at 32% of the token cost. The ablations attribute the gain to both halves separately. The merge rule is worth 5.7 points over online k-means and matched DP-means. The grouped packer is worth 5.0 points over flat concatenation. It reproduces on RealMem, beating Budget-RAG, Streaming-Proto and the A-MEM agentic memory baseline, and landing level with BM25-RAG rather than above it. The authors state that higher-token baselines stay stronger outside this budget range. Paper: https://academy.dair.ai/papers/compact-memory-llm-agents-via-online-max-member-clustering-and-atom-aware-packin-2609.04915

![Good work on improving memory for long-horizon agents. They separate two things that agent memory papers usually collapse into one. How memories get merged when they are written, and how retrieved con](../../../../assets/images/2026/09/09/2097555607389896732-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2097555607389896732)

---

### 🕐 01:31 UTC · @dair_ai

> Great study on what actually predicts vibe-coding ability. 100 tertiary-level students completed measures of computer-science achievement, domain-general cognitive skills and written-communication proficiency, then took a vibe-coding assessment. The study was preregistered, which matters because the intuitive answer here, that writing ability carries everything, is what a post-hoc analysis would tend to find. Tasks were curated through an eight-expert consensus process and run in a purpose-built vibe-coding environment that mirrors commercial tools while allowing controlled measurement. They find that writing skill predicts performance. So does computer-science achievement, and it stays significant after controlling for domain-general cognitive skills, so it is measuring something specific to CS training rather than general ability. The practical question the authors point at is a curriculum one. How much time to spend teaching people to write good prompts, against how much to spend on computer-science fundamentals, for the people who will build software this way. Paper: https://academy.dair.ai/papers/computer-science-achievement-and-writing-skills-predict-vibe-coding-proficiency-2603.14133

![Great study on what actually predicts vibe-coding ability. 100 tertiary-level students completed measures of computer-science achievement, domain-general cognitive skills and written-communication pro](../../../../assets/images/2026/09/09/2097497977149624340-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2097497977149624340)

---
