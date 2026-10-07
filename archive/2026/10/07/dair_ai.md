# 🐦 @dair_ai

## 📅 October 07, 2026

> 7 post(s) archived.

---

### 🕐 17:07 UTC · @dair_ai

> Agent-to-agent communication with a personal agent on top is wild. Wow. I underestimated how well models like Opus 5.5 can coordinate already. This opens a whole new set of experiences with agents. But it takes a bit of tuning (automations, webhooks, system prompts, tooling, etc.) and retrieving context at the right time. I don&apos;t have a perfect setup yet, but I feel like I&apos;m already living in the future. My agent team can do work (higher quality than I could imagine) at speeds I can&apos;t even keep up with. It&apos;s crazy how fast things have moved in about a year. I started with individual Claude Code sessions. Then, just a couple of months later, I moved to multi-agent systems with subagents, parallelizing work. Then, a couple of months ago, I built a persistent, higher-level agent team, similar to Grok Bot. Of course, with my own agent orchestrator and a team of like 8 specialized bots (CFO, CSO, CTO, CMO, CCO, CoS, etc.) Then, about a month ago, I started playing around with agent-to-agent communication with a personal agent. And I can tell you, most of the apps like Code and Claude Desktop are way behind. But they will catch up. This is why I believe we should all be building our own agent orchestrator/harness. You need to personalize to what works for you, which creates an important edge. You can start with a fork; who cares. Start somewhere. It&apos;s just mind-blowing to see agents coordinate and do things on their own that would take a village or an entire org in some cases. Just sharing my raw thoughts here, but things will dramatically change again in the next couple of months, leading into next year. Sharing a snapshot of one of my personal agents, Clio (Chief Content Officer), doing research all day and putting together high-quality content to inform me on things I am interested in and things I am writing about on X.

![Agent-to-agent communication with a personal agent on top is wild. Wow. I underestimated how well models like Opus 5.5 can coordinate already. This opens a whole new set of experiences with agents. Bu](../../../../assets/images/2026/10/07/2107880581216477417-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2107880581216477417)

---

### 🕐 15:37 UTC · @dair_ai

> Reading eval results is now the slowest part of building agents. I&apos;m Elvis, founder of @dair_ai. I lead research, build, and teach about AI agents. I run harness experiments every night, but reading the results was eating my mornings. Every change to my harness gets evaluated overnight, whether it touches memory, tool use, or context compaction. The morning after is the hard part. I check which tasks my agent got right yesterday but wrong today. Then I open the logs for each failure, one by one, to figure out which of my changes caused it. I tried a dashboard first. It showed the pass rate dropped. It couldn&apos;t tell me why. That is the job Viktor, an AI employee in Slack, is built for. He reviews the results overnight. Here is how that plays out. Say 23 tasks that passed yesterday fail today. Viktor checks all 23 logs, traces them to the one change that caused them, and suggests undoing it. I check the logs and make the call. Viktor does the digging. I decide what goes into the harness. He is also proactive. He flags problems before you ask, which helps you stay on track with complex eval runs and other research tasks. Harness engineers, do you check every eval run, or only when the pass rate drops? Try free at @viktor_com. $100 in credits, no card. Full link in my first reply. Thanks to the team for partnering with me on this post

![Reading eval results is now the slowest part of building agents. I&apos;m Elvis, founder of @dair_ai. I lead research, build, and teach about AI agents. I run harness experiments every night, but read](../../../../assets/images/2026/10/07/2107857835526639705-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2107857835526639705)

---

### 🕐 15:25 UTC · @dair_ai

> This is a great paper from AWS AI Labs. They show that multi-agent coding teams raised their test pass rate by 28.2% and cut wall time by 16.5% without changing the model. The authors achieve this by changing how the agents communicate. In free-form agent teams, shared findings are just context. Agents can ignore them, and the harness never checks whether an implementation still matches the interface the team agreed on. They introduce AECP, a protocol that requires agents to communicate only through structured artifacts, and the harness acts on them. It supplies recorded findings when an agent opens relevant code, screens implementations against interface commitments, and makes affected agents revisit an agreement when it changes. Results hold across Doc2Repo, NL2Repo, and CodeProjectEval with models including Opus-4.8 and DeepSeek-V4-Flash. There is a security benefit too. Malicious instructions relayed between agents reach another agent 0% of the time instead of 95%, and get acted on 0% of the time instead of 40%. Paper: https://academy.dair.ai/papers/aecp-artifact-exclusive-communication-protocol-for-multi-agent-code-generation-2610.06481

![This is a great paper from AWS AI Labs. They show that multi-agent coding teams raised their test pass rate by 28.2% and cut wall time by 16.5% without changing the model. The authors achieve this by ](../../../../assets/images/2026/10/07/2107854720476057796-1.jpg)

🔗 [View original post](https://x.com/dair_ai/status/2107854720476057796)

---

### 🕐 15:04 UTC · @dair_ai

> Banger paper from NVIDIA. One exciting trend I am seeing is building verifiable environments for your agents and training the harness alongside the model. Co-evolving the harness and the model is a big part of owning the intelligence stack. And many frontier AI companies have started doing that. This paper shows how this works: VERA turns benchmark trajectories into more than 9,000 restartable sandboxes with rubric scoring, and keeps only environments that run and can be scored from observable evidence. It then updates both the model weights and the harness. A harness edit is kept only if it passes self-tests and adds at least 5 points on the development set. The system rejects a model checkpoint if its score drops by more than 20%. At 9B, the co-evolved agent beats the strongest single-axis baseline by 10.3 points on AutoCoWorkBench and 13.0 points on AutoMedBench. At 27B, it scores 71.6 on AutoCoWorkBench, above Claude Opus 4.8. The environment corpus is open-sourced. Paper: https://arxiv.org/abs/2610.05923 Chat with Paper: https://academy.dair.ai/papers/vera-scaling-verifiable-environments-for-agentic-co-evolution-2610.05923

![Banger paper from NVIDIA. One exciting trend I am seeing is building verifiable environments for your agents and training the harness alongside the model. Co-evolving the harness and the model is a bi](../../../../assets/images/2026/10/07/2107849444897243141-1.jpg)

🔗 [View original post](https://x.com/omarsar0/status/2107849444897243141)

---

### 🕐 14:29 UTC · @dair_ai

> AI voice products need to know who spoke and what they said. That is harder than transcription or diarization alone, especially when speakers talk over each other. Pulse by @smallest_AI is now #1 on the Diarization + ASR track of the @voicearena_ai&apos;s Diarization Bench, with 24.4% DER. DER is an error rate, so lower is better. The next system in the track scores 40.7%. Pulse by @smallest_AI currently ranks #1 in the Diarization + ASR track by DER, as the newest entry on the Voice Arena Diarization Bench. The Diarization + ASR track ranks Speaker-Attributed ASR systems that return speaker labels together with the transcript. Seven systems are in…

🔗 [View original post](https://x.com/omarsar0/status/2107840660711563495)

---

### 🕐 13:40 UTC · @dair_ai

> Explore the top AI papers of the week with our brand-new MCP tools. Connect it to Codex, Claude Code, or Grok Bot. Introducing MCP tools for @dair_ai. Connect the MCP to your Codex/Claude/Grok Bot to discover and explore the top AI papers. We carefully curate the papers, so you can expect mostly bangers. The index has all the papers I have featured on X over the last couple of years. Get star…

🔗 [View original post](https://x.com/dair_ai/status/2107828509934559509)

---

### 🕐 13:39 UTC · @dair_ai

> Introducing MCP tools for @dair_ai. Connect the MCP to your Codex/Claude/Grok Bot to discover and explore the top AI papers. We carefully curate the papers, so you can expect mostly bangers. The index has all the papers I have featured on X over the last couple of years. Get started: https://academy.dair.ai/papers &gt; find and summarize awesome papers &gt; explore our harness engineering collection &gt; find new methods to experiment with &gt; find sota results around AI topics &gt; generate literature review/surveys &gt; build your personal collection &gt; visualize papers &gt; and much more The demo shows how to install it, including some ideas inspired by @karpathy for visualizing a paper. We are just getting started. Reach out if you have feedback. We are releasing a few benchmarks with this in the next couple of weeks and will ship regular additions and improvements. Stay tuned! Media

🔗 [View original post](https://x.com/omarsar0/status/2107828097433137595)

---
