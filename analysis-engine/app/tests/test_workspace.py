"""Unit test suite for WorkspaceManager and the Workspace domain models."""

import shutil
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.workspace import (
    Workspace,
    WorkspaceManager,
    WorkspaceAlreadyExistsError,
    WorkspaceCleanupError,
    WorkspaceCreationError,
    WorkspaceNotFoundError,
)


class TestWorkspaceManager(unittest.TestCase):
    """Tests for managing workspace creation, check, cleanup, and configuration."""

    def setUp(self) -> None:
        # Create a temporary directory to act as the workspace root for tests
        self.temp_root_dir = tempfile.mkdtemp()
        self.workspace_root = Path(self.temp_root_dir)
        self.manager = WorkspaceManager(
            workspace_root=self.workspace_root,
            keep_workspace=False,
        )

    def tearDown(self) -> None:
        # Clean up the test root directory after each test
        if self.workspace_root.exists():
            shutil.rmtree(self.workspace_root)

    def test_workspace_creation_and_contents(self) -> None:
        analysis_id = uuid.uuid4()
        workspace = self.manager.create_workspace(analysis_id)

        # 3. Verify workspace contents
        self.assertIsInstance(workspace, Workspace)
        self.assertEqual(workspace.analysis_id, analysis_id)
        self.assertIsInstance(workspace.id, uuid.UUID)
        self.assertEqual(workspace.path, self.workspace_root / str(analysis_id))
        self.assertTrue(workspace.path.exists())
        self.assertTrue(workspace.path.is_dir())

    def test_automatic_creation_of_workspace_root(self) -> None:
        # Delete root directory first
        shutil.rmtree(self.workspace_root)
        self.assertFalse(self.workspace_root.exists())

        # Creation should automatically generate the root path
        analysis_id = uuid.uuid4()
        workspace = self.manager.create_workspace(analysis_id)
        self.assertTrue(self.workspace_root.exists())
        self.assertTrue(workspace.path.exists())

    def test_workspace_existence_detection(self) -> None:
        analysis_id = uuid.uuid4()
        workspace = self.manager.create_workspace(analysis_id)

        # 4. Verify existence checks
        self.assertTrue(self.manager.workspace_exists(workspace))

        # Perform cleanup
        self.manager.cleanup_workspace(workspace)
        self.assertFalse(self.manager.workspace_exists(workspace))

    def test_path_resolution(self) -> None:
        # 5. Path resolution
        analysis_id = uuid.uuid4()
        resolved_path = self.manager.get_workspace_path(analysis_id)
        self.assertEqual(resolved_path, self.workspace_root / str(analysis_id))

    def test_successful_cleanup(self) -> None:
        # 6. Successful cleanup
        analysis_id = uuid.uuid4()
        workspace = self.manager.create_workspace(analysis_id)
        self.assertTrue(workspace.path.exists())

        self.manager.cleanup_workspace(workspace)
        self.assertFalse(workspace.path.exists())

    def test_cleanup_nonexistent_workspace_raises_error(self) -> None:
        # 7. Cleanup behavior when workspace does not exist
        analysis_id = uuid.uuid4()
        # Mock workspace that doesn't exist on disk
        workspace = Workspace(
            id=uuid.uuid4(),
            analysis_id=analysis_id,
            path=self.workspace_root / str(analysis_id),
            created_at=datetime.now(timezone.utc),
        )
        self.assertFalse(workspace.path.exists())

        with self.assertRaises(WorkspaceNotFoundError):
            self.manager.cleanup_workspace(workspace)

    def test_custom_workspace_root_configuration(self) -> None:
        # 8. Custom WORKSPACE_ROOT configuration
        new_temp_dir = tempfile.mkdtemp()
        new_root = Path(new_temp_dir)
        try:
            custom_manager = WorkspaceManager(workspace_root=new_root)
            self.assertEqual(custom_manager.workspace_root, new_root)
            analysis_id = uuid.uuid4()
            workspace = custom_manager.create_workspace(analysis_id)
            self.assertEqual(workspace.path, new_root / str(analysis_id))
        finally:
            if new_root.exists():
                shutil.rmtree(new_root)

    def test_keep_workspace_true_behavior(self) -> None:
        # 9. KEEP_WORKSPACE=true behavior
        keep_manager = WorkspaceManager(
            workspace_root=self.workspace_root,
            keep_workspace=True,
        )
        analysis_id = uuid.uuid4()
        workspace = keep_manager.create_workspace(analysis_id)
        self.assertTrue(workspace.path.exists())

        # Cleanup should skip deletion
        keep_manager.cleanup_workspace(workspace)
        self.assertTrue(workspace.path.exists())

    def test_workspace_already_exists_raises_error(self) -> None:
        # 10. Failure scenario: workspace already exists
        analysis_id = uuid.uuid4()
        self.manager.create_workspace(analysis_id)

        # Attempting to create it again must raise WorkspaceAlreadyExistsError
        with self.assertRaises(WorkspaceAlreadyExistsError):
            self.manager.create_workspace(analysis_id)

    def test_workspace_creation_error_on_invalid_path(self) -> None:
        # 10. Failure scenario: creation failure (e.g. workspace root is a file)
        dummy_file = self.workspace_root / "dummy_file"
        dummy_file.touch()

        # Try to make a workspace manager with root pointing to the file
        broken_manager = WorkspaceManager(workspace_root=dummy_file)
        with self.assertRaises(WorkspaceCreationError):
            broken_manager.create_workspace(uuid.uuid4())


if __name__ == "__main__":
    unittest.main()
