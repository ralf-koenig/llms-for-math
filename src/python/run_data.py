#!/usr/bin/env python3
"""
Command-line tool for evaluating math datasets against LLMs.

Replicates the Tab 2 (Dataset Evaluation Mode) functionality from the Streamlit app.
Each question is sent to the LLM three ways: direct answer, Python code generation
(executed in sandbox), and Lean4 code generation (executed via Kimina server).
Results are compared against ground truth and saved to CSV.

Usage:
    python run_data.py --dataset data/math10.json --model alias-code
    python run_data.py --dataset data/math500.json --model alias-huge --output results.csv
    python run_data.py --dataset data/math10.json --model alias-code --methods direct python
    python run_data.py --dataset data/math10.json --model alias-code --rows 0-9
"""

import argparse
import datetime
from datetime import timedelta
import functools
import json
import os
import re
import sys
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI


# --- Configuration ---
load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.helmholtz-blablador.fz-juelich.de/v1/")
SANDBOX_URL = os.getenv("SANDBOX_URL", "http://localhost:8000/run")
KIMINA_URL = os.getenv("KIMINA_URL", "http://localhost:80")


def create_client():
    if not LLM_API_KEY:
        print("Error: LLM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=LLM_API_KEY, base_url=BASE_URL)


MAX_RETRIES = 5
RETRY_DELAY = 30  # seconds


def retry_on_error(func):
    """Retry a function up to MAX_RETRIES times with RETRY_DELAY seconds between attempts."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_result = None
        for attempt in range(1, MAX_RETRIES + 1):
            result = func(*args, **kwargs)
            last_result = result
            # All wrapped functions return (value, error) tuples.
            # Retry if the error field (second element) is set.
            if result[1] is None or result[1] == "":
                return result
            if attempt < MAX_RETRIES:
                print(f"    Retry {attempt}/{MAX_RETRIES} after error: {result[1]}  "
                      f"(waiting {RETRY_DELAY}s)")
                time.sleep(RETRY_DELAY)
        print(f"    All {MAX_RETRIES} attempts failed.")
        return last_result
    return wrapper


# --- Helper Functions (same logic as app.py) ---

def strip_tags_and_thinking(text):
    """Remove thinking tags and Markdown code blocks from text."""
    html_pattern = r'(.|\n)*<\/think>'
    text = re.sub(html_pattern, '', text, flags=re.DOTALL)
    text = re.sub(r"^```[a-zA-Z]*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n```$", "", text)
    return text.strip()


@retry_on_error
def run_raw_llm(client, question, model_name):
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


@retry_on_error
def generate_code(client, question, model_name):
    """Generate Python code to solve a math question."""
    try:
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
            You are a Python code generator specialized in solving math problems.
            Rules:
            1. Return ONLY valid Python code, no Markdown, no backticks, no explanations.
            2. You may use sympy for symbolic math.
            3. The code must compute the answer to the user's question and print the result using print().
            4. Keep the code safe to run in a sandbox.
            """},
                {"role": "user", "content": question}
            ]
        )
        code = r.choices[0].message.content.strip()
        code = strip_tags_and_thinking(code)
        return code, None
    except Exception as e:
        return None, f"Code generation error: {str(e)}"


@retry_on_error
def execute_python(code):
    """Execute Python code in sandbox and return output."""
    if code is None:
        return "", "No code to execute"
    try:
        r = requests.post(SANDBOX_URL, json={"code": code}, timeout=10)
        r.raise_for_status()
        result = r.json()
        return result.get("stdout", "").strip(), result.get("stderr", "").strip()
    except requests.exceptions.Timeout:
        return "", "Sandbox execution timed out"
    except requests.exceptions.ConnectionError:
        return "", "Could not connect to sandbox server"
    except Exception as e:
        return "", f"Sandbox error: {str(e)}"


@retry_on_error
def generate_lean(client, question, model_name):
    """Generate Lean4 code to solve a math question."""
    try:
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
                   You are a Lean4 (lean version v4.26.0) code generator specialized in solving math problems.
                   Rules:
                   1. Return ONLY valid Lean4 (lean version v4.26.0) code, no Markdown, no backticks, no explanations.
                   2. You may use Mathlib for symbolic math.
                   3. The code must compute the answer to the user's question and print the result using #eval.
                   4. Keep the code safe to run in a sandbox.
                   """},
                {"role": "user", "content": question}
            ]
        )
        code = r.choices[0].message.content.strip()
        code = strip_tags_and_thinking(code)
        return code, None
    except Exception as e:
        return None, f"Lean code generation error: {str(e)}"


@retry_on_error
def execute_lean(code):
    """Execute Lean4 code via Kimina server and return output."""
    if code is None:
        return "", "No code to execute"
    try:
        from kimina_client import KiminaClient
        kimina_client = KiminaClient(api_url=KIMINA_URL)
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


@retry_on_error
def compare_with_ground_truth(client, question, output, ground_truth):
    """Compare output with ground truth using LLM."""
    try:
        prompt = f"""
Compare the compiler output with the ground truth. See if they are practically the same.
You are only allowed to respond with either "Match" or "Mismatch" as the first word. Also add an explanation in the next line.

Compiler output: {output}
Ground truth: {ground_truth}
"""
        r = client.chat.completions.create(
            model="alias-huge",
            messages=[
                {"role": "system", "content": "You are a math tutor. You score the answers to mathematical questions."},
                {"role": "user", "content": prompt}
            ]
        )
        return strip_tags_and_thinking(r.choices[0].message.content), None
    except Exception as e:
        return None, f"Comparison error: {str(e)}"


def parse_row_range(row_range_str, total):
    """Parse a row range string like '0-9' or '5' into a list of indices."""
    if row_range_str is None:
        return list(range(total))
    parts = row_range_str.split("-")
    if len(parts) == 1:
        idx = int(parts[0])
        return [idx]
    elif len(parts) == 2:
        start, end = int(parts[0]), int(parts[1])
        return list(range(start, min(end + 1, total)))
    else:
        print(f"Error: Invalid row range '{row_range_str}'", file=sys.stderr)
        sys.exit(1)


def list_models(client):
    """List available models."""
    models = client.models.list().data
    for m in models:
        print(m.id)


def run_evaluation(client, dataset_path, model_name, output_path, methods, row_range_str):
    """Run the full dataset evaluation."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    rows = dataset["rows"]
    total = len(rows)
    indices = parse_row_range(row_range_str, total)

    print(f"Dataset: {dataset_path}")
    print(f"Model: {model_name}")
    print(f"Methods: {', '.join(methods)}")
    print(f"Questions: {len(indices)} of {total}")
    print()

    results = []
    errors_encountered = []

    for count, i in enumerate(indices):
        item = rows[i]
        r = item["row"]
        q = r["problem"]
        uid = r.get("unique_id", f"row_{i}")
        print(f"[{count + 1}/{len(indices)}] Processing: {uid}")

        result_row = {
            "ID": uid,
            "Problem": q,
            "Ground Truth Answer": r["answer"],
            "Ground Truth Solution": r.get("solution", ""),
            "Model": model_name,
        }

        # --- Direct LLM answer ---
        if "direct" in methods:
            raw, raw_err = run_raw_llm(client, q, model_name)
            if raw_err:
                errors_encountered.append(f"Row {i}: Raw LLM error - {raw_err}")
                print(f"  [direct] Error: {raw_err}")

            raw_correct = False
            gt_cmp_raw = "Error"
            if raw and not raw_err:
                gt_cmp_raw, gt_raw_err = compare_with_ground_truth(client, q, raw, r["answer"])
                if gt_raw_err:
                    errors_encountered.append(f"Row {i}: Raw LLM comparison error - {gt_raw_err}")
                else:
                    raw_correct = gt_cmp_raw.lower().startswith("match")

            status = "MATCH" if raw_correct else "MISS"
            print(f"  [direct] {status}")

            result_row.update({
                "Pure LLM Answer": raw if raw else "Error",
                "Pure LLM Comparison": gt_cmp_raw,
                "Pure LLM Correct": raw_correct,
            })

        # --- Python code generation + execution ---
        if "python" in methods:
            code, code_err = generate_code(client, q, model_name)
            if code_err:
                errors_encountered.append(f"Row {i}: Python code generation error - {code_err}")
                print(f"  [python] Code gen error: {code_err}")
            out, err = execute_python(code)

            python_correct = False
            gt_cmp = "Error"
            if out and not err:
                gt_cmp, gt_err = compare_with_ground_truth(client, q, out, r["answer"])
                if gt_err:
                    errors_encountered.append(f"Row {i}: Python comparison error - {gt_err}")
                else:
                    python_correct = gt_cmp.lower().startswith("match")

            status = "MATCH" if python_correct else "MISS"
            print(f"  [python] {status}")

            result_row.update({
                "Python Code": code if code else "Error",
                "Python Answer": out if out else (err if err else "No output"),
                "Python Comparison": gt_cmp,
                "Python Answer Correct": python_correct,
            })

        # --- Lean4 code generation + execution ---
        if "lean4" in methods:
            lean, lean_err = generate_lean(client, q, model_name)
            if lean_err:
                errors_encountered.append(f"Row {i}: Lean code generation error - {lean_err}")
                print(f"  [lean4] Code gen error: {lean_err}")
            out_lean, err_lean = execute_lean(lean)

            lean_correct = False
            gt_cmp_lean = "Error"
            if out_lean and not err_lean:
                gt_cmp_lean, gt_lean_err = compare_with_ground_truth(client, q, out_lean, r["answer"])
                if gt_lean_err:
                    errors_encountered.append(f"Row {i}: Lean comparison error - {gt_lean_err}")
                else:
                    lean_correct = gt_cmp_lean.lower().startswith("match")

            status = "MATCH" if lean_correct else "MISS"
            print(f"  [lean4] {status}")

            result_row.update({
                "Lean4 Code": lean if lean else "Error",
                "Lean4 Answer": out_lean if out_lean else (err_lean if err_lean else "No output"),
                "Lean4 Comparison": gt_cmp_lean,
                "Lean4 Answer Correct": lean_correct,
            })

        results.append(result_row)

    # --- Save results ---
    df = pd.DataFrame(results)

    if output_path is None:
        current_date_time = datetime.datetime.now(
            tz=datetime.timezone(offset=timedelta(hours=1))
        ).strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"results_{current_date_time}.csv"

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nResults saved to {output_path}")

    # --- Print summary ---
    print(f"\n{'='*50}")
    print(f"SUMMARY — {len(results)} questions evaluated")
    print(f"{'='*50}")

    if "direct" in methods:
        correct = df["Pure LLM Correct"].sum()
        acc = correct / len(df) * 100 if len(df) > 0 else 0
        print(f"  Direct LLM:  {correct}/{len(df)} correct ({acc:.1f}%)")

    if "python" in methods:
        correct = df["Python Answer Correct"].sum()
        acc = correct / len(df) * 100 if len(df) > 0 else 0
        print(f"  Python:      {correct}/{len(df)} correct ({acc:.1f}%)")

    if "lean4" in methods:
        correct = df["Lean4 Answer Correct"].sum()
        acc = correct / len(df) * 100 if len(df) > 0 else 0
        print(f"  Lean4:       {correct}/{len(df)} correct ({acc:.1f}%)")

    if errors_encountered:
        print(f"\n{len(errors_encountered)} errors encountered:")
        for error in errors_encountered:
            print(f"  - {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate math datasets against LLMs (direct answer, Python, Lean4)."
    )
    parser.add_argument(
        "--dataset", "-d", required=True,
        help="Path to the JSON dataset file."
    )
    parser.add_argument(
        "--model", "-m", required=True,
        help="Model name/alias to use (e.g. alias-code, alias-huge)."
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output CSV file path. Defaults to results_<timestamp>.csv."
    )
    parser.add_argument(
        "--methods", nargs="+", default=["direct", "python", "lean4"],
        choices=["direct", "python", "lean4"],
        help="Evaluation methods to run. Default: all three."
    )
    parser.add_argument(
        "--rows", default=None,
        help="Row range to evaluate, e.g. '0-9' or '5'. Default: all rows."
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="List available models and exit."
    )

    args = parser.parse_args()
    client = create_client()

    if args.list_models:
        list_models(client)
        return

    run_evaluation(client, args.dataset, args.model, args.output, args.methods, args.rows)


if __name__ == "__main__":
    main()
