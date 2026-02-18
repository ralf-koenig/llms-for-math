# Practical experience during LLM direct answer evaluations

## Experiment setup

* 100 questions from Math500 dataset
* each question: 5 repetitions
* for a perfect score 500 correct answers would be needed
* The LLMs were NOT instructed for any "tool use" like web search or MCP agents. But it was also not explicitely forbidden in the prompt.

## Surprising results regarding graphics

* LLM input: for illustrations, especially in geometry tasks, prompts include Asymptote (asy) drawings in problem input (which can be directly integrated into LaTeX documents)
* LLMs (eg. GPT 5 mini, GPT OSS 120b) can make basic sense of it, if the necessary information can be extracted easily as numbers
* LLM input: interpretation from rendering the Asy graphics? What about third-party package imports like TrigMacros?
* LLM output: the LLMs so far did NOT produce Asymptote drawing code themselves, while the ground truth solution in the data set does in a number of cases

## Limitations

* Manual check whether the direct LLM answer result is equal to ground truth result was done, no check of the step-by-step path to the solution by the LLM.
* Checks whether direct LLM answer and ground truth are the same were done manually with care.
* No check whether (1) there is a step by step explanation by the model at all nor (2) whether it is entirely correct. 
  * Reason: in verbosity=low sometimes only a result is returned and no way to this result. 
  * Other reason: in verbosity=medium, output can be 3.000 to 16.000 characters for 1 question (example Qwen3 Coder Next). This would be many pages if printed. Manual checking not feasible even for this amount of runs.

## Commercial: OpenAI API servers
* hard to optimize the combination of 
  * model 
  *	inference parameters (reasoning, verbosity), 
  * number of repetitions for majority vote (to reduce hallucinations)
  * and keep overall resulting cost low (simpler models, less reasoning, less tokens in and out)

* Much quicker 
  * about 4 seconds per answer for GPT5.2, reasoning None.
  * about 7 seconds per answer for GPT-5-mini, reasoning high.
* more reliable in terms of timely response, no timeout in our evaluations.

* Cost problem: high prices for reasoning in combination with large output for frontier model
  * solutions: limit output tokens explicitly
  * use simpler models (GPT 5 mini instead of GPT 5.2) with way lower prices
  * use lower reasoning (reasoning low or none instead of high)
  * use lower value for verbosity

## Free for scientific use: Blablador API by AI Supercomputing Center Julich (Germany)
* no good documentation on API use
* takes longer for answers
* also less reliable (timeouts)
  * "Proxy Error"
  * "Model not available" 
* needs more manual error handling or retries

* one answer with reasoning=high verbosity=low takes about 20-25 seconds on average 
	=> large variance, can be two seconds or 2 minutes
	=> can be painful for interactive use
* larger jobs should be run in batch mode
* but still better than most humans solving these math problems, just not what we expect from computers, symbolic math programs, or Python code

## Hallucinations and predictability:
* same question => can have multiple contradicting answers (especially with reasoning=none),
* mostly more answers are correct than incorrect (majority vote could help)
* same question, same model, same reasoning, same verbosity -> can return: 
  * a correct result 
  * a false result
  * can timeout (Blablador)

## ``Reasoning effort`` parameter:
* ``none`` => can come with some explanations, or only result
* ``low`` => not tried
* ``medium`` => not tried
* ``high`` => usually math problem then get with final check, sometimes not
* ``xhigh`` => not tried
 
* response can be over the reasoning token cutoff => empty result returned
* more reasoning adds reasoning tokens quickly, higher cost
* reasoning tokens can take the token count for small requests with verbosity low
from 200 (100 in, 100 out) to 10.000 with the same task
* Important: Check number of reasoning tokens in the results!
* Blablador: reasoning ``high`` => can be accepted by API server, but no reasoning actually done (see: resasoning_tokens=0; ministral)
* OpenAI servers: instead will report an error for this, client then must submit parameter combinations that are allowed

## ``verbosity`` parameter
* ``low`` => can come with explanations, or only result
* ``medium`` => can be very repetitive in their argumentation; usually with final check, sometimes not; increases number of output tokens
* ``high`` => not tried for these simple math tasks, medium should be enough, high likely does not improve results
* answer can still be vary widely even for same task and same verbosity and reasoning

## Mathematical notation:
* inline LaTeX notation, often without $ signs around math expressions, but sometimes with them
* \boxed is very common for final answer, could be used for extraction
* \boxed answer often (but not always) repeated at or near the end
* in some rare cases: additional answer at the very beginning.

## Dataset "Math500" (our excerpt of 100 questions)
* many answers with very simple structure: 
  * an integer like 4, 10 or -256
  * a simple expression of two terms like 6+5i or \frac{3}{2} or 2516_8
  * a polynom  Expression like x^5-x^4+x^3-x^2+x-1
  * an ordered pair lije (2,-1)
  * a set of 2 items like {-1, 2} or 1+\sqrt{19}, 1-\sqrt{19}
  * a set of three values like {3, 5, 7}
  * a vector of 3 items like (1/3, 2/3, 5/3)

These are relatively easy to memorize in terms of tokens.
They may not be representative for more serious math tasks that
return large lists, vectors, or matrices. Or that need thoughtful
reasoning on proofs.

## Overall findings

* using LLM inference is a non-deterministic process
  * same question can be answered correctly, answered wrong or even fail to give an answer at all
  * runtime is not deterministic as well
* trade-off between cost, runtime, result quality with commercial API servers
* tested models seem capable for Math500 tasks with the direct answer, but limited generalization from there, as Math 500 dataset ist likely in training data of the models; 
* therefore, from these results no generalization is possible
* some LLMs need reasoning-effort set to at least medium to solve them (GPT 5.2, gpt 5 mini), other models without reasoning support (e.g. Qwen3 Coder Next Feb 2026) perform better right away
* accuracy of direct LLM answer drops with difficulty level even on these Math500 tasks that are likely in training data 

* many of the problems in Math 500 are relatively simple and often based on symbolic math
* assumption: they would better be handled by a symbolic math program such as Python package ``sympy`` directly, Octave, Mathematica, Wolfram Alpha, Matlab Symbolic Math Toolbox 
* using a symbolic math programm would yield a number of benefits in terms of reliability and explainability:
  * repeatability and reliable generalization for other input values 
  * reliable computations: short, correct answer
  * solutions can reliably be checked in the symbolic math program as well (back-calculation)
  * these symbolic math programs likely need way less compute resources: no GPUs, but CPUs, quicker response
  * better overall explainability from rule-based math
* some geometry tasks with vector graphics in Asymptote ( https://asymptote.ualberta.ca/ ) are especially hard to handle for these LLMs
  * long reasoning (internal modality change to images?)
  * many transmission errors (answer times out)

* as the Math500 tasks are not really tasks to prove or reject mathematical statements/hypotheses, Lean4 is not an ideal match for them
* the returned Lean4 code is partly trivial like 1-3 eval() commands on sub-results
* this eval() then only does a simple wrap up of sub-results determined by LLM itself, but is not written to solve the actual math problem
* Python code with package ``sympy`` is the better match to the Math500 questions and also looks more appropriate really tackling the math problem
