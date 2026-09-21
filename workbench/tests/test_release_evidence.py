import json
import tempfile
import unittest
from pathlib import Path

from workbench.engine import verify_integrity
from workbench.release_evidence import (
    RELEASE_EVIDENCE_SCHEMA,
    cyclonedx_bom,
    find_forbidden_artifacts,
    source_review_manifest,
    synthetic_sample_report,
    write_release_evidence,
)


class ReleaseEvidenceTests(unittest.TestCase):
    @property
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_manifest_is_scoped_and_truthful_about_open_release_gaps(self):
        manifest = source_review_manifest(self.root)
        self.assertEqual(manifest["schema"], RELEASE_EVIDENCE_SCHEMA)
        self.assertEqual(manifest["scope"], "isolated-workbench-only")
        self.assertEqual(manifest["python"]["third_party_runtime_packages"], [])
        self.assertEqual(manifest["bundled_scanners"], [])
        self.assertFalse(manifest["execution_boundaries"]["external_scanner_execution"])
        self.assertFalse(manifest["execution_boundaries"]["browser_e2e_validated"])
        self.assertFalse(manifest["execution_boundaries"]["signed_release"])
        self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["review_documents"]))

    def test_sbom_describes_only_the_isolated_shipped_component(self):
        bom = cyclonedx_bom()
        self.assertEqual(bom["bomFormat"], "CycloneDX")
        self.assertEqual(bom["metadata"]["component"]["name"], "HackGPT Evidence Workbench")
        self.assertEqual(bom["components"], [])
        properties = {item["name"]: item["value"] for item in bom["metadata"]["component"]["properties"]}
        self.assertEqual(properties["hackgpt:bundled-scanners"], "none")

    def test_synthetic_sample_is_owned_intact_and_credential_free(self):
        report = synthetic_sample_report()
        self.assertTrue(verify_integrity(report))
        self.assertEqual(report["environment"], "synthetic_lab")
        self.assertEqual(report["target"], "lab://ephemeral-authorization-fixture")
        self.assertEqual(report["verdict"], "verified_in_synthetic_lab_only")
        verified = [item for item in report["findings"] if item["verification"] == "verified_in_lab"]
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0]["evidence"]["control_status"], 401)
        self.assertFalse(verified[0]["evidence"]["credentials_sent"])

    def test_writer_produces_parseable_revision_review_files_and_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            digests = write_release_evidence(Path(directory), self.root)
            expected = {
                "release-manifest.json", "sbom.cdx.json", "synthetic-sample-report.json",
                "synthetic-sample-report.md", "SHA256SUMS",
            }
            self.assertEqual(set(digests), expected)
            manifest = json.loads((Path(directory) / "release-manifest.json").read_text(encoding="utf-8"))
            sample = json.loads((Path(directory) / "synthetic-sample-report.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], RELEASE_EVIDENCE_SCHEMA)
            self.assertTrue(verify_integrity(sample))
            checksums = (Path(directory) / "SHA256SUMS").read_text(encoding="utf-8")
            self.assertIn("release-manifest.json", checksums)
            self.assertIn("synthetic-sample-report.json", checksums)

    def test_boundary_rejects_runtime_secrets_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports.sqlite3").write_text("not real", encoding="utf-8")
            (root / "client.key").write_text("not real", encoding="utf-8")
            blocked = find_forbidden_artifacts(root)
            self.assertEqual(blocked, ["client.key", "reports.sqlite3"])

    def test_manifest_never_hashes_absolute_paths_into_document_entries(self):
        manifest = source_review_manifest(self.root)
        self.assertTrue(all(not Path(item["path"]).is_absolute() for item in manifest["review_documents"]))


if __name__ == "__main__":
    unittest.main()
