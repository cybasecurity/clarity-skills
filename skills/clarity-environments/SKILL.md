---
name: clarity-environments
description: "Why Clarity behaves differently in simnet, devnet, testnet and mainnet: costs, limits, epochs, boot contracts, forks. Use when something works in one environment but not another, or to pick where to test."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Environments

## Key distinctions

- **Network, execution epoch, contract Clarity version and tool release are separate inputs:** Matching source alone does not reproduce execution.
- **Mainnet and testnet do not inherently have different cost schedules:** Compare their active epochs and node limits. Simulator limits can differ from both.
- Remote mainnet data still runs inside a simulator. A successful read-only call, impersonated sender or patched balance does not prove transaction admission.
- An application `(err ...)`, VM runtime abort, postcondition abort, admission rejection, SDK exception and node process panic are different outcomes. Preserve the exact receipt and error layer; compare committed state and fees/nonces, not only display text.
- SDK cost tracking and transaction postconditions need explicit configuration. Their defaults can hide failures.

## Choose the environment

| Environment | Use for | Does not establish |
|---|---|---|
| Simnet | Fast deterministic contract tests; use Clarigen clients | Signatures, fees, mempool inclusion, real block production |
| Simnet with remote data | Pinned production state and contract interactions | Complete historical replay, future liquidity or signer eligibility |
| Devnet | Real node, Bitcoin regtest, signed transactions, API/indexer and wallet flows | Production miner policy, signer sets, timing or economic state |
| Public testnet | Shared app/wallet/relayer rehearsals | Mainnet contract identities, liquidity, upgrade schedule or permanent history (resets wipe state) |
| Mainnet | Current identities/state; requested final smoke checks | Exhaustive testing or guaranteed future execution |

- Start with a deterministic local fixture and the project's typed test client (Clarigen by default). Use remote data for protocol composition, devnet with pinned node/signer images for signed payloads, sponsorship, postconditions, indexer handling and boot transitions.

## Run devnet

Needs Docker running. Devnet runs a Bitcoin regtest node, stacks-node, signers, the Hiro API and explorers, and applies `deployments/default.devnet-plan.yaml` on start.

```sh
clarinet devnet start --no-dashboard     # plain logs; omit the flag for the terminal UI
clarinet devnet package -n devnet.json   # optional (Clarinet 3.x): bundle plan and settings for 'devnet start --package'
```

| Service | Default |
|---|---|
| Stacks node RPC | `http://localhost:20443` |
| Stacks API (use for `@stacks/transactions`, Connect, tx polling) | `http://localhost:3999` |
| Stacks explorer / Bitcoin explorer | `http://localhost:8000` / `http://localhost:8001` |

- Accounts, balances (`balance`, `sbtc_balance`) and ports come from `settings/Devnet.toml`; each default account lists its `secret_key` in a comment. These keys are public: never reuse them elsewhere.
- Point clients at devnet: `network: 'devnet'` in `@stacks/transactions` (defaults to port 3999), or `client: { baseUrl: 'http://localhost:3999' }`. Connect accepts `network: 'devnet'`, but the wallet itself must support a custom node.
- After startup, read `/v2/pox` and `/v2/info` ([capture commands](#capture-the-execution-context)): configured future epochs are not active epochs.
- `--from-genesis` skips the bundled snapshot. Use `-d` to start from the on-disk devnet plan instead of recomputing it.
- Historical regtest epochs 2.0 through 2.4 use enlarged budgets in stacks-core defaults. Do not infer devnet limits from mainnet or vice versa.
- Wallet and frontend flows: [clarity-wallets](../clarity-wallets/SKILL.md). Scripted deployment against devnet: [deploy script rules](../clarity-deployment/SKILL.md#release-script-rules).

## Simulator traps

- **Enable cost tracking explicitly:** semantic regression tests need it too.

```typescript
// SDK 3.26.0: cost tracking is off unless requested
import assert from "node:assert/strict";
import { initSimnet } from "@stacks/clarinet-sdk";

const simnet = await initSimnet("./Clarinet.toml", true, {
  trackCosts: true,
  trackCoverage: false,
});
// Select before dynamic deployments; manifest contracts need matching settings.
simnet.setEpoch("4.0");
assert.equal(simnet.currentEpoch, "4.0");
```

- The free tracker can hide cost-computation failures, not only over-budget execution. Some failures appear only with tracking on (for example `from-consensus-buff?` on an empty buffer under Clarity 4 / epoch 3.3); use [version gates](../clarity-epochs/SKILL.md) for fixes.
- SDK 3.26.0 logs an invalid epoch and falls back to its default. Assert `currentEpoch`; accepting a string is not evidence that an epoch is supported.
- **Postcondition omission is not wallet parity:** Omit both `postConditions` and `postConditionMode` and checks are disabled; supply either and checks apply, with `deny` as the default mode. An empty list therefore differs from omission. Use the same serialized conditions in signed devnet/live transactions.
- Nonce tracking exists in SDK 3.26.0. A simulated nonce increment still does not establish valid signatures, fee funding or mempool eligibility.
- `mineBlock` batches independent transactions. A returned `(err ...)` allows later entries; a runtime exception throws out of the loop, leaving earlier transactions committed and later entries unexecuted. Inspect resulting state before retrying ([batch recipes](../clarity-testing/SKILL.md#blocks-clocks-and-same-block-batches)).
- Plain simnet uses testnet network semantics; mainnet remote-data sessions use mainnet semantics. Wallet address formatting alone does not switch the execution network.
- **Partial trait mocks pass in simnet but can fail on a node:** Simnet calls skip mempool admission, so a contract passed as a trait argument needs only the function the VM calls. A node's mempool (devnet, testnet, mainnet) rejects a contract call unless each contract argument implements the whole trait (in any list, only the first element is checked; see the [admission type check](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/analysis/type_checker/v2_1/mod.rs)), so the same transaction fails when broadcast unless the mock sits later in a list. Give test mocks every trait function, and never treat either check as security: bind expected principals ([trait arguments](../clarity-ecosystem/SKILL.md#key-distinctions)).
- Simnet rewrites mainnet boot contract literals such as `'SP000000000000000000002Q6VF78.pox-4` to their `ST000000000000000000002AMW42H` twins (the bare address stays), which can hide a wrong literal in a real deployment. Check each boot principal against the target network.
- STX locking is native code keyed to the boot PoX contract's identity: a deployed PoX copy can return the same success tuples but locks nothing. Call the boot contract, never a copy, and verify lock state and allowance failures, not only returned tuples.
- Simulated time increments are deterministic fixture behavior. Test clock boundaries; do not infer real block intervals from them.

## Costs and limits

- Measure all five cost dimensions and leave room for remaining tenure budget and miner policy ([clarity-optimizer](../clarity-optimizer/SKILL.md)).
- Epoch 4.0 node read limits are 30,000 reads / 200,000,000 read bytes; SDK 3.26.0 reports 15,000 / 100,000,000, so its cost ratios are not production ratios.
- Fetch `/v2/pox` from each target node; do not assume mainnet and testnet match. `epochs[]` can already list a future epoch such as `Epoch41`; simnet cannot select 4.1, so it is visible on the network but not testable there.
- Simnet batching does not establish aggregate block/tenure admission: it creates a fresh cost tracker per call, while real block production shares budgets.
- Deployment analysis/storage accounting and transaction admission can differ between SDK releases and nodes. Compare the target node's actual deployment receipt, not only a simnet deployment number.

## Remote data, epochs and networks

- Remote-data simulation: pin a height, record the resolved block ID, check `currentEpoch` and archive availability, and never silently replace missing history with latest state. Fork settings and funding: [mainnet forks](../clarity-testing/SKILL.md#mainnet-forks).
- In a mainnet remote-data session, a Clarity 1 or 2 contract that calls `get-block-info?` with the height of a tenure from epoch 3.0 on, before the fork point, gets the Stacks block at that height instead of a block from that tenure ([Clarinet #1999](https://github.com/stx-labs/clarinet/issues/1999)). Check the issue's status and validate such lookups against a node.
- Test before and after an epoch boundary while keeping an old contract's Clarity version; cross-contract calls can span language versions.
- A receipt's `(err none)` need not be an application response: VM runtime and analysis failures produce it, and so do epoch 4.0 problematic-transaction markers, which skip the payload. Inspect status, VM error and execution evidence.
- For cryptographic mismatches, compare Wasm and native builds with identical vectors, and check the SDK's bundled stacks-core revision, not only its selected epoch.
- **Public testnet resets:** Stacks Labs announced a reset of the canonical testnet for 2026-07-30, starting a new PoX-5 (epoch 4.0) genesis and wiping all prior state ([announcement](https://www.stacks.co/blog/the-public-pox-5-testnet-is-live-test-bitcoin-staking-before-mainnet)). The current testnet's first block is dated 2026-08-05 15:06:56 UTC; contracts, balances and addresses from before it are gone (for example the SIP-listed testnet traits). `api.testnet.hiro.so` and the former preview host `api.testnet-pox5.hiro.so` serve that same chain. Detect a newer reset with `GET /extended/v2/blocks/1`. Protocols may deploy different code or configuration on testnet; save fixtures and receipts needed for long-term regressions.
- Custom devnets can use custom chain IDs, and Stacks testnet does not imply Bitcoin testnet3/testnet4: inspect the configured burnchain.
- A requested mainnet smoke test bounds actual exposure and uses the intended transaction protections and observability. Fake tokens still consume real STX fees and do not reproduce production asset IDs, allowlists, oracle mappings, decimals or liquidity. A production canary complements local/node tests; it does not justify adversarial testing in live pools.

## Reproduce the difference

- Capture the [execution context](#capture-the-execution-context) before comparing environments or claiming production readiness.
- Reproduce public reachability with the intended postconditions and cost tracking. Compare response, rollback, events, balances, nonce and costs separately.
- For historical failures, use the historical epoch and pre-state. A current-node rerun is a new observation.
- Missing archived state or a deleted testnet transaction means **unresolved**, not proof of an equivalent outcome.
- A duplicated Windows manifest path is a host-tooling error, not different Clarity semantics ([testing troubleshooting](../clarity-testing/references/troubleshooting.md#windows-manifest-paths)).
- For unit-test syntax, clocks and batching: [clarity-testing](../clarity-testing/SKILL.md). For epoch gates: [clarity-epochs](../clarity-epochs/SKILL.md). For budgets: [clarity-optimizer](../clarity-optimizer/SKILL.md).
- For canonical receipts and STXER: [clarity-apis](../clarity-apis/SKILL.md). For live deployment: [clarity-deployment](../clarity-deployment/SKILL.md).

### Capture the execution context

- Pin contract source/hash and declared Clarity version, including every dependency. Record exact principals, arguments and the sender/caller path.
- Record API URL, network/chain ID, node release, tool versions, execution epoch and language, Stacks block ID/height and burn height.
- Record state **before** the transaction. Replaying against the containing block's final state can repeat its effects or observe later transactions.
- Preserve raw transaction bytes, origin/sponsor, fee, nonce, postcondition mode/list, argument bytes and receipt status.
- Record mainnet-to-local remaps, seeded roles, mock signers/oracles and state overrides.
- Fetch context from the intended node, not an explorer's selected label:

```bash
clarity_api_url='https://api.hiro.so'
curl --fail --silent --show-error "$clarity_api_url/v2/info" > node-info.json
curl --fail --silent --show-error "$clarity_api_url/v2/pox" > node-pox.json
```

- `/v2/info`: inspect `network_id`, `server_version`, `stacks_tip_height`, tip hashes and `burn_block_height`.
- `/v2/pox`: inspect `current_epoch`, `epochs[].block_limit`, activation heights and active boot contract.
- Separate reads may span different tips. Record the observed tips; pin subsequent reads/simulation to one supported canonical block context.

## Recheck upstream when debugging

- [Clarinet releases](https://github.com/stx-labs/clarinet/releases), [issues](https://github.com/stx-labs/clarinet/issues) and [Clarigen issues](https://github.com/hstove/clarigen/issues).
- [SDK postcondition options](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarinet-sdk/common/src/sdkProxyHelpers.ts), [VM context and limits](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarity-repl/src/repl/interpreter.rs), [batch execution](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarinet-sdk-wasm/src/core.rs).
- [Node epoch/budget tables](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/core/mod.rs), [devnet defaults](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarinet-files/src/network_manifest.rs).
- Simulator limitations (PoX, requirement remapping) change between Clarinet releases: check the installed release's issues before treating one as current.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
