import os
import tempfile
import unittest
from pathlib import Path

from workbench.project_adapter import ProjectMetadataAdapter, ProjectScanPolicy


class ProjectMetadataAdapterTests(unittest.TestCase):
    def test_vulnerable_fixture_reports_filename_without_reading_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.production").write_text("DATABASE_PASSWORD=SHOULD_NOT_LEAK")
            (root / "app.py").write_text("print('ok')")
            result = ProjectMetadataAdapter().run(root, asset_key="project-fixture")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["coverage"]["objects_tested"], 2)
        self.assertEqual(len(result["findings"]), 1)
        finding = result["findings"][0]
        self.assertEqual(finding["verification"], "candidate")
        self.assertEqual(finding["evidence"]["relative_path"], ".env.production")
        self.assertFalse(finding["evidence"]["content_read"])
        self.assertNotIn("SHOULD_NOT_LEAK", repr(result))

    def test_corrected_fixture_has_no_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("print('ok')")
            result = ProjectMetadataAdapter().run(root, asset_key="project-fixture")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["coverage"]["objects_total"], 1)

    def test_file_limit_marks_coverage_partial_and_total_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(5):
                (root / f"file-{index}.txt").write_text("x")
            result = ProjectMetadataAdapter(ProjectScanPolicy(max_files=2)).run(root, asset_key="project-fixture")
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["coverage"]["objects_tested"], 2)
        self.assertIsNone(result["coverage"]["objects_total"])
        self.assertTrue(any("partial" in note.lower() for note in result["coverage"]["notes"]))

    def test_excluded_directory_is_not_scanned_and_is_disclosed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ignored = root / "node_modules"
            ignored.mkdir()
            (ignored / ".env").write_text("SECRET=not-read")
            (root / "main.py").write_text("pass")
            result = ProjectMetadataAdapter().run(root, asset_key="project-fixture")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["coverage"]["objects_tested"], 1)
        self.assertTrue(any("node_modules" in note for note in result["coverage"]["notes"]))

    def test_symlink_outside_root_is_never_followed(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external = Path(outside) / ".env"
            external.write_text("OUTSIDE_SECRET=not-read")
            try:
                (root / "external-link").symlink_to(external)
            except OSError:
                self.skipTest("symlink creation unavailable")
            result = ProjectMetadataAdapter().run(root, asset_key="project-fixture")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["coverage"]["objects_tested"], 0)
        self.assertTrue(any("symlink" in note.lower() for note in result["coverage"]["notes"]))

    def test_symlink_root_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as link_parent:
            link = Path(link_parent) / "root-link"
            try:
                link.symlink_to(Path(directory), target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(ValueError):
                ProjectMetadataAdapter().run(link, asset_key="project-fixture")

    def test_non_directory_root_is_rejected(self):
        with tempfile.NamedTemporaryFile() as file:
            with self.assertRaises(ValueError):
                ProjectMetadataAdapter().run(file.name, asset_key="project-fixture")

    def test_policy_rejects_unbounded_or_unsafe_values(self):
        for kwargs in (
            {"max_files": 0}, {"max_files": 5001}, {"max_depth": 17}, {"timeout_seconds": 0},
            {"excluded_dirs": frozenset({"../outside"})}, {"excluded_dirs": {"node_modules"}},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ProjectScanPolicy(**kwargs)

    def test_execution_declaration_reflects_policy_and_has_no_execution_escape(self):
        declaration = ProjectMetadataAdapter(ProjectScanPolicy(max_files=77, timeout_seconds=9)).execution_declaration()
        self.assertEqual(declaration["launcher"], "native_python")
        self.assertEqual(declaration["effect_level"], "read_only")
        self.assertEqual(declaration["filesystem"], "read_only_metadata")
        self.assertEqual(declaration["network"], "none")
        self.assertFalse(declaration["subprocess"])
        self.assertFalse(declaration["writes"])
        self.assertFalse(declaration["follows_symlinks"])
        self.assertEqual(declaration["limits"]["max_objects"], 77)
        self.assertEqual(declaration["limits"]["timeout_seconds"], 9)

    def test_fingerprint_is_stable_for_same_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "credentials.json").write_text("not read")
            adapter = ProjectMetadataAdapter()
            first = adapter.run(root, asset_key="same-project")
            second = adapter.run(root, asset_key="same-project")
        self.assertEqual(first["findings"][0]["fingerprint"], second["findings"][0]["fingerprint"])

    def test_fingerprint_changes_between_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "credentials.json").write_text("not read")
            adapter = ProjectMetadataAdapter()
            first = adapter.run(root, asset_key="project-a")
            second = adapter.run(root, asset_key="project-b")
        self.assertNotEqual(first["findings"][0]["fingerprint"], second["findings"][0]["fingerprint"])


if __name__ == "__main__":
    unittest.main()
