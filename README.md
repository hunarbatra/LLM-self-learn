# GPT-GQ

## LLMs with Google Queries access for self-learning

```sandbox-script.py```: Run this script to play around with the Self-Learning model <br>
```/benchmarking/baselines```: Code for benchmarking baseline models including- Vanilla GPT-3, CoT and Few-shot CoT <br>
```/benchmarking```: Code for different model variants including the following--
  1. Self-Learning (```self-learning.py```): Uses Google Search scraped info to answer questions
  2. Self-Learning with KB (```self-learning-with-kb.py```): Uses Google Search scraped info to answer questions and stores learnt info in an internal knowledge base <br> <br>

More info about the models: [Slides](https://docs.google.com/presentation/d/12WO_ctwQxs89-CvcuTpLOUGVQ8MUDd_YLCdMOZ76nzE/edit#slide=id.g1be62203bf9_0_166)

Benchmarking over MMLU:
1. MMLU College Physics Test
<img src="https://github.com/hunarbatra/LLM-self-learn/blob/master/benchmarking/results/mmlu1.png" width=450>
2. MMLU Global Facts Test
<img src="https://github.com/hunarbatra/LLM-self-learn/blob/master/benchmarking/results/mmlu2.png" width=450>

(please note: the code was written pretty quickly and might be a little messy for the benchmarking bit)
