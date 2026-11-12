# 🐦 @rasbt

## 📅 November 12, 2026

> 3 post(s) archived.

---

### 🕐 15:20 UTC · @rasbt

> Hoping Nemotron keeps going. Thankfully, open weight LLMs have some alternatives. But their open data and full training recipes would be much harder to replace.

🔗 [View original post](https://x.com/rasbt/status/2120899453510942743)

---

### 🕐 15:08 UTC · @rasbt

> LLM training is hard. Hard to be a jack of all trades. im surprised there isnt more pretrain-postrain codesign i guess companies really do ship their org charts

🔗 [View original post](https://x.com/rasbt/status/2120896608543924560)

---

### 🕐 15:02 UTC · @rasbt

> In reasoning model development, it&apos;s always been this interesting tension between training/optimizing chain-of-thoughts (CoTs) vs not touching them to preserve monitorability. CoTs are cool because we can check what the model is up to (e.g., whether it cheats or not) as long as it spells out its thought process. And we risk losing that if we explicitly optimize CoTs. Two caveats: 1) I.e., the catch of CoT and monitorability is that this only works if the written thinking reflects what the model is actually doing. 2) Also, when models become more capable, they spell out less in the CoT (like a cleverer math student needs less note-taking when solving problems during an exam). Nothing new on that front, but an interesting thread below on how to measure &quot;harder to monitor&quot;, with some interesting results that confirm the existing intuitions: 1) no-CoT capability (meaning how much reasoning the model can do in a single forward pass without writing anything down) - Better pretraining (lower perplexity) raises this no-CoT capability - Architecture mostly doesn&apos;t matter 2) CoT controllability (meaning how well the model can change its written reasoning when asked to add, remove, or change parts of it) - RL alone raises controllability a lot - Controllability is passed on through distillation * Higher no-CoT capability and higher controllability both make monitoring harder. PS: Perhaps the good news is that it seems that process supervision wasn&apos;t the main culprit. (1/10) Today, we’re sharing new research from @OpenAI: How does CoT monitorability (no-CoT capability and CoT controllability) evolve over the model training lifecycle? We emerged with unsurprising but sobering findings: as we scale toward more intelligent systems, models are be…

🔗 [View original post](https://x.com/rasbt/status/2120895037064020406)

---
