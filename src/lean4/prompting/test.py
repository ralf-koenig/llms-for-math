import json
import os
import sys
from contextlib import redirect_stdout
from io import StringIO

import pandas as pd
from huggingface_hub.utils.tqdm import progress_bar_states, tqdm

from src.lean4.prompting.ask_questions import ask_question
from src.lean4.prompting.helpers import create_new_file
from src.lean4.prompting.prompt_llm import choose_model_scads

with open('../../../data/math500.json') as json_file:
    math500 = json.load(json_file)

lean_version = "leanprover/lean4:4.27.0-rc1"
n = 10
pre_prompt = f"You are a mathematical expert. Provide only a Lean4 script (version: {lean_version}) as an answer with no explanation and no additional text.\n"
question = math500["rows"][6]["row"]["problem"]
prompt = pre_prompt + question

filename = "results"

if __name__ == '__main__':
    model_id = choose_model_scads()
    index = 0
    test_results = list()

    dataset = math500["rows"][0:n]
    #pbar = tqdm(total=n)
    for question in tqdm(dataset):

        ### EXAMPLE ROW
        #{
        #   "row_idx": 0,
        #         "row": {
        #           "problem": "Convert the point $(0,3)$ in rectangular coordinates to polar coordinates.  Enter your answer in the form $(r,\\theta),$ where $r > 0$ and $0 \\le \\theta < 2 \\pi.$",
        #           "solution": "We have that $r = \\sqrt{0^2 + 3^2} = 3.$  Also, if we draw the line connecting the origin and $(0,3),$ this line makes an angle of $\\frac{\\pi}{2}$ with the positive $x$-axis.\n\n[asy]\nunitsize(0.8 cm);\n\ndraw((-0.5,0)--(3.5,0));\ndraw((0,-0.5)--(0,3.5));\ndraw(arc((0,0),3,0,90),red,Arrow(6));\n\ndot((0,3), red);\nlabel(\"$(0,3)$\", (0,3), W);\ndot((3,0), red);\n[/asy]\n\nTherefore, the polar coordinates are $\\boxed{\\left( 3, \\frac{\\pi}{2} \\right)}.$",
        #           "answer": "\\left( 3, \\frac{\\pi}{2} \\right)",
        #           "subject": "Precalculus",
        #           "level": 2,
        #           "unique_id": "test/precalculus/807.json"
        #         },
        #   "truncated_cells": []
        #},
        problem = question["row"]["problem"]
        ground_truth_solution = question["row"]["solution"]
        ground_truth_answer = question["row"]["answer"]

        prompt = pre_prompt + problem

        results = ask_question(prompt, model_id)
        test_row = dict(problem = problem, ground_truth_answer = ground_truth_answer, ground_truth_solution = ground_truth_solution, llm_answer = results["llm_answer"], llm_solution = results["llm_solution"], inspection_needed=results["inspection_needed"])

        test_results.append(test_row)

        # results.append({
        #     "ID": r["unique_id"],
        #     "Raw LLM Answer": raw,
        #     "Python Output": out,
        #     "Dataset Answer": r["answer"],
        #     "Dataset Comparison": gt_cmp,
        #     "Python Correct?": python_correct,
        #     "LLM vs Python": llm_match
        # })

    df = pd.DataFrame(test_results)
    csv = df.to_csv(f'{filename}.csv', index=False)

    # WRITE JSON
    # result_file = create_new_file(f'{filename}.json')
    # with result_file:
    #     result_file.write(json.dumps (test_results, ensure_ascii=False, indent=4))
    #     result_file.close()

