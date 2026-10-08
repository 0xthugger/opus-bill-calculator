# Bill calculator for the scenario in the article.
# All prices are USD per 1M tokens, from the public Anthropic pricing page (checked Oct 2026).
# This is a CALCULATION from list prices, not a measurement.

PRICES = {
    #            input, output, cache_read, cache_write_5m
    "opus-5.5":  (4.00, 20.00, 0.20, 5.00),
    "haiku-5.5": (0.10,  0.50, 0.01, 0.125),  # prompts up to 100k tokens
}

CALLS = 100_000      # requests per month
PREFIX = 6_000       # stable tokens (system prompt + policy docs)
USER_IN = 500        # new input tokens per request
OUT = 800            # output tokens per request

def per_call(model, hit=0.0, out_scale=1.0, batch=False):
    pin, pout, pread, pwrite = PRICES[model]
    if hit > 0:
        prefix_cost = PREFIX * (hit * pread + (1 - hit) * pwrite)
    else:
        prefix_cost = PREFIX * pin
    cost = prefix_cost + USER_IN * pin + OUT * out_scale * pout
    cost = cost / 1_000_000
    return cost * (0.5 if batch else 1.0)

def month(share_haiku=0.0, hit=0.0, out_scale=1.0, batch_share=0.0):
    opus = (1 - share_haiku) * CALLS
    haiku = share_haiku * CALLS
    opus_cost = opus * ((1 - batch_share) * per_call("opus-5.5", hit, out_scale)
                        + batch_share * per_call("opus-5.5", hit, out_scale, True))
    haiku_cost = haiku * per_call("haiku-5.5", hit, 1.0)
    return opus_cost + haiku_cost

steps = [
    ("0 baseline: everything on Opus 5.5, no tricks", dict()),
    ("1 + cache the 6,000 token prefix (90% hit rate)", dict(hit=0.9)),
    ("2 + batch the 30% of Opus work that can wait", dict(hit=0.9, batch_share=0.3)),
    ("3 + trim Opus output by 25%", dict(hit=0.9, batch_share=0.3, out_scale=0.75)),
    ("4 + send 60% of easy requests to Haiku 5.5", dict(hit=0.9, batch_share=0.3, out_scale=0.75, share_haiku=0.6)),
]

if __name__ == "__main__":
    base = month()
    for name, kw in steps:
        c = month(**kw)
        print(f"{name:55s} ${c:9,.0f}  ({c/base*100:5.1f}% of baseline)")
