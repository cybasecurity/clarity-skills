# Security Policy

## Reporting a Vulnerability

Report suspected security vulnerabilities in the Clarity skills privately to [security@cybasecurity.io](mailto:security@cybasecurity.io), or with GitHub's private vulnerability reporting (Report a vulnerability, on the repository's Security tab).

Please do not disclose vulnerabilities in public GitHub issues, pull requests, or discussions before coordinating with us.

Include the affected release or commit, the skill and file, a description of the issue and its potential impact, and enough detail to help us reproduce it, such as a minimal example or chain evidence. Remove credentials, private keys, seed phrases, and API keys from any logs or attachments.

We will review the report and coordinate any fix and disclosure with you.

For ordinary bugs and feature requests, use the [GitHub issue tracker](https://github.com/cybasecurity/clarity-skills/issues).

## Security Posture

The Clarity skills guide the code an AI agent writes and the reviews it performs. They do not make that code safe: review and test what the agent produces, and have contracts that hold value audited before you deploy them.

- There is no telemetry: nothing reports usage, prompts, or code to us or anyone else.
- Nothing is fetched at run time: the skills never load instructions or data from a remote copy.
- On hosts that run it, the [startup hook](/plugin/hooks/clarity-context.sh) reads files in the project to tell whether it is a Clarity project and adds one line of context. It writes nothing and makes no network call.
- The bundled scripts use only the Python standard library and never sign or broadcast a transaction. Most work offline; two make read-only requests to a Stacks node API when an agent runs them, and send `HIRO_API_KEY`, if set, only to Hiro hosts. In Claude Code, only the offline scripts run without a permission prompt.
