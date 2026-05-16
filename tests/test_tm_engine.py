"""
tests/test_tm_engine.py
Bölüm 1 için pytest testleri
"""

import pytest
from pathlib import Path
from turinglab import SingleTapeTM, RunResult, Configuration

MACHINES_DIR = Path(__file__).parent.parent / "machines"


def tm(filename: str) -> SingleTapeTM:
    return SingleTapeTM.from_yaml(MACHINES_DIR / filename)


def test_yaml_loading_valid():
    """Geçerli YAML başarıyla yüklenmeli."""
    machine = tm("binary_increment.yaml")
    assert machine.name == "binary_increment"
    assert "q_scan" in machine.states
    assert "q_accept" in machine.accept_states
    assert machine.blank == "B"


def test_yaml_loading_invalid_raises(tmp_path):
    """Bozuk YAML ValueError fırlatmalı."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("states: [q0\n  broken: yaml: ::::", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML parse hatası"):
        SingleTapeTM.from_yaml(bad_yaml)


def test_yaml_missing_required_field_raises(tmp_path):
    """Zorunlu alan eksikse ValueError fırlatmalı."""
    incomplete = tmp_path / "incomplete.yaml"
    incomplete.write_text("name: test\nstates: [q0]\n", encoding="utf-8")
    with pytest.raises(ValueError):
        SingleTapeTM.from_yaml(incomplete)


@pytest.mark.parametrize("inp, expected_tape", [
    ("0",    "1"),
    ("1",    "10"),
    ("101",  "110"),
    ("1011", "1100"),
    ("1111", "10000"),
])
def test_binary_increment_correct(inp, expected_tape):
    """binary_increment doğru sonuç üretmeli."""
    machine = tm("binary_increment.yaml")
    result = machine.run(inp, max_steps=500)
    assert result.accepted is True
    assert result.final_tape.strip("B") == expected_tape


@pytest.mark.parametrize("inp, expected_len", [
    ("1", 2), ("11", 3), ("111", 4), ("1111", 5), ("11111", 6),
])
def test_unary_increment_correct(inp, expected_len):
    """unary_increment bir fazla '1' üretmeli."""
    machine = tm("unary_increment.yaml")
    result = machine.run(inp, max_steps=200)
    assert result.accepted is True
    assert len(result.final_tape.strip("B")) == expected_len


@pytest.mark.parametrize("inp, should_accept", [
    ("",     True),
    ("aa",   True),
    ("aaaa", True),
    ("a",    False),
    ("aaa",  False),
])
def test_even_a_accept_reject(inp, should_accept):
    """even_a çift/tek sayıda 'a' için doğru karar vermeli."""
    machine = tm("even_a.yaml")
    result = machine.run(inp, max_steps=200)
    assert result.accepted is should_accept


def test_timeout(tmp_path):
    """max_steps aşılınca timeout dönmeli."""
    looping = tmp_path / "loop.yaml"
    looping.write_text("""
name: infinite_loop
states: [q0]
input_alphabet: ["a"]
tape_alphabet: ["a", "B"]
blank: "B"
start_state: q0
accept_states: []
reject_states: []
transitions:
  - {state: q0, read: "a", next: q0, write: "a", move: R}
  - {state: q0, read: "B", next: q0, write: "B", move: L}
""", encoding="utf-8")
    machine = SingleTapeTM.from_yaml(looping)
    result = machine.run("aaa", max_steps=50)
    assert result.accepted is False
    assert result.reason == "timeout"
    assert result.steps == 50


def test_history_length_and_fields():
    """history steps+1 adet Configuration içermeli."""
    machine = tm("binary_increment.yaml")
    result = machine.run("101", max_steps=100)
    assert result.accepted is True
    assert len(result.history) == result.steps + 1
    for config in result.history:
        assert isinstance(config, Configuration)
        assert isinstance(config.state, str)
        assert isinstance(config.head_position, int)


def test_no_transition():
    """Tanımsız geçişte no_transition dönmeli."""
    machine = tm("even_a.yaml")
    result = machine.run("b", max_steps=100)
    assert result.accepted is False
    assert result.reason == "no_transition"


def test_verbose_output_format(capsys):
    """verbose=True modunda doğru format çıkmalı."""
    machine = tm("unary_increment.yaml")
    machine.run("11", max_steps=50, verbose=True)
    captured = capsys.readouterr().out
    lines = [l for l in captured.strip().splitlines() if l]
    assert len(lines) >= 1
    for line in lines:
        assert "Adım" in line
        assert "Durum:" in line
        assert "Şerit:" in line


def test_empty_input():
    """Boş girdi doğru işlenmeli."""
    machine = tm("binary_increment.yaml")
    result = machine.run("", max_steps=100)
    assert result.accepted is True
    assert result.final_tape.strip("B") == "1"


def test_run_result_fields():
    """RunResult tüm alanlara sahip olmalı."""
    machine = tm("binary_increment.yaml")
    result = machine.run("1", max_steps=100)
    assert hasattr(result, "accepted")
    assert hasattr(result, "reason")
    assert hasattr(result, "final_tape")
    assert hasattr(result, "steps")
    assert hasattr(result, "history")
    assert isinstance(result.steps, int)