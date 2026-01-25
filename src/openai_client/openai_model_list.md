# OpenAI Models as of 2026-01-25

See description at: https://platform.openai.com/docs/models

babbage-002
chatgpt-4o-latest
chatgpt-image-latest
dall-e-2
dall-e-3
davinci-002
gpt-3.5-turbo
gpt-3.5-turbo-0125
gpt-3.5-turbo-1106
gpt-3.5-turbo-16k
gpt-3.5-turbo-instruct
gpt-3.5-turbo-instruct-0914
gpt-4
gpt-4-0125-preview
gpt-4-0613
gpt-4-1106-preview
gpt-4-turbo
gpt-4-turbo-2024-04-09
gpt-4-turbo-preview
gpt-4.1
gpt-4.1-2025-04-14
gpt-4.1-mini
gpt-4.1-mini-2025-04-14
gpt-4.1-nano
gpt-4.1-nano-2025-04-14
gpt-4o
gpt-4o-2024-05-13
gpt-4o-2024-08-06
gpt-4o-2024-11-20
gpt-4o-audio-preview
gpt-4o-audio-preview-2024-12-17
gpt-4o-audio-preview-2025-06-03
gpt-4o-mini
gpt-4o-mini-2024-07-18
gpt-4o-mini-audio-preview
gpt-4o-mini-audio-preview-2024-12-17
gpt-4o-mini-realtime-preview
gpt-4o-mini-realtime-preview-2024-12-17
gpt-4o-mini-search-preview
gpt-4o-mini-search-preview-2025-03-11
gpt-4o-mini-transcribe
gpt-4o-mini-transcribe-2025-03-20
gpt-4o-mini-transcribe-2025-12-15
gpt-4o-mini-tts
gpt-4o-mini-tts-2025-03-20
gpt-4o-mini-tts-2025-12-15
gpt-4o-realtime-preview
gpt-4o-realtime-preview-2024-12-17
gpt-4o-realtime-preview-2025-06-03
gpt-4o-search-preview
gpt-4o-search-preview-2025-03-11
gpt-4o-transcribe
gpt-4o-transcribe-diarize
gpt-5
gpt-5-2025-08-07
gpt-5-chat-latest
gpt-5-codex
gpt-5-mini
gpt-5-mini-2025-08-07
gpt-5-nano
gpt-5-nano-2025-08-07
gpt-5-pro
gpt-5-pro-2025-10-06
gpt-5-search-api
gpt-5-search-api-2025-10-14
gpt-5.1
gpt-5.1-2025-11-13
gpt-5.1-chat-latest
gpt-5.1-codex
gpt-5.1-codex-max
gpt-5.1-codex-mini
gpt-5.2
gpt-5.2-2025-12-11
gpt-5.2-chat-latest
gpt-5.2-codex
gpt-5.2-pro
gpt-5.2-pro-2025-12-11
gpt-audio
gpt-audio-2025-08-28
gpt-audio-mini
gpt-audio-mini-2025-10-06
gpt-audio-mini-2025-12-15
gpt-image-1
gpt-image-1-mini
gpt-image-1.5
gpt-realtime
gpt-realtime-2025-08-28
gpt-realtime-mini
gpt-realtime-mini-2025-10-06
gpt-realtime-mini-2025-12-15
o1
o1-2024-12-17
o1-pro
o1-pro-2025-03-19
o3
o3-2025-04-16
o3-mini
o3-mini-2025-01-31
o4-mini
o4-mini-2025-04-16
omni-moderation-2024-09-26
omni-moderation-latest
sora-2
sora-2-pro
text-embedding-3-large
text-embedding-3-small
text-embedding-ada-002
tts-1
tts-1-1106
tts-1-hd
tts-1-hd-1106
whisper-1

## Remarks

See https://platform.openai.com/docs/models for an overview.

### Frontier models

    gpt-5.2-pro, gpt-5-pro            Version of GPT-5 that produces smarter and more precise responses
    gpt-5.2-pro-2025-12-11            uses more compute to think harder and provide consistently better answers.
    gpt-5-pro-2025-10-06              Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.

    designed to tackle tough problems, some requests may take several minutes to finish
    5 Pro always reasoning.effort: high
    5.2 Pro: reasoning.effort: medium, high, xhigh.

    400,000 context window
    5 Pro: 272,000 max output tokens, 5.2 Pro: 128,000 max output tokens
    5 Pro: Sep 30, 2024 knowledge cutoff, 5.2 Pro: Aug 31, 2025 knowledge cutoff
    Reasoning token support
    5 Pro: input 15.00 USD/1M tokens, output 120.00 USD/1M tokens
    5.2 Pro: input 21.00 USD/1M tokens, output 168.00 USD/1M tokens

                                      Complex reasoning, broad world knowledge, and code-heavy or multi-step agentic tasks
    gpt-5.1 -> gpt-5.2                Flagship model for coding and agentic tasks with configurable reasoning and non-reasoning effort
    gpt-5.1-2025-11-13 -> gpt-5.2-2025-12-11  Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
    gpt-5.1-chat-latest -> gpt-5.2-chat-latest
                                      has a new "none" reasoning setting for faster responses, increased steerability in model output
    5.1: Input $1.25, cached input $0.125, output $10.00
    5.2: Input $1.75, cached input $0.175, output $14.00

    gpt-5.1-codex -> gpt-5.2-codex    Version of GPT-5 optimized for agentic coding tasks in Codex or similar environments.
    gpt-5.1-codex-mini
    same cost

    400,000 context window
    128,000 max output tokens
    5.1 Sep 30, 2024 knowledge cutoff
    5.2 Aug 31, 2025 knowledge cutoff
    Reasoning token support

    gpt-5-2025-08-07                  Previous model for coding, reasoning, and agentic tasks across domains.
                                      OpenAI recommends using the latest GPT-5.1.
    same cost as 5.1

                                      Cost-optimized reasoning and chat; balances speed, cost, and capability
    gpt-5-mini                        faster, more cost-efficient version of GPT-5. It's great for well-defined tasks and precise prompts.
    gpt-5-mini-2025-08-07             Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
    400,000 context window
    128,000 max output tokens
    May 31, 2024 knowledge cutoff
    Reasoning token support
    Input $0.25, cached input $0.025, output $2.00

                                      High-throughput tasks, especially simple instruction-following or classification
    gpt-5-nano                        fastest, cheapest version of GPT-5. It's great for summarization and classification tasks.
    gpt-5-nano-2025-08-07             Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent.
    400,000 context window
    128,000 max output tokens
    May 31, 2024 knowledge cutoff
    Reasoning token support
    Input $0.05, cached input $0.005, output $0.40
