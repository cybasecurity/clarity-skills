# Changelog

All notable changes to the Clarity skills. Versions apply to every skill and every manifest together.

## 1.0.0 (2026-11-02)

First public release, under the [MIT License](/LICENSE).

- 22 skills for Clarity and Stacks development: `clarity:start` (router) plus scholar, security, auditor, testing, fuzzing, optimizer, deployment, upgrades, governance, epochs, assets, sip-compliance, protocols, ecosystem, oracles, staking, bitcoin-proofs, wallets, environments, apis and system-integration.
- One repository for every host. The plugin lives in `plugin/`: Claude Code and the Claude apps (`.claude-plugin/marketplace.json`, install `clarity@clarity-skills`) and Codex and ChatGPT (`.agents/plugins/marketplace.json`, per-skill `agents/openai.yaml`) list its skills under the plugin namespace (`clarity:start`, `clarity:scholar`, `clarity:fuzzing`). Its `SessionStart` hook points sessions inside Clarinet projects at `clarity:start`, the skills for common tasks and the router's pre-finish checklist.
- Hosts that list skills by folder name read the top-level `skills/`, a copy generated from `plugin/skills/` whose skills carry a `clarity-` prefix (`clarity-start`, `clarity-security`), so they cannot clash with other skill sets: Gemini CLI (`gemini-extension.json`, with `GEMINI.md` loading the router as context), Google Antigravity, GitHub Copilot and VS Code, Factory Droid, Devin, OpenCode and the `skills` CLI. The [install guide](/docs/INSTALL.md) gives the steps per host; `llms.txt` indexes the skills.
- Skills carry rules, decisions, exact call shapes and short fragments; the must-follow content of each skill is in its `SKILL.md`, and references keep lookup material. Each `SKILL.md` body stays within 24,000 bytes, the most Antigravity loads.
- Short skill descriptions: every session carries about 1,940 tokens of skill names and descriptions (measured with `claude plugin details`), under the 2,000 at which Claude Code's official marketplace flags a plugin.
- Skills that run bundled offline scripts pre-approve them for Claude Code (`allowed-tools`: `check_registry.py`, `lookup_function.py`, `compare_costs.py`, `inspect_costs.py`); the two scripts that reach the network still ask. Eight skills state their toolchain in `compatibility`.
- Directory listing metadata: logo and composer icon in `plugin/assets/`, category, brand color and links for the OpenAI plugin directory (`extensions.com.openai.interface`) and the Anthropic directory (`.claude-plugin/plugin.json`).
- Icons in black and gold: the plugin shows the three Clarity brackets, and each skill has its own glyph (`assets/icon-small.svg`, `assets/icon-large.png`), which Codex shows in its skill list (`agents/openai.yaml`) and the README shows in the skills table.
- [SECURITY.md](/docs/SECURITY.md) (private reports, and what the skills, the startup hook and the bundled scripts do on your machine), [CONTRIBUTING.md](/docs/CONTRIBUTING.md), a [code of conduct](/docs/CODE_OF_CONDUCT.md), an [AGENTS.md](/AGENTS.md) guide for agents working in the repository (imported by `CLAUDE.md`), bug report and addition request forms, a pull request template, and a CI workflow that checks the skills, the generated copy and every manifest on each push and pull request.
- Versioned releases: `main` holds the latest release, tagged `v<version>` with a GitHub Release, and work lands on `develop` first. Pin a tag to stay on one release.
- Baseline: Stacks epoch 4.0 (mainnet), Clarity 1-6, Clarinet 3.26.0, Clarinet SDK 3.26.0, Vitest 5.0.5, Clarigen 4.1.7, `@stacks/transactions` 7.6.0, Node 22.18 or later. Protocol (195 contracts) and system (18 records) address registries verified on chain, oldest check 2026-10-20 (dates in each owning skill).
