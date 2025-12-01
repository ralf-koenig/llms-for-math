import json

with open('../../../data/math500.json') as json_file:
    math500 = json.load(json_file)

pre_prompt = "You are a mathematical expert. Provide only a Lean4 Script as an answer with no explanation and no additional text. Dont use any symbols in the answer that dont belong to the script.\n"
question = math500["rows"][1]["row"]["problem"]

prompt = pre_prompt + question