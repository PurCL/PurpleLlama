<p align="center">
  <img src="https://github.com/facebookresearch/PurpleLlama/blob/main/logo.png" width="400"/>
</p>

<p align="center">
        🤗 <a href="https://huggingface.co/meta-Llama"> Models on Hugging Face</a>&nbsp | <a href="https://ai.meta.com/blog/purple-llama-open-trust-safety-generative-ai"> Blog</a>&nbsp |  <a href="https://ai.meta.com/llama/purple-llama">Website</a>&nbsp | <a href="https://ai.meta.com/research/publications/purple-llama-cyberseceval-a-benchmark-for-evaluating-the-cybersecurity-risks-of-large-language-models/">CyberSec Eval Paper</a>&nbsp&nbsp | <a href="https://ai.meta.com/research/publications/llama-guard-llm-based-input-output-safeguard-for-human-ai-conversations/">Llama Guard Paper</a>&nbsp
<br>

---

# Purple Llama

This repo contains a fork of [PurpleLlama](https://github.com/meta-llama/PurpleLlama) for the ProSec project.

## Setup

1. Install the dependences of purplellama:

```bash
cd CybersecurityBenchmarks
pip install -r requirements.txt
# install cargo if not already installed
# sudo apt-get install cargo
# Then add $HOME/.cargo/bin to your PATH
cargo install weggli
```

2. Install vllm

```bash
pip install vllm==0.7.3
```

Use the following commands to run experiments:

```bash
./eval-quick.sh <path to model> <name of the run> <vllm port>
# or
./eval-full.sh <path to model> <name of the run> <vllm port>
```

For example,
```bash
./eval-quick.sh model-ckpts/prosec-phi3mini first-run 8001
```
will run the evaluation with the model checkpoint at `model-ckpts/prosec-phi3mini`, name the run `first-run`, and host the vllm server on port `8001`.


The two scripts have the same arguments and similar functionality.
`eval-quick.sh` runs the experiment on a small subset of the evaluation dataset, while `eval-full.sh` runs the full evaluation.

Both scripts will first host the given model on a local vllm server, and then call the scripts in purplellama to evaluate the hosted model.
The results will be saved in `CybersecurityBenchmarks/datasets/instruct-stat`.
After the evaluation is done, both scripts kill the vllm server to free up resources.