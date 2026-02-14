# Prerequisites:
# Set OPENAI_API_KEY in an environment variable before.
# Make sure to have some budget for API usage at OpenAI. USD 5 is ok for a start.
# Watch your remaining credits at OpenAI Usage web page and remaining credit balance.

import os
import json
import pandas as pd
from datetime import datetime

from openai import OpenAI

from openai.types.shared_params.reasoning import Reasoning
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

# Repetitions per question
REPETITIONS = 5    # Warning: Keep in mind OpenAI costs for API calls !!

# maximum number of questions, max 100 for our version of math500.json which is reduced to 100 questions
MAX_QUESTION = 100   # max 100, as only 100 questions in dataset

#### OPENAI llm models
# LLM_MODEL = "gpt-5.2-pro-2025-12-11" # USE WITH CARE! Enforces reasoning effort=medium or higher!
#                                        HIGH COST QUICKLY due to many reasoning tokens even with low verbosity.
# LLM_MODEL = "gpt-5.2-2025-12-11"  # USE WITH CARE. High cost for reasoning effort = medium or high!
# LLM_MODEL = "gpt-5-mini-2025-08-07" # USE WITH CARE when combining
# LLM_MODEL = "gpt-5-nano-2025-08-07"

#### Blablador llm models
# LLM_MODEL = "0 - Ministral-3-14B-Instruct-2512 - The latest Ministral from Dec.2.2025"
LLM_MODEL = "1 - GPT-OSS-120b - an open model released by OpenAI in August 2025"
# LLM_MODEL = "2 - Qwen3 235, a great model from Alibaba with a long context size"
# LLM_MODEL = "7 - Qwen3-Coder-Next from Feb 2026"

OUTPUT_FILE = "llm_direct_answer_results"

def list_openai_models():
    model_list=[]

    # Use for OpenAI services at their OpenAI servers
    # client = OpenAI()

    # Use for Blablador services at Helmholtz Center
    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url="https://api.helmholtz-blablador.fz-juelich.de/v1/"
    )

    # Get list of available models from OpenAI metadata server
    models = client.models.list()
    # Print model IDs in sorted order
    for model in models.data:
        model_list.append(model.id)
    model_list.sort()
    print( "\n".join(model_list))
    return

if __name__ == '__main__':

    # list_openai_models()
    # exit()

    number_of_errors = 0

    start_time = f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"
    print("Start time", start_time)

    with open('../../data/math500.json') as json_file:
        math500 = json.load(json_file)

    # use only the first MAX_QUESTION questions
    dataset = math500["rows"][0:MAX_QUESTION]

    test_results = list()

    for question in dataset:

        row_idx = question["row_idx"]
        subject = question["row"]["subject"]
        level = question["row"]["level"]

        problem = question["row"]["problem"]
        ground_truth_solution = question["row"]["solution"]
        ground_truth_answer = question["row"]["answer"]

        prompt = problem

        print("row_idx", row_idx)
        for i in range(REPETITIONS):
            print("repetition", i)

            # Use for OpenAI services at their OpenAI servers
            # client = OpenAI()

            # Use for Blablador services at Helmholtz Center
            client = OpenAI(
                api_key=os.getenv("LLM_API_KEY"),
                base_url="https://api.helmholtz-blablador.fz-juelich.de/v1/"
            )

            try:
                response = client.responses.create(
                    model = LLM_MODEL,
                    input=prompt,
                    reasoning = Reasoning (effort = "high",
                                                   # none (default for GPT 5.1 and 5.2) -> for low-latency interactions
                                                                # only then temperature XOR top_p or logprobs can be used
                                                   # minimal - for GPT 5 nano and mini
                                                   # low -> simple reasoning model, about 10-fold input size for 100 token prompt
                                                   # medium (default and minimum for GPT 5.2 Pro), use with caution due to cost
                                                   # high (default for GPT 5-Pro), use with caution due to cost.
                                                   #       is most advanced option for GPT5-mini and GPT5-nano.
                                                   # xhigh (option for GPT 5.2 Pro and 5.2)
                                # summary = "auto", # organization must be verified, for analysis of reasoning process
                                           ),
                    text = ResponseTextConfigParam (verbosity = "medium"),
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
            except Exception as e:

                number_of_errors += 1
                print("Errors: ", number_of_errors)

                # simple object to fill a few attributes with essentially empty values
                # deliberately no retry to avoid increasing total run time
                response = lambda: None
                response.output_text = f"ERROR: {e}"
                response.usage="None"
                response.reasoning = lambda: None
                response.reasoning.summary = "None"


            test_row = dict(row_idx=row_idx,
                            problem=problem,
                            level=level,
                            subject=subject,
                            ground_truth_solution=ground_truth_solution,
                            ground_truth_answer=ground_truth_answer,
                            llm_direct_solution=response.output_text,
                            llm_answer_correct="",
                            count=1,
                            model=LLM_MODEL,
                            request_date=datetime.today().strftime('%Y-%m-%d'),
                            # input tokens, cached_tokens, output_tokens, reasoning tokens, total_tokens
                            response_usage = response.usage,
                            # description on reasoning
                            response_reasoning_summary = response.reasoning.summary,
            )

            test_results.append(test_row)

    df_results = pd.DataFrame(test_results)
    # df_results.to_csv(f'{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}-{OUTPUT_FILE}.csv', index=False)
    # Excel format is better for adding the field if the answer is correct manually
    df_results.to_excel(f'{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}-{OUTPUT_FILE}.xlsx', index=False)

    print("Start time", start_time)
    print("End time", f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}")
    print("Errors: ", number_of_errors)
