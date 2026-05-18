"""
tests/test_machines.py
Bölüm 2: 4 TM için testler
"""

import pytest
from pathlib import Path
from turinglab import SingleTapeTM

MACHINES_DIR = Path(__file__).parent.parent / "machines"


def tm(filename):
    return SingleTapeTM.from_yaml(MACHINES_DIR / filename)


# ===========================================================================
# TM-1: Unary → Binary
# ===========================================================================

@pytest.mark.parametrize("inp, expected", [
    ("1",       "1"),
    ("11",      "10"),
    ("111",     "11"),
    ("1111",    "100"),
    ("11111",   "101"),
])
def test_unary_to_binary_accept(inp, expected):
    """Unary girdi doğru binary çıktı üretmeli."""
    result = tm("unary_to_binary.yaml").run(inp, max_steps=10000)
    assert result.accepted is True
    assert result.final_tape.strip("B") == expected


def test_unary_to_binary_single():
    """Tek '1' -> '1' olmalı."""
    result = tm("unary_to_binary.yaml").run("1", max_steps=1000)
    assert result.accepted is True
    assert result.final_tape.strip("B") == "1"


def test_unary_to_binary_large():
    """Büyük girdi (8 tane 1) -> 1000 olmalı."""
    result = tm("unary_to_binary.yaml").run("11111111", max_steps=20000)
    assert result.accepted is True
    assert result.final_tape.strip("B") == "1000"


def test_unary_to_binary_wrong_symbol():
    """Yanlış sembol -> no_transition."""
    result = tm("unary_to_binary.yaml").run("0", max_steps=100)
    assert result.accepted is False
    assert result.reason == "no_transition"
# ===========================================================================
# TM-2: Binary Karşılaştırma
# ===========================================================================

@pytest.mark.parametrize("inp, expected", [
    ("1011#1010", True),   # 11 > 10 → kabul
    ("1100#1011", True),   # 12 > 11 → kabul
    ("1#0",       True),   # 1 > 0 → kabul
    ("1010#1011", False),  # 10 < 11 → ret
    ("1010#1010", False),  # 10 = 10 → ret
])
def test_binary_compare(inp, expected):
    """binary_compare doğru kabul/ret kararı vermeli."""
    result = tm("binary_compare.yaml").run(inp, max_steps=2000)
    assert result.accepted is expected


def test_binary_compare_zero():
    """0 > 0 eşit olduğu için ret etmeli."""
    result = tm("binary_compare.yaml").run("0#0", max_steps=500)
    assert result.accepted is False


def test_binary_compare_empty_reject():
    """Sağ taraf yoksa no_transition veya reject olmalı."""
    result = tm("binary_compare.yaml").run("1#0", max_steps=500)
    assert result.accepted is True
# ===========================================================================
# TM-3: Dizgi Kopyalayıcı
# ===========================================================================

@pytest.mark.parametrize("inp, expected", [
    ("a",    "a#a"),
    ("b",    "b#b"),
    ("ab",   "ab#ab"),
    ("abba", "abba#abba"),
    ("ba",   "ba#ba"),
])
def test_string_copy_accept(inp, expected):
    """string_copy doğru kopyayı üretmeli."""
    result = tm("string_copy.yaml").run(inp, max_steps=10000)
    assert result.accepted is True
    assert result.final_tape.strip("B") == expected


def test_string_copy_wrong_symbol():
    """Yanlış sembol -> no_transition."""
    result = tm("string_copy.yaml").run("1", max_steps=100)
    assert result.accepted is False
    assert result.reason == "no_transition"


def test_string_copy_single_a():
    """Tek 'a' -> 'a#a' olmalı."""
    result = tm("string_copy.yaml").run("a", max_steps=1000)
    assert result.accepted is True
    assert result.final_tape.strip("B") == "a#a"
# ===========================================================================
# TM-4: Parantez Denge Kontrolü
# ===========================================================================

@pytest.mark.parametrize("inp, expected", [
    ("()",     True),   # basit çift
    ("(())",   True),   # iç içe
    ("(()())", True),   # karma
    ("((",     False),  # açık kaldı
    (")",      False),  # sadece kapanış
])
def test_student_choice_parametric(inp, expected):
    """Parantez denge kontrolü doğru karar vermeli."""
    result = tm("student_choice.yaml").run(inp, max_steps=1000)
    assert result.accepted is expected


def test_student_choice_empty():
    """Boş girdi kabul edilmeli."""
    result = tm("student_choice.yaml").run("", max_steps=100)
    assert result.accepted is True


def test_student_choice_wrong_order():
    """Ters sıra -> ret."""
    result = tm("student_choice.yaml").run(")(", max_steps=100)
    assert result.accepted is False       