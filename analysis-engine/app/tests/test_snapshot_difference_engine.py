"""Unit tests for the SHA-256 Snapshot Difference Engine."""

import unittest
from datetime import datetime, timezone
from typing import Dict

from app.incremental import (
    ChangeType,
    IncrementalAnalysisValidationError,
    FileFingerprint,
    RepositorySnapshot,
    SHA256SnapshotDifferenceEngine,
)


class TestSnapshotDifferenceEngine(unittest.TestCase):
    """Verifies diffing logic, change additions, deletions, modifications, and sorting determinism."""

    def setUp(self) -> None:
        self.engine = SHA256SnapshotDifferenceEngine()
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Baseline file fingerprints
        self.fp_a_old = FileFingerprint(path="a.py", hash="hash_a_1", size=10, last_modified=self.time_utc)
        self.fp_b_old = FileFingerprint(path="b.js", hash="hash_b_1", size=20, last_modified=self.time_utc)
        self.fp_c_old = FileFingerprint(path="c.ts", hash="hash_c_1", size=30, last_modified=self.time_utc)

        self.snap_empty = RepositorySnapshot(commit_id="c_empty", fingerprints={})
        self.snap_old = RepositorySnapshot(
            commit_id="c_old",
            fingerprints={
                "a.py": self.fp_a_old,
                "b.js": self.fp_b_old,
                "c.ts": self.fp_c_old,
            },
        )

    def test_invalid_arguments(self) -> None:
        """Verifies validation rejects invalid or None parameters."""
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.engine.diff_snapshots(None, self.snap_old)  # type: ignore

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.engine.diff_snapshots(self.snap_old, "not_a_snapshot")  # type: ignore

    def test_empty_vs_empty_snapshots(self) -> None:
        """Verifies diffing two empty snapshots yields no changes."""
        res = self.engine.diff_snapshots(self.snap_empty, self.snap_empty)
        self.assertEqual(len(res), 0)

    def test_empty_vs_populated_snapshots(self) -> None:
        """Verifies diffing empty baseline vs populated target marks all files as ADDED."""
        res = self.engine.diff_snapshots(self.snap_empty, self.snap_old)
        self.assertEqual(len(res), 3)
        for cf in res:
            self.assertEqual(cf.change_type, ChangeType.ADDED)
            self.assertIsNone(cf.old_fingerprint)
            self.assertIsNotNone(cf.new_fingerprint)

    def test_populated_vs_empty_snapshots(self) -> None:
        """Verifies diffing populated baseline vs empty target marks all files as DELETED."""
        res = self.engine.diff_snapshots(self.snap_old, self.snap_empty)
        self.assertEqual(len(res), 3)
        for cf in res:
            self.assertEqual(cf.change_type, ChangeType.DELETED)
            self.assertIsNotNone(cf.old_fingerprint)
            self.assertIsNone(cf.new_fingerprint)

    def test_identical_snapshots(self) -> None:
        """Verifies comparing identical snapshots flags all files as UNCHANGED."""
        res = self.engine.diff_snapshots(self.snap_old, self.snap_old)
        self.assertEqual(len(res), 3)
        for cf in res:
            self.assertEqual(cf.change_type, ChangeType.UNCHANGED)
            self.assertEqual(cf.old_fingerprint, cf.new_fingerprint)

    def test_added_deleted_modified_mix_and_sorting(self) -> None:
        """Verifies mixed repository scenario detects all change types with sorted output paths."""
        # a.py modified, b.js deleted, c.ts unchanged, d.py added
        fp_a_new = FileFingerprint(path="a.py", hash="hash_a_modified", size=15, last_modified=self.time_utc)
        fp_d_new = FileFingerprint(path="d.py", hash="hash_d_new", size=50, last_modified=self.time_utc)

        snap_new = RepositorySnapshot(
            commit_id="c_new",
            fingerprints={
                "a.py": fp_a_new,
                "c.ts": self.fp_c_old,
                "d.py": fp_d_new,
            },
        )

        res = self.engine.diff_snapshots(self.snap_old, snap_new)

        # Expected output sorted alphabetically: a.py, b.js, c.ts, d.py
        self.assertEqual(len(res), 4)
        self.assertEqual([cf.path for cf in res], ["a.py", "b.js", "c.ts", "d.py"])

        # a.py
        self.assertEqual(res[0].change_type, ChangeType.MODIFIED)
        self.assertEqual(res[0].old_fingerprint, self.fp_a_old)
        self.assertEqual(res[0].new_fingerprint, fp_a_new)

        # b.js
        self.assertEqual(res[1].change_type, ChangeType.DELETED)
        self.assertEqual(res[1].old_fingerprint, self.fp_b_old)
        self.assertIsNone(res[1].new_fingerprint)

        # c.ts
        self.assertEqual(res[2].change_type, ChangeType.UNCHANGED)
        self.assertEqual(res[2].old_fingerprint, self.fp_c_old)
        self.assertEqual(res[2].new_fingerprint, self.fp_c_old)

        # d.py
        self.assertEqual(res[3].change_type, ChangeType.ADDED)
        self.assertIsNone(res[3].old_fingerprint)
        self.assertEqual(res[3].new_fingerprint, fp_d_new)


if __name__ == "__main__":
    unittest.main()
