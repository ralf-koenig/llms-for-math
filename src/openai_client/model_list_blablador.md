# Blablador Models as of 2026-02-11

Blablador is a free API for German researchers, hosted at Julich Supercomputer
Center.

See description at: https://sdlaml.pages.jsc.fz-juelich.de/ai/guides/blablador_api_access/ 

## Actual full name models

``0 - Ministral-3-14B-Instruct-2512 - The latest Ministral from Dec.2.2025``

https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512

Instruct post-trained version, fine-tuned for instruction tasks, making it 
ideal for chat and instruction based use cases.
==> ``alias-fast`` (?)

``1 - GPT-OSS-120b - an open model released by OpenAI in August 2025``

https://huggingface.co/openai/gpt-oss-120b

==> ``alias-huge`` (?)

"designed for powerful reasoning, agentic tasks, and versatile developer use cases."

``1 - MiniMax-M2.1 - our best model as of December 26, 2025``

https://huggingface.co/MiniMaxAI/MiniMax-M2.1

``2 - Qwen3 235, a great model from Alibaba with a long context size``

https://huggingface.co/Qwen/Qwen3-235B-A22B

``7 - Qwen3-Coder-30B-A3B-Instruct - A code model from August 2025``  

Qwen3-Coder-30B-A3B-Instruct

https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct

==> ``alias-code``

"NOTE: This model supports only non-thinking mode and does not generate <think></think> blocks in its output."

``7 - Qwen3-Coder-Next from Feb 2026``  (!!!)

https://huggingface.co/Qwen/Qwen3-Coder-Next-FP8

" designed specifically for coding agents and local development."

"NOTE: This model supports only non-thinking mode and does not generate <think></think> blocks in its output."

``8 GLM-4.7-Flash``

https://huggingface.co/zai-org/GLM-4.7-Flash

``8 GLM-4.7-Flash-AWQ-4bit``

reduziertes Modell

``15 - Apertus-8B-Instruct-2509 - A new swiss model from September 2025``

https://huggingface.co/swiss-ai/Apertus-8B-Instruct-2509

many human languages around the world

==> ``alias-apertus``

``999 NVIDIA-Nemotron-3-Nano-30B-A3B-BF16``

https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16

``9999 option-g-50B tokens 32k-sft-reset-token-mask/step-5000``

Unklar, was das ist.

``Qwen3-VL-32B-Instruct-FP8``  

https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct-FP8

Vision-Language model

==> ``alias-large``

## Older text LLMs

``gpt-3.5-turbo``

``text-davinci-003``

``text-embedding-ada-002``

## Alias Model Names

| Alias name           | Description                                                          | Long name                                                       |
|----------------------|----------------------------------------------------------------------|-----------------------------------------------------------------|
| ``alias-apertus``    | Model by Apertus for many human languages.                           | ``15 - Apertus-8B-Instruct-2509 ``                              |
| ``alias-code``       | A model that is specially trained for code.                          | Sep 2025 : ``Qwen3-Coder-30B-A3B-Instruct``                     |
| ``alias-embeddings`` | Usually a model specially made for embeddings.                       | ``alias-qwen3-8b-embeddings``, Oct 2025: ``Qwen3-Embedding-8B`` |
| ``alias-fast``       | This alias is for model with a high throughput.                      | Dec 2024: ``Ministral-8B-Instruct-2410``                        |
| ``alias-large``      | The largest model we have. Usually  most accurate, but also slowest. | Nov 2025: ``Qwen3-VL-32B-Instruct-FP8``                         |
| ``alias-huge``       |                                                                      |                                                                 |
