import re
from traceback import print_exc


def sanitize_llm_answer(string):
    string = re.sub(pattern=r"```\w*\n?", repl='', string=string).strip()
    #return string.replace("\n", "\\n")
    return string

def create_new_json(filename):
    try:
        f = open(filename, "x", encoding='utf-8')
    except FileExistsError as fee:
        overwrite = input(f"File {filename} already exists. Overwrite? (y/n):\n")
        if overwrite.lower() == "y":
            print(f"Overwriting existing file: {filename}")
            f = open(filename, "w", encoding='utf-8')
        else:
            print("Aborting.")
            raise fee
    return f