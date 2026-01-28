# Set you OPENAI_API_KEY in an environment variable before and make sure to have
# some budget for API usage.

import json
import pandas as pd
from datetime import datetime

from openai import OpenAI

from openai.types.shared_params.reasoning import Reasoning
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

REPETITIONS = 5
MAX_QUESTION = 100

# OPENAI_MODEL = "gpt-5.2-pro-2025-12-11" # USE WITH CARE! ALWAYS REASONING EFFORT HIGH! HIGH COST QUICKLY!
OPENAI_MODEL = "gpt-5.2-2025-12-11"  # USE WITH CARE. High cost for reasoning = medium or high!
# OPENAI_MODEL = "gpt-5-mini-2025-08-07",
# OPENAI_MODEL = "gpt-5-nano-2025-08-07",

OUTPUT_FILE = "llm_direct_answer_results"

def list_openai_models():
    client = OpenAI()
    # Get list of available models from OpenAI metadata server
    models = client.models.list()
    # Print model IDs
    for model in models.data:
        print(model.id)
    return

if __name__ == '__main__':

    with open('../../data/math500.json') as json_file:
        math500 = json.load(json_file)

    # use only the first MAX_QUESTION questions
    dataset = math500["rows"][0:MAX_QUESTION]

    test_results = list()

    for question in dataset:

        problem = question["row"]["problem"]
        ground_truth_solution = question["row"]["solution"]
        ground_truth_answer = question["row"]["answer"]

        prompt = problem

        for i in range(REPETITIONS):
            client = OpenAI()

            response = client.responses.create(
                model = OPENAI_MODEL,
                input=prompt,
                reasoning = Reasoning (effort = "none",
                                               # none (default for GPT 5.1 and 5.2) -> for low-latency interactions
                                                            # only then temperature XOR top_p or logprobs can be used
                                               # minimal - for GPT 5 nano and mini
                                               # low -> simple reasoning model, about 10-fold input size for 100 token prompt
                                               # medium (default for GPT 5), use with caution due to cost
                                               # high (default for GPT 5-Pro), use with caution due to cost
                                               # xhigh (option for GPT 5.2 Pro and 5.2)
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

            test_row = dict(problem=problem,
                            ground_truth_solution=ground_truth_solution,
                            ground_truth_answer=ground_truth_answer,
                            llm_direct_solution=response.output_text,
                            llm_answer_correct="",
                            model=OPENAI_MODEL,
                            request_date=datetime.today().strftime('%Y-%m-%d'),
                            # input tokens, cached_tokens, output_tokens, reasoning tokens, total_tokens
                            response_usage = response.usage,
                            # description on reasoning
                            response_reasoning_summary = response.reasoning.summary,
            )

            test_results.append(test_row)

    df_results = pd.DataFrame(test_results)
    df_results.to_csv(f'{OUTPUT_FILE}.csv', index=False)
    df_results.to_excel(f'{OUTPUT_FILE}.xlsx', index=False)
