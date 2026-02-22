from textwrap import dedent
from unittest import TestCase

import straight.straight as straight


class TestStraight(TestCase):
    def test_dependency(self):
        x = straight.Dependency(name="NAME", commit="COMMIT")
        self.assertEqual('("NAME" . "COMMIT")', x.into_cons_cell())

    def test_dependencies(self):
        with self.subTest("from empty string"):
            self.assertEqual(straight.Dependencies([]), straight.Dependencies.from_str(""))

        cases = [
            (
                "empty",
                straight.Dependencies([]),
                dedent("""\
                    ()
                    :epsilon"""),
            ),
            (
                "one",
                straight.Dependencies([straight.Dependency(name="NAME", commit="COMMIT")]),
                dedent("""\
                    (("NAME" . "COMMIT"))
                    :epsilon"""),
            ),
            (
                "two",
                straight.Dependencies(
                    [
                        straight.Dependency(name="NAME", commit="COMMIT"),
                        straight.Dependency(name="NAME2", commit="COMMIT2"),
                    ]
                ),
                dedent("""\
                    (("NAME" . "COMMIT")
                     ("NAME2" . "COMMIT2"))
                    :epsilon"""),
            ),
        ]
        for title, deps, want in cases:
            with self.subTest(title=title):
                with self.subTest("into_str"):
                    got = deps.into_str()
                    self.assertEqual(want, got)
                with self.subTest("from_str"):
                    got = straight.Dependencies.from_str(want)
                    self.assertEqual(deps, got)
