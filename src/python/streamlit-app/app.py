import datetime
from datetime import timedelta

import streamlit as st
import requests
from openai import OpenAI
import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG


LLM_API_KEY = os.getenv("LLM_API_KEY")

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url="https://api.helmholtz-blablador.fz-juelich.de/v1/"
)

# HELPER FUNCTIONS

def strip_tags_and_thinking(text):
    """Remove HTML tags and markdown code blocks from text."""
    html_pattern = r'<[^>]+>(.|\n)*<\/[^>]+>'
    text = re.sub(html_pattern, '', text, flags=re.DOTALL)
    text = re.sub(r"^```[a-zA-Z]*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n```$", "", text)
    return text.strip()


def run_raw_llm(question, model_name):
    """Get raw LLM answer for a math question."""
    try:
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Return only the final math answer."},
                {"role": "user", "content": question}
            ]
        )
        return r.choices[0].message.content.strip(), None
    except Exception as e:
        return None, f"LLM API error: {str(e)}"


def generate_code(question, model_name):
    """Generate Python code to solve a math question."""
    try:
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
        code = strip_tags_and_thinking(code)
        return code, None
    except Exception as e:
        return None, f"Code generation error: {str(e)}"


def execute_python(code):
    """Execute Python code in sandbox and return output."""
    if code is None:
        return "", "No code to execute"
    try:
        r = requests.post(
            "http://sandbox:8000/run",
            json={"code": code},
            timeout=10
        )
        r.raise_for_status()
        result = r.json()
        return result.get("stdout", "").strip(), result.get("stderr", "").strip()
    except requests.exceptions.Timeout:
        return "", "Sandbox execution timed out"
    except requests.exceptions.ConnectionError:
        return "", "Could not connect to sandbox server"
    except Exception as e:
        return "", f"Sandbox error: {str(e)}"


def generate_lean(question, model_name):
    """Generate Lean4 code to solve a math question."""
    try:
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
                   You are a Lean4 (lean version v4.26.0) code generator specialized in solving math problems.
                   Rules:
                   1.⁠ ⁠Return ONLY valid Lean4 (lean version v4.26.0) code, no Markdown, no backticks, no explanations.
                   2.⁠ ⁠You may use Mathlib for symbolic math.
                   3.⁠ ⁠The code must compute the answer to the user's question and print the result using #eval.
                   4.⁠ ⁠Keep the code safe to run in a sandbox.
                   """},
                {"role": "user", "content": question}
            ]
        )
        code = r.choices[0].message.content.strip()
        code = strip_tags_and_thinking(code)
        return code, None
    except Exception as e:
        return None, f"Lean code generation error: {str(e)}"


def execute_lean(code):
    """Execute Lean4 code via Kimina server and return output."""
    if code is None:
        return "", "No code to execute"
    try:
        from kimina_client import KiminaClient
        kimina_address = "http://server:8000"
        kimina_client = KiminaClient(api_url=kimina_address)
        response = kimina_client.check(code, timeout=600)

        if response.results[0].id is None:
            return "Request failed", f"Kimina server error: {response}"

        messages = response.results[0].response['messages']
        answer_compiler = "no answer found"
        info_counter = 0

        for message in messages:
            if message["severity"] == "error":
                answer_compiler = message["data"]
                break
            elif message["severity"] == "info":
                info_counter += 1
                if info_counter >= 2:
                    answer_compiler = str(messages)
                    break
                answer_compiler = message["data"]
            else:
                answer_compiler = str(messages)
                break

        return answer_compiler, response.results[0].error
    except Exception as e:
        return "", f"Lean execution error: {str(e)}"


def compare_with_ground_truth(question, output, ground_truth):
    """Compare output with ground truth using LLM."""
    try:
        prompt = f"""
Compare the Compiler Output with the Ground Truth. See if they are practically the same.
You are only allowed to response with either "Match" or "Mismatch" as the first Word. Also add a Explanation in the next line.

Compiler Output: {output}
Ground Truth: {ground_truth}
"""
        r = client.chat.completions.create(
            model="alias-huge",
            messages=[
                {"role": "system", "content": "You are a Math-Tutor. You score the answers to mathematical Questions"},
                {"role": "user", "content": prompt}
            ]
        )

        return strip_tags_and_thinking(r.choices[0].message.content) , None
    except Exception as e:
        return None, f"Comparison error: {str(e)}"


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
                # Get raw LLM answer
                raw, raw_err = run_raw_llm(question, model_name)
                if raw_err:
                    st.error(f"Raw LLM failed: {raw_err}")

                # Generate and execute Python code
                code, code_err = generate_code(question, model_name)
                if code_err:
                    st.error(f"Code generation failed: {code_err}")
                out, err = execute_python(code)

                # Generate and execute Lean code
                lean, lean_gen_err = generate_lean(question, model_name)
                if lean_gen_err:
                    st.error(f"Lean generation failed: {lean_gen_err}")
                out_lean, err_lean = execute_lean(lean)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Raw LLM Answer")
                if raw:
                    st.info(raw)
                    gt_raw, gt_raw_err = compare_with_ground_truth(question, raw, true_answer)
                    st.subheader("Ground Truth Comparison")
                    if gt_raw_err:
                        st.error(f"Comparison failed: {gt_raw_err}")
                    elif gt_raw.lower().startswith("match"):
                        st.success("Output matches ground truth.")
                        st.info(gt_raw)
                    else:
                        st.error("Output does NOT match ground truth.")
                        st.warning(gt_raw)
                else:
                    st.warning("No raw answer available")

            with col2:
                st.subheader("Executed Python")
                if code:
                    st.code(code, language="python")
                else:
                    st.warning("No code generated")
                st.success(out if out else "(no output)")
                if err:
                    st.error(err)

                # Ground truth check Python
                if out and not err:
                    gt, gt_err = compare_with_ground_truth(question, out, true_answer)
                    st.subheader("Ground Truth Comparison")
                    if gt_err:
                        st.error(f"Comparison failed: {gt_err}")
                    elif gt.lower().startswith("match"):
                        st.success("Python output matches ground truth.")
                        st.info(gt)
                    else:
                        st.error("Python output does NOT match ground truth.")
                        st.warning(gt)

            with col3:
                st.subheader("Executed Lean")
                if lean:
                    st.code(lean, language="lean4")
                else:
                    st.warning("No Lean code generated")
                st.success(out_lean if out_lean else "(no output)")
                if err_lean:
                    st.error(err_lean)

                # Ground truth check Lean
                if out_lean and not err_lean:
                    gt_lean, gt_lean_err = compare_with_ground_truth(question, out_lean, true_answer)
                    st.subheader("Ground Truth Comparison")
                    if gt_lean_err:
                        st.error(f"Comparison failed: {gt_lean_err}")
                    elif gt_lean.lower().startswith("match"):
                        st.success("Lean output matches ground truth.")
                        st.info(gt_lean)
                    else:
                        st.error("Lean output does NOT match ground truth.")
                        st.warning(gt_lean)

    # Auto-Loop Dataset Evaluation
    st.markdown("")
    st.header("📊 Auto-Loop Over Entire Dataset")

    if st.button("Run Full Evaluation"):
        results = []
        errors_encountered = []
        progress = st.progress(0)
        status_text = st.empty()
        total = len(rows)

        for i, item in enumerate(rows):
            r = item["row"]
            q = r["problem"]
            status_text.text(f"Processing {i + 1}/{total}: {r.get('unique_id', 'unknown')}")

            # Get raw LLM answer
            raw, raw_err = run_raw_llm(q, model_name)
            if raw_err:
                errors_encountered.append(f"Row {i}: Raw LLM error - {raw_err}")

            # Compare raw answer with ground truth
            raw_correct = False
            gt_cmp_raw = "Error"
            if raw and not raw_err:
                gt_cmp_raw, gt_raw_err = compare_with_ground_truth(q, raw, r["answer"])
                if gt_raw_err:
                    errors_encountered.append(f"Row {i}: Raw comparison error - {gt_raw_err}")
                else:
                    raw_correct = gt_cmp_raw.lower().startswith("match")

            # Generate and execute Python code
            code, code_err = generate_code(q, model_name)
            if code_err:
                errors_encountered.append(f"Row {i}: Code generation error - {code_err}")
            out, err = execute_python(code)

            # Generate and execute Lean code
            lean, lean_err = generate_lean(q, model_name)
            if lean_err:
                errors_encountered.append(f"Row {i}: Lean generation error - {lean_err}")
            out_lean, err_lean = execute_lean(lean)

            # Compare Python output with ground truth
            python_correct = False
            gt_cmp = "Error"
            if out and not err:
                gt_cmp, gt_err = compare_with_ground_truth(q, out, r["answer"])
                if gt_err:
                    errors_encountered.append(f"Row {i}: Python comparison error - {gt_err}")
                else:
                    python_correct = gt_cmp.lower().startswith("match")

            # Compare Lean output with ground truth
            lean_correct = False
            gt_cmp_lean = "Error"
            if out_lean and not err_lean:
                gt_cmp_lean, gt_lean_err = compare_with_ground_truth(q, out_lean, r["answer"])
                if gt_lean_err:
                    errors_encountered.append(f"Row {i}: Lean comparison error - {gt_lean_err}")
                else:
                    lean_correct = gt_cmp_lean.lower().startswith("match")

            results.append({
                "ID": r["unique_id"],
                "Problem": q,
                "Ground Truth Answer": r["answer"],
                "Ground Truth Solution": r.get("solution", ""),
                "Pure LLM Answer": raw if raw else "Error",
                "Pure LLM Comparison": gt_cmp_raw,
                "Pure LLM Correct": raw_correct,
                "Python Code": code if code else "Error",
                "Python Answer": out if out else (err if err else "No output"),
                "Python Comparison": gt_cmp,
                "Python Answer Correct": python_correct,
                "Lean4 Code": lean if lean else "Error",
                "Lean4 Answer": out_lean if out_lean else (err_lean if err_lean else "No output"),
                "Lean4 Comparison": gt_cmp_lean,
                "Lean4 Answer Correct": lean_correct,
                "Model": model_name
            })

            progress.progress((i + 1) / total)

        status_text.text("Evaluation complete!")

        # Display any errors encountered
        if errors_encountered:
            with st.expander(f"⚠️ {len(errors_encountered)} errors encountered during evaluation"):
                for error in errors_encountered:
                    st.warning(error)

        df = pd.DataFrame(results)
        st.session_state["results_df"] = df
        st.dataframe(df)

        # Save results to file with safe filename
        csv = df.to_csv(index=False)
        current_date_time = datetime.datetime.now(
            tz=datetime.timezone(offset=timedelta(hours=1))
        ).strftime("%Y-%m-%d_%H-%M-%S")
        results_filename = f"/results/results_{current_date_time}.csv"

        try:
            with open(results_filename, "w", encoding="utf-8") as f:
                f.write(csv)
            st.success(f"Results saved to {results_filename}")
        except Exception as e:
            st.error(f"Failed to save results: {e}")

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

    # Python metrics
    python_correct = df["Python Answer Correct"].sum()
    python_accuracy = python_correct / total * 100 if total > 0 else 0

    # Lean metrics
    lean_correct = df["Lean4 Answer Correct"].sum()
    lean_accuracy = lean_correct / total * 100 if total > 0 else 0

    # Raw LLM metrics
    raw_correct = df["Pure LLM Correct"].sum()
    raw_accuracy = raw_correct / total * 100 if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Questions", total)
    col2.metric("Raw LLM Correct", f"{raw_correct} ({raw_accuracy:.1f}%)")
    col3.metric("Python Correct", f"{python_correct} ({python_accuracy:.1f}%)")
    col4.metric("Lean4 Correct", f"{lean_correct} ({lean_accuracy:.1f}%)")

    # Bar Chart: Comparison across methods
    st.subheader("Correctness by Method")
    comparison_data = pd.DataFrame({
        "Method": ["Raw LLM", "Python", "Lean4"],
        "Correct": [raw_correct, python_correct, lean_correct],
        "Incorrect": [total - raw_correct, total - python_correct, total - lean_correct]
    })
    st.bar_chart(comparison_data.set_index("Method"))

    # Pie Chart for Python
    st.subheader("Python Correctness Distribution")
    python_counts = df["Python Answer Correct"].value_counts().rename(
        index={True: "Correct", False: "Incorrect"}
    )
    fig, ax = plt.subplots()
    ax.pie(python_counts, labels=python_counts.index, autopct="%1.1f%%", colors=["#2ecc71", "#e74c3c"])
    ax.set_title("Python Answer Correctness")
    st.pyplot(fig)

    # Filter & Explore Incorrect
    st.subheader("Filter Incorrect Predictions")
    filter_method = st.selectbox(
        "Filter by method:",
        ["Python Incorrect", "Lean4 Incorrect", "Raw LLM Incorrect", "All Incorrect"]
    )

    if filter_method == "Python Incorrect":
        incorrect_df = df[df["Python Answer Correct"] == False]
    elif filter_method == "Lean4 Incorrect":
        incorrect_df = df[df["Lean4 Answer Correct"] == False]
    elif filter_method == "Raw LLM Incorrect":
        incorrect_df = df[df["Pure LLM Correct"] == False]
    else:
        incorrect_df = df[
            (df["Python Answer Correct"] == False) |
            (df["Lean4 Answer Correct"] == False) |
            (df["Pure LLM Correct"] == False)
        ]

    if len(incorrect_df) == 0:
        st.success("Great! No incorrect predictions for this filter!")
    else:
        st.warning(f"{len(incorrect_df)} incorrect predictions found:")
        st.dataframe(incorrect_df)
