# run_data.py 

  1. Gets a direct LLM answer
  2. Generates and executes Python code (via sandbox)
  3. Generates and executes Lean4 code (via Kimina server)
  4. Compares each output against ground truth using the LLM judge
  5. Saves results to CSV with the same column structure

  CLI options:
  python run_data.py --dataset data/math10.json --model alias-code

  ## Only run specific methods
  python run_data.py -d data/math500.json -m alias-huge --methods direct python

  ## Run a subset of rows
  python run_data.py -d data/math10.json -m alias-code --rows 0-4

  ## Custom output path
  python run_data.py -d data/math10.json -m alias-code --output my_results.csv

  ## List available models
  python run_data.py -d dummy -m dummy --list-models

  ## Environment variables (same as the Streamlit app):
  - LLM_API_KEY — required, API key for the LLM service
  - LLM_BASE_URL — optional, defaults to the Helmholtz blablador endpoint
  - SANDBOX_URL — optional, defaults to http://sandbox:8000/run
  - KIMINA_URL — optional, defaults to http://server:8000

