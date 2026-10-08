from router import pick_model

def test_easy_goes_cheap():
    assert pick_model("Please reset password for my account") == "haiku"

def test_unsure_escalates():
    assert pick_model("Please reset password", cheap_confidence=0.6) == "opus"

def test_hard_goes_to_opus():
    assert pick_model("Our contract renewal has a legal clause problem " * 20) == "opus"

def test_unknown_goes_to_opus():
    assert pick_model("What is the meaning of life?") == "opus"
