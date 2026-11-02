# Positions, simulation and inclusion proofs

### Discover positions, then value them

Clarity maps have no key enumeration and the map-entry RPC needs a known key. Routers, contract wallets and nested calls can create contract-owned positions.

- Inspect the deployed entrypoints, state schema and events to identify the actual owner/account and position key. Transaction origin is not the owner: never substitute `tx-sender` from transaction metadata for an explicit account field.
- Index the state-owning contract's committed events, including events from nested calls. Use emitter + versioned schema + account/position identifiers, not a matching tuple shape alone.
- Backfill from deployment or a verified migration checkpoint; follow pagination and reconcile with live delivery. Handle duplicates and reorgs using the [recoverable processing](../SKILL.md#recoverable-processing) rules.
- Track creation, transfers of ownership, closure, migration and state-only changes. A token transfer alone may not identify the position being changed.
- If events omit keys, look for explicit indexed getters/counters or a documented indexer. State the coverage gap if no complete enumeration source exists; inventing a map-scanning RPC does not solve it.
- Discovery produces candidate keys, not current health. For each candidate, query a principal-aware read-only view at a pinned supported tip, or compute the documented model from consistent state.
- Include current accrued debt indexes, share dilution, prices/units/freshness, asset enablement and risk-group configuration. Stored principal or the last emitted debt is not necessarily current debt.
- A read-only view can calculate hypothetical accrual without storing it. It cannot invoke a state-writing accrual path; use a transaction simulation when execution requires updates or oracle payloads.
- Keep the API's call sender distinct from the queried account. Read-only query parameters do not establish signing authority.
- Re-simulate liquidation against recent state with the actual caller, oracle updates, repay cap, minimum collateral/profit and all costs. A healthy preview can become stale before execution; bind bounds on-chain.
- Coverage tests: create positions directly, through a router and for a contract wallet, and discover every real owner. Include multiple positions/events in one transaction, state-only updates, ownership changes, empty/closed positions and a late reverted operation.
- Compare cold/warm accrual paths and two updates in one block. Replayed pages must not duplicate positions; orphaned events must not leave phantom borrowers.
- Test migration backfill and operation when a configured external price feed is unavailable. Report incomplete discovery separately from inability to value a known position.

Sources: [Clarity map semantics](https://docs.stacks.co/reference/clarity/functions#map-get), [node map-entry RPC](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/net/api/getmapentry.rs), [node read-only RPC](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/net/api/callreadonly.rs), [Stacks Blockchain API schemas](https://github.com/hirosystems/stacks-blockchain-api). Check current endpoint schemas before writing a client.

### STXER: transaction inspection and simulation

- [STXER](https://stxer.xyz) does for Clarity roughly what Tenderly does for EVM chains: transaction debugging, execution traces and simulation. The comparison claims no feature parity or affiliation.
- [Example mainnet transaction](https://stxer.xyz/tx/mainnet/0xe8b2ac705dcbb35d487a4efd7a0fe384bbad1d1d97ea970410ad82a3cd0d9daf): inspect calls, values, failures and costs, then corroborate the canonical node/indexer receipt. This link is an inspection example, not a security conclusion about that transaction.
- SDK: [stxer/stxer-sdk](https://github.com/stxer/stxer-sdk), [issues](https://github.com/stxer/stxer-sdk/issues). Refresh source/package support before using APIs.

| Need | SDK capability | Important distinction |
|---|---|---|
| Trace an executed transaction | `getTransactionTrace` | Uses Stacks block hash, not index block hash; missing trace is not proof of no execution |
| Multi-step simulation with UI | `SimulationBuilder` | Returns a simulation ID; choose network and pinned block context |
| Tests with per-step assertions | `createSimulationSession`, `submitSimulationSteps` | Read results/receipts and record overrides; use alongside Clarigen tests |
| Single-transaction preview | `instantSimulation` | Transient; no debug trace and no UI-viewable session |
| Simulated transaction trace | `getSimulationTrace` | Requires tracing; simulated block identity is not canonical chain evidence |
| Trace cost breakdown | `traceNodeCost`, `traceNodeSelfCost` | Inclusive versus exclusive cost; summing inclusive nodes double counts |
| Batch/read-only state | `batchRead`, `callReadonly`, `readVariable`, `readMap` | Distinguish current chain state from session-fork state |
| Cycle/time scenarios | `addAdvanceBlocks`, `getSimulationTip` | Synthetic burn/Stacks progression, not observed future chain state |

- Use transaction steps when fee/nonce, postconditions, receipts and events matter.
- `Eval` can mutate simulated state without normal transaction checks; `EvalReadonly` is read-only. Neither proves the same behavior as an admitted user transaction.
- The builder defaults postcondition mode to `Allow`; set the intended mode and conditions explicitly. Otherwise a preview may omit the protections of the real transaction.
- Code/state replacements and synthetic blocks are test assumptions. Record them in the result and separately test real public reachability.
- Trace availability, historical state, API format and service behavior can change. Check SDK source and the actual API response rather than inventing endpoints.
- Simulation does not broadcast, confirm a transaction, guarantee future liquidity, or establish production signer/permission eligibility. Keep simulated and canonical receipts distinct.
- Keep network, SDK version, state tip, sender, transaction fields, overrides and trace/receipt URLs with each reproduction.

### Stacks transaction inclusion with clarity-stacks

- [MarvinJanssen/clarity-stacks](https://github.com/MarvinJanssen/clarity-stacks) is an on-chain inclusion verifier plus TypeScript proof/header helpers. Use node/indexer APIs or STXER for ordinary transaction lookup and execution inspection.
- The manifest targets Clarity 3, epoch 3.1. The code is Nakamoto-specific; do not assume pre-Nakamoto or future header formats work.
- `was-tx-mined-compact(txid, proof, tx-block-height, header-without-signer-signatures)` verifies the transaction's inclusion against an anchored Stacks header.
- Proof tuple: `{tx-index: uint, hashes: (list 14 (buff 32)), tree-depth: uint}`; header buffer limit: 712 bytes.
- Stacks uses tagged SHA-512/256 Merkle hashing: leaf tag `0x00`, internal-node tag `0x01`. These are not Bitcoin double-SHA-256 branches or the Clarity 6 Bitcoin proof format.
- The local TypeScript helper exposes `MerkleTree.new`, `proof_cv`, `fetch_nakamoto_block_struct` and `raw_block_header`. Build from the block's exact ordered transactions, including transactions whose execution failed.
- Inspect its actual exports before copying README snippets; it is repository code, not an established package import shown here.
- **Mined does not mean successful:** A failed contract deployment can be included, leave its principal undeployed, and later be followed by different code at that principal. `code-body-prover` therefore proves a deployment transaction payload, not the source of a successfully deployed contract.
- Its serializer hardcodes Clarity 3, standard P2PKH authorization, Allow postcondition mode and no postconditions. It is not a generic sponsored/multisig/new-version deployment decoder.
- Repository `clarity-stacks.clar` sets `debug-mode true`, uses caller-settable mock header hashes, and aborts mainnet deployment in that configuration. Treat it as a development baseline; inspect reviewed production source and disable/remove the mock path.
- Its TypeScript fetcher does not check HTTP status before parsing and uses an older Stacks.js API. Wrap bounded requests/status checks and verify the installed decoder against the actual raw block format.
- The README's claim that Clarity cannot inspect a code hash is historical: **Clarity 4+ `contract-hash?`** returns the SHA-512/256 code-body hash of an existing contract. Prefer it when the question is deployed-code identity; still verify permissions, traits and mutable state separately.
- Before depending on the library, check [issues/PRs](https://github.com/MarvinJanssen/clarity-stacks/issues), current VM behavior and the selected deployment's source/ABI and canonical success receipt. Test the exact supported header/transaction formats.

Sources: [verifier](https://github.com/MarvinJanssen/clarity-stacks/blob/119dab916740ee0779f3f3243cb8d502a1385712/contracts/clarity-stacks.clar), [payload prover](https://github.com/MarvinJanssen/clarity-stacks/blob/119dab916740ee0779f3f3243cb8d502a1385712/contracts/code-body-prover.clar), [TypeScript helpers](https://github.com/MarvinJanssen/clarity-stacks/blob/119dab916740ee0779f3f3243cb8d502a1385712/src/clarity-stacks.ts), [current VM reference](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity/src/vm/docs/mod.rs).
