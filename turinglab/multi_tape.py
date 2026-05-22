"""
TuringLab - Çok Şeritli Turing Makinesi Motoru
Bonus A: Multi-tape Deterministic TM
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import yaml

from turinglab.tm_engine import Tape, Configuration, RunResult


@dataclass
class MultiConfig:
    """Çok şeritli TM'nin anlık konfigürasyonu."""
    state: str
    tapes: list[str]        # Her şeridin string temsili
    heads: list[int]        # Her kafanın pozisyonu


@dataclass
class MultiRunResult:
    """MultiTapeTM.run() sonucu."""
    accepted: bool
    reason: str
    final_tapes: list[str]
    steps: int
    history: list[MultiConfig] = field(default_factory=list)


class MultiTapeTM:
    """
    Deterministic Multi-Tape Turing Machine.
    YAML'da num_tapes ile şerit sayısı belirlenir.
    Her geçişte read, write, move listeleri k uzunluğundadır.
    """

    def __init__(self, config: dict) -> None:
        self._validate(config)
        self.name: str = config.get("name", "unnamed")
        self.description: str = config.get("description", "")
        self.num_tapes: int = config["num_tapes"]
        self.states: set[str] = set(config["states"])
        self.blank: str = config["blank"]
        self.start_state: str = config["start_state"]
        self.accept_states: set[str] = set(config["accept_states"])
        self.reject_states: set[str] = set(config.get("reject_states", []))

        # δ: (state, tuple(reads)) -> (next, tuple(writes), tuple(moves))
        self._transitions: dict = {}
        for t in config.get("transitions", []):
            key = (t["state"], tuple(t["read"]))
            self._transitions[key] = (
                t["next"],
                tuple(t["write"]),
                tuple(t["move"]),
            )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "MultiTapeTM":
        """YAML dosyasından MultiTapeTM yükler."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML bulunamadı: {path}")
        with open(path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"YAML parse hatası: {e}") from e
        return cls(config)

    @staticmethod
    def _validate(config: dict) -> None:
        """Zorunlu alanları kontrol eder."""
        required = ["num_tapes", "states", "blank",
                    "start_state", "accept_states", "transitions"]
        for f in required:
            if f not in config:
                raise ValueError(f"Zorunlu alan eksik: '{f}'")

    def run(
        self,
        input_string: str,
        max_steps: int = 10_000,
        verbose: bool = False,
    ) -> MultiRunResult:
        """
        Multi-tape TM'yi çalıştırır.
        Girdi sadece 1. şeride yazılır, diğerleri boş başlar.
        """
        tapes = [Tape(input_string, self.blank)]
        for _ in range(self.num_tapes - 1):
            tapes.append(Tape("", self.blank))

        heads = [0] * self.num_tapes
        current_state = self.start_state
        history: list[MultiConfig] = []

        def snapshot() -> MultiConfig:
            return MultiConfig(
                state=current_state,
                tapes=[t.to_string(h) for t, h in zip(tapes, heads)],
                heads=list(heads),
            )

        history.append(snapshot())

        if verbose:
            print(f"Adım 0 | Durum: {current_state}")
            for i, (t, h) in enumerate(zip(tapes, heads)):
                print(f"  Şerit {i+1}: {t.to_string(h)}")

        for step in range(1, max_steps + 1):
            if current_state in self.accept_states:
                return MultiRunResult(
                    accepted=True, reason="accept",
                    final_tapes=[t.to_plain_string() for t in tapes],
                    steps=step - 1, history=history,
                )
            if current_state in self.reject_states:
                return MultiRunResult(
                    accepted=False, reason="reject",
                    final_tapes=[t.to_plain_string() for t in tapes],
                    steps=step - 1, history=history,
                )

            reads = tuple(t.read(h) for t, h in zip(tapes, heads))
            key = (current_state, reads)

            if key not in self._transitions:
                return MultiRunResult(
                    accepted=False, reason="no_transition",
                    final_tapes=[t.to_plain_string() for t in tapes],
                    steps=step - 1, history=history,
                )

            next_state, writes, moves = self._transitions[key]

            for i, (tape, write, move) in enumerate(
                zip(tapes, writes, moves)
            ):
                tape.write(heads[i], write)
                if move == "R":
                    heads[i] += 1
                elif move == "L":
                    heads[i] -= 1
                # "S" ise kafa yerinde kalir

            current_state = next_state
            history.append(snapshot())

            if verbose:
                print(f"Adım {step} | Durum: {current_state}")
                for i, (t, h) in enumerate(zip(tapes, heads)):
                    print(f"  Şerit {i+1}: {t.to_string(h)}")

        return MultiRunResult(
            accepted=False, reason="timeout",
            final_tapes=[t.to_plain_string() for t in tapes],
            steps=max_steps, history=history,
        )

    def __repr__(self) -> str:
        return (f"MultiTapeTM(name={self.name!r}, "
                f"tapes={self.num_tapes}, "
                f"transitions={len(self._transitions)})")


__all__ = ["MultiTapeTM", "MultiRunResult", "MultiConfig"]