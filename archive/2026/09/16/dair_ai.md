# 🐦 @dair_ai

## 📅 September 16, 2026

> 2 post(s) archived.

---

### 🕐 10:20 UTC · @dair_ai

> Interesting safety paper from Microsoft. They find that a weaker, unaligned model can split a harmful task into harmless-looking subquestions, ask an aligned frontier model each one in a separate session, and combine the answers locally. The authors call this capability laundering. Each request passes on its own, because no single answer from the frontier model is a harmful task. They tested GPT-5.5, Claude Opus 4.8 and Grok-4.3 as the consulted models. On CyBench, Gemma-4-31B recovered 8 of 14 tasks it failed alone when it consulted GPT-5.5. On a CBRN attack chain, consultation raised its mean rubric score from 62.3 to 83.1. Paper: https://academy.dair.ai/papers/divide-consult-conquer-capability-laundering-through-aligned-llms-2609.15383

![Interesting safety paper from Microsoft. They find that a weaker, unaligned model can split a harmful task into harmless-looking subquestions, ask an aligned frontier model each one in a separate sess](../../../../assets/images/2026/09/16/2100167820135059579-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2100167820135059579)

---

### 🕐 04:20 UTC · @dair_ai

> Giving an assistant extra tools seems harmless. Surprisingly, this paper shows it can make the assistant stop answering questions it knows. Across six models, the answer rate on questions that need no tool fell from 98.2% to 63.5% when a related tool was merely available. So the drop comes from the tool being present, even when it goes unused. The benchmark has 500 query pairs across 10 domains, each with a tool-unavailable control. A preceding tool call recovered some lost answers and caused new losses. A one-sentence system instruction that tells the model what the tool is for recovered up to 45.6 points. Paper: https://academy.dair.ai/papers/when-tools-get-in-the-way-the-effect-of-unnecessary-tool-availability-on-llm-ans-2609.14157

![Giving an assistant extra tools seems harmless. Surprisingly, this paper shows it can make the assistant stop answering questions it knows. Across six models, the answer rate on questions that need no](../../../../assets/images/2026/09/16/2100077223252512956-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2100077223252512956)

---
