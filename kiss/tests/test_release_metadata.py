from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[2]


class ReleaseMetadataTests(unittest.TestCase):
    def test_historical_manifest_retains_its_version_and_provenance(self):
        manifest = json.loads(
            (REPO / "release-manifest.json").read_text(encoding="utf-8"))
        changelog = (REPO / "DESKTOP_CHANGELOG.md").read_text(encoding="utf-8")

        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertIn(f'## v{manifest["version"]}', changelog)
        self.assertEqual(manifest["ki_library"]["package_count"], 127)
        self.assertRegex(manifest["source"]["code_commit"], r"^[0-9a-f]{40}$")

    def test_all_desktop_release_assets_include_audit_metadata(self):
        spec = (REPO / "kiss" / "GeoForgeDesktopWindows.spec").read_text(encoding="utf-8")
        workflow = (REPO / ".github" / "workflows" / "windows-release.yml").read_text(
            encoding="utf-8")

        self.assertIn('release-manifest.json"), "."', spec)
        self.assertIn('DESKTOP_CHANGELOG.md"), "."', spec)
        for name in ("release-manifest.json", "DESKTOP_CHANGELOG.md",
                     "SHA256SUMS-Windows.txt", "Windows-release-validation.json",
                     "windows-frozen-smoke.json", "windows-installed-smoke.json"):
            self.assertIn(name, workflow)
        self.assertIn("-Algorithm SHA256", workflow)
        self.assertIn("historical_manifest =", workflow)
        self.assertIn("source_repository = $env:GITHUB_REPOSITORY", workflow)
        self.assertIn("source_commit = (git rev-parse HEAD)", workflow)

    def test_windows_release_versions_and_runtime_gate_agree(self):
        with (REPO / "kiss" / "pyproject.toml").open("rb") as stream:
            version = tomllib.load(stream)["project"]["version"]
        spec = (REPO / "kiss" / "GeoForgeDesktopWindows.spec").read_text(encoding="utf-8")
        installer = (REPO / "kiss" / "installer" / "GeoForgeDesktopWindows.iss").read_text(encoding="utf-8")
        workflow = (REPO / ".github" / "workflows" / "windows-release.yml").read_text(encoding="utf-8")
        self.assertIn(f'#define AppVersion "{version}"', installer)
        self.assertNotIn("default: windows-v", workflow)
        self.assertIn('"v$version", "windows-v$version"', workflow)
        self.assertIn('version=version_info', spec)
        self.assertIn('if len(ki_packages) != 127:', spec)
        self.assertNotIn('(str(REPO / "models"), "models")', spec)
        self.assertEqual(workflow.count('python tools/windows_release_smoke.py'), 2)

    def test_release_entrypoint_only_builds_native_windows(self):
        workflows = REPO / ".github" / "workflows"
        # BaseLoader keeps GitHub's YAML-1.2 key `on` intact.
        entry = yaml.load((workflows / "release.yml").read_text(encoding="utf-8"),
                          Loader=yaml.BaseLoader)
        native = yaml.load((workflows / "windows-release.yml").read_text(encoding="utf-8"),
                           Loader=yaml.BaseLoader)
        self.assertEqual(set(entry["jobs"]), {"windows"})
        self.assertEqual(entry["jobs"]["windows"]["uses"],
                         "./.github/workflows/windows-release.yml")
        self.assertEqual(entry["on"]["push"]["tags"], ["v*", "windows-v*"])
        self.assertNotIn("default", entry["on"]["workflow_dispatch"]["inputs"]["tag"])
        self.assertEqual(set(native["on"]), {"workflow_call"})
        self.assertEqual(set(native["jobs"]), {"build-and-publish"})
        self.assertEqual(native["jobs"]["build-and-publish"]["runs-on"], "windows-latest")
        steps = native["jobs"]["build-and-publish"]["steps"]
        self.assertTrue(any(step.get("with", {}).get("python-version") == "3.11"
                            for step in steps))
        self.assertTrue(any("kiss/GeoForgeDesktopWindows.spec" in step.get("run", "")
                            for step in steps))

    def test_release_workflows_preserve_existing_releases_and_fail_closed(self):
        workflow = (REPO / ".github" / "workflows" / "windows-release.yml").read_text(
            encoding="utf-8")
        for forbidden in ("--clobber", "gh release delete", "--delete-tag"):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("gh api --paginate", workflow)
        self.assertIn("cannot check existing releases; refusing publication", workflow)
        self.assertIn("release already exists (including drafts)", workflow)
        self.assertIn("gh release create $env:RELEASE_TAG @assets --verify-tag --draft", workflow)
        self.assertLess(workflow.index("release already exists"),
                        workflow.index("python -m PyInstaller"))

    def test_installer_support_and_updates_belong_to_windows_repository(self):
        installer = (REPO / "kiss" / "installer" / "GeoForgeDesktopWindows.iss").read_text(
            encoding="utf-8")
        self.assertIn('#define AppUrl "https://github.com/lzwei196/GeoForge-Desktop-Windows"',
                      installer)


if __name__ == "__main__":
    unittest.main()
