# Set you OPENAI_API_KEY in an environment variable before and make sure to have
# some budget for API usage.

from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    # model="gpt-5-nano",
    model="gpt-5-mini",
    # input="Write a one-sentence bedtime story about a unicorn."
    input="Work like a program for symbolic math. What is 123123123123123123123123123123123123123123123123123123123123123123123123123123 + 123123123123123123123123123123123123123123123123123123123123123123123123 ? Output only the result."
)

# correct answer:
#       123123123123123123123123123123123123123123123123123123123123123123123123123123
# +           123123123123123123123123123123123123123123123123123123123123123123123123
# ====================================================================================
#       123123246246246246246246246246246246246246246246246246246246246246246246246246

# answers by ChatGPT 5 mini (way too long!)
# First try:
# 123123123123123246246246246246246246246246246246246246246246246246246246246246246246

print(response.output_text)
