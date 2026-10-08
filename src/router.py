# Lever 4: a cheap gate in front of the expensive model.
# Rule of thumb: the cheap model answers only when BOTH checks pass.
EASY_WORDS = ("reset password", "change email", "invoice copy", "opening hours")

def is_easy(ticket: str) -> bool:
    t = ticket.lower()
    short = len(t) < 400
    known = any(w in t for w in EASY_WORDS)
    return short and known

def pick_model(ticket: str, cheap_confidence: float | None = None, threshold: float = 0.85) -> str:
    if not is_easy(ticket):
        return "opus"                      # hard or unknown: pay for quality
    if cheap_confidence is not None and cheap_confidence < threshold:
        return "opus"                      # cheap model unsure: escalate
    return "haiku"

if __name__ == "__main__":
    assert pick_model("Please reset password for my account") == "haiku"
    assert pick_model("Please reset password", cheap_confidence=0.6) == "opus"
    assert pick_model("Our contract renewal has a legal clause problem " * 20) == "opus"
    print("router ok")
