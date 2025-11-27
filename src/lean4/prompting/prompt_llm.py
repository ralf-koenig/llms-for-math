import os
from src.blablador_client.blablador import Models, Completions
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def prompt_model(provider, input_prompt,  model = 0):
    match provider:
        case "blablador":
            model_id = model
            models = Models(api_key=os.getenv("BLABLADOR_API_KEY")).get_model_ids()
            completions = Completions(api_key=os.getenv("BLABLADOR_API_KEY"), model=models[model_id], max_tokens=68928)
            return completions.get_completion(prompt=input_prompt)
        case "scads":
            client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=os.getenv("SCADS_API_KEY"))
            models = client.models.list().data
            model = models[model]
            model_id= model.id
            print("used model: ", model_id)
            response = client.responses.create(input=input_prompt, model=model_id)
            content = response.output_text
            return content
    raise Exception("Invalid provider")

def pretty_json(json_object):
    import json
    if type(json_object) == str:
        json_object = json.loads(json_object)
    return json.dumps(json_object, indent=4, sort_keys=True)

def main(input_prompt, provider = "blablador", model = 0, ):
   return prompt_model(provider=provider, model=model , input_prompt=input_prompt)

if __name__ == '__main__':
    # for testing
    llm_response = (main(input_prompt ="whats the url of google?", model=21, provider="scads"))
    print(llm_response)