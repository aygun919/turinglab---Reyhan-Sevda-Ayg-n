"""
TuringLab - Non-Deterministic Turing Makinesi
Bonus B: NTM - BFS ile hesaplama agaci
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
from pathlib import Path
import yaml

from turinglab.tm_engine import Tape


@dataclass
class NTMConfig:
    """NTM'nin anlık konfigürasyonu."""
    state: str
    tape_cells: dict
    head: int
    blank: str
    path: list[str] = field(default_factory=list)

    def tape_str(self) -> str:
        if not self.tape_cells:
            return self.blank
        mn, mx = min(self.tape_cells), max(self.tape_cells)
        return "".join(self.tape_cells.get(i, self.blank)
                       for i in range(mn, mx + 1))

    def read(self) -> str:
        return self.tape_cells.get(self.head, self.blank)

    def write(self, symbol: str) -> dict:
        new = dict(self.tape_cells)
        new[self.head] = symbol
        return new

    def move_head(self, direction: str) -> int:
        if direction == "R":
            return self.head + 1
        elif direction == "L":
            return self.head - 1
        return self.head


@dataclass
class NTMResult:
    """NondeterministicTM.run() sonucu."""
    accepted: bool
    reason: str
    steps: int
    accepting_paths: list[list[str]] = field(default_factory=list)


class NondeterministicTM:
    """
    Non-Deterministic Turing Machine.
    BFS ile hesaplama agacini gezer.
    Her durumdan birden fazla gecis olabilir.
    """

    def __init__(self, config: dict) -> None:
        self._validate(config)
        self.name: str = config.get("name", "unnamed")
        self.description: str = config.get("description", "")
        self.states: set[str] = set(config["states"])
        self.blank: str = config["blank"]
        self.start_state: str = config["start_state"]
        self.accept_states: set[str] = set(config["accept_states"])
        self.reject_states: set[str] = set(config.get("reject_states", []))

        # δ: (state, symbol) -> list of (next, write, move)
        self._transitions: dict[tuple, list] = {}
        for t in config.get("transitions", []):
            key = (t["state"], t["read"])
            if key not in self._transitions:
                self._transitions[key] = []
            self._transitions[key].append(
                (t["next"], t["write"], t["move"])
            )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "NondeterministicTM":
        """YAML dosyasindan NTM yukler."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML bulunamadi: {path}")
        with open(path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"YAML parse hatasi: {e}") from e
        return cls(config)

    @staticmethod
    def _validate(config: dict) -> None:
        required = ["states", "blank", "start_state",
                    "accept_states", "transitions"]
        for f in required:
            if f not in config:
                raise ValueError(f"Zorunlu alan eksik: '{f}'")

    def run(
        self,
        input_string: str,
        max_depth: int = 1000,
        max_branches: int = 10000,
    ) -> NTMResult:
        """
        NTM'yi BFS ile calistirir.

        Args:
            input_string: Baslangic girdisi
            max_depth: Maksimum adim derinligi
            max_branches: Maksimum dal sayisi

        Returns:
            NTMResult: kabul/ret, kabul yollari
        """
        # Baslangic konfigurasyonu
        start = NTMConfig(
            state=self.start_state,
            tape_cells={i: c for i, c in enumerate(input_string)},
            head=0,
            blank=self.blank,
            path=[f"{self.start_state}"],
        )

        queue: deque[NTMConfig] = deque([start])
        visited_count = 0
        accepting_paths = []

        while queue:
            if visited_count >= max_branches:
                return NTMResult(
                    accepted=bool(accepting_paths),
                    reason="max_branches",
                    steps=visited_count,
                    accepting_paths=accepting_paths,
                )

            config = queue.popleft()
            visited_count += 1

            # Derinlik kontrolu
            if len(config.path) > max_depth:
                continue

            # Kabul kontrolu
            if config.state in self.accept_states:
                accepting_paths.append(config.path)
                return NTMResult(
                    accepted=True,
                    reason="accept",
                    steps=visited_count,
                    accepting_paths=accepting_paths,
                )

            # Ret kontrolu
            if config.state in self.reject_states:
                continue

            # Gecisler
            symbol = config.read()
            key = (config.state, symbol)
            choices = self._transitions.get(key, [])

            if not choices:
                continue  # Bu dal oldu, diger dallara devam

            for next_state, write, move in choices:
                new_cells = config.write(write)
                new_head = config.move_head(move)
                new_path = config.path + [
                    f"{next_state}(r={symbol},w={write},m={move})"
                ]
                new_config = NTMConfig(
                    state=next_state,
                    tape_cells=new_cells,
                    head=new_head,
                    blank=self.blank,
                    path=new_path,
                )
                queue.append(new_config)

        return NTMResult(
            accepted=False,
            reason="reject",
            steps=visited_count,
            accepting_paths=[],
        )

    def __repr__(self) -> str:
        return (f"NondeterministicTM(name={self.name!r}, "
                f"transitions={len(self._transitions)})")


__all__ = ["NondeterministicTM", "NTMResult", "NTMConfig"]