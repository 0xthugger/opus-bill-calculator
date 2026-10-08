# Cut your Opus 5.5 bill by 6x: 4 levers and the exact math

[IMAGE 01: cover]

Most teams do not have a model problem.

They have a bill problem.

Same prompt, same model, same answer. Just 6x too expensive.

In this article I take one realistic workload, price it at list prices, and pull four levers one by one. You get the formulas, the code, and a safe way to test each lever before you touch production.

A note before we start. Every dollar number below is a CALCULATION from public list prices and the assumptions I state. It is not a measurement from my own account. The script is at the end, so you can plug in your own numbers.

## The scenario

A support assistant. 100,000 requests per month.

Each request has:

- 6,000 tokens of stable text (system prompt and policy docs, the same every time)
- 500 tokens of new user text
- 800 tokens of output

Everything runs on Opus 5.5 at $4 per 1M input tokens and $20 per 1M output tokens.

Input: 650M tokens x $4 = $2,600
Output: 80M tokens x $20 = $1,600
Total: $4,200 per month

[IMAGE 02: where the money goes]

Look at the input side. 6,000 of the 6,500 input tokens are identical on every call. You are paying full price to send the same text 100,000 times.

That is lever one.

## Lever 1: cache the part that never changes

Prompt caching lets you store a long prefix and re-read it at a fraction of the price.

From Anthropic pricing for Opus 5.5:

- Normal input: $4 per 1M
- Cache write (5 minute): $5 per 1M
- Cache read: $0.20 per 1M

A cache read costs 5 percent of normal input. A write costs 25 percent more, once.

[IMAGE 03: cache lever]

Assume a 90 percent hit rate (9 of 10 calls find a warm cache):

Prefix cost per call = 6,000 x (0.9 x $0.20 + 0.1 x $5.00) / 1M = $0.00408
Before: 6,000 x $4 / 1M = $0.024

New monthly total: $2,208. That is a saving of $1,992 with zero change in answer quality, because the model sees exactly the same text.

How to do it:

```python
system=[{
    "type": "text",
    "text": POLICY,
    "cache_control": {"type": "ephemeral"},
}]
```

Three rules that break caching:

- The stable text must come FIRST. Put the changing user text after it.
- One changed character inside the prefix makes it a new prefix.
- Check `cache_read_input_tokens` in the response. If it is 0, you are not caching.

The minimum cacheable prompt for Opus 5.5 is 512 tokens, so most real system prompts qualify.

## Lever 2: stop paying live prices for work that can wait

Not every request needs an answer in 3 seconds.

Nightly summaries, ticket tagging, bulk classification, report drafts. If it can wait, use the Batch API. It gives 50 percent off both input and output, and it stacks with caching.

Assume 30 percent of your Opus work can wait.

Monthly total: $1,877. Saving: another $331.

```python
batch = client.messages.batches.create(requests=[
    {"custom_id": f"ticket-{i}",
     "params": {"model": "claude-opus-5-5", "max_tokens": 800,
                "messages": [{"role": "user", "content": t}]}}
    for i, t in enumerate(tickets)
])
```

[IMAGE 04: price table]

## Lever 3: pay less for output

Output costs 5x more than input on Opus 5.5 ($20 versus $4). So a shorter answer is the cheapest feature you can ship.

Three cheap fixes:

- Ask for a format. "Answer in max 5 sentences" or "return JSON with these 3 fields".
- Set `max_tokens` to what you really need, not to the maximum.
- Stop asking the model to repeat the question back.

Assume you cut Opus output by 25 percent (800 tokens down to 600).

Monthly total: $1,537. Saving: another $340.

One honest warning. Thinking tokens are billed as output. If your outputs are long because the model reasons a lot, a tight `max_tokens` can cut quality. Measure before you trust the number.

## Lever 4: do not send easy work to the expensive model

This is the biggest lever and the only risky one.

Many requests are easy: reset a password, send an invoice copy, give opening hours. A small model handles these well. Haiku 5.5 costs $0.10 input and $0.50 output per 1M tokens. That is 40x cheaper than Opus 5.5.

Put a cheap gate in front:

```python
def pick_model(ticket, cheap_confidence=None, threshold=0.85):
    if not is_easy(ticket):
        return "opus"
    if cheap_confidence is not None and cheap_confidence < threshold:
        return "opus"
    return "haiku"
```

Rule: the cheap model answers only when the request looks easy AND the cheap model is confident. Anything else escalates to Opus.

[IMAGE 05: the gate]

Assume 60 percent of requests qualify.

Monthly total: $649.

## The full picture

| Step | Monthly cost | Saved |
|---|---|---|
| Baseline, all Opus 5.5 | $4,200 | - |
| 1. Cache the prefix | $2,208 | $1,992 |
| 2. Batch what can wait | $1,877 | $331 |
| 3. Trim output 25% | $1,537 | $340 |
| 4. Route 60% to Haiku 5.5 | $649 | $888 |

$4,200 down to $649. That is 6.5x cheaper on paper.

[IMAGE 06: waterfall]

Notice the order. The two safest levers (caching and batch) did more than half the work, and they cannot hurt quality. Do those first.

## How to test lever 4 without breaking anything: shadow mode

Never switch traffic on a hunch. Use shadow mode.

- Users still get the Opus answer.
- In the background, the cheap model answers the same request.
- A judge compares the two.
- You count how often the cheap answer was good enough.

[IMAGE 07: shadow mode]

```python
rate = ok / len(tickets)
print(f"cheap model good enough on {ok}/{len(tickets)} = {rate:.0%}")
print("GO" if rate >= 0.95 else "NO GO: keep it on Opus")
```

My suggested rule: go only above 95 percent on that class of request, and keep Opus as the fallback for everything under the confidence threshold.

Two traps:

- A judge model can be wrong. Spot check 20 of its decisions by hand.
- Test each request class separately. "Reset password" can pass at 99 percent while "refund dispute" fails at 70.

## What I would do on Monday

- Add the cache marker to your longest prompt. 10 minutes of work, largest safe saving.
- Move anything nightly to the Batch API.
- Set honest `max_tokens` and an output format.
- Run shadow mode for one week before routing a single real user.

## Check my math

All formulas and prices are in one script. Change the five numbers at the top to match your traffic.

```python
CALLS = 100_000
PREFIX = 6_000
USER_IN = 500
OUT = 800
```

Run it and you get your own table in under a second.

## Limits of this article

- All dollar figures are calculated from list prices (checked October 2026) and my assumptions: 90 percent cache hit rate, 30 percent batchable, 25 percent shorter output, 60 percent routable. Your numbers will differ.
- Batch is applied to 30 percent of the remaining Opus calls, and Haiku calls are not batched.
- Prices change. Check the official pricing page before you plan a budget.
- This is not financial advice.

If this saved you a few thousand dollars on paper, save it and send the script to whoever owns your API bill.

Built by 0xkrystalll
