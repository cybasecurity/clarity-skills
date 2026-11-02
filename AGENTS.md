# Contributing to the Clarity Skills

This file is for AI agents working in this repository. People start with [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md); this file adds the technical detail an agent needs to make a change that passes review.

## Resources

Specifications and official documentation:

- [Agent Skills specification](https://agentskills.io/specification), the format every host reads
- [Claude Code plugins](https://code.claude.com/docs/en/plugins) and [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

The rules for a change are in [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). What the startup hook and the scripts may do on a user's machine is in [docs/SECURITY.md](docs/SECURITY.md).

Reference skills to copy from:

| Shape | Skill | What it shows |
|---|---|---|
| One file | [oracles](plugin/skills/oracles/) | A self-contained `SKILL.md` with Codex metadata and icons |
| References and a script | [scholar](plugin/skills/scholar/) | Lookup material in `references/`, an offline script pre-approved in `allowed-tools` |
| Registries and the network | [protocols](plugin/skills/protocols/) | Dated address registries, an offline age check and a read-only network check |
| Router | [start](plugin/skills/start/) | The task table that names the skills to load, and the pre-finish checklist |

## Technical Reference

### Repository Layout

```
plugin/                        # what Claude Code, the Claude apps and Codex install
  plugin.json                  # Codex manifest
  .claude-plugin/plugin.json   # Claude Code manifest
  hooks/                       # the SessionStart hook
  skills/<name>/
    SKILL.md                   # frontmatter and the must-follow rules
    references/                # lookup material, loaded on demand
    scripts/                   # Python standard library helpers
    agents/openai.yaml         # Codex display name, short description and icons
    assets/                    # icon-small.svg and icon-large.png
skills/clarity-<name>/         # generated copy for hosts that list skills by folder name
docs/                          # install guide, contributing, security policy, code of conduct, changelog
  assets/banner.png            # README banner, rendered by the maintainers' logo generator
plugin.json                    # Agent Plugins manifest for hosts that read skills/
gemini-extension.json          # Gemini CLI manifest; GEMINI.md loads the router as context
llms.txt                       # generated index of the skills
```

The marketplaces live in `.claude-plugin/`, `.agents/plugins/`, `.github/plugin/`, `.factory-plugin/` and `.cursor-plugin/`.

Edit skills only in `plugin/skills/`. Never edit `skills/` or `llms.txt` by hand: maintainers regenerate them at each release, renaming `clarity:<name>` to `clarity-<name>`. Until then they lag behind `develop`, and CI skips the copy check there.

### Frontmatter

From `plugin/skills/scholar/SKILL.md`:

```yaml
---
name: scholar
description: "Write, build or refactor Clarity (.clar) contracts: syntax, types, responses, errors, traits, loops and layout. Use before writing or editing Clarity code, fixing compile errors, or answering how Clarity code behaves: what an expression returns, what aborts or rolls back, what the VM checks."
license: MIT
compatibility: "Optional: Python 3.10+ for scripts/lookup_function.py. Examples assume Clarinet 3.26.0 (Clarity 6 at epoch 4.0)."
allowed-tools: "Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/lookup_function.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-10-19"
---
```

- Use only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Some hosts reject any other field.
- `name` equals the folder name: lowercase words joined by hyphens.
- Keep each field on one line, quote the description, and quote every value in the `metadata` map. The check parses nothing else.
- The description is at most 1,024 characters. Say what the skill covers, then when to use it, in the words a user would type.
- `allowed-tools` may only pre-approve bundled scripts, as `Bash(python3 <path> *)` with `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`. Pre-approve offline scripts only; a network script must always ask.
- Leave `metadata.version` alone. A release bumps every skill and manifest together.
- `baseline_date` is the date of the skill's last editorial review.

### Budgets

- Every session carries every skill's name and description, so all descriptions together stay within 4,650 characters.
- A `SKILL.md` body stays under 24,000 bytes, the most Google Antigravity reads. Move lookup material to `references/`.

### Names and Links

- Refer to another skill as `clarity:<name>` in text, and link to it with a relative path such as `../security/SKILL.md#security-patterns-a01-a29`.
- Links inside `plugin/` must resolve and stay inside `plugin/`.
- Links in `docs/` start with `/`, such as `/docs/SECURITY.md`. GitHub's Contributing and Security tabs resolve links from the repository root.

### Scripts

- Use only the Python 3.10 standard library.
- Give each script a module docstring that says what it does and how to run it.
- Read files and print results. Write a file only to a path the user passes.
- Never execute the user's repository or contracts, and never sign or broadcast a transaction.
- A new network call needs discussion in an issue first. The existing network scripts query a Stacks node API and send `HIRO_API_KEY` only to `hiro.so` hosts.

### Startup Hook

`plugin/hooks/clarity-context.sh` runs at every session start, clear and compact. Keep it POSIX `sh`, fast and offline. It writes nothing and prints one line of context or nothing. A change to its message changes how often the skills load, so explain the reason in the pull request.

## Quality Standards

### What a Skill Holds

- `SKILL.md` holds the rules, decisions, exact call shapes and short fragments an agent must follow. `references/` holds lookup material: tables, signatures and longer examples.
- Teach what models get wrong about Clarity and Stacks. Do not restate what a model already knows.
- Say why a rule exists and what fails without it.
- Never tell an agent to fetch instructions or registries at run time.

### Evidence

- Back each claim about Clarity behavior with a link to the implementation or specification, pinned to a commit.
- List every commit a skill's links use in its `Reference baseline` section, and name the Clarity version and epoch its examples were checked on.
- An address or function signature needs the deployed contract: its source, the deployment transaction and, for state, a read-only call result.
- Address registries record when they were last verified (`registry_verified_at`). Releases refresh them, so describe an address change in the pull request with its evidence.

### Style

Short sentences, no em dashes, and examples that run.

## Adding or Renaming a Skill

Change all of these together:

- the folder in `plugin/skills/<name>/`, with `SKILL.md`, `agents/openai.yaml`, `assets/icon-small.svg` and `assets/icon-large.png`
- the router's "Load by task" table in `plugin/skills/start/SKILL.md`
- the skills table in `README.md` (the Skills section)
- the Skill dropdown in `.github/ISSUE_TEMPLATE/bug_report.yml`

Keep the description budget in mind. Maintainers regenerate `skills/` and `llms.txt`.

When a change alters what the hook or a script does, update `docs/SECURITY.md`. When it alters an install step or a manifest, update that host's section in `docs/INSTALL.md`, and the short install commands in `README.md` if they change. Add an entry for any user-visible change to the unreleased section at the top of `docs/CHANGELOG.md`.

## Branches and Releases

- Branch from `develop` and open the pull request against `develop`. A pull request that fixes a bug links to its report from the [bug report form](https://github.com/cybasecurity/clarity-skills/issues/new?template=bug_report.yml). `main` holds the latest release. Its pull requests come only from `develop` or a `hotfix/` branch, and CI rejects any other.
- A release bumps `metadata.version` and every manifest, regenerates `skills/` and `llms.txt`, and dates the changelog section. Maintainers merge it into `main`, tag it `v<version>` and publish a GitHub Release with that changelog section as its notes.
- Hosts follow releases: Claude Code updates when the version changes, Gemini CLI installs the latest GitHub Release, and the skills CLI reads `main`.

## Before Finishing

Pull requests run [`.github/workflows/validate.yml`](.github/workflows/validate.yml) on GitHub, so nothing needs to run locally. It runs `.github/scripts/check_package.py` (with `--develop` on `develop`, which skips the generated copy), compiles every bundled script and runs `claude plugin validate --strict` on `plugin/` and on the repository root. A pull request into `main` also runs `.github/scripts/check_release.py`, which needs a version newer than the last release and a dated changelog section. If the user wants the result before pushing, `python3 .github/scripts/check_package.py --develop` only reads the repository.

### What the Check Enforces

Each of these fails the pull request, so there is no need to check them by hand:

- frontmatter fields, the name, the description and compatibility lengths, and the `metadata` map
- `metadata.version` matching `plugin/plugin.json`
- `allowed-tools` naming only `Bash(python3 <path> *)` rules for scripts that exist
- `agents/openai.yaml` pointing `icon_small` and `icon_large` at files that exist
- the body size and the description budget
- the generated `skills/` copy holding the same skills and files as `plugin/skills/`, on `main` and pull requests into it
- relative links that resolve, GitHub `blob` and `tree` links in skill pages pinned to a 40-hex commit, root-relative links in `docs/`, and the images in `README.md`
- the bug report form listing every skill
- every manifest and marketplace naming the same plugin, version and source
- for a pull request into `main`: a source branch of `develop` or `hotfix/`, a newer version and a dated changelog section

### What No Tool Checks

- The description triggers on the words a user would type.
- The rule is correct on the epoch it names, and the evidence supports it.
- The examples run.
- The change does not contradict another skill, such as `clarity:security` and `clarity:scholar` on the same function.
- Addresses and signatures match the deployed contracts.
