# Model Evaluation Results

## GPT-5.2 (OpenAI)

* reasoning = none (due to cost for reasoning tokens)
* verbosity = low (short answer)
* max output tokens = 10.000 (default)

## GPT5-mini (OpenAI)

* reasoning = high (reasonable cost even with reasoning tokens)
* verbosity = low (short answer)
* max output tokens = 10.000 (default) - rarely used with verbosity low

## GPT-OSS-120b (Blablador)

* reasoning = high
* verbosity = medium (no cost for tokens, also return step-by-step sequence of calculations)
* max output tokens = 5.000 (then model runs out of reasoning tokens too often: 59 out of 500 times, which is 11.8%)
* also max output tokens = 10.000 (default value), only 

# Ministral-3-14B-Instruct-2512  (Blablador)

* reasoning = high
* verbosity = medium (no cost for tokens, also return step-by-step sequence of calculations)
* max output tokens = 5.000 (otherwise: Blablador service often times out too often)

# Qwen3-Coder-Next  (Blablador)

* reasoning = high
* verbosity = medium (no cost for tokens, also return step-by-step sequence of calculations)
* max output tokens = 5.000 (otherwise: Blablador service often times out too often)

