import json
import os
import sys
from src.blablador_client.blablador import Models, Completions
from config import prompt
from dotenv import load_dotenv
import subprocess


load_dotenv()
model_id = 0

models = Models(api_key=os.getenv("BLABLADOR_API_KEY")).get_model_ids()
completions = Completions(api_key=os.getenv("BLABLADOR_API_KEY"), model=models[model_id], max_tokens=100)

def prompt_model(prompt_input, completions_instance):
    return completions_instance.get_completion(prompt=prompt_input)

def read_file(path):
    with open(path) as f:
        return f.read()

def parse_lean_to_repl(lean):
    replaced_newlines = lean.replace("\n", "\\n")
    cmd_string = f'{{ "cmd": "{replaced_newlines}" }}'
    return cmd_string

def execute_lean(repl_json):
    # subprocess.run(["echo", repl_json], stdout=subprocess.PIPE)
    repl_cmd = subprocess.run(['lake', 'exe', 'repl'], input=repl_json, stdout=subprocess.PIPE, encoding='utf-8')
    return repl_cmd.stdout

def main():
   # lean = read_file("example_gpt_output.txt")
   # repl_json = parse_lean_to_repl(lean)
   # lean_messages = execute_lean(repl_json)
   return prompt_model(prompt, completions)

if __name__ == '__main__':
    # use argparse maybe
    print("Input: ", prompt)
    args = sys.argv
    output = main()
    with open("blablador_response.json", "w") as f:
        f.write(json.dumps(output))
    output_json = output
    print("Output: ", output_json["choices"][0]["text"])