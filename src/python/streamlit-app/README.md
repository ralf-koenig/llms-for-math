# Setup & Run


## 1. Clone the repository

```bash
git clone <your-repo-url>
cd math-llm-app
```

---

## 2. Set your LLM API key

```bash
export LLM_API_KEY="your_api_key_here"
```

## 3. Build and start the Docker containers

```bash
docker compose up --build
```

* Streamlit app will be available at: [http://localhost:8501](http://localhost:8501)
* Sandbox service runs internally on port 8000

---

## 4. Open the app in your browser

```
http://localhost:8501
```