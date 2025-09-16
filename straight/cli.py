import argparse
import json
import traceback
from pathlib import Path
from textwrap import dedent

from .cmd import Lock, Renovate
from .log import setup
from .renovate import LockFile, custom_manager_entry
from .repo import Root
from .straight import DefaultEntries


def main() -> int:
    """Entrypoint."""
    parser = argparse.ArgumentParser(
        description="Applying Renovate to `straight-default.el` in Emacs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """\
        First, generate the lock file for renovate.

        python -m emacs-straight-renovate -e /path/to/straight-default.el -d /path/to/straight/repos -r /path/to/lockfile renovate

        Then, add following custom manager to renovate.json.

        {}

        If Renovate updates lockfile, apply them to straight-default.el.

        python -m emacs-straight-renovate -e /path/to/straight-default.el -d /path/to/straight/repos -r /path/to/lockfile lock
        """,
        ).format(json.dumps(custom_manager_entry(["example_file"]), indent=2)),
    )
    parser.add_argument("--default-el", "-e", action="store", type=Path, help="straight-default.el")
    parser.add_argument("--repodir", "-d", action="store", type=Path, help="straight/repos")
    parser.add_argument(
        "--renovate-lock", "-r", action="store", type=Path, default="renovate.lock", help="lockfile for renovate"
    )
    parser.add_argument("--debug", action="store_true", help="enable debug log")
    subp = parser.add_subparsers(dest="cmd")

    subp.add_parser("renovate", help="generate renovate lock file")
    subp.add_parser("lock", help="generate straight-default.el")

    args = parser.parse_args()
    setup(args.debug)

    deps = DefaultEntries.new(args.default_el)
    repos = Root.new(args.repodir)
    locks = LockFile.new(args.renovate_lock)

    try:
        match args.cmd:
            case "renovate":
                Renovate(deps=deps, repos=repos, locks=locks).run()
            case "lock":
                Lock(deps=deps, repos=repos, locks=locks).run()
            case _:
                raise Exception(f"unknown subcommand: {args.cmd}")
    except Exception:
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
