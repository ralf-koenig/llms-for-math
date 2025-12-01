import os
from dotenv import load_dotenv
from exceptiongroup import catch

from config import prompt
from prompt_llm import prompt_model
from repl import compile_lean

load_dotenv()

def ask_question():
    results = dict(question, ground_truth_answer, ground_truth_solution, llm_answer, llm_solution)
    print(results.keys())
    # model 21 was openai/gpt-oss-120b, not always
    try:
        lean_script = (prompt_model("scads", prompt, 21))
        answer_compiler = compile_lean(lean_script, os.getenv('REPL_DIR'))
    except Exception as e:
        raise Exception('ask question failed', e)
    # debugging
    with open("lean_script", "w") as f:
        f.write(answer_compiler)

if __name__ == "__main__":
    # ask_question()