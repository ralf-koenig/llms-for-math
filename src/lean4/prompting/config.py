import json

with open('../../../data/math500.json') as json_file:
    math500 = json.load(json_file)

lean_version = "leanprover/lean4:4.27.0-rc1"
pre_prompt = f"You are a mathematical expert. Provide only a Lean4 script (version: {lean_version}) as an answer with no explanation and no additional text.\n"
question = math500["rows"][1]["row"]["problem"]

prompt = pre_prompt + question