import os
from src.blablador_client.blablador import Models, Completions
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_models_scads():
    client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=os.getenv("SCADS_API_KEY"))
    print("""Available models Scads.AI:""")
    index = 0
    for model in client.models.list().data:
        print(index, model.id)
        index = index + 1


def prompt_model(provider, input_prompt,  model):
    if provider is None or input_prompt is None or model is None:
        raise Exception("Invalid arguments", f"Provider {provider}, input prompt {input_prompt}, model {model}")
    match provider:
        case "blablador":
            try:
                model_id = model
                models = Models(api_key=os.getenv("BLABLADOR_API_KEY")).get_model_ids()
                completions = Completions(api_key=os.getenv("BLABLADOR_API_KEY"), model=models[model_id], max_tokens=68928)
                return completions.get_completion(prompt=input_prompt)
            except Exception as e:
                raise Exception(f"Error occured when trying to use blablador", e)
        case "scads":
            try:
                client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=os.getenv("SCADS_API_KEY"))
                models = client.models.list().data
                model = models[model]
                model_id = model.id
                response = client.responses.create(input=input_prompt, model=model_id)
                content = response.output_text
                return content
            except Exception as e:
                raise Exception(f"Error occured when trying to use scads", e)
    raise Exception("Invalid provider")

def choose_model_scads():
    client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=os.getenv("SCADS_API_KEY"))
    print("""Available models Scads.AI:""")
    index = 0
    for model in client.models.list().data:
        print(f"{index}:" , model.id)
        index = index + 1
    return int(input("Which model would you like to use? (Enter a NUMBER)\n"))

if __name__ == '__main__':
    # for testing
    get_models_scads()