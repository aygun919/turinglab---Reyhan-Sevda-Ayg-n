"""
TuringLab - Tek Şeritli Turing Makinesi Motoru
Bölüm 1: Deterministic Single-Tape Turing Machine
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import yaml


@dataclass
class Configuration:
    """Bir hesaplama adımındaki anlık makine konfigürasyonu."""
    state: str
    tape: str
    head_position: int


@dataclass
class RunResult:
    """tm.run() çağrısından dönen sonuç nesnesi."""
    accepted: bool
    reason: str
    final_tape: str
    steps: int
    history: list[Configuration] = field(default_factory=list)


class Tape:
    """
    Sonsuz genişleyebilen Turing makinesi şeridi.
    Dahili olarak dict[int, str] kullanır — negatif indeks güvenli.
    """

    def __init__(self, input_string: str, blank: str = "B") -> None:
        self.blank = blank
        self._cells: dict[int, str] = {}
        for i, ch in enumerate(input_string):
            self._cells[i] = ch

    def read(self, pos: int) -> str:
        """Verilen konumdaki sembolü oku; yazılmamışsa blank döner."""
        return self._cells.get(pos, self.blank)

    def write(self, pos: int, symbol: str) -> None:
        """Verilen konuma sembol yaz."""
        self._cells[pos] = symbol

    def to_string(self, head_pos: Optional[int] = None) -> str:
        """Şeridi okunabilir string olarak döndürür. Kafa köşeli parantez içinde."""
        if not self._cells:
            return f"[{self.blank}]" if head_pos == 0 else self.blank

        min_pos = min(self._cells)
        max_pos = max(self._cells)

        if head_pos is not None:
            min_pos = min(min_pos, head_pos)
            max_pos = max(max_pos, head_pos)

        result = []
        for pos in range(min_pos, max_pos + 2):
            ch = self._cells.get(pos, self.blank)
            if head_pos is not None and pos == head_pos:
                result.append(f"[{ch}]")
            else:
                result.append(ch)
        return "".join(result)

    def to_plain_string(self) -> str:
        """Kafa göstergesi olmadan düz string döndürür."""
        if not self._cells:
            return self.blank
        min_pos = min(self._cells)
        max_pos = max(self._cells)
        return "".join(self._cells.get(p, self.blank) for p in range(min_pos, max_pos + 1))


class SingleTapeTM:
    """
    Deterministic Single-Tape Turing Machine.
    YAML dosyasından yüklenir; run() ile çalıştırılır.
    """

    def __init__(self, config: dict) -> None:
        self._validate_config(config)
        self.name: str = config.get("name", "unnamed")
        self.description: str = config.get("description", "")
        self.states: set[str] = set(config["states"])
        self.input_alphabet: set[str] = set(config["input_alphabet"])
        self.tape_alphabet: set[str] = set(config["tape_alphabet"])
        self.blank: str = config["blank"]
        self.start_state: str = config["start_state"]
        self.accept_states: set[str] = set(config["accept_states"])
        self.reject_states: set[str] = set(config.get("reject_states", []))
        self._transitions: dict[tuple[str, str], tuple[str, str, str]] = {}
        for t in config.get("transitions", []):
            key = (t["state"], t["read"])
            self._transitions[key] = (t["next"], t["write"], t["move"])

    @classmethod
    def from_yaml(cls, path: str | Path) -> "SingleTapeTM":
        """
        YAML dosyasından TM yükler.
        Raises: ValueError, FileNotFoundError
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML dosyası bulunamadı: {path}")
        with open(path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"YAML parse hatası ({path}): {e}") from e
        if not isinstance(config, dict):
            raise ValueError(f"YAML dosyası geçerli bir sözlük değil: {path}")
        return cls(config)

    @staticmethod
    def _validate_config(config: dict) -> None:
        """Zorunlu alanları doğrular. Raises: ValueError"""
        required = ["states", "input_alphabet", "tape_alphabet",
                    "blank", "start_state", "accept_states", "transitions"]
        for field_name in required:
            if field_name not in config:
                raise ValueError(f"YAML'da zorunlu alan eksik: '{field_name}'")
        if config["blank"] not in config["tape_alphabet"]:
            raise ValueError(f"Blank sembolü şerit alfabesinde bulunmuyor.")
        if config["start_state"] not in config["states"]:
            raise ValueError(f"Başlangıç durumu durum listesinde yok.")
        for s in config["accept_states"]:
            if s not in config["states"]:
                raise ValueError(f"Kabul durumu '{s}' durum listesinde yok.")

    def run(self, input_string: str, max_steps: int = 10_000, verbose: bool = False) -> RunResult:
        """
        TM'yi verilen girdi üzerinde çalıştırır.

        Args:
            input_string: Başlangıç girdisi
            max_steps: Timeout için maksimum adım sayısı
            verbose: True ise her adım ekrana yazdırılır

        Returns:
            RunResult nesnesi
        """
        tape = Tape(input_string, blank=self.blank)
        current_state = self.start_state
        head = 0
        history: list[Configuration] = []

        def snapshot() -> Configuration:
            return Configuration(
                state=current_state,
                tape=tape.to_string(head),
                head_position=head,
            )

        history.append(snapshot())
        if verbose:
            print(f"Adım 0 | Durum: {current_state} | Şerit: {tape.to_string(head)} | Hareket: -")

        for step in range(1, max_steps + 1):
            if current_state in self.accept_states:
                return RunResult(
                    accepted=True, reason="accept",
                    final_tape=tape.to_plain_string(),
                    steps=step - 1, history=history,
                )
            if current_state in self.reject_states:
                return RunResult(
                    accepted=False, reason="reject",
                    final_tape=tape.to_plain_string(),
                    steps=step - 1, history=history,
                )

            symbol = tape.read(head)
            key = (current_state, symbol)

            if key not in self._transitions:
                return RunResult(
                    accepted=False, reason="no_transition",
                    final_tape=tape.to_plain_string(),
                    steps=step - 1, history=history,
                )

            next_state, write_symbol, direction = self._transitions[key]
            tape.write(head, write_symbol)

            if direction == "R":
                head += 1
            elif direction == "L":
                head -= 1

            current_state = next_state
            history.append(snapshot())

            if verbose:
                print(f"Adım {step} | Durum: {current_state} | Şerit: {tape.to_string(head)} | Hareket: {direction}")

        return RunResult(
            accepted=False, reason="timeout",
            final_tape=tape.to_plain_string(),
            steps=max_steps, history=history,
        )

    def __repr__(self) -> str:
        return (f"SingleTapeTM(name={self.name!r}, "
                f"states={len(self.states)}, "
                f"transitions={len(self._transitions)})")


__all__ = ["SingleTapeTM", "Tape", "RunResult", "Configuration"]