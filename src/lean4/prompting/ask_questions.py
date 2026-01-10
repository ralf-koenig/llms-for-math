from dotenv import load_dotenv
from prompt_llm import prompt_model
from helpers import sanitize_llm_answer
from kimina_client import KiminaClient


load_dotenv()

def ask_question(question, model_id):

    # model 21 was openai/gpt-oss-120b, not always
    # alias-code = 9
    kimina_address = "http://localhost:80"
    inspect = False
    answer_compiler = "no answer found"
    try:
        #ask for a lean script to answer the question
        lean_script = (prompt_model("scads", question, model_id))
        sanitized_lean_script = sanitize_llm_answer(lean_script)

        # for debugging
        #sanitized_lean_script = "#eval 55 + 55"
        print(sanitized_lean_script)


        # send a request to the kimina server to compile the script
        client = KiminaClient(api_url=kimina_address)  # Defaults to "http://localhost:8000", no API key
        response = client.check(sanitized_lean_script, timeout=600)

        messages = response.results[0].response["messages"]
        # analyse the compiler output
        # a single error == WRONG ANSWER
        # multiple info messages == multiple answers == INSPECTION NEEDED (flag)
        # single info message == ANSWER
        info_counter = 0
        for message in messages:
            if message["severity"] == "error":
                answer_compiler = message["data"]
                break

            elif message["severity"] == "info":
                info_counter += 1
                if info_counter >= 2:
                    answer_compiler = messages
                    inspect = True
                    break
                answer_compiler = message["data"]

            else:
                answer_compiler = messages
                inspect = True
                break
    except Exception as e:
        raise Exception('ask question failed', e)
    results = dict(llm_answer = answer_compiler, llm_solution = sanitized_lean_script, inspection_needed=inspect)
    return results
    # for debugging
    #with open("results.json", "w", encoding='utf-8') as f:
        #json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    ask_question()
