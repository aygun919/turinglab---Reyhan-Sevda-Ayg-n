"""
tests/test_ntm.py
Bonus B: NondeterministicTM testleri
"""

import pytest
from pathlib import Path
from turinglab.ntm import NondeterministicTM

MACHINES_DIR = Path(__file__).parent.parent / "machines"


def ntm(filename):
    return NondeterministicTM.from_yaml(MACHINES_DIR / filename)


def test_ntm_loading():
    """YAML dogru yuklenmeli."""
    m = ntm("ntm_contains_01.yaml")
    assert m.name == "ntm_contains_01"
    assert "q_accept" in m.accept_states


@pytest.mark.parametrize("inp, expected", [
    ("01",  True),
    ("001", True),
    ("101", True),
    ("10",  False),
    ("11",  False),
])
def test_contains_01_parametric(inp, expected):
    """'01' iceren diziler kabul, icermeyenler ret edilmeli."""
    m = ntm("ntm_contains_01.yaml")
    result = m.run(inp, max_depth=100, max_branches=1000)
    assert result.accepted is expected


def test_contains_01_long():
    """Uzun dizide '01' varsa kabul edilmeli."""
    m = ntm("ntm_contains_01.yaml")
    result = m.run("1110100111", max_depth=200, max_branches=5000)
    assert result.accepted is True


def test_contains_01_empty():
    """Bos girdi ret edilmeli."""
    m = ntm("ntm_contains_01.yaml")
    result = m.run("", max_depth=100, max_branches=1000)
    assert result.accepted is False


def test_ntm_result_fields():
    """NTMResult tum alanlara sahip olmali."""
    m = ntm("ntm_contains_01.yaml")
    result = m.run("01", max_depth=100, max_branches=1000)
    assert hasattr(result, "accepted")
    assert hasattr(result, "reason")
    assert hasattr(result, "steps")
    assert hasattr(result, "accepting_paths")
    assert len(result.accepting_paths) > 0


def test_ntm_accepting_path():
    """Kabul yolu donmeli."""
    m = ntm("ntm_contains_01.yaml")
    result = m.run("01", max_depth=100, max_branches=1000)
    assert result.accepted is True
    assert result.accepting_paths != []