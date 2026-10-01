# Windows repository migration — 2026-10-01

GeoForge Desktop's Windows application source, installer and releases now belong
to [GeoForge-Desktop-Windows](https://github.com/lzwei196/GeoForge-Desktop-Windows).
Future development uses `main`.

## Source provenance

- Original repository: `lzwei196/KISS---Knowledge-Infrastructure-for-Scientific-Simulation`
  (now the canonical [KISS repository](https://github.com/lzwei196/KISS-Knowledge-Infrastructure-for-Scientific-Simulation)).
- Original branch: `windows-version`.
- Imported source commit: `96409ba3bcbf64322ca7a8eba4ba8e2bf32df535`.
- The migration commit descends from that commit; the Windows branch's Git
  history is retained rather than replaced by a source-only snapshot.
- Historical tags and migrated release assets identify their original builds.
  Moving an asset does not rebuild it or extend its original verification scope.

This is a source/repository migration, **not a new compiled release**. No native
Windows build, installer run, provider acceptance test, scientific model run or
calibration was rerun as part of the split. The application version is unchanged.
`release-manifest.json` and older build reports are deliberately retained as
historical evidence; their original repository/branch/commit fields are not
rewritten to imply that they describe a new build in this repository.

## Repository responsibilities

| Repository | Responsibility |
| --- | --- |
| [Windows](https://github.com/lzwei196/GeoForge-Desktop-Windows) | Windows application, packaging, tests, issues and releases |
| [macOS](https://github.com/lzwei196/GeoForge-Desktop-macOS) | macOS application and releases |
| [Linux](https://github.com/lzwei196/GeoForge-Desktop-Linux) | Linux application and releases |
| [KISS](https://github.com/lzwei196/KISS-Knowledge-Infrastructure-for-Scientific-Simulation) | Canonical KI library on `main` |

`models/` and `ki_tools_common/` remain siblings of `kiss/`. They are still part
of the offline application bundle; splitting repositories is not a submodule
conversion or a change to the discovery/import contract. Automatic KI updates
use canonical KISS `main`, with the existing Windows guidance-preservation guard
and environment override behavior unchanged. The legacy first-run KI `v0.2.0`
download endpoint is retained for compatibility, not redirected to Desktop.

## Future releases

The [release entrypoint](../.github/workflows/release.yml) only delegates to the
[native Windows workflow](../.github/workflows/windows-release.yml). It does not
build or upload macOS/Linux artifacts. New releases require a version-matching
existing tag and successful source, frozen and installed-application checks.
Existing releases, including drafts, are refused: there is no asset clobber or
automatic draft deletion. See [the release guide](WINDOWS_RELEASE.md).

## Migration source checks

On macOS with Python 3.13, using this checkout's `kiss/` and `ki_tools_common/`
on `PYTHONPATH` (not an unrelated installed editable package):

- Focused release metadata, updater, Windows contract, portability and bundled
  harness checks: **55 passed, 30 skipped, 2 subtests passed**. Skips include
  native Windows-only checks; localhost fixture tests required socket access.
- Existing shared-library/Flow source suite: **327 passed, 7 skipped**; six
  expected unequal-length metric fixture warnings.
- Source CLI catalogue discovery: **127 of 127 packages**.
- Workflow YAML contract tests, changed Python/spec parsing, smoke-driver
  `--help`, and `git diff --check` passed.

The broader Desktop run was **not fully green** on this host: **1,450 passed,
38 skipped, 288 subtests passed, 9 failed**. All nine failures are in the
unchanged `kiss/tests/test_runtime.py`, and reproduce when run alone: eight
mock Windows `os.name` and encounter Python 3.13's `WindowsPath` construction
refusal on macOS; one expects `telemac2d.exe` while POSIX returns `telemac2d`.
That test file and the involved `install.py`/`runnable.py` implementations are
identical to the imported source commit. They were not relaxed or changed to
make a Windows-oriented suite appear green on this non-Windows host.

PowerShell and `actionlint` were unavailable on this host. No Windows executable
or installer was built or run, and these source checks do not substitute for
the native release workflow's acceptance checks.
