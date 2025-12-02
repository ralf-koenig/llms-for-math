# Set you OPENAI_API_KEY in an environment variable before and make sure to have
# some budget for API usage.

from openai import OpenAI

from openai.types.shared_params.reasoning import Reasoning
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

client = OpenAI()

# # Get list of available models
# models = client.models.list()
# # Print model IDs
# for model in models.data:
#     print(model.id)

###########################################################
# https://platform.openai.com/docs/models
# Frontier models
###########################################################

# gpt-5-pro                         Version of GPT-5 that produces smarter and more precise responses
#                                   uses more compute to think harder and provide consistently better answers.
# gpt-5-pro-2025-10-06              Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.

# designed to tackle tough problems, some requests may take several minutes to finish
# always: reasoning.effort: high

# 400,000 context window
# 272,000 max output tokens
# Sep 30, 2024 knowledge cutoff
# Reasoning token support
# input 15.00 USD/1M tokens, output 120.00 USD/1M tokens

#                                   Complex reasoning, broad world knowledge, and code-heavy or multi-step agentic tasks
# gpt-5.1                           Flagship model for coding and agentic tasks with configurable reasoning and non-reasoning effort
# gpt-5.1-2025-11-13                Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
# gpt-5.1-chat-latest
#                                   has a new "none" reasoning setting for faster responses, increased steerability in model output
# Input $1.25, cached input $0.125, output $10.00

# gpt-5.1-codex                     Version of GPT-5 optimized for agentic coding tasks in Codex or similar environments.
# gpt-5.1-codex-mini
# same cost

# 400,000 context window
# 128,000 max output tokens
# Sep 30, 2024 knowledge cutoff
# Reasoning token support

# gpt-5-2025-08-07                  Previous model for coding, reasoning, and agentic tasks across domains.
#                                   OpenAI recommends using the latest GPT-5.1.
# same cost as 5.1

#                                   Cost-optimized reasoning and chat; balances speed, cost, and capability
# gpt-5-mini                        faster, more cost-efficient version of GPT-5. It's great for well-defined tasks and precise prompts.
# gpt-5-mini-2025-08-07             Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
# 400,000 context window
# 128,000 max output tokens
# May 31, 2024 knowledge cutoff
# Reasoning token support
# Input $0.25, cached input $0.025, output $2.00

#                                   High-throughput tasks, especially simple instruction-following or classification
# gpt-5-nano                        fastest, cheapest version of GPT-5. It's great for summarization and classification tasks.
# gpt-5-nano-2025-08-07             Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
# 400,000 context window
# 128,000 max output tokens
# May 31, 2024 knowledge cutoff
# Reasoning token support
# Input $0.05, cached input $0.005, output $0.40


response = client.responses.create(
    # model = "gpt-5-pro-2025-10-06", # USE WITH CARE! ALWAYS REASONING EFFORT HIGH! HIGH COST QUICKLY!
    model = "gpt-5.1-2025-11-13", # USE WITH CARE. High cost for reasoning = medium or high!
    # model = "gpt-5-mini-2025-08-07",
    # model = "gpt-5-nano-2025-08-07",
    # input = "Write a one-sentence bedtime story about a unicorn."
    input="Work like a program for symbolic math. What is 123123123123123123123123123123123123123123123123123123123123123123123123123123 + 123123123123123123123123123123123123123123123123123123123123123123123123 ? Output only the result.",

    # input="Remember how to add two long integers in decimal representation digit by digit, including the carry-over! What is 123123123123123123123123123123123123123123123123123123123123123123123123123123 + 123123123123123123123123123123123123123123123123123123123123123123123123 ? Output only the result.",

    reasoning = Reasoning (effort = "none", # none (default for GPT 5.1) -> for low-latency interactions
                                                # only then temperature XOR top_p or logprobs can be used
                                        # minimal - for GPT 5 nano and mini
                                   # low -> reasoning model
                                   # medium (default for GPT 5), use with caution due to cost
                                   # high (default for GPT 5-Pro), use with caution due to cost
                # summary = "auto", # organization must be verified, for analysis of reasoning process
                           ),
    text = ResponseTextConfigParam (verbosity = "low"),
                                # low : produces shorter, more concise code with minimal commentary
                                # medium (default):  yield longer, more structured code with inline explanations
                                # high:
    # max_output_tokens = 10000,   # An upper bound for the number of tokens that can be generated for a response,
                                # including visible output tokens and (!) reasoning tokens (!)

    # max_tool_calls = 1,       # The maximum number of total calls to built-in tools that can be processed in a
                                # response. This maximum number applies across all built-in tool calls, not per
                                # individual tool. Any further attempts to call a tool by the model will be ignored.
                                # USE this to limit tool use and cost.

    # temperature=0.15,         # max: 2
                                # What sampling temperature to use. Higher values like 0.8 will make the output more
                                # random, while lower values like 0.2 will make it more focused and deterministic.
                                # We generally recommend altering this or top_p but not both.

    # top_p =  0.10             # number · min: 0.01 · max: 1
                                # An alternative to sampling with temperature, called nucleus sampling, where the
                                # model considers the results of the tokens with top_p probability mass.
                                # So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                                # We generally recommend altering this or temperature but not both.
)

# correct answer:
#       123123123123123123123123123123123123123123123123123123123123123123123123123123
# +           123123123123123123123123123123123123123123123123123123123123123123123123
# ====================================================================================
#       123123246246246246246246246246246246246246246246246246246246246246246246246246

# Answers by :
# First try: (gtp-5-mini), Nov 23 2025, way too long, no other parameters
# 123123123123123246246246246246246246246246246246246246246246246246246246246246246246
# Second try: (gpt-5-nano) Nov 25 2025 -- too short, no other parameters
#          246246246246246246246246246246246246246246246246246246246246246246246246246
# Third try: (gpt-5.1, reasoning: none) -- too short, no other parameters
#             123123123123123246246246246246246246246246246246246246246246246246246246
# Fourth try: (gpt-5.1, reasoning: low) -- too short; 780 reasoning tokens!; max_output_tokens = 1.000
#             123246246246246246246246246246246246246246246246246246246246246246246246
# Fifth try: (gpt-5.1, reasoning: medium) -- way too long; 4.240 reasoning tokens!; max_output_tokens = 10.000
#            costs 5 US-cents for this query alone!
# 123123123123123123123123123123123123123123123123123123246246246246246246246246246246246246246246246246246246246246246246246246
# Sixth try: (gpt-5.1, reasoning: high) -- good length, too high; 4.619 reasoning tokens!; max_output_tokens not defined
#            costs 5 US-cents for this query alone!
#       123246246246246246246246246246246246246246246246246246246246246246246246246246
# Seventh try: (gpt-5.1, reasoning: none) -- correct answer! no reasoning tokens; no limit on tool use or max output tokens.
#       cost: near nothing
#       123123246246246246246246246246246246246246246246246246246246246246246246246246
# Eighth try: (gpt-5.1, reasoning: none) -- good length, but wrong! no reasoning tokens; max_tool_use = 1
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
# Nineth try: (gpt-5.1, reasoning: none) -- good length, but wrong! no reasoning tokens; no limit on tool use or max output tokens.
#       123123123123123123123123246246246246246246246246246246246246246246246246246246

# GPT 5.1, Reasoning none, set temperature
# temperature 0.15 - all wrong
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#             123123123123123123123123246246246246246246246246246246246246246246246246

# temperature 0.25 - all wrong
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246
#       123123123123123123123123246246246246246246246246246246246246246246246246246246

# New prompt with Remember how to ...
# First try: (gpt-5.1), Nov 25 2025, reasoning_effort none, way too short and wrong
#             123123123123123123123123246246246246246246246246246246246246246246246246
# Second try: (gpt-5.1), Nov 25 2025, reasoning_effort low, 2462 reasoning tokens, way too long!
#       123123123123123123123123123123123123123123246246246246246246246246246246246246246246246246246246

print(response.output_text)

# prints input tokens, cached_tokens, output_tokens, reasoning tokens, total_tokens
print(response.usage)

# print(response.reasoning.summary)
