import os
import sys
from src.blablador_client.blablador import Models, Completions
from config import prompt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()




def prompt_model(provider, input,  model = 0):
    match provider:
        case "blablador":
            model_id = model
            models = Models(api_key=os.getenv("BLABLADOR_API_KEY")).get_model_ids()
            completions = Completions(api_key=os.getenv("BLABLADOR_API_KEY"), model=models[model_id], max_tokens=68928)
            return completions.get_completion(prompt=input)
        case "scads":
            client = OpenAI(base_url="https://llm.scads.ai/v1", api_key=os.getenv("SCADS_API_KEY"))
            # Get models
            print("""
                Available models:
                """)
            for model in client.models.list().data:
                print(model.id)

            model_name = "alias-ha"

            # Use model
            response = client.chat.completions.create(messages=[{"role": "user", "content": "Tell me a joke!"}],
                                                      model=model_name)

            # Print the joke
            print("""
                Your joke:
                """)
            joke = response.choices[0].message.content
            return joke


def main(prompt, provider = "blablador", model = 0, ):
   return prompt_model(provider=provider, model=model , input=prompt)

if __name__ == '__main__':
    print(main("prompt", "scads"))