# 🐦 @omarsar0

## 📅 November 06, 2026

> 1 post(s) archived.

---

### 🕐 14:43 UTC · @omarsar0

> Weight memory vs. retrieval in agents. Brilliant work from Amazon. This work shows weight memory can outperform text memory on recall of user facts. But the best part is that you can leverage both. Using the same model and user data, this work shows that plain fine-tuning stores user facts in weights at 36.9% accuracy, while on-policy self-distillation reaches 59.9%. That second number also beats retrieval. On eight HaluMem-Long users, the distilled model answers with no retrieved context and beats MemOS-style retrieval (47.8%), extracted context (51.9%), and the raw dialogue (51.3%). The gain holds for every user and at 4B, 9B, and 27B. How it works: a teacher, which is the same model reading the user&apos;s memory, trains a student that has to answer without it. Weight memory has clear limits. It forgets older facts and cannot tell when something was never recorded. A verify-then-regenerate router checks each answer against the text store and adds 6.2 points. The recommendation is to keep a text store for recent and missing facts, and move stable user knowledge into weights. https://arxiv.org/abs/2611.05636 Chat with Paper: https://academy.dair.ai/papers/route-to-remember-adaptive-memory-selection-for-llm-agents-2611.05636

![Weight memory vs. retrieval in agents. Brilliant work from Amazon. This work shows weight memory can outperform text memory on recall of user facts. But the best part is that you can leverage both. Us](../../../../assets/images/2026/11/06/2118715786152001580-1.png)

🔗 [View original post](https://x.com/omarsar0/status/2118715786152001580)

---
