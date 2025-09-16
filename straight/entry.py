import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Protocol, Self, Type, TypeVar


class Entries(Protocol):
    @classmethod
    def from_str(cls, data: str) -> Self: ...

    def into_str(self) -> str: ...


T = TypeVar("T", bound=Entries)


class FileHandlerException(Exception):
    pass


@dataclass
class FileHandler(Generic[T]):
    """Implement serde via file for T."""

    generic_type: Type[T]  # because we cannot get the actual type of T in methods
    path: Path

    def read(self) -> T | None:
        logging.debug("FileHandler: read from %s", self.path)
        if not self.path.exists():
            logging.info("FileHandler: not exists %s", self.path)
            return None
        if not self.path.is_file():
            raise FileHandlerException(f"failed to read: {self.path}")
        with self.path.open() as f:
            data = f.read()
        # call Entries.from_str()
        return self.generic_type.from_str(data)

    def write(self, entries: T) -> None:
        logging.info("FileHandler: write to %s", self.path)
        with self.path.open("w") as f:
            print(entries.into_str(), file=f, end="")
