"""Integration test suite for the complete Sprint 11 execution pipeline."""

import os
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path

from app.core.config import settings
from app.workspace import WorkspaceManager
from app.repositories import RepositoryCloneService, RepositoryNotFoundError
from app.scanner import ScannerPipeline, Language, ScanResult
from app.services import AnalysisService


class TestIntegrationPipeline(unittest.TestCase):
    """End-to-end integration tests traversing all pipeline boundaries."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        
        # Configure temporary paths
        self.temp_workspace_root = tempfile.mkdtemp()
        self.temp_repo_source = tempfile.mkdtemp()
        
        self.workspace_manager = WorkspaceManager(
            workspace_root=Path(self.temp_workspace_root),
            keep_workspace=False
        )
        self.clone_service = RepositoryCloneService()
        self.scanner_pipeline = ScannerPipeline()
        
        self.service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
        )

    def tearDown(self) -> None:
        if os.path.exists(self.temp_workspace_root):
            shutil.rmtree(self.temp_workspace_root)
        if os.path.exists(self.temp_repo_source):
            shutil.rmtree(self.temp_repo_source)

    def test_e2e_pipeline_with_mixed_languages_and_ignored_dirs(self) -> None:
        # Arrange - Populate source repository with mixed language files and ignored directories
        repo_path = Path(self.temp_repo_source)
        
        # 1. Mixed languages & extensions
        (repo_path / "main.py").write_text("print('hello')")
        (repo_path / "index.js").write_text("console.log('js')")
        (repo_path / "Component.tsx").write_text("const C = () => null;")
        
        # 2. Files without extensions & uppercase extensions
        (repo_path / "LICENSE").write_text("MIT License")
        (repo_path / "SCRIPT.PY").write_text("print('UPPER')")
        
        # 3. Deep directory structure
        deep_dir = repo_path / "src" / "components" / "utils"
        deep_dir.mkdir(parents=True)
        (deep_dir / "helper.ts").write_text("export const run = () => {}")
        
        # 4. Ignored directories (must not be traversed)
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]")

        node_dir = repo_path / "node_modules" / "lodash"
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / "index.js").write_text("module.exports = {}")

        # Act - Trigger the E2E analysis orchestration
        result = self.service.analyze_repository(
            repository_url=str(repo_path),
            project_id=self.project_id
        )

        # Assert ScanResult schema outputs
        self.assertIsInstance(result, ScanResult)
        
        # 5. Verify counts
        # Discovered files (excluding .git and node_modules):
        # - main.py
        # - index.js
        # - Component.tsx
        # - LICENSE
        # - SCRIPT.PY
        # - src/components/utils/helper.ts
        # Total = 6 files.
        self.assertEqual(result.total_files, 6)
        self.assertEqual(result.supported_files, 5)    # py, js, tsx, PY, ts
        self.assertEqual(result.unsupported_files, 1)  # LICENSE

        # 6. Verify languages counts mapping
        self.assertEqual(result.languages[Language.PYTHON], 2)
        self.assertEqual(result.languages[Language.JAVASCRIPT], 1)
        self.assertEqual(result.languages[Language.TYPESCRIPT], 2)
        self.assertEqual(result.languages[Language.UNKNOWN], 1)

        # 7. Check scan duration
        self.assertGreater(result.scan_duration, 0.0)

        # 8. Check that workspace cleanup was executed
        workspace_path = self.workspace_manager.get_workspace_path(self.project_id)
        self.assertFalse(workspace_path.exists())

    def test_e2e_pipeline_with_empty_repository(self) -> None:
        # Act
        result = self.service.analyze_repository(
            repository_url=self.temp_repo_source,
            project_id=self.project_id
        )
        
        # Assert empty result
        self.assertEqual(result.total_files, 0)
        self.assertEqual(result.supported_files, 0)
        self.assertEqual(result.unsupported_files, 0)
        
        # Verify workspace cleanup
        workspace_path = self.workspace_manager.get_workspace_path(self.project_id)
        self.assertFalse(workspace_path.exists())

    def test_e2e_pipeline_with_unsupported_only_repository(self) -> None:
        repo_path = Path(self.temp_repo_source)
        (repo_path / "notes.txt").write_text("text")
        (repo_path / "config.yaml").write_text("yaml")

        result = self.service.analyze_repository(
            repository_url=self.temp_repo_source,
            project_id=self.project_id
        )

        self.assertEqual(result.total_files, 2)
        self.assertEqual(result.supported_files, 0)
        self.assertEqual(result.unsupported_files, 2)
        self.assertEqual(result.languages[Language.UNKNOWN], 2)

    def test_large_scale_file_count_performance(self) -> None:
        # Scale: Create 200 dummy files inside the source directory
        repo_path = Path(self.temp_repo_source)
        for i in range(200):
            (repo_path / f"file_{i}.js").write_text("console.log(1);")

        # Run analysis pipeline and measure time performance
        result = self.service.analyze_repository(
            repository_url=self.temp_repo_source,
            project_id=self.project_id
        )

        self.assertEqual(result.total_files, 200)
        self.assertEqual(result.supported_files, 200)
        # Traversal and analysis should be extremely quick (sub-second)
        self.assertLess(result.scan_duration, 1.0)


if __name__ == "__main__":
    unittest.main()
