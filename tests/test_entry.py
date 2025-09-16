import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase

import straight.entry as entry


@dataclass
class ExampleEntries:  # implements entry.Entries
    data: str

    @classmethod
    def from_str(cls, data: str) -> "ExampleEntries":
        return cls(data=data)

    def into_str(self) -> str:
        return self.data


class ExampleHandler(entry.FileHandler[ExampleEntries]):
    @classmethod
    def new(cls, path: Path) -> "ExampleHandler":
        return cls(generic_type=ExampleEntries, path=path)


class TestFileHandler(TestCase):
    def test_read(self):
        with self.subTest(title="not exists"):
            self.assertIsNone(ExampleHandler.new(path=Path("not_found")).read())

        with self.subTest(title="not a file"):
            with tempfile.TemporaryDirectory() as dir:
                with self.assertRaises(entry.FileHandlerException):
                    ExampleHandler.new(path=Path(dir)).read()

        with self.subTest(title="read file"):
            with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
                fp.write(b"DATA")
                fp.close()
                h = ExampleHandler.new(path=Path(fp.name))
                got = h.read()
                self.assertEqual(ExampleEntries(data="DATA"), got)

    def test_write(self):
        with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
            fp.close()
            h = ExampleHandler.new(path=Path(fp.name))
            h.write(ExampleEntries(data="DATA"))
            with open(fp.name) as f:
                got = f.read()
            self.assertEqual("DATA", got)
