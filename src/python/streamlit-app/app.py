import streamlit as st
import requests
from openai import OpenAI
import os
import re

# --- Configuration ---
LLM_API_KEY = os.getenv("LLM_API_KEY")

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url="https://api.helmholtz-blablador.fz-juelich.de/v1/"
)

st.set_page_config(layout="wide")
st.title("🧮 Math LLM – Compare Raw vs Executable Answer")

# --- 1. Question Input with Button ---
# Use st.form for a better combination of input and button,
# which also handles re-running the script only when submitted.
with st.form("math_question_form"):
    question = st.text_input("Enter a math question:", key="question_input")
    # This button submits the form. The Enter key in the text_input also submits the form.
    submitted = st.form_submit_button("Send Question 🚀")

if submitted and question:
    # --- 2. Processing and Comparison ---
    with st.spinner("Processing..."):
        
        # 1️⃣ Get raw LLM answer
        raw_response = client.chat.completions.create(
            model="alias-code",
            messages=[
                {"role": "system", "content": "You are a math expert. Answer the question directly, concisely, and correctly. Make sure the answer is readable. Do not return code. Return only the answer, no justification needed."},
                {"role": "user", "content": question}
            ]
        )
        raw_answer = raw_response.choices[0].message.content.strip()

        # 2️⃣ Generate Python code
        code_response = client.chat.completions.create(
            model="alias-code",
            messages=[
                {"role": "system", "content": """
You are a Python code generator specialized in solving math problems. 

Rules:
1. Return ONLY valid Python code, no Markdown, no backticks, no explanations.
2. You may use sympy for symbolic math.
3. The code must compute the answer to the user's question and print the result using print().
4. Keep the code safe to run in a sandbox.
""" },
                {"role": "user", "content": question}
            ]
        )
        code = code_response.choices[0].message.content.strip()
        code = re.sub(r"^```[a-zA-Z]*\n", "", code)
        code = re.sub(r"\n```$", "", code)

        # 3️⃣ Execute Python code in sandbox
        exec_output = ""
        exec_error = ""
        try:
            r = requests.post(
                "http://sandbox:8000/run",
                json={"code": code},
                timeout=10
            )
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = r.json()
            exec_output = result.get("stdout", "").strip()
            exec_error = result.get("stderr", "").strip()
        except requests.exceptions.RequestException as e:
            exec_error = f"Error communicating with sandbox: {e}"
        except Exception as e:
            exec_error = f"An unexpected error occurred: {e}"

    st.subheader("Results")
    
    # 4️⃣ Display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### LLM Raw Answer 🤖")
        st.info(raw_answer)

    with col2:
        st.markdown("### Python Script Execution 🐍")
        st.code(code, language="python")
        st.text("Output:")
        st.success(exec_output if exec_output else "No output.")
        if exec_error:
            st.text("Errors:")
            st.error(exec_error)
            
    # --- 5. Match Check Conclusion ---
    if raw_answer and exec_output and not exec_error:
        comparison_prompt = f"""
I asked the following math question: {question}
The LLM returned this answer: {raw_answer}
The Python code execution returned this output: {exec_output}
Do these results match? Respond with 'Match' if they are the same or 'Mismatch' if they differ. If they differ, explain briefly.
Respond only in plain text.
"""
        comparison_response = client.chat.completions.create(
            model="alias-code",
            messages=[
                {"role": "system", "content": "You are a math expert who compares two answers and provides a clear match or mismatch conclusion."},
                {"role": "user", "content": comparison_prompt}
            ]
        )
        comparison_text = comparison_response.choices[0].message.content.strip()

        # Improved UI for the comparison result
        st.subheader("Conclusion: Match Check")
        
        if comparison_text.lower().startswith("match"):
            st.balloons()
            st.success(f"**✅ Match**")
            st.markdown(f"The LLM confirmed that the results are the same.")
        else:
            st.error(f"**❌ Mismatch**")
            st.markdown(f"The LLM detected a difference:")
            st.warning(comparison_text)

