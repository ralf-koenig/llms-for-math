import os
from dotenv import load_dotenv
import json

from config import prompt
from prompt_llm import prompt_model
from repl import compile_lean
from helpers import sanitize_llm_answer

load_dotenv()

def ask_question():

    # model 21 was openai/gpt-oss-120b, not always
    # alias-code = 9
    model_id = 18
    try:
        lean_script = (prompt_model("scads", prompt, model_id))
        sanitized_lean_script = sanitize_llm_answer(lean_script)
        answer_compiler = compile_lean(sanitized_lean_script, os.getenv('REPL_DIR'))
    except Exception as e:
        raise Exception('ask question failed', e)
    results = dict(question = prompt, ground_truth_answer = '', ground_truth_solution = '', llm_answer = answer_compiler, llm_solution = sanitized_lean_script)

    # debugging
    with open("results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ask_question()
