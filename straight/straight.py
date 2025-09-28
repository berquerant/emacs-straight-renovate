import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from .entry import FileHandler


@dataclass
class Dependency:
    name: str
    commit: str

    def into_cons_cell(self) -> str:
        return f'("{self.name}" . "{self.commit}")'


class Dependencies(list[Dependency]):
    @classmethod
    def from_str(cls, data: str) -> Self:
        return cls(
            [Dependency(name=name, commit=commit) for name, commit in re.findall(r'"([^"]+)" \. "([^"]+)"', data)]
        )

    def into_str(self) -> str:
        contents = "\n ".join(x.into_cons_cell() for x in self)
        return f"({contents})\n:epsilon"


class DefaultEntries(FileHandler[Dependencies]):
    @classmethod
    def new(cls, path: Path) -> Self:
        return cls(generic_type=Dependencies, path=path)
