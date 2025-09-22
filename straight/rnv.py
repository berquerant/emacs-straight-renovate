import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Rnv:
    cmd: str
    path: Path

    def __run(self, *args, **kwargs) -> subprocess.CompletedProcess[str]:  # type: ignore
        cmd = [self.cmd, str(self.path)] + list(args)
        logging.debug("Dir: dir = %s, cmd = %s", self.path, cmd)
        return subprocess.run(cmd, **kwargs)

    def __common_args(self, capture_output: bool = True) -> dict[str, Any]:
        return {
            "check": True,
            "text": True,
            # "capture_output": capture_output,
            "cwd": str(self.path),
            "stdout": subprocess.PIPE,
            "stderr": None,
        }

    def generate(self) -> str:
        return self.__run("gen", **self.__common_args()).stdout.rstrip()

    def lock(self, lines: str) -> str:
        return self.__run("lock", input=lines, **self.__common_args()).stdout.rstrip()
