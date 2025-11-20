import logging
import re
from dataclasses import dataclass
from pathlib import Path

from .repo import Root
from .stat import Stat
from .straight import DefaultEntries, Dependencies, Dependency


@dataclass
class Command:
    deps: DefaultEntries
    repos: Root
    locks: Path
    fail_fast: bool
    exclude: str

    def run(self) -> None:
        stat = Stat()
        logging.info("Gen: start")
        exclude = re.compile(self.exclude)
        outputs = []
        deps = self.deps.read() or Dependencies([])
        for i, dep in enumerate(deps):
            stat.incr("processed")
            logging.info("Gen: process %s", dep.into_cons_cell())
            if exclude.search(dep.name) is not None:
                logging.info("Gen: exclude %s", dep.into_cons_cell())
                stat.incr("excluded")
                continue
            try:
                line = self.__run(dep)
            except Exception as e:
                stat.incr("failed")
                if self.fail_fast:
                    e.add_note(f"From line {i + 1}, {dep.into_cons_cell()}")
                    raise
                logging.warn("Gen: failed %s: %s", dep.into_cons_cell(), e)
                continue
            stat.incr("success")
            outputs.append(line)
        with self.locks.open("w") as f:
            print("\n".join(outputs), file=f, end="")
        logging.info("Gen: end")
        logging.info("Gen: stat: %s", stat)

    def __run(self, dep: Dependency) -> str:
        return self.repos.rnv(dep.name).generate()
