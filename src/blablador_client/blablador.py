import requests
import json

base_url = "https://api.helmholtz-blablador.fz-juelich.de/v1"

class Models:
   
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'accept': 'application/json', 'Authorization': f'Bearer {api_key}'}

    url = base_url + "/models"
     
    def get_model_data(self):
        try:
            response = requests.get(url = self.url, headers = self.headers)
            if response.status_code > 299:
                raise ConnectionError(response.status_code, response.text)

            response = json.loads(response.text)
            return response["data"]
        except Exception as e:
            raise Exception('Get model data failed', e)

    def get_model_ids(self):
        try:
            response = requests.get(url = self.url, headers = self.headers)
            if response.status_code > 299:
                raise ConnectionError(response.status_code, response.text)

            response = json.loads(response.text)
            ids = []
            for model in response["data"]:
                ids.append(model["id"])

            return ids
        except Exception as e:
            raise Exception('Get model ids failed', e)

class Completions:

    def __init__(self, api_key, model,temperature = 0.7, choices = 1, max_tokens =  50, user = "default"):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.choices = choices
        self.max_tokens = max_tokens
        self.user = user

        self.headers = {'accept': 'application/json', 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    url = base_url + "/completions"
    
    # don't know what these are, using default values from https://helmholtz-blablador.fz-juelich.de:8000/docs#/

    suffix = "string"
    logprobs = 0
    echo = "false"
    top_p =  1 # has something to do with temperature...
    presence_penalty = 0
    frequency_penalty = 0

    def get_completion(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "n": self.choices,
            "max_tokens": self.max_tokens,
            "stop": [
                "string"
            ],
            "stream": "false",
            "top_p": self.top_p,
            "logprobs":self.logprobs,
            "echo":self.echo,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "user": self.user
        }

        payload = json.dumps(payload)

        try:
            response = requests.post(url = self.url, headers = self.headers, data=payload)
            if response.status_code > 299:
                raise ConnectionError(response.status_code, response.text)
            else:
                response = json.loads(response.text)
            return response
        except Exception as e:
            raise Exception('Get completion failed', e)
