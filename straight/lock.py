import logging
from dataclasses import dataclass
from pathlib import Path

from .repo import Root
from .stat import Stat
from .straight import DefaultEntries, Dependencies


@dataclass
class Command:
    deps: DefaultEntries
    repos: Root
    locks: Path
    fail_fast: bool

    def run(self) -> None:
        stat = Stat()
        logging.info("Lock: start")
        deps = self.deps.read() or Dependencies([])
        dep_map = {x.name: x for x in deps}
        with self.locks.open() as f:
            locks = f.read()
        for dep_name in dep_map:
            stat.incr("processed")
            logging.info("Lock: process %s", dep_name)
            try:
                commit = self.repos.rnv(dep_name).lock(locks)
            except Exception as e:
                stat.incr("failed")
                if self.fail_fast:
                    e.add_note(f"From dep {dep_name}")
                    raise
                logging.warn("Lock: failed %s: %s", dep_name, e)
                continue
            stat.incr("success")
            old_commit = dep_map[dep_name].commit
            if old_commit == commit:
                stat.incr("no_changes")
                logging.info("Lock: no changes, %s = %s", dep_name, commit)
                continue
            stat.incr("updated")
            logging.info("Lock: update, %s, %s -> %s", dep_name, old_commit, commit)
            dep_map[dep_name].commit = commit
        self.deps.write(Dependencies(list(dep_map.values())))
        logging.info("Lock: end")
        logging.info("Lock: stat: %s", stat)
