import cost_calc as c

def test_baseline():
    assert round(c.month()) == 4200

def test_each_lever_matches_article():
    expected = [4200, 2208, 1877, 1537, 649]
    got = [round(c.month(**kw)) for _, kw in c.steps]
    assert got == expected

def test_total_saving_is_6_5x():
    ratio = c.month() / c.month(**c.steps[-1][1])
    assert 6.4 < ratio < 6.6

def test_cache_read_is_cheaper_than_normal_input():
    pin, _, pread, pwrite = c.PRICES["opus-5.5"]
    assert pread < pin < pwrite
