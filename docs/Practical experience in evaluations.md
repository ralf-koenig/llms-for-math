# Practical experience during the model evaluations

## Experiment setup

* 100 questions from Math500 dataset
* each question: 5 repetitions
* for a perfect score 500 correct answers would be needed
* The LLMs were NOT allowed any "tool use" like web search or MCP agents.

## Surprising results

* LLM input: for illustrations, especially in geometry tasks, prompts include Asymptote (asy) drawings in problem input (which can be directly integrated into LaTeX documents)
* LLMs (eg. GPT OSS 120b) can make basic sense of it, if the necessary information can be extracted easily 
* LLM input: interpretation from rendering the Asy graphics? What about third-party package imports like TrigMacros?
* LLM output: the LLMs so far did NOT produce Asymptote drawing code themselves

## Limitations

* Manual check whether the direct LLM answer result is equal to ground truth result, no check of the step-by-step path to the solution by the LLM.
* Checks whether direct LLM answer and ground truth are the same were done manually with care.
* No check whether there is a step by step explanation by the model. 
  * Reason: in verbosity=low sometimes only a result is returned and no way to this result. 
  * Other reason: in verbosity=medium, output can be 3.000 to 16.000 characters (example Qwen3 Coder Next). This would be many pages if printed.


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

* Cost problem: 

## Free for scientific use: Blablador API by Helmholtz Center 
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
* same question => can have multiple contradicting answers, mostly more correct than incorrect (majority vote could help)
* same question, same model, same reasoning, same verbosity -> can bring a correct result, can bring a false answer, can timeout (Blablador)

## ``Reasoning effort`` parameter:
* ``none`` => can come with some explanations, or only result
* ``low`` => not tried
* ``medium`` => not tried
* ``high`` => usually math problem then get with final check, sometimes not
* ``xhigh`` => not tried
 
* response can be over the reasoning token cutoff => empty result
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

Relatively easy to memorize in terms of tokens.