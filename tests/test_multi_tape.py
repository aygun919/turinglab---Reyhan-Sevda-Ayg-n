"""
tests/test_multi_tape.py
Bonus A: MultiTapeTM testleri
"""

import pytest
from pathlib import Path
from turinglab.multi_tape import MultiTapeTM

MACHINES_DIR = Path(__file__).parent.parent / "machines"


def mtm(filename):
    return MultiTapeTM.from_yaml(MACHINES_DIR / filename)


# ===========================================================================
# MultiTapeTM Motor Testleri
# ===========================================================================

def test_multi_tape_loading():
    """YAML dosyasi dogru yuklenmeli."""
    m = mtm("multi_tape_palindrome.yaml")
    assert m.name == "multi_tape_palindrome"
    assert m.num_tapes == 2
    assert "q_accept" in m.accept_states


@pytest.mark.parametrize("inp, expected", [
    ("abba", True),   # palindrom
    ("aba",  True),   # palindrom
    ("a",    True),   # tek harf
    ("bb",   True),   # iki ayni harf
    ("ab",   False),  # palindrom degil
])
def test_palindrome_parametric(inp, expected):
    """Palindrom testi dogru karar vermeli."""
    m = mtm("multi_tape_palindrome.yaml")
    result = m.run(inp, max_steps=1000)
    assert result.accepted is expected


def test_palindrome_long():
    """Uzun palindrom kabul edilmeli."""
    m = mtm("multi_tape_palindrome.yaml")
    result = m.run("abbaabba", max_steps=5000)
    assert result.accepted is True


def test_palindrome_reject():
    """Palindrom olmayan ret edilmeli."""
    m = mtm("multi_tape_palindrome.yaml")
    result = m.run("abcd", max_steps=1000)
    assert result.accepted is False


def test_multi_result_fields():
    """MultiRunResult tum alanlara sahip olmali."""
    m = mtm("multi_tape_palindrome.yaml")
    result = m.run("abba", max_steps=1000)
    assert hasattr(result, "accepted")
    assert hasattr(result, "reason")
    assert hasattr(result, "final_tapes")
    assert hasattr(result, "steps")
    assert hasattr(result, "history")
    assert len(result.final_tapes) == 2


def test_multi_timeout():
    """max_steps asilinca timeout donmeli."""
    m = mtm("multi_tape_palindrome.yaml")
    result = m.run("abba", max_steps=3)
    assert result.accepted is False
    assert result.reason == "timeout"