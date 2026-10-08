Sources and notes (checked October 2026)

- Anthropic pricing page: Opus 5.5 $4 input, $20 output, cache read $0.20, 5 min cache write $5, 1 hour write $8; Sonnet 5.5 $2/$10, cache read $0.10; Haiku 5.5 $0.10/$0.50 for prompts up to 100k tokens, cache read $0.01. https://platform.claude.com/docs/en/about-claude/pricing
- Batch API gives 50% off input and output, and stacks with prompt caching. Same pricing page.
- Prompt caching docs: 5 minute write is 1.25x input, cache read for Opus 5.5 and Sonnet 5.5 is 0.05x, minimum cacheable prompt for Opus 5.5 is 512 tokens. https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Haiku 5.5 write price of $0.125 in cost_calc.py is calculated as 1.25 x $0.10.
- The model id claude-haiku-5-5 in shadow_mode.py is a placeholder. Check the exact id in your console.
- Scenario numbers (100,000 requests, 6,000 token prefix, 500 new, 800 output, 90% hit rate, 30% batchable, 25% shorter output, 60% routable) are assumptions. All dollar results are calculated, not measured. Run cost_calc.py with your own numbers.
- Reference format only: structure of the beamnxw article was used as inspiration. No text, images or claims were copied.
