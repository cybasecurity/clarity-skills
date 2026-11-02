# Contributing

Corrections and additions are welcome as issues or pull requests. Open pull requests against the `develop` branch; `main` holds the latest release. Report every bug with the [bug report form](https://github.com/cybasecurity/clarity-skills/issues/new?template=bug_report.yml), which asks for the evidence listed below. A pull request that fixes a bug links to its report. Ask for a new protocol, skill or host with the [addition request form](https://github.com/cybasecurity/clarity-skills/issues/new?template=addition_request.yml). For security problems, follow [SECURITY.md](/docs/SECURITY.md) instead of opening an issue.

## What a Change Needs

- Back the change with evidence: a minimal example, the affected Clarity version and epoch, and a link to the implementation, specification or chain evidence. Address and signature changes need the deployed contract: its source, the deployment transaction and, for state, a read-only call result.
- Edit the skills in [`plugin/skills/`](/plugin/skills). The top-level [`skills/`](/skills) folder is generated from them (`clarity:<name>` becomes `clarity-<name>`); maintainers regenerate it at each release.
- Leave version numbers alone: each release bumps every skill and manifest together.
- Keep descriptions short, since every session carries each skill's name and description: 4,650 characters across all skills. Keep each `SKILL.md` body under 24,000 bytes, the most Google Antigravity reads, and move lookup material to `references/`.
- Do not fetch anything at run time: skills never load instructions or registries from a remote copy. Bundled scripts use only the Python 3.10 standard library, and a new network call needs discussion first.
- Write short sentences and examples that run.

## Checks

Pull requests run [`.github/workflows/validate.yml`](/.github/workflows/validate.yml) on GitHub, so you do not need to run anything on your machine. If a check fails, the pull request shows why and a maintainer can help fix it. Issues need no checks: the bug report form asks for the evidence listed above.

## Releases

Work lands on `develop`. When it is ready, maintainers merge it into `main` with a new version for every skill and manifest, regenerate `skills/`, and tag the release (`v1.0.0`) with its notes from the [changelog](/docs/CHANGELOG.md).

## Conduct and License

Participation follows the [code of conduct](/docs/CODE_OF_CONDUCT.md). Contributions are licensed under the [MIT License](/LICENSE).
