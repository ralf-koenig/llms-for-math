import os
from dotenv import load_dotenv
from config import prompt
from prompt_llm import prompt_model
from repl import compile_lean

load_dotenv()

def ask_question():
    # model 21 is openai/gpt-oss-120b
    lean_script = (prompt_model("scads", prompt, 21))
    answer_compiler = compile_lean(lean_script, os.getenv('REPL_DIR'))

    # debugging
    with open("lean_script", "w") as f:
        f.write(answer_compiler)

if __name__ == "__main__":
    ask_question()