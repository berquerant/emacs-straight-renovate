import logging
from dataclasses import dataclass
from datetime import datetime

from .renovate import LockEntries, LockEntry, LockFile
from .repo import Dir, Root
from .straight import DefaultEntries, Dependencies, Dependency


@dataclass
class Renovate:
    deps: DefaultEntries
    repos: Root
    locks: LockFile

    class Stat:
        """Runtime statistics."""

        def __init__(self) -> None:
            self.start = datetime.now()
            self.process = 0
            self.succeed = 0
            self.failure = 0

        def __duration(self) -> int:
            return (datetime.now() - self.start).seconds

        def into_str(self) -> str:
            return "process={} succeed={} failure={} duration_sec={}".format(
                self.process,
                self.succeed,
                self.failure,
                self.__duration(),
            )

    def run(self) -> None:
        stat = self.Stat()
        logging.info("Renovate: start")
        deps = self.__read_deps()
        entries = LockEntries([])
        for dep in deps:
            stat.process += 1
            logging.info("Renovate: process %s", dep.into_cons_cell())
            r = self.__get_repo(dep)
            try:
                e = self.__new_lock_entry(dep, r)
                entries.append(e)
                logging.info("Renovate: add %s", e.into_str())
                stat.succeed += 1
            except Exception as e:
                logging.warn("Renovate: failed to craete lock entry for %s, %s", dep.name, e)
                stat.failure += 1
        self.locks.write(entries)
        logging.info("Renovate: stat, %s", stat.into_str())
        logging.info("Renovate: end")

    def __read_deps(self) -> Dependencies:
        return self.deps.read() or Dependencies([])

    def __get_repo(self, dep: Dependency) -> Dir:
        r = self.repos.dir(dep.name)
        r.fetch()
        return r

    def __new_lock_entry(self, dep: Dependency, dir: Dir) -> LockEntry:
        return LockEntry(
            value=dir.get_same_or_newer_or_latest_tag(),
            datasource=dir.renovate_datasource(),
            dep_name=dir.renovate_dep_name(),
            straight_name=dep.name,
        )


@dataclass
class Lock:
    deps: DefaultEntries
    repos: Root
    locks: LockFile

    class Stat:
        """Runtime statistics."""

        def __init__(self) -> None:
            self.start = datetime.now()
            self.process = 0
            self.succeed = 0
            self.failure = 0
            self.ignored = 0
            self.changed = 0
            self.not_changed = 0
            self.lock_process = 0
            self.lock_succeed = 0
            self.lock_failure = 0

        def __duration(self) -> int:
            return (datetime.now() - self.start).seconds

        def into_str(self) -> str:
            data = [
                ("process", self.process),
                ("ignored", self.ignored),
                ("changed", self.changed),
                ("not_changed", self.not_changed),
                ("lock_process", self.lock_process),
                ("lock_succeed", self.lock_succeed),
                ("lock_failure", self.lock_failure),
                ("duration_sec", self.__duration()),
            ]
            return " ".join("{}={}".format(k, v) for k, v in data)

    def run(self) -> None:
        stat = self.Stat()
        logging.info("Lock: start")
        dep_map = {x.name: x for x in self.__read_deps()}
        for x in self.__generate_deps(stat):
            stat.process += 1
            if x.name not in dep_map:
                logging.warn("Lock: locks has %s but straight", x.name)
                stat.ignored += 1
                continue
            old = dep_map[x.name]
            if old.commit == x.commit:
                logging.debug("Lock: %s = %s, not changed", x.name, x.commit)
                stat.not_changed += 1
                continue
            dep_map[x.name] = x
            logging.info("Lock: %s: %s -> %s", x.name, old.commit, x.commit)
            stat.changed += 1
        new_deps = Dependencies(list(dep_map.values()))
        self.deps.write(new_deps)
        logging.info("Lock: stat, %s", stat.into_str())
        logging.info("Lock: end")

    def __read_deps(self) -> Dependencies:
        return self.deps.read() or Dependencies([])

    def __get_repo(self, dep_name: str) -> Dir:
        r = self.repos.dir(dep_name)
        r.fetch()
        return r

    def __read_locks(self) -> LockEntries:
        return self.locks.read() or LockEntries([])

    def __new_dep(self, lock: LockEntry) -> Dependency:
        r = self.__get_repo(lock.straight_name)
        commit = r.get_commit_from_tag(lock.value)
        logging.debug("Lock: create dep from lock: %s => %s", lock.into_str(), commit)
        return Dependency(name=lock.straight_name, commit=commit)

    def __generate_deps(self, stat: Stat) -> Dependencies:
        deps = Dependencies([])
        locks = self.__read_locks()
        for lock in locks:
            stat.lock_process += 1
            logging.info("Lock: process lock: %s", lock.into_str())
            try:
                dep = self.__new_dep(lock)
                deps.append(dep)
                stat.lock_succeed += 1
            except Exception as e:
                logging.warn("Lock: failed to create renovate entry for %s, %s", lock.into_str(), e)
                stat.lock_failure += 1
        return deps
