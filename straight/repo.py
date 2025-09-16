import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self


class DirException(Exception):
    pass


@dataclass
class Dir:
    path: Path

    def fetch(self) -> None:
        self.__run("fetch", **self.__common_args(capture_output=False))

    def get_commit_from_tag(self, tag: str) -> str:
        try:
            return self.__run("rev-parse", tag, **self.__common_args()).stdout.rstrip()
        except Exception as e:
            raise DirException(f"failed to get commit from tag: {self.path}, {tag}") from e

    def get_tag_from_commit(self, commit: str) -> str:
        try:
            return self.__run("describe", "--tags", "--exact-match", commit, **self.__common_args()).stdout.rstrip()

        except Exception as e:
            raise DirException(f"failed to get tag from commit: {self.path}, {commit}") from e

    def get_latest_tag(self, commit: str) -> str:
        try:
            return self.__run("describe", "--abbrev=0", "--tags", commit, **self.__common_args()).stdout.rstrip()

        except Exception as e:
            raise DirException(f"failed to get latest tag: {self.path}, {commit}") from e

    def list_tags_order_by_creatordate_asc(self) -> list[str]:
        try:
            stdout = self.__run("tag", "-l", "--sort=creatordate", "--format=%(refname)", **self.__common_args()).stdout
            return [x.removeprefix("refs/tags/") for x in stdout.rstrip().split()]
        except Exception as e:
            raise DirException(f"failed to list tags: {self.path}") from e

    def get_same_or_newer_or_latest_tag(self) -> str:
        commit = self.current_commit()
        try:
            return self.get_tag_from_commit(commit)
        except Exception:
            logging.debug("get_newer_or_same_tag: current commit is not a tag: %s", commit)
        latest_tag = self.get_latest_tag(commit)
        tags = self.list_tags_order_by_creatordate_asc()
        try:
            latest_tag_index = tags.index(latest_tag)
        except ValueError:
            raise DirException(f"latest_tag {latest_tag} exists but not found in all tags from {self.path}")
        next_tag_index = latest_tag_index + 1
        if next_tag_index < len(tags):
            return tags[next_tag_index]
        logging.debug("get_newer_or_same_tag: next tag of %s is not found", latest_tag)
        return latest_tag

    def default_branch(self) -> str:
        stdout = self.__run(
            "remote",
            "show",
            "origin",
            **self.__common_args(),
        ).stdout
        g = re.search(r"HEAD branch: (\w+)", stdout)
        if g and g.groups():
            return g.group(1)
        raise Exception(f"failed to get default branch: {self.path}")

    def current_commit(self) -> str:
        return self.__run("show", "--format=%H", "--no-patch", **self.__common_args()).stdout.rstrip()

    def remote_origin_url(self) -> str:
        return self.__run(
            "config",
            "--get",
            "remote.origin.url",
            **self.__common_args(),
        ).stdout.rstrip()

    def renovate_dep_name(self) -> str:
        origin = self.remote_origin_url()
        if origin.startswith("https://github.com/"):
            return origin.removeprefix("https://github.com/").removesuffix(".git")
        raise DirException(f"cannot infer renovate dep name from {origin}")

    def renovate_datasource(self) -> str:
        origin = self.remote_origin_url()
        if origin.startswith("https://github.com/"):
            return "github-tags"
        raise DirException(f"cannot infer renovate datasource from {origin}")

    def __run(self, *args, **kwargs) -> subprocess.CompletedProcess[str]:  # type: ignore
        cmd = ["git"] + list(args)
        logging.debug("Repo: dir = %s, cmd = %s", self.path, cmd)
        return subprocess.run(cmd, **kwargs)

    def __common_args(self, capture_output: bool = True) -> dict[str, Any]:
        return {
            "check": True,
            "text": True,
            "capture_output": capture_output,
            "cwd": str(self.path),
        }


@dataclass
class Root:
    root: Path

    @classmethod
    def new(cls, root: Path) -> Self:
        return cls(root=root)

    def dir(self, path: str) -> Dir:
        p = self.root / path
        if not p.exists():
            raise DirException(f"RepoDir not exists: {p}")
        if not p.is_dir():
            raise DirException(f"RepoDir is not a directory: {p}")
        return Dir(path=p)
