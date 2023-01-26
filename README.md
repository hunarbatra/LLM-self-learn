# GPT-GQ

- LLMs with Google Queries access for self-learning

```/benchmarking```: Code for different model variants
- Self-Learning: Uses Google Search scraped info to answer questions
- Self-Learning with KB: Uses Google Search scraped info to answer questions and stores learnt info in an internal knowledge base
```/benchmarking/baselines```: Code for benchmarking baseline models including- Vanilla GPT-3, CoT and Few-shot CoT
```sandbox-script.py```: Run this script to play around with the Self-Learning model

More info about the models: ![Slides](https://docs.google.com/presentation/d/12WO_ctwQxs89-CvcuTpLOUGVQ8MUDd_YLCdMOZ76nzE/edit#slide=id.g1be62203bf9_0_166)

Benchmarking over MMLU:
![MMLU College Physics Test](https://github.com/hunarbatra/LLM-self-learn/benchmarking/results/mmlu1.png)
![MMLU Global Facts Test](https://github.com/hunarbatra/LLM-self-learn/benchmarking/results/mmlu2.png)

(please note: the code was written pretty quickly and might be a little messy for the benchmarking bit)