# Results Summary — MATH-500 Subset (n=100), GPT-OSS-120b

## Overall Accuracy

| Approach | Correct | Accuracy |
|----------|---------|----------|
| Pure LLM | 95/100 | 95% |
| Python/SymPy | 88/100 | 88% |
| Lean 4 | 44/100 | 44% |

## Accuracy by Difficulty Level

| Level | n | Pure LLM | Python | Lean 4 |
|-------|---|----------|--------|--------|
| 1 | 11 | 91% | 100% | 64% |
| 2 | 25 | 96% | 100% | 48% |
| 3 | 19 | 100% | 95% | 42% |
| 4 | 22 | 100% | 82% | 55% |
| 5 | 23 | 87% | 70% | 22% |

## Analysis

**Pure LLM** is the strongest approach, achieving perfect scores on Level 3 and 4 problems (100%) and only faltering at the hardest difficulty (Level 5: 87%). It solved 7 problems that neither of the other two methods could.

**Python/SymPy** is strongest on easy problems (100% on Levels 1-2) but degrades more steeply than Pure LLM at higher difficulties (Level 4: 82%, Level 5: 70%). The code generation + execution pipeline introduces failure modes — the LLM may generate incorrect code or code that doesn't produce parseable output — that outweigh any precision advantage of symbolic computation.

**Lean 4** significantly underperforms the other methods. Its best result is on the easiest problems (Level 1: 64%) and it drops to just 22% at Level 5. The main bottleneck is code generation: Lean 4's strict type system and less mature ecosystem means the LLM frequently produces code that fails to compile (e.g., type synthesis errors for numeric literals on R). Lean 4 never uniquely solved a problem that both other methods missed.

## Agreement

- All 3 correct: 41 questions
- None correct: 3 questions
- Only Pure LLM correct: 7 questions
- Only Lean 4 correct: 0 questions

## Key Takeaway

For this model, direct LLM reasoning outperforms tool-assisted approaches. The overhead of code generation introduces more errors than it prevents, particularly for Python at high difficulty and for Lean 4 across the board.