import re

def sanitize_llm_answer(string):
    string = re.sub(pattern=r"```\w*\n?", repl='', string=string).strip()
    return string.replace("\n", "\\n")