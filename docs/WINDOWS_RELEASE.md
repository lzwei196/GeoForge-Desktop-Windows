# Windows builds and releases

Use [GeoForge-Desktop-Windows releases](https://github.com/lzwei196/GeoForge-Desktop-Windows/releases)
for Windows installers and portable packages. The [main README](../README.md)
contains end-user setup instructions. The repository split did not create a new
binary; see [migration provenance](REPOSITORY_SPLIT.md).

## Native build contract

Build on native Windows x64 with Python 3.11 and Inno Setup 6. Keep `kiss/`,
`models/` and `ki_tools_common/` together. The checked-in
[`GeoForgeDesktopWindows.spec`](../kiss/GeoForgeDesktopWindows.spec) bundles the
Windows browser/tray frontend, console bridge, 127 KI packages, shared library
and calibration dependencies. Do not replace it with the old generic PyInstaller
command lines or use a macOS/Linux host to claim a Windows binary.

The automated steps live in
[`windows-release.yml`](../.github/workflows/windows-release.yml):

1. Refuse an existing release (including a draft) and check that the existing
   Git tag matches both the checked-out commit and application version.
2. Install build dependencies; run Desktop and shared-library regression tests
   separately because their top-level test package names overlap.
3. Build the checked-in Windows spec and check the Python DLL, KI count and UI.
4. Run [`windows_release_smoke.py`](../tools/windows_release_smoke.py) against
   the frozen folder outside the source checkout.
5. Compile the Inno Setup installer, install it to an isolated runner directory,
   run the same smoke checks there, then check silent uninstallation.
6. Package the portable ZIP, calculate SHA-256 hashes, and generate provenance
   and validation reports from that run.
7. Create a new draft with all assets, then publish it only after upload succeeds.

The test scope is application packaging and installation, not paid AI access or
scientific simulation/calibration acceptance. These checks must actually pass on
Windows before a new artifact is described as tested. Static workflow checks on
another OS do not establish that the native build succeeds.

## Publish a new version

Update `kiss/pyproject.toml`, the installer default version and the changelog as
appropriate for the new source release. Preserve historical manifests/reports;
`Windows-release-validation.json` records the new workflow's repository, tag,
source commit and check results. The bundled `release-manifest.json` remains a
clearly identified historical record and is not fresh build provenance.

Push a new `v<version>` or `windows-v<version>` tag, or run **Windows desktop
release** manually with an already-existing version-matching tag. Manual runs
have no historical-tag default. `windows-release.yml` is reusable only and is
called by this entrypoint; it is not a second independent publisher.

Never rerun this workflow to migrate or replace an old release. An existing
release fails the preflight, and release creation also fails if another run
created it in the meantime. A failed upload may leave a draft; that draft and
its assets are kept for an authorized maintainer to inspect. The workflow never
deletes a draft, retargets a tag or overwrites an asset.
