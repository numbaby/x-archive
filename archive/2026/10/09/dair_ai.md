# 🐦 @dair_ai

## 📅 October 09, 2026

> 2 post(s) archived.

---

### 🕐 00:53 UTC · @dair_ai

> Build your own harness, folks. Reading papers like this makes me realize how underexplored harness engineering really is. The authors find that on whole-repository migration, GPT-5.6 Sol goes from 6.5% to 31.0% when Codex is replaced with the HERMES harness, with the same model and effort setting. The gain comes from the harness. HERMES pairs each repository component with a resident LLM that knows its own code and dependencies. A dependency-aware step decides which components to activate, and a diagnosis step maps test failures back to the components that need changes. Across four software engineering benchmarks, it beats matched baseline harnesses by 12.4 points on average. With strong activation and diagnosis models, Qwen3-8B components come within 4.5 points of an all-GPT-5.6 Sol setup and cut Terminal-Bench 4.0 inference cost by 26.2%. Paper: https://arxiv.org/abs/2610.07832 Chat with Paper: https://academy.dair.ai/papers/harness-engineering-for-software-engineering-via-modular-executable-dev-primitiv-2610.07832

![Build your own harness, folks. Reading papers like this makes me realize how underexplored harness engineering really is. The authors find that on whole-repository migration, GPT-5.6 Sol goes from 6.5](../../../../assets/images/2026/10/09/2108360049848717588-1.png)

🔗 [View original post](https://x.com/omarsar0/status/2108360049848717588)

---

### 🕐 00:50 UTC · @dair_ai

> Interesting paper from Sakana AI on memory for recurrent models. Recurrent models are good at state tracking, but they usually keep everything in one hidden vector, so short-term computation and long-term storage compete for the same space. The Continuous Memory Machine gives the model two memory matrices. One short-term memory tracks recent neuron activity, and the other long-term memory stores information for later steps. A Transformer reads and writes both at every step. It builds on Sakana&apos;s Continuous Thought Machine and beats LSTM, DNC, RMC, and CTM baselines on copy, associative recall, sorting, few-shot regression, and maze solving. It also generalizes to longer inputs than earlier memory-augmented networks. The attention maps show the model uses long-term memory for algorithmic and in-context tasks and skips it when the task does not need it. Paper: https://academy.dair.ai/papers/continuous-memory-machines-2610.07907

![Interesting paper from Sakana AI on memory for recurrent models. Recurrent models are good at state tracking, but they usually keep everything in one hidden vector, so short-term computation and long-](../../../../assets/images/2026/10/09/2108359294609768715-1.png)

🔗 [View original post](https://x.com/dair_ai/status/2108359294609768715)

---
