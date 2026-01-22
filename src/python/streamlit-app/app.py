import streamlit as st
import requests
from kimina_client import KiminaClient
from openai import OpenAI
import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG


LLM_API_KEY = os.getenv("LLM_API_KEY")

## REMOVE for debugging
LLM_API_KEY = "glpat-Go6lnd22oMrxAYx7lkkCOG86MQp1Om5uNAk.01.0z1sdbhhc"

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url="https://api.helmholtz-blablador.fz-juelich.de/v1/"
)

st.set_page_config(layout="wide")
st.title("🧮 Math LLM Evaluation Suite")

# TABS 
tab1, tab2, tab3 = st.tabs([
    "📌 Single Question Mode",
    "📁 Dataset Evaluation Mode",
    "📊 Visualize Auto-Loop Results"
])

# TAB 1 — SINGLE QUESTION MODE
with tab1:
    st.header("Raw vs Executable Answer Comparison")

    with st.form("math_question_form"):
        question = st.text_input("Enter a math question:", key="question_input_tab1")
        submitted = st.form_submit_button("Send Question 🚀")

    if submitted and question:
        with st.spinner("Processing..."):
            # RAW ANSWER
            raw_response = client.chat.completions.create(
                model="alias-code",
                messages=[
                    {"role": "system", "content": "You are a math expert. Answer concisely and directly, no code."},
                    {"role": "user", "content": question}
                ]
            )
            raw_answer = raw_response.choices[0].message.content.strip()

            # PYTHON CODE GENERATION
            code_response = client.chat.completions.create(
                model="alias-code",
                messages=[
                    {"role": "system", "content": """
                You are a Python code generator specialized in solving math problems. 
                Rules:
                1.⁠ ⁠Return ONLY valid Python code, no Markdown, no backticks, no explanations.
                2.⁠ ⁠You may use sympy for symbolic math.
                3.⁠ ⁠The code must compute the answer to the user's question and print the result using print().
                4.⁠ ⁠Keep the code safe to run in a sandbox.
                """},
                    {"role": "user", "content": question}
                ]
            )
            code = code_response.choices[0].message.content.strip()
            code = re.sub(r"^```[a-zA-Z]*\n", "", code)
            code = re.sub(r"\n```$", "", code)

            # RUN PYTHON IN SANDBOX
            exec_output = ""
            exec_error = ""
            try:
                r = requests.post(
                    "http://sandbox:8000/run",
                    json={"code": code},
                    timeout=10
                )
                r.raise_for_status()
                result = r.json()
                exec_output = result.get("stdout", "").strip()
                exec_error = result.get("stderr", "").strip()
            except Exception as e:
                exec_error = str(e)

        # DISPLAY RESULTS 
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
                st.error(exec_error)

        # MATCH CHECK
        if raw_answer and exec_output and not exec_error:
            prompt = f"""
I asked the following question: {question}
Raw LLM answer: {raw_answer}
Python output: {exec_output}
Respond with “Match” or “Mismatch” and explain briefly if mismatch.
"""
            comparison_response = client.chat.completions.create(
                model="alias-code",
                messages=[
                    {"role": "system", "content": "You compare math answers."},
                    {"role": "user", "content": prompt}
                ]
            )
            comparison_text = comparison_response.choices[0].message.content.strip()

            st.subheader("Conclusion: Match Check")
            if comparison_text.lower().startswith("match"):
                st.balloons()
                st.success("✅ Match")
            else:
                st.error("❌ Mismatch")
                st.warning(comparison_text)

# TAB 2 — DATASET EVALUATION MODE
with tab2:
    st.header("Dataset Evaluation System (Upload Mode)")

    uploaded_file = st.file_uploader("📁 Upload JSON dataset", type=["json"])
    if uploaded_file is None:
        st.info("Upload a dataset JSON file to begin.")
        st.stop()

    dataset = json.load(uploaded_file)
    rows = dataset["rows"]

    models = client.models.list().data


    def label_model(model):
        return model.id


    st.write("## Model")
    model = st.selectbox('model', models, format_func=label_model)
    model_name = model.id
    print(model_name)

    # Helper Functions

    def run_raw_llm(question):
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Return only the final math answer."},
                {"role": "user", "content": question}
            ]
        )
        return r.choices[0].message.content.strip()


    def generate_code(question):
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
            You are a Python code generator specialized in solving math problems. 
            Rules:
            1.⁠ ⁠Return ONLY valid Python code, no Markdown, no backticks, no explanations.
            2.⁠ ⁠You may use sympy for symbolic math.
            3.⁠ ⁠The code must compute the answer to the user's question and print the result using print().
            4.⁠ ⁠Keep the code safe to run in a sandbox.
            """},
                {"role": "user", "content": question}
            ]
        )
        code = r.choices[0].message.content.strip()
        code = re.sub(r"^```[a-zA-Z]*\n", "", code)
        code = re.sub(r"\n```$", "", code)
        return code


    def execute_python(code):
        try:
            r = requests.post(
                "http://sandbox:8000/run",
                json={"code": code},
                timeout=10
            )
            r.raise_for_status()
            result = r.json()
            return result.get("stdout", "").strip(), result.get("stderr", "").strip()
        except Exception as e:
            return "", str(e)


    def generate_lean(question):
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
                   You are a Lean4 code generator specialized in solving math problems. 
                   Rules:
                   1.⁠ ⁠Return ONLY valid Lean4 code, no Markdown, no backticks, no explanations.
                   2.⁠ ⁠You may use sympy for symbolic math.
                   3.⁠ ⁠The code must compute the answer to the user's question and print the result using #eval.
                   4.⁠ ⁠Keep the code safe to run in a sandbox.
                   """},
                {"role": "user", "content": question}
            ]
        )
        code = r.choices[0].message.content.strip()
        code = re.sub(r"^```[a-zA-Z]*\n", "", code)
        code = re.sub(r"\n```$", "", code)
        return code


    def execute_lean(code):
        try:
            # kimina_address = "http://localhost:80"
            kimina_address = "http://server:8000"
            # send a request to the kimina server to compile the script
            kimina_client = KiminaClient(api_url=kimina_address)  # Defaults to "http://localhost:8000", no API key
            response = kimina_client.check(code, timeout=600)
            if response.results[0].id is None:
                raise Exception('kimina server request failed', response)

            messages = response.results[0].response['messages']
            # analyse the compiler output
            # a single error == WRONG ANSWER
            # multiple info messages == multiple answers == INSPECTION NEEDED (flag)
            # single info message == ANSWER
            answer_compiler = "no answer found"
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

            return answer_compiler, response.results[0].error
        except Exception as e:
            return "ask question failed", str(e)


    #     def compare_match(q, raw, out):
    #         prompt = f"""
    # Question: {q}
    # Raw LLM answer: {raw}
    # Python output: {out}
    # Respond only 'Match' or 'Mismatch' plus brief explanation if mismatch.
    # """
    #         r = client.chat.completions.create(
    #             model="alias-code",
    #             messages=[
    #                 {"role": "system", "content": "You compare mathematical equivalence."},
    #                 {"role": "user", "content": prompt}
    #             ]
    #         )
    #         return r.choices[0].message.content.strip()

    def compare_with_ground_truth(q, code, true):
        prompt = f"""
Compare the Compiler Output with the Ground Truth. See if they match mathematically.
You are only allowed to response with either "Match" or "Mismatch" as the first Word. Also add a Explanation in the next line.

Compiler Output: {code}
Ground Truth: {true}
"""
        r = client.chat.completions.create(
            model="alias-large",
            messages=[
                {"role": "system", "content": "Evaluate exact mathematical equivalence."},
                {"role": "user", "content": prompt}
            ]
        )
        return r.choices[0].message.content.strip()


    # Single Question Selector
    st.subheader("Select a Single Question")
    row_labels = [f"{row['row_idx']} — {row['row']['unique_id']}" for row in rows]
    selected_label = st.selectbox("Pick a dataset row:", row_labels)
    idx = row_labels.index(selected_label)
    row = rows[idx]["row"]
    question = row["problem"]
    true_answer = row["answer"]
    st.write("### Problem:")
    st.info(question)
    st.write("#### Solution:")
    st.latex(true_answer)

    if model_name is not None:
        if st.button("Run Evaluation"):

            with st.spinner("Processing..."):
                raw = run_raw_llm(question)
                code = generate_code(question)
                out, err = execute_python(code)

                lean = generate_lean(question)
                out_lean, err_lean = execute_lean(lean)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Raw LLM Answer")
                st.info(raw)

                gt_raw = compare_with_ground_truth(question, raw, true_answer)
                st.subheader("Ground Truth Comparison")
                if gt_raw.lower().startswith("match"):
                    st.success("Output matches ground truth.")
                    st.info(gt_raw)
                else:
                    st.error("Output does NOT match ground truth.")
                    st.warning(gt_raw)

            with col2:
                st.subheader("Executed Python")
                st.code(code, language="python")
                st.success(out if out else "(no output)")
                if err:
                    st.error(err)

                    # Ground truth check Python
                if out and not err:
                    gt = compare_with_ground_truth(question, out, true_answer)
                    st.subheader("Ground Truth Comparison")
                    if gt.lower().startswith("match"):
                        st.success("Python output matches ground truth.")
                        st.info(gt)
                    else:
                        st.error("Python output does NOT match ground truth.")
                        st.warning(gt)

            with col3:
                st.subheader("Executed Lean")
                st.code(lean, language="coq")
                st.success(out_lean if out_lean else "(no output)")
                if err_lean:
                    st.error(err_lean)

                if out_lean and not err_lean:
                    gt_lean = compare_with_ground_truth(question, out_lean, true_answer)
                    st.subheader("Ground Truth Comparison")
                    if gt_lean.lower().startswith("match"):
                        st.success("Lean output matches ground truth.")
                        st.info(gt_lean)
                    else:
                        st.error("Lean output does NOT match ground truth.")
                        st.warning(gt_lean)

            # LLM-Python Match
            # if out and not err:
            #     match = compare_match(question, raw, out)
            #     st.subheader("LLM vs Python Match")
            #     if match.lower().startswith("match"):
            #         st.success("Match")
            #     else:
            #         st.error("Mismatch")
            #         st.warning(match)

    # Auto-Loop Dataset Evaluation
    st.markdown("")
    st.header("📊 Auto-Loop Over Entire Dataset")

    if st.button("Run Full Evaluation"):

        results = []
        progress = st.progress(0)
        total = len(rows)

        for i, item in enumerate(rows):
            r = item["row"]
            q = r["problem"]

            raw = run_raw_llm(q)
            code = generate_code(q)
            out, err = execute_python(code)

            lean = generate_lean(q)
            out_lean, err_lean = execute_lean(lean)

            if out and not err:
                gt_cmp = compare_with_ground_truth(q, out, r["answer"])
                python_correct = gt_cmp.lower().startswith("match")
            else:
                gt_cmp = "Error"
                python_correct = False

            if out_lean and not err_lean:
                gt_cmp_lean = compare_with_ground_truth(q, out_lean, r["answer"])
                lean_correct = gt_cmp.lower().startswith("match")
            else:
                gt_cmp_lean = "Error"
                lean_correct = False

            # if out and not err:
            #     llm_match = compare_match(q, raw, out)
            # else:
            #     llm_match = "Error"

            results.append({
                "ID": r["unique_id"],
                "Raw LLM Answer": raw,
                "Python Output": out,
                "Dataset Answer": r["answer"],
                "Dataset Comparison Python": gt_cmp,
                "Python Correct?": python_correct,
                # "LLM vs Python": llm_match,
                "Lean4 Output": out_lean,
                "Dataset Comparison Lean4": gt_cmp_lean,
                "Lean4 Correct?": lean_correct,
                "Model": model_name
            })

            progress.progress((i + 1) / total)

        df = pd.DataFrame(results)
        st.session_state["results_df"] = df
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "results.csv", "text/csv")

# TAB 3 — VISUALIZATION OF AUTO-LOOP RESULTS
with tab3:
    st.header("📊 Dataset Evaluation — Visual Summary")

    if "results_df" not in st.session_state:
        st.info("Run the Auto-Loop in Tab 2 to generate results.")
        st.stop()

    df = st.session_state["results_df"]
    st.subheader("Raw Results Table")
    st.dataframe(df)

    # Summary Metrics
    st.subheader("Summary Metrics")
    total = len(df)
    correct = df["Python Correct?"].sum()
    accuracy = correct / total * 100 if total > 0 else 0
    colA, colB, colC = st.columns(3)
    colA.metric("Total Questions", total)
    colB.metric("Correct Python Outputs", correct)
    colC.metric("Python Accuracy (%)", f"{accuracy:.2f}%")

    # Bar Chart: Correct vs Incorrect
    st.subheader("Correct vs Incorrect Predictions")
    counts = df["Python Correct?"].value_counts().rename(index={True: "Correct", False: "Incorrect"})
    st.bar_chart(counts)

    # Pie Chart
    st.subheader("Distribution")
    fig, ax = plt.subplots()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
    ax.set_title("Correctness Distribution")
    st.pyplot(fig)

    # LLM vs Python Match
    st.subheader("LLM vs Python Match Distribution")
    match_counts = df["LLM vs Python"].value_counts()
    st.bar_chart(match_counts)

    # Filter & Explore
    st.subheader("Filter Incorrect Predictions")
    incorrect_df = df[df["Python Correct?"] == False]
    if len(incorrect_df) == 0:
        st.success("Great! No incorrect predictions!")
    else:
        st.warning(f"{len(incorrect_df)} incorrect predictions found:")
        st.dataframe(incorrect_df)
