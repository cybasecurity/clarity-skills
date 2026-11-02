# Installing the Clarity Skills

The skills link to each other: install the whole set, never a single folder. Install it separately in each tool you use.

| Host | Install | Startup hook | Skills appear as |
|---|---|---|---|
| [Claude Code](#claude-code) | Plugin marketplace | Yes | `/clarity:start` |
| [Codex CLI](#codex-cli) | Plugin marketplace | Yes, after you review it | `$clarity:start` |
| [Gemini CLI](#gemini-cli) | Extension | No; the router loads as context | `clarity-start` |
| [Google Antigravity](#google-antigravity) | Plugin | No | `/clarity-start` |
| [OpenCode](#opencode) | Clone and add the folder to the config | No | `clarity-start` |
| [Other agents](#other-agents) | Skills CLI, ask your agent, copy, or point at the router | No | `clarity-start` |
| [Coming soon](#coming-soon) | Claude apps, ChatGPT, GitHub Copilot and VS Code, Factory Droid, Devin CLI, Cline, Kiro, Cursor, and the Claude and ChatGPT directories | | |

Claude Code, the Claude apps and Codex install the plugin in [`plugin/`](/plugin) and list its skills under the `clarity:` namespace. The other hosts read the repository's top-level [`skills/`](/skills) folder: a generated copy of the same skills whose names carry a `clarity-` prefix (`clarity-start`, `clarity-security`), so they cannot clash with other skill sets. Where the startup hook doesn't run, begin a Clarity task by asking for the router (`clarity-start`), or add the project instruction from [Other agents](#other-agents).

---

## Claude Code

Works in the terminal, the VS Code and JetBrains extensions, and the desktop app's Code tab.

```text
/plugin marketplace add cybasecurity/clarity-skills
/plugin install clarity@clarity-skills
```

Or in one step from your shell:

```sh
claude plugin install clarity --marketplace cybasecurity/clarity-skills
```

- When asked, choose the user (every project), project (shared with the repository's collaborators) or local scope.
- Describe the task and the router picks the skills, or invoke one directly: `/clarity:start`, `/clarity:scholar`, `/clarity:fuzzing`.
- Update with `claude plugin update clarity@clarity-skills`. Marketplaces you add don't update automatically unless you turn it on in `/plugin` > Marketplaces.
- Remove with `claude plugin uninstall clarity@clarity-skills`, then `claude plugin marketplace remove clarity-skills`.
- Try a checkout without installing it with `claude --plugin-dir /path/to/clarity-skills/plugin`.

For a team, commit this to the project's `.claude/settings.json`. Collaborators get the plugin after they trust the folder:

```json
{
  "extraKnownMarketplaces": {
    "clarity-skills": { "source": { "source": "github", "repo": "cybasecurity/clarity-skills" } }
  },
  "enabledPlugins": { "clarity@clarity-skills": true }
}
```

Claude Code on the web (cloud sessions) does not install plugins.

The plugin registers one `SessionStart` hook ([plugin/hooks/clarity-context.sh](/plugin/hooks/clarity-context.sh)). When a session starts in a Clarity/Stacks project (a `Clarinet.toml` or `.clar` files three levels deep with `node_modules` skipped, an `@stacks/` or Clarinet dependency in `package.json`, or sBTC/Clarinet named in the top-level `TASK.md`, `README.md` or `AGENTS.md`), it adds one line of context (about 200 tokens) naming `clarity:start` and the skills for common tasks (audit, contract changes, upgrades, tests, deployment, protocol integration, chain data), and asking that builds and contract changes pass the router's "Before calling a contract done" checklist before they are reported as done; elsewhere it prints nothing. Without it, sessions that begin inside an existing repository rarely consult any skill. Remove `plugin/hooks/` from your copy to disable it.

---

## Claude Apps (claude.ai, Claude Desktop, Cowork)

*Coming soon: these steps are not verified yet.*

Needs a Pro, Max, Team or Enterprise plan, with **Code execution and file creation** turned on in Settings > Capabilities.

1. Open **Customize > Plugins** ([claude.ai/customize/plugins](https://claude.ai/customize/plugins)).
2. Select **Add > Add marketplace** and enter `cybasecurity/clarity-skills`.
3. Add **clarity**.

The plugin is saved to your account, so it also loads in Cowork and, as a synced plugin, in Claude Code. In chat, describe the task, or type `/` and pick a `clarity:` skill. To update, select **Check for updates**, or turn on **Sync automatically** for the marketplace. Chat does not run the startup hook; Cowork does.

On Team and Enterprise plans, an Owner can add the marketplace for everyone in **Organization settings > Plugins & skills** and make the plugin available, installed by default or required.

---

## Codex CLI

```sh
codex plugin marketplace add cybasecurity/clarity-skills
codex plugin add clarity@clarity-skills
```

Start a new session afterwards. You can also install from `/plugins` inside Codex. The ChatGPT desktop app (**Plugins > +**) is coming soon. The Codex IDE extension does not load plugins.

- Describe the task, or invoke a skill with `$clarity:start`, `$clarity:auditor` and so on. The skill picker shows display names such as **Clarity Fuzzing**.
- Codex asks you to review the startup hook before it runs it.
- Update with `codex plugin marketplace upgrade clarity-skills`.
- Remove with `codex plugin remove clarity@clarity-skills`.

The plugin's manifest is [`plugin/plugin.json`](/plugin/plugin.json) and the Codex marketplace [`.agents/plugins/marketplace.json`](/.agents/plugins/marketplace.json). Each skill also carries Codex metadata in `agents/openai.yaml`.

---

## ChatGPT Workspaces

*Coming soon: these steps are not verified yet.*

Workspace admins can offer the plugin to their members: **Admin > Plugins > Add > Import marketplace**, enter `https://github.com/cybasecurity/clarity-skills`, then make `clarity` available or installed for the roles that need it. Members pick it with `@` in a chat. The workspace re-syncs the marketplace daily.

---

## Gemini CLI

```sh
gemini extensions install https://github.com/cybasecurity/clarity-skills
```

- Skills appear as `clarity-start`, `clarity-security` and so on. Instead of a startup hook, [`GEMINI.md`](/GEMINI.md) loads the router into every session as context.
- Update with `gemini extensions update clarity`.
- Remove with `gemini extensions uninstall clarity`.

---

## Google Antigravity

```sh
agy plugin install https://github.com/cybasecurity/clarity-skills
```

- Each skill is also a slash command: `/clarity-start`, `/clarity-security`.
- Remove with `agy plugin uninstall clarity`. To update, install again.

---

## GitHub Copilot CLI and VS Code

*Coming soon: these steps are not verified yet.*

Copilot CLI:

```sh
copilot plugin marketplace add cybasecurity/clarity-skills
copilot plugin install clarity@clarity-skills
```

- Update with `copilot plugin update clarity`.
- Remove with `copilot plugin uninstall clarity`.

VS Code (agent plugins, with `chat.plugins.enabled` on): run **Chat: Install Plugin From Source** from the Command Palette and enter `https://github.com/cybasecurity/clarity-skills`.

Copilot and VS Code list the skills as `clarity-start`, `clarity-security` and so on, and do not run the startup hook.

---

## Factory Droid

*Coming soon: these steps are not verified yet.*

```sh
droid plugin marketplace add cybasecurity/clarity-skills
droid plugin install clarity@clarity-skills --scope user
```

- Update with `droid plugin update clarity@clarity-skills`.
- Remove with `droid plugin uninstall clarity@clarity-skills`.

Use `--scope project` to share the install with a repository.

---

## Devin CLI

*Coming soon: these steps are not verified yet.*

```sh
devin plugins install cybasecurity/clarity-skills
```

- Update with `devin plugins update clarity`.
- Remove with `devin plugins remove clarity`.

---

## OpenCode

Clone the repository and add its `skills` folder to your OpenCode config (`~/.config/opencode/opencode.json`, or `opencode.json` in a project):

```sh
git clone https://github.com/cybasecurity/clarity-skills ~/clarity-skills
```

```json
{
  "skills": { "paths": ["~/clarity-skills/skills"] }
}
```

`opencode debug skill` lists the 22 skills, from `clarity-apis` to `clarity-wallets`. Update with `git pull` in the clone. OpenCode does not run the startup hook.

---

## Cline

*Coming soon: these steps are not verified yet.*

```sh
cline skill add https://github.com/cybasecurity/clarity-skills/tree/main/skills --skill '*' -g
```

This installs the 22 skills into `~/.agents/skills`, which the Cline CLI and the VS Code extension both read; `cline config skills` lists them. Update with `npx skills update -g`. Cline does not run the startup hook.

The repository root is also an [Agent Plugin](https://agent-plugins.org): the Cline CLI loads a clone in `~/.agents/plugins/clarity` as one plugin that can be turned on and off, with its skills named `clarity:clarity-start` and so on. The VS Code extension does not read that folder.

---

## Kiro

*Coming soon: these steps are not verified yet.*

```sh
npx skills add https://github.com/cybasecurity/clarity-skills/tree/main/skills --skill '*' -a kiro-cli -g
```

This installs the 22 skills into `~/.kiro/skills`, which the Kiro IDE and CLI both read. Each skill is also a slash command (`/clarity-start`). Update with `npx skills update -g`.

In the IDE you can instead add the repository as a power: **Powers > Add Custom Power > Import power from GitHub**, then enter `https://github.com/cybasecurity/clarity-skills`. The Kiro CLI installs a clone as a power with `kiro-cli powers install ~/clarity-skills`, and uses powers only with the v3 agent engine. Kiro activates a power when the conversation mentions one of its keywords.

---

## Coming Soon

Support for the Claude apps, the ChatGPT desktop app and workspaces, GitHub Copilot and VS Code, Factory Droid, Devin CLI, Cline, Kiro and Cursor is on the way, and so are listings in the Claude directory and the ChatGPT Plugins directory. Those hosts' sections above show the expected steps, which are not verified yet. Until then, most of these tools can use the [Other agents](#other-agents) route.

---

## Other Agents

Any other tool that reads [Agent Skills](https://agentskills.io/specification) can use the top-level [`skills/`](/skills) folder. Its skills carry the `clarity-` prefix, so they can sit next to other skill sets. Install all 22, since they link to each other, in any of these ways:

- Use the Skills CLI, pointed at the `skills/` folder rather than the repository root, where it would also pick up the Claude Code plugin's copies:

  ```sh
  npx skills add https://github.com/cybasecurity/clarity-skills/tree/main/skills --skill '*'
  ```

- Ask your agent by pasting this into its chat:

  ```text
  Install the Clarity skills from https://github.com/cybasecurity/clarity-skills: copy every folder in its skills/ directory into your skills directory, then use clarity-start for Clarity and Stacks tasks.
  ```

- Clone the repository and copy or link every `skills/clarity-*` folder into your tool's skills directory.
- Clone the repository and point the agent at the router in its project instructions (`AGENTS.md` or a rules file):

  ```text
  Before writing, testing or reviewing Clarity contracts, read /path/to/clarity-skills/skills/clarity-start/SKILL.md and the skills it names for the task.
  ```

[`llms.txt`](/llms.txt) lists every skill with its description.

For developers: the Claude Agent SDK loads the plugin folder of a clone as a local plugin (`plugins: [{ type: "local", path: "./clarity-skills/plugin" }]`). The Claude API takes skills uploaded one folder at a time to `/v1/skills`, at most 20 per request: upload folders from `skills/`, and attach `clarity-start` and the skills the task needs.

---

## Example Prompts

```text
Build a USDCx vault with a 7-day withdrawal queue and tests.
Review contracts/vault.clar for security issues.
Make this vault upgradable without migrating user funds.
Integrate a Zest flash loan to liquidate an unhealthy position, then deposit the surplus in Hermetica.
Deploy this project to mainnet; it depends on sBTC.
```
