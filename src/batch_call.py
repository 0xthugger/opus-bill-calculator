# Lever 2: send work that can wait through the Batch API (50% off input and output).
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

tickets = ["ticket one text", "ticket two text"]   # replace with your queue

batch = client.messages.batches.create(requests=[
    {
        "custom_id": f"ticket-{i}",
        "params": {
            "model": "claude-opus-5-5",
            "max_tokens": 800,
            "messages": [{"role": "user", "content": t}],
        },
    }
    for i, t in enumerate(tickets)
])
print("batch id:", batch.id, "status:", batch.processing_status)
# Poll later with client.messages.batches.retrieve(batch.id), then read results.
