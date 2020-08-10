from utils import flatten, extract


def test_flat():
    assert flatten("ABC") == ["ABC"]
    assert flatten([[["A"]], "B"]) == ["A", "B"]
    assert flatten([[[]], "A"]) == ["A"]


def test_extract():
    info = {
        "A": 12,
        "B": {"B1": 12, "B2": 13,},
        "C": [{"C_Key1": "Val_C1"}, {"C_Key1": "Val_C2"}, {"C_Key2": "Val_C3"}],
        "D": {"X": {"Key": "ValX",}, "Y": {"Key": "ValY"},},
    }
    assert extract(info, "NOPATH") is None
    assert extract(info, "A") == 12
    assert extract(info, "B/B1") == 12
    assert extract(info, "B/*") == [12, 13]
    assert extract(info, "B/NOAPTH") is None
    assert extract(info, "C/C_Key1") is None
    assert extract(info, "C/0/C_Key1") == "Val_C1"
    assert extract(info, "C/*/C_Key1") == ["Val_C1", "Val_C2"]
    assert extract(info, "C/*/C_Key2") == ["Val_C3"]
    assert extract(info, "D/{X|Y}/Key") == ["KeyX", "KeyY"]
