from unittest import TestCase

import straight.renovate as renovate


class TestLockEntry(TestCase):
    def test_lock_entry(self):
        with self.subTest(title="invalid"):
            with self.assertRaises(renovate.LockEntryException):
                renovate.LockEntry.from_str("empty")
        with self.subTest(title="parse"):
            data = "straight=NAME depName=DEP datasource=SRC value=VALUE"
            entry = renovate.LockEntry(
                value="VALUE",
                datasource="SRC",
                dep_name="DEP",
                straight_name="NAME",
            )
            with self.subTest(title="from_str"):
                got = renovate.LockEntry.from_str(data)
                self.assertEqual(got, entry)
            with self.subTest(title="into_str"):
                got = entry.into_str()
                self.assertEqual(got, data)
