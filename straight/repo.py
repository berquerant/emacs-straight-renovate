from dataclasses import dataclass
from pathlib import Path

from .rnv import Rnv


class DirException(Exception):
    pass


@dataclass
class Root:
    root: Path
    rnv_cmd: str

    def rnv(self, path: str) -> Rnv:
        p = self.root / path
        if not p.exists():
            raise DirException(f"RepoDir not exists: {p}")
        if not p.is_dir():
            raise DirException(f"RepoDir is not a directory: {p}")
        return Rnv(cmd=self.rnv_cmd, path=p)
