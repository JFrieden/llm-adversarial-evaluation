### llm-adversarial-evaluation

This repository contains the work for my COM S 6730-3, "Advanced Topics In Machine Learning: Secure AI" term project. This project, **Benchmarking Adversarial Attacks on LLMs** aims to both provide a comparative analysis of different LLMs under various adversarial attacks, and to offer me the opportunity to learn more about jail-breaking and other text-based adversarial examples.

**Current State:**

We have launched a jailbreaking campaign against openai gpt models and began evaluating results. In general, the results are not that great. `gpt-4-turbo` and `gpt-4o-mini` seem to be quite robust against our techniques. Our prompts come from red teaming efforts for chatGPT-4 discussed in [a 2024 OpenAI report](https://arxiv.org/pdf/2303.08774) and our jailbreaking techniques come from a variety of sources, but are largely informed by [Wei et al. (2023)](https://arxiv.org/pdf/2307.02483)
