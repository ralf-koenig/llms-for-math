# Benchmarking Program-Aided vs. Natural Language Mathematical Reasoning in LLMs

**10-Minute Presentation**

---

## 0. What Have We Done?

- Benchmarked **program-aided** language models against **non-aided** language models on mathematical tasks
- Compared the mathematical performance of state-of-the-art LLMs across three modalities:
    - **Natural language** reasoning (direct answers)
    - **Python interpreter** (code generation + execution)
    - **LEAN4 interpreter** (formal proof generation + verification)

---

## 1. Motivation (2 Minutes)

### Breakthrough: LLMs + LEAN4 for Mathematical Proofs

- **AlphaProof** (Google DeepMind, Nov 2025) achieved silver-medal performance at IMO 2024
    - Solved 3 of 6 problems, including P6 — the hardest problem, solved by only 5 of 609 human participants
    - Scored 28 out of 42 points
- **Formal verification** with LEAN4 enables automatic checking of mathematical correctness, effectively eliminating the hallucination problem

> **Ref:** Hubert, T. et al. (2025). Olympiad-level formal mathematical reasoning with reinforcement learning. _Nature_. https://doi.org/10.1038/s41586-025-09833-y

### At the Same Time: Complete Reasoning Breakdown on Simple Tasks

- State-of-the-art models suffer complete breakdowns on deceptively simple problems
- **Alice in Wonderland problem:** _"Alice has N brothers and M sisters. How many sisters does Alice's brother have?"_
    - Top models frequently answer incorrectly despite the trivial logic involved

*TODO Add Reference*
### Therefore: Our Research Goals

1. Analyze the mathematical performance of LLMs using **simple zero-shot prompts** — the way a typical user would interact with them
2. Compare performance when the same LLM is aided by **Python** and **LEAN4** interpreters, to see if accuracy can be easily improved
3. Test whether **code-specialized LLMs** outperform general-purpose LLMs when paired with a code interpreter
4. Build a **user interface** for side-by-side comparison of LLM answers across all three modalities (natural language, Python, LEAN4)

### Zero-Shot Prompting

Zero-shot prompting means giving the model a task without any worked examples or prior demonstrations — just the question itself. This reflects how a typical end-user would interact with an LLM, and establishes a realistic baseline for performance.

### Why Python?

- Dominant language in AI/ML research — LLMs have seen vast amounts of Python training data
- Rich ecosystem of mathematical libraries (NumPy, SciPy, SymPy)
- LLMs can generate executable Python code that offloads arithmetic to a deterministic interpreter

### Why LEAN4?

- Purpose-built for **formal mathematical proof**
- **Deterministic:** identical input always produces the same verified output
- **Binary correctness:** a proof either verifies or it doesn't — no confidence scores or trust required
- Every inference step is **auditable and traceable**

---

## 2. State of the Art (2–3 Minutes)

### LLMs as Middlemen: Code Generation as a Solution Strategy

Beyond AlphaProof, several sophisticated systems improve mathematical performance by pairing LLMs with code interpreters to mitigate arithmetic and reasoning failures.

**PAL (Program-Aided Language Models):**

- LLM translates natural language problems → Python code; interpreter executes calculations
- Achieved a **15% absolute improvement** over Chain-of-Thought prompting on GSM8K

> **Ref:** Gao, L. et al. (2023). PAL: Program-aided Language Models. _ICML 2023_.

**Example Workflow:**

```
User: "A tank has 18,000 gallons capacity. Wanda filled 1/4..."
   ↓
LLM generates:
   tank_capacity = 18000
   wanda_fill = tank_capacity * (1/4)
   ...
   ↓
Python interpreter executes → deterministic, correct result
```

**ToRA (Tool-integrated Reasoning Agent):**

- Interleaves natural-language reasoning with tool calls (Python, etc.) across multiple steps
- Achieved 44% on MATH with CodeLlama; up to **72% with GPT-4**

> **Ref:** Gou, Z. et al. (2024). ToRA: A Tool-Integrated Reasoning Agent. _ICLR 2024_.

**MathCoder:**

- Fine-tunes LLMs to seamlessly switch between natural language and code within a single solution
- Achieved **45.2% on MATH**

> **Ref:** Wang, K. et al. (2024). MathCoder: Seamless Code Integration in LLMs for Enhanced Mathematical Reasoning. _ICLR 2024_.

### Mathematical Benchmarks

| Benchmark    | Description                                     | Top Performance     |
| ------------ | ----------------------------------------------- | ------------------- |
| **MATH-500** | 500 diverse problems across 5 difficulty levels | >90% for top models |

> **Ref:** Hendrycks, D. et al. (2021). Measuring Mathematical Problem Solving With the MATH Dataset. _NeurIPS 2021_.

### General-Purpose vs. Coding-Specialized LLMs

| Type                   | Examples                | Strengths                                            |
| ---------------------- | ----------------------- | ---------------------------------------------------- |
| **General-Purpose**    | GPT-4, Claude, Gemini   | Broad world knowledge, strong language understanding |
| **Coding-Specialized** | GLM-4.7, DeepSeek-Coder | Optimized code generation, agent-oriented workflows  |

---

## 3. Hypotheses (1 Minute)

### H1: Easy problems are solvable across all modalities

> _A general-purpose LLM can answer easy mathematical questions directly and coherently, and can also generate correct code for easy tasks._

- **Expected:** High accuracy on MATH-500 Level 1–2 across natural language, Python, and LEAN4

### H2: Hard problems benefit from code generation

> _A general-purpose LLM fails on difficult mathematical questions when reasoning in natural language, but can generate code that solves them._

- **Expected:** Significant accuracy drop on Level 4–5 for natural language; improved accuracy when using Python
- **Caveat:** On the hardest problems, the LLM may also fail to generate correct code zero-shot (no feedback loop)

### H3: Coding-specialized LLMs outperform general-purpose LLMs as program-aided models

> _When paired with a code interpreter, coding-specialized LLMs achieve higher accuracy than general-purpose LLMs._

- **Basis:** o1-mini scores 90% on MATH-500 but only 62.3% on HardMath-mini; GPT-4 scores 43.8% on HardMath

> **Ref:** Fan, J. et al. (2024). HARDMATH: A Benchmark Dataset for Challenging Problems in Applied Mathematics. _NeurIPS 2024_.

### H4: Zero-shot LEAN4 proof generation has very low success rates

> _Generating valid formal proofs without fine-tuning or guided search is significantly harder than generating Python code, resulting in near-zero accuracy for zero-shot LEAN4._

- **Rationale:** Formal proof requires precise tactic sequences with no tolerance for approximation — a much narrower target than executable Python

---

## 4. Implementation (2–3 Minutes)

### 4.1 Dataset: MATH-500

- **500 diverse problems** from the MATH benchmark (HuggingFace: AI-ModelScope/MATH-500)
- **5 difficulty levels** (Level 1 = easiest, Level 5 = hardest)
- **7 topic areas:** Algebra, Geometry, Number Theory, Probability, Trigonometry, Counting & Combinatorics, Precalculus
- Answers provided in LaTeX format: `\boxed{answer}`

> **Ref:** Hendrycks, D. et al. (2021). _NeurIPS 2021_.

### 4.2 Models

#### Model 1: [TBD — General-Purpose LLM via Blablador]

- **Type:** Open-source general-purpose LLM
- **Role:** Baseline for natural language reasoning and general code generation
- _(Finalize once Blablador model catalog is confirmed)_

#### Model 2: GLM-4.7 (Z.ai)

- **Type:** Open-source coding-specialized agent
- **Parameters:** 358B (Mixture of Experts)
- **Release:** December 22, 2025
- **Key benchmarks:**
    - SWE-bench Verified: 73.8%
    - SWE-bench Multilingual: 66.7%
    - HLE (Humanity's Last Exam): 42.8% (+12.4 pp vs. predecessor)
- **Notable feature:** "Preserved Thinking" — maintains coherent reasoning across multi-turn conversations

> **Ref:** Z.ai (2025). GLM-4.7: Advancing the Coding Capability. https://z.ai/blog/glm-4.7

### 4.3 Infrastructure: Blablador (Helmholtz)

- Open-source inference server operated by Forschungszentrum Jülich
- Designed for scientific LLM applications — free for researchers with a Helmholtz/Eduroam account
- Provides an **OpenAI-compatible API** with a catalog of hosted models — no private infrastructure required

> **Ref:** Strube (2024). Helmholtz Blablador: An Inference Server for Scientific LLMs. _Helmholtz AI Conference 2024_.

### 4.4 Execution Environments

#### Python Sandbox

- Isolated, sandboxed execution environment (no system access)
- Timeout mechanism to guard against infinite loops
- Access to mathematical libraries: `math`, `numpy`, `sympy`

#### Kimina-LEAN-Server

- Server wrapping the LEAN4 toolchain for remote proof verification
- Accepts LLM-generated tactic sequences and returns verification results (verified / error)
- Enables fast, secure proof checking without requiring a local LEAN4 installation
*TODO add Reference*
### 4.5 Evaluation

#### Automatic Pre-Check: LLM-as-Judge

Because answers can appear in many equivalent formats (e.g., `\frac{4}{3}` vs. `4/3` vs. `1.333...`), simple string matching is insufficient. We use an LLM-as-Judge to handle **LaTeX normalization and semantic equivalence**:

- A capable LLM compares each model's output against the ground truth
- Responds with **"Match"** or **"Mismatch"**, followed by a brief explanation
- Prompt design:

> _"Compare the Compiler Output with the Ground Truth. See if they are practically the same. You are only allowed to respond with either 'Match' or 'Mismatch' as the first word. Also add an explanation in the next line._ _Compiler Output: {output}_ _Ground Truth: {ground_truth}"_

#### Manual Evaluation of Solution Paths

For deeper analysis beyond final-answer correctness:

- **Accuracy:** Is the final answer correct?
- **Reasoning quality:** Are intermediate steps logical and comprehensible?
- **Completeness:** Are important steps missing?

**Error type classification:**

- Complete misunderstanding of the problem
- Partial misunderstanding
- Wrong method chosen
- Correct method, incorrectly applied
- Calculation/arithmetic error
- No solution produced

---

## 5. Results _(to be completed)_

### Planned Metrics

- Accuracy per difficulty level (1–5) across all three modalities
- Accuracy comparison: natural language vs. Python vs. LEAN4
- Error type distribution per modality and difficulty level
- Head-to-head: general-purpose LLM vs. coding-specialized LLM

### Planned Visualizations

- Grouped bar chart: accuracy by difficulty level × modality
- Error type breakdown table
- Model comparison summary table

---

## 6. Discussion (1–2 Minutes)

### LLMs Are Surprisingly Performant — But Not Truly Reasoning

- Significant progress in recent years; reasoning-oriented models (o1, DeepSeek-R1) show strong mathematical capabilities
- However, benchmark performance does not equal genuine understanding

### Zero-Shot Code Generation Has Clear Limitations

- Without a feedback loop, complex tasks frequently fail due to syntax errors, missing imports, or logical errors in code
- On **Level 5 problems**, the LLM may also fail to generate correct code — zero-shot has no self-correction mechanism
- **Advanced pipelines** substantially outperform our simple setup:
    - MathCoder: specialized fine-tuning + code integration → 45.2% on MATH
    - ToRA: multi-tool integration with iterative reasoning
    - PAL + Self-Consistency: multiple samples + majority voting

### Trivial Errors Persist on Simple Tasks

- LLMs still fail at surprisingly simple tasks: counting letters, comparing decimals (9.9 vs. 9.11), basic family-relationship reasoning, arithmetic with large numbers
- "Unpuzzles" — trivialized versions of standard puzzles — lead to _worse_ performance, suggesting pattern matching rather than true reasoning

> **Ref:** Nezhurina et al. (2024). Alice in Wonderland: Simple Tasks Showing Complete Reasoning Breakdown in State-Of-the-Art Large Language Models. _arXiv_.

### Implications for Practice

1. **Code generation with verification** is more robust than direct natural-language reasoning
2. **Multi-step pipelines** with feedback loops significantly improve results over zero-shot approaches
3. **Formal languages** (LEAN4, Coq) offer correctness guarantees that natural language and Python cannot provide

---

## References

1. Hubert, T. et al. (2025). Olympiad-level formal mathematical reasoning with reinforcement learning. _Nature_. https://doi.org/10.1038/s41586-025-09833-y
2. Gao, L. et al. (2023). PAL: Program-aided Language Models. _ICML 2023_. https://arxiv.org/abs/2211.10435
3. Hendrycks, D. et al. (2021). Measuring Mathematical Problem Solving With the MATH Dataset. _NeurIPS 2021_.
4. Wang, K. et al. (2024). MathCoder: Seamless Code Integration in LLMs for Enhanced Mathematical Reasoning. _ICLR 2024_.
5. Fan, J. et al. (2024). HARDMATH: A Benchmark Dataset for Challenging Problems in Applied Mathematics. _NeurIPS 2024_.
6. Gou, Z. et al. (2024). ToRA: A Tool-Integrated Reasoning Agent for Mathematical Problem Solving. _ICLR 2024_.
7. Nezhurina, M. et al. (2024). Alice in Wonderland: Simple Tasks Showing Complete Reasoning Breakdown in State-Of-the-Art Large Language Models. _arXiv_.
8. Cobbe, K. et al. (2021). Training Verifiers to Solve Math Word Problems. _arXiv:2110.14168_.
9. Z.ai (2025). GLM-4.7: Advancing the Coding Capability. https://z.ai/blog/glm-4.7
10. Strube (2024). Helmholtz Blablador: An Inference Server for Scientific LLMs. _Helmholtz AI Conference 2024_.

---

## Time Schedule

|Section|Time|
|---|---|
|1. Motivation|2 min|
|2. State of the Art|2–3 min|
|3. Hypotheses|1 min|
|4. Implementation|2–3 min|
|5. Results|1 min|
|6. Discussion|1–2 min|
|**Total**|**~10 min**|