# 🐦 @dair_ai

## 📅 October 06, 2026

> 1 post(s) archived.

---

### 🕐 00:20 UTC · @dair_ai

> Context compression is a huge bottleneck for long-running agents. This work finds that context compression hurts long-horizon agents at a few specific points. They propose PAIR, which replays the agent from the same state with and without a given compression, instead of comparing whole runs that differ in many random ways. A typical compression adds a few extra steps. The large drops in success come from a small number of compression events. The harmful compressions drop task conditions the agent hasn&apos;t resolved yet. In one Venmo task, the summary dropped the &quot;only from coworkers&quot; filter and reported the total of all 36 payments as the answer. Other compressions reduce API specs the agent already read to vague prose, so the agent reopens the docs and logs in again, which adds about five steps. PAIR then diagnoses what information those compressions dropped and rewrites the matching sections of the compression prompt. The agent, compressor model, and tools stay fixed. On AppWorld, OfficeBench, and tau-Bench Retail, it gives the most consistent task completion of any compressed method and comes close to running with no compression at all. Compression also lowers run-to-run reliability before it makes tasks unsolvable, so check consistency across repeated runs in your own evals. Paper: https://arxiv.org/abs/2609.36526 Chat with Paper: https://academy.dair.ai/papers/adapting-context-compression-for-long-horizon-agents-with-counterfactual-continu-2609.36526

![Context compression is a huge bottleneck for long-running agents. This work finds that context compression hurts long-horizon agents at a few specific points. They propose PAIR, which replays the agen](../../../../assets/images/2026/10/06/2107264582687584567-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2107264582687584567)

---
