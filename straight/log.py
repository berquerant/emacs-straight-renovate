import logging
import sys


def setup(debug: bool) -> None:
    """Prepare logging settings."""
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )
