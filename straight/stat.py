from collections import defaultdict
from datetime import datetime


class Stat:
    """Runtime statistics."""

    def __init__(self) -> None:
        self.__start = datetime.now()
        self.__values: dict[str, int] = defaultdict(int)

    def __duration(self) -> int:
        return (datetime.now() - self.__start).seconds

    def __str__(self) -> str:
        return "duration={} ".format(self.__duration()) + " ".join(
            "{}={}".format(k, self.__values[k]) for k in sorted(self.__values.keys())
        )

    def incr(self, key: str) -> None:
        self.__values[key] += 1
