# Lever 1: cache the stable prefix. Put the long, unchanging text FIRST and mark it.
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

POLICY = open("examples/policy_docs.example.txt").read()   # replace with your real 6,000 token stable prefix

def ask(ticket_text: str):
    resp = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=800,
        system=[{
            "type": "text",
            "text": POLICY,
            "cache_control": {"type": "ephemeral"},   # 5 minute cache
        }],
        messages=[{"role": "user", "content": ticket_text}],
    )
    u = resp.usage
    # If both numbers are 0, your prefix was too short or it changed between calls.
    print("cache write:", u.cache_creation_input_tokens, "cache read:", u.cache_read_input_tokens)
    return resp.content[0].text
