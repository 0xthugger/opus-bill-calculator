# Lever 4 safety net: SHADOW MODE.
# Run the cheap model next to the expensive one on real tickets. Users still get the expensive answer.
# You only look at how often the cheap answer would have been good enough.
import json, os, sys
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
OPUS, CHEAP = "claude-opus-5-5", "claude-haiku-5-5"   # check the exact cheap model id in your console

def answer(model, ticket):
    r = client.messages.create(model=model, max_tokens=800,
                               messages=[{"role": "user", "content": ticket}])
    return r.content[0].text

def judge(ticket, a, b):
    prompt = (f"Ticket:\n{ticket}\n\nAnswer A:\n{a}\n\nAnswer B:\n{b}\n\n"
              "Is answer B at least as correct and helpful as answer A? Reply with only YES or NO.")
    return answer(OPUS, prompt).strip().upper().startswith("YES")

def main(path, n=200):
    tickets = [json.loads(l)["text"] for l in open(path)][:n]
    ok = 0
    for t in tickets:
        ref, cheap = answer(OPUS, t), answer(CHEAP, t)
        ok += judge(t, ref, cheap)
    rate = ok / len(tickets)
    print(f"cheap model good enough on {ok}/{len(tickets)} = {rate:.0%}")
    print("GO: route this class to the cheap model" if rate >= 0.95 else "NO GO: keep it on Opus")

if __name__ == "__main__":
    main(sys.argv[1])
