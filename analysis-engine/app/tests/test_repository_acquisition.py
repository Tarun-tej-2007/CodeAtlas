"""Unit test suite for RepositoryCloneService and acquisition exceptions."""

import os
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.workspace.models import Workspace
from app.repositories import (
    RepositoryCloneService,
    RepositoryAcquisitionError,
    RepositoryCloneError,
    RepositoryCopyError,
    RepositoryNotFoundError,
    InvalidRepositorySourceError,
)


class TestRepositoryAcquisition(unittest.TestCase):
    """Tests for repository clone service supporting local copies and Git URL targets."""

    def setUp(self) -> None:
        self.service = RepositoryCloneService()
        
        # Isolated test temporary directories
        self.workspace_dir = tempfile.mkdtemp()
        uuid_mock = uuid_generator()
        self.workspace = Workspace(
            id=uuid_mock,
            analysis_id=uuid_mock,
            path=Path(self.workspace_dir),
            created_at=MagicMock(),
        )
        self.source_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)
        if os.path.exists(self.source_dir):
            shutil.rmtree(self.source_dir)

    def test_clone_local_directory_success(self) -> None:
        # 1. Create a dummy file in the source directory
        dummy_file = Path(self.source_dir) / "app.js"
        dummy_file.write_text("console.log('hello');")

        # Copy/Clone
        local_path = self.service.clone_repository(self.source_dir, self.workspace)

        # Verify
        self.assertEqual(local_path, self.workspace.path)
        copied_file = local_path / "app.js"
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_text(), "console.log('hello');")

    def test_invalid_local_path_raises_not_found(self) -> None:
        # 2. Invalid local path
        invalid_source = os.path.join(self.source_dir, "nonexistent_subfolder")
        
        with self.assertRaises(RepositoryNotFoundError):
            self.service.clone_repository(invalid_source, self.workspace)

    def test_source_is_not_a_directory_raises_invalid_source(self) -> None:
        # 3. Path is not a directory
        dummy_file = Path(self.source_dir) / "file.txt"
        dummy_file.write_text("Not a directory")

        with self.assertRaises(InvalidRepositorySourceError):
            self.service.clone_repository(str(dummy_file), self.workspace)

    @patch("subprocess.run")
    def test_successful_git_clone(self, mock_run) -> None:
        # 4. Successful Git clone
        mock_run.return_value = MagicMock(returncode=0)

        git_url = "https://github.com/user/repo.git"
        local_path = self.service.clone_repository(git_url, self.workspace)

        self.assertEqual(local_path, self.workspace.path)
        mock_run.assert_called_once_with(
            ["git", "clone", git_url, str(self.workspace.path)],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_failed_git_clone_raises_clone_error(self, mock_run) -> None:
        # 5. Failed Git clone
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "clone"],
            stderr="fatal: repository not found"
        )

        git_url = "https://github.com/user/repo-does-not-exist.git"

        # Verify custom exception and exception chaining
        with self.assertRaises(RepositoryCloneError) as ctx:
            self.service.clone_repository(git_url, self.workspace)
        
        self.assertIn("Git clone failed: fatal: repository not found", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, subprocess.CalledProcessError)

    def test_invalid_repository_source_empty_raises_error(self) -> None:
        # 6. Invalid repository URL/source
        with self.assertRaises(InvalidRepositorySourceError):
            self.service.clone_repository("", self.workspace)

        with self.assertRaises(InvalidRepositorySourceError):
            self.service.clone_repository(None, self.workspace)  # type: ignore

    def test_invalid_workspace_destination_raises_error(self) -> None:
        # 7. Existing workspace destination validation
        with self.assertRaises(InvalidRepositorySourceError):
            self.service.clone_repository(self.source_dir, None)

        # Workspace missing path attribute
        broken_workspace = MagicMock(spec=[])
        with self.assertRaises(InvalidRepositorySourceError):
            self.service.clone_repository(self.source_dir, broken_workspace)


# Helper generator for stable uuids
def uuid_generator() -> uuid.UUID:
    import uuid
    return uuid.uuid4()


if __name__ == "__main__":
    unittest.main()
