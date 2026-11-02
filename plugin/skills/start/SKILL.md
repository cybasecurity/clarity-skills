---
name: start
description: "Start here for any Clarity (.clar) or Stacks smart-contract task: contracts, tokens, vaults, DeFi, tests, deployment, audits, sBTC or protocol integration, and questions about Clarity behavior, versions or addresses. Writing or changing a contract also needs clarity:scholar and clarity:security; this skill names the rest."
license: MIT
allowed-tools: "Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/scholar/scripts/lookup_function.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity: start here

This skill is a router. Read the request (and any task file it points to), then load every skill whose row matches, in the same turn, before writing code, reviewing or answering from memory. The rules live in those skills, not here: models routinely get Clarity wrong from Solidity habits and older Clarity versions.

## Load by task

| Task | Load |
|---|---|
| How Clarity code behaves: what an expression returns, what aborts or rolls back, what the VM checks at deployment or call time | `clarity:scholar` **and** `clarity:security` |
| Write or refactor a contract (vault, token, protocol) | `clarity:scholar` **and** `clarity:security`; `clarity:assets` if it holds or moves tokens |
| Tests, new project setup, coverage | `clarity:testing`; `clarity:fuzzing` for invariants/property tests |
| Integrate Zest, Granite, Bitflow, Stacks Swap, Hermetica, USDCx, Pyth | `clarity:protocols` for addresses and calls; `clarity:ecosystem` for position contracts and when two or more protocols compose; `clarity:oracles` for prices |
| Deploy, publish, initialize | `clarity:deployment`; `clarity:environments` for testnet/devnet differences |
| Works in one environment (simnet, devnet, testnet, mainnet) but not another; where to test | `clarity:environments` |
| Audit, review, find bugs | `clarity:auditor` **and** `clarity:security` (always both: the auditor holds the method and PoC rules, security holds the A01-A29 patterns and native-behavior tables); `clarity:assets` when tokens move |
| Upgradeable design, replacing logic or a contract, v2 migration | `clarity:upgrades`; `clarity:governance` for who may approve |
| DAO, multisig, admin roles, timelocks | `clarity:governance` |
| Execution cost, block limits | `clarity:optimizer` |
| Language version or epoch questions, compile errors on a keyword | `clarity:epochs` |
| SIP-010/009/013 tokens, SIP-018 signatures | `clarity:sip-compliance` |
| Off-chain scripts, events, indexers, sBTC deposit history | `clarity:apis` |
| Bitcoin transaction proofs, sBTC settlement | `clarity:bitcoin-proofs` |
| PoX staking | `clarity:staking` |
| Wallet connection, frontends, Ledger | `clarity:wallets` |
| Boot contracts, SIP trait addresses, chain mechanics | `clarity:system-integration` |

- Load only what the task needs; install the whole bundle so sibling links resolve.
- A build usually needs `clarity:scholar`, `clarity:security` and `clarity:testing`; add the integration skills only for the protocols actually used.
- New projects: toolchain and test setup in [clarity:testing](../testing/SKILL.md#new-project); which Clarity version to target in [clarity:epochs](../epochs/SKILL.md#current-network-and-versions).
- Principals, traits and function signatures come from `clarity:protocols` (protocols) and `clarity:system-integration` (boot contracts, SIP traits), never from memory.
- Exact VM text for any function: `python3 <skills>/scholar/scripts/lookup_function.py 'as-contract?'` (`<skills>` is the directory holding the skill folders).

## Before calling a contract done

Each line is a common defect; its link holds the rule and how to test it. Fix each failing item that applies instead of reporting it as unmet. Skip items for features the contract does not have; when an item conflicts with a design the user asked for, say so instead of silently reshaping the design.

- **Trait arguments** checked against the stored principal for their role ([security A02](../security/references/patterns.md#a02-trait-confusion--wrong-role-contract)).
- **Upgrade targets**, when the contract has them: the exact staged target is required at activation after the delay, with no bypass; by default typed `(target <logic-trait>)` and probed before the delay ([make a contract upgradable](../upgrades/SKILL.md#make-a-contract-upgradable)).
- **Privileged setters** check the caller, print an event and validate input; sensitive changes (fund-moving roles, prices, code) are fixed or timelocked, and a protocol holding user funds has an instant pause; contract roles reject wallets ([security](../security/SKILL.md#implement-or-repair), [governance](../governance/SKILL.md#default-decision-rule)).
- **Outflows** bounded by exact `as-contract?` allowances, share-token burns included, and protocol calls with the contract's own assets made inside the scope ([security A04](../security/references/patterns.md#a04-broad-asset-allowances), [allowance scope](../ecosystem/SKILL.md#allowance-scope)).
- **Zero, self and dust amounts** skipped or rejected deliberately, and a dust request cannot block a queue ([security A27](../security/references/patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows), [liquidity](../ecosystem/SKILL.md#liquidity-and-share-minting)).
- **Valuation** at redeemable value, times a verified on-chain oracle price for assets other than the vault's unit (a keeper- or admin-supplied price only when the design accepts that trust, bounded and disclosed); never cost basis or a spot price ([value](../ecosystem/SKILL.md#value)).
- **Lazer prices** verified with every check ([price checks](../oracles/SKILL.md#lazer-price-checks)).
- **Share mints** resist first-deposit inflation ([security A29](../security/references/patterns.md#a29-first-deposit-and-donation-share-inflation)).
- **Minimums and deadlines** are non-zero and chosen by the signer; operator swaps also have an oracle floor ([protocol calls](../protocols/SKILL.md#rules-for-every-protocol-call)).
- **Capital that is out** never freezes deposits or claims and counts at what it can still return, not at the amount released ([liquidity](../ecosystem/SKILL.md#liquidity-and-share-minting)).
- **Protocol call shapes** match the deployed contracts, and each position is accounted for by the contract that owns it: by default a one-owner position contract per protocol, or direct calls with explicit per-position accounting ([position contracts](../ecosystem/SKILL.md#position-contracts), [what differs between protocols](../ecosystem/SKILL.md#what-differs-between-protocols)).
- **Complete exits:** every leg has a tested path back to the vault ([test the entire operation](../ecosystem/references/testing.md#test-the-entire-operation)).
- **Real contracts** exercised at a pinned height at least once, and `clarinet check` passes on its own from requirements ([mainnet forks](../testing/SKILL.md#mainnet-forks)).
- **Tests** drive public functions through attacker contracts, with 0, 1, maximum amounts and failure rollback ([attacker contracts](../testing/SKILL.md#drive-public-functions-through-attacker-contracts)).
- **Deployment prep**, when the task includes deployment or the contract needs initialization, uses the project's deployment tooling or an executable Clarinet plan or release script. A plan can handle straightforward releases; recommend a resumable script for more complex setup, verification, signatures, waits or transaction postconditions constructed in code ([release script rules](../deployment/SKILL.md#release-script-rules)).

## Reference baseline

Source pins for this skill; each linked skill keeps its own dates and pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
