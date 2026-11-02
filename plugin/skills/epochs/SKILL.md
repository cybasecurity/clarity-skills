---
name: epochs
description: "Clarity versions and Stacks epochs: which version to target, names added or removed (as-contract, block-height, at-block), behavior changes. Use when a keyword fails to compile or to ask when something changed."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Epochs

Establish what exists for the contract and what the executing network actually does.

## Key distinctions

- Three independent axes; check all three before judging code:
  1. **Clarity version** of each contract: fixed at deploy, decides which names exist and some per-version semantics.
  2. **Epoch** at execution: decides costs, limits, and epoch-gated fixes that apply to *every* contract, old ones included.
  3. **Tooling** version: decides what you can simulate.
- Accepted SIPs, repository HEAD and simulator support do not prove network activation.
- Epoch 3.4 disables `at-block` even in existing Clarity 1–4 contracts.
- Clarity 1 `principal-of?` and Clarity 4 `secp256r1-verify` retain their version-specific behavior.
- Depth, value size, serialized size and deployment transaction size are different limits.

## Resolve compatibility

- Record every target contract's declared version, executing epoch, node revision and installed tooling.
- Query the node and keep the retrieval time and selected tip (testnet: `api.testnet.hiro.so`):
  - `curl -s https://api.hiro.so/v2/pox | jq '{current_epoch, epochs: [.epochs[] | {epoch_id, start_height, read_count: .block_limit.read_count}]}'`
  - `curl -s https://api.hiro.so/v2/info | jq '{server_version, burn_block_height, stacks_tip_height}'`
  - If `current_epoch` is `Epoch40`, apply rules up to 4.0 and ignore 4.1: its `start_height` 9223372036854775807 is a sentinel, not a date.
- Read the relevant rows of [version-specific behavior](#version-specific-behavior).
- Compare [Stacks documentation](https://docs.stacks.co/reference/clarity/functions) with [VM documentation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs), version lookup tables, implementation and tests.
- Trace both version gates and epoch gates. A change advertised for a newer language can be epoch-wide; a historical bug may remain in old contracts.
  - Version gates: `clarity/src/vm/functions/mod.rs` (NativeFunctions table: name, first and last version) and `clarity/src/vm/variables.rs`.
  - Epoch gates: `StacksEpochId` methods in [`stacks-common/src/types/mod.rs`](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stacks-common/src/types/mod.rs) (for example `supports_at_block`, `fixes_map_off_by_one`, `supports_call_with_constant`) and [`clarity-types/src/version.rs`](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity-types/src/version.rs) (`ClarityVersion::default_for_epoch`, `supports_variadic_concat`).
  - Find call sites by searching `clarity/src` for each method name and for `ClarityVersion::`.
- Reproduce at the affected epoch and contract version. An old `clarity_version` on a new simulator epoch is not a historical reproduction.
- For a migration, list changed names, signatures, allowance semantics, clocks, costs and observable outcomes. Test dependent contracts too.
- State activation evidence, supported tool range and unresolved discrepancies. Never raise a deployed contract's language version merely to make a test compile.

## Current network and versions

- **Epoch 4.0 is active on mainnet:** from burn height 960,230, with deployable Clarity 1–6 and default Clarity 6 (SIP-044 Clarity 6, SIP-045 PoX-5).
- **Epoch 4.1** (source only, unscheduled) rejects every deploy transaction that pins a Clarity version, including Clarity 7. Deploys must be unversioned and receive the epoch default, Clarity 7. Before 4.1 activates, check that your tool can emit an unversioned deploy; do not keep `clarity_version` in `Clarinet.toml` or deployment plans meant for it.
- This snapshot adds no Clarity 7 natives. From 4.1, analysis of every new deploy enforces these two rules; they do not change contracts deployed earlier:
  - `fold`: the result type covers both the initial value and the return type of the function (earlier epochs used the function's return type alone).
  - Tuples that must share one type (the two branches of `if`, the arguments of `is-eq`, the elements of a `list`) must have the same fields; earlier epochs could drop fields that only one of the tuples had.
- Clarinet/SDK 3.26.0 default to epoch 4.0 / Clarity 6 and cannot select epoch 4.1.
- Removed names: `as-contract` (Clarity 1–3), `block-height` and `get-block-info?` (1–2), `at-block` (1–4), `with-stacking` (4–5) do not exist in later versions; replacements are in the scholar's [names that no longer exist](../scholar/SKILL.md#names-that-no-longer-exist).
- Added names per version are in the scholar's [function catalog](../scholar/references/functions.md#additions-by-version); its index and lookup script give every name's range.

### Epochs and Clarity versions

| Epoch | Mainnet start (burn height) | Deployable Clarity | Default | Introduced by |
|---|---|---|---|---|
| 2.0 | 666,050 | 1 | 1 | launch of Stacks 2.0 |
| 2.05 | 713,000 | 1 | 1 | cost and limit changes |
| 2.1 | 781,551 | 1–2 | 2 | SIP-015 (Clarity 2) |
| 2.2 / 2.3 / 2.4 / 2.5 | 787,651 / 788,240 / 791,551 / 840,360 | 1–2 | 2 | fixes; 2.5 adds PoX-4 |
| 3.0 | 867,867 | 1–3 | 3 | Nakamoto (SIP-021) |
| 3.1 / 3.2 | 875,000 / 907,740 | 1–3 | 3 | SIP-029 / SIP-031 |
| 3.3 | 923,222 | 1–4 | 4 | SIP-033 (Clarity 4) |
| 3.4 | 943,333 | 1–5 | 5 | SIP-039 (Clarity 5) + SIP-040, SIP-042 |
| **4.0** | **960,230 (active)** | **1–6** | 6 | SIP-044 (Clarity 6) + SIP-045 (PoX-5) |
| 4.1 | unscheduled (sentinel height) | 7, via unversioned deploy only | 7 | no SIP in the snapshot |

- Heights above are burn heights from `/v2/pox`; re-query `epochs[]` (testnet differs).
- Sources: [SIP-033](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-033), [SIP-034](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-034), [SIP-039](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-039), [SIP-040](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-040), [SIP-042](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-042), [SIP-044](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-044), [SIP-045](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-045).

## Version-specific behavior

| Topic | Behavior | Action |
|---|---|---|
| Heights | `block-height` exists in Clarity 1–2 only; since epoch 3.0 it returns the **tenure** height. Clarity 3+ has `stacks-block-height` (every Stacks block) and `tenure-height`. `burn-block-height` is the Bitcoin tip height of the block being evaluated (before 3.0: of the parent block). | Pick the clock for the job. Never treat block counts as durations. |
| Current time | `get-block-info?`/`get-stacks-block-info? time` return `none` for the current block. Clarity 4 adds `stacks-block-time` (current block's miner-set timestamp: strictly greater than the parent's, at most ~15 s in the future). `get-tenure-info? time` is the **Bitcoin** block time. | Clarity 4+: `stacks-block-time`. Older code only has the previous block's time, which lags. |
| `as-contract` → `as-contract?` | Clarity 1–3 `as-contract` gives callees unlimited authority over the contract's assets. Clarity 4 removes it; `as-contract?` takes up to 128 allowances, evaluates them **before** the body in the outer context, checks cumulative outflows **once at scope end**, and on violation rolls back the scope and returns `(err index)` (`u128` = an asset with no allowance). **No** body expression may be a response. | Capture actors before the scope; `try!` inside; propagate the result. |
| `restrict-assets?` | Same body rule as `as-contract?`: the type checker rejects any response-typed body expression, not only the last. The VM docs say the final expression only, and say the error type is `int`; the checker returns `(response A uint)`. | Handle body responses with `try!`/`unwrap!` inside the body; match the err side as `uint`. |
| Allowance kinds | `with-stx`, `with-ft` (`"*"` = all FTs of a contract), `with-nft` (`"*"` likewise, but only the listed IDs, ≤ 128), `with-all-assets-unsafe` (sole allowance, `as-contract?` only). Clarity 4–5: `with-stacking amount` (total lock). Clarity 6: `with-stacking` **removed**; `with-staking amount` and `with-pox` (no amount; required for unstake/bond-update style PoX-5 calls). From 3.4, STX transfers + burns are summed against `with-stx`. | Match allowances to actual outflows: some [wSTX wrappers](../assets/SKILL.md#key-distinctions) move native STX, others an FT; inspect the wrapper. |
| `current-contract` | Clarity 4+. | Replaces `(as-contract tx-sender)`. |
| `at-block` | SIP-042: from epoch **3.4** existing Clarity 1–4 contracts abort when they reach `at-block` (fee charged); new Clarity 1–4 deploys fail analysis; Clarity 5+ has no `at-block`. | Do not recommend it. Treat any old dependency on it as broken. |
| `principal-of?` | Clarity 1 contracts derive a **testnet** address on every network and epoch; Clarity 2+ use the execution network (`special_principal_of` checks the contract's version). The VM doc note "fixed in 2.1" applies only to newer contracts. | Test Clarity 1 code on mainnet settings. |
| `secp256r1-verify` | Clarity 4 hashes `message-hash` again (double SHA-256, documented in SIP-035); Clarity 5+ verifies the prehash. High-S allowed. | Keep Clarity 4 contracts' double-hash expectations. |
| secp256k1 | `secp256k1-verify` rejects high-S; `secp256k1-recover?` does not enforce low-S. Clarity 6 adds `secp256k1-decompress?` returning `(response (buff 65) uint)` (SIP-044's text says `optional`; the VM returns a response). | Deduplicate by message hash. |
| `from-consensus-buff?` | Empty input hit a zero-length log cost path; Clarity 5 guards it. Epoch 3.4 treats unexpected serialization as `none`. | Test empty/garbage buffers on the exact target. |
| Constant `contract-call?` targets | `(contract-call? CONST ...)` type-checks from Clarity 2 but works at runtime only from epoch 3.4, and **not during deployment** (top-level code). The read-only checker rejects it in `define-read-only` code, even through a private helper. | Use a literal principal in read-only code, in top-level code and on epochs before 3.4. Clarinet SDK 3.26.0 simnet runs the constant form during deployment; a node fails the deployment. |
| `concat` | Two arguments before Clarity 6; variadic (and cheaper) from Clarity 6. | Do not emit variadic `concat` for older targets. |
| `map` over several lists | Before epoch 4.0, an empty sequence could cause an arity error (abort) or a spurious element; fixed from 4.0 for all contracts. | Guard empty lists on old epochs. |
| Clarity 6 additions | `ed25519-verify` (strict RFC 8032), `secp256k1-decompress?`, `verify-merkle-proof`, `get-bitcoin-tx-output?`, `with-staking`, `with-pox`. | Read exact formats and byte orders in [pinned VM documentation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs). |
| Locally defined trait during deployment | Top-level trait dispatch can fail with `NoSuchContract` while the trait-defining contract is still deploying. The [targeted upstream implementation](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/functions/database.rs) adds local-context lookup at **epoch 4.1**, not a Clarity-5 gate. | Check network activation; Clarinet 3.26.0 cannot select 4.1, so simnet tests do not exercise this fix. |
| Historical trait/type bugs | Epoch 2.2/2.3 trait regressions; SIP-024 least-supertype repair (2.4). | Reproduce with the historical epoch, not just an old `clarity_version`. |

## Resource limits

- **Execution budget:** five dimensions, in `/v2/pox` → `epochs[].block_limit`. Epoch 4.0: runtime 5,000,000,000; reads 30,000; read bytes 200,000,000; writes 15,000; write bytes 15,000,000. Epochs 2.05–3.4: reads 15,000 and read bytes 100,000,000, the rest unchanged.
  - Since Nakamoto, blocks share this **tenure** budget. A tenure extension resets it (from 3.3, per dimension via SIP-034).
  - Default miners stop adding contract calls to a block once it passes 25% of the remaining tenure budget (`tenure_cost_limit_per_block_percentage`, configurable), but the [call that crosses it](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/nakamoto/miner.rs#L902-L922) is still included. A transaction that overflows a tenure less than 20% used is [dropped as too big](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/nakamoto/miner.rs#L945-L959); one that overflows a fuller tenure stays in the mempool for a later one. These are miner policy, not consensus ceilings. Plan headroom against the target miner and remaining tenure budget. Higher fees cannot cure consensus overruns.
- **Cost schedule:** `default_cost_contract_for_epoch` selects costs_3 for 2.1–3.2, costs_4 for 3.3–3.4, costs_5 for 4.0–4.1 ([pinned cost schedule](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/costs/costs_5.rs)). From 4.0 the active schedule is native Rust; historical boot cost contracts still exist. SIP-006 cost voting is disabled (SIP-044): schedules change only by hard fork. Formulas and measurement: [optimizer](../optimizer/SKILL.md).
- **Call stack depth:** 64 before epoch 3.4, 128 from 3.4 (raised in stacks-core 3.3.0.0.6). Every call still running holds a level, built-ins included, and a new call needs a free one: a call inside another call's argument, a `let` or an `if` costs an extra level, and each `contract-call?` hop costs two. At epoch 4.0, a chain of plain user-function calls fits 128 levels, 64 when each call sits inside one wrapper (`(try! (f))`, `(let (...) (f))`) and 43 inside two. Count the deepest path across contracts (router, pool, callback, token) and test it at the target epoch.
  - Exceeding it at runtime aborts with `MaxStackDepthReached`; the transaction is included, fails and pays its fee.
  - Source nesting is capped at the stack limit + 5: up to 68 levels of parentheses before 3.4 and 132 from 3.4, counting the outer `define`; tuple literals count too. Deeper source fails parsing with `ExpressionStackDepthTooDeep` (`VaryExpressionStackDepthTooDeep` when tuples push it over), "AST has too deep of an expression nesting". Before 3.4 such a deployment cannot be included in a block; from 3.4 it is included as a failed deployment that pays its fee.
  - Clarinet SDK 3.26.0 applies the limit of the simnet epoch: tests at epoch 3.3 or earlier see 64.
- **Type depth:** 32. A base type counts 1 and each `optional`, `response`, `list` or tuple layer adds 1: `(response (optional (list 10 {a: uint})) uint)` has depth 5. A deeper type in a definition, a signature or a constructed value fails analysis with `TypeSignatureTooDeep` ("created a type which was deeper than maximum allowed type depth"; a `define-data-var` reports "invalid variable definition"). The failed deployment is included and pays its fee.
- **Rarer depth errors:** two errors make a deployment impossible to include in any epoch. `TraitReferenceChainTooDeep` ("trait-reference chain exceeds the maximum allowed type-checker recursion depth") fires when a value of one trait is passed where another trait is expected and the comparison follows trait-typed parameters through more than 30 nested traits (passing the same trait skips the comparison). `ReadOnlyCheckerRecursionLimitExceeded` (160 levels) cannot occur, because source nesting stops at 132.
- **Sizes:** values ≤ 1 MiB (`MAX_VALUE_SIZE`; `string-utf8` ≤ 262,144 chars); local context depth 256; ≤ 256 function parameters; ≤ 128 allowances; deployment/call-target contract names 1–40 bytes; identifiers ≤ 128. The value limit bounds Clarity value sizing, not every encoded buffer or transaction; serialization has separate overhead and `BOUND_VALUE_SERIALIZATION_BYTES`.
  - Upcoming contract-name checks: VM principal values historically permit contract names up to 128 bytes. Epoch 4.1 adds checks on overlong names in transaction values, principal destructuring and deserialization; existing stored values remain readable. This is upcoming source behavior, not evidence of activation ([name checks](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/crates/stacks-transactions/src/lib.rs), [principal handling](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/functions/principals.rs)).
- **Contract size:** no explicit code-size constant. The deploy transaction must fit `MAX_TRANSACTION_LEN` = 2 MiB (also the block size) minus transaction overhead and pass parsing, analysis, memory (100,000,000 bytes) and cost checks. It is not the 1 MiB value limit, and not Ethereum's 24 KiB. Every caller pays the source length (comments included) plus constant data on every `contract-call?`.
- **Events:** under 50 MiB of `print` data per transaction. Events of rolled-back contexts (an `err`-returning public function, a read-only function even when a public function calls it, a violated `as-contract?` or `restrict-assets?` scope, a failed transaction) are dropped.
- **Simulator:** Clarinet SDK 3.26.0 reports epoch-2.1 read limits (15,000 reads / 100 MB) even at epoch 4.0. Report against the real `/v2/pox` limits. Check [environment fidelity](../environments/SKILL.md) for version-scoped limits, free-tracker behavior and signed admission differences.
- Sources: [limits](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/core/mod.rs), [call stack depth](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity-types/src/lib.rs), [source nesting](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/ast/stack_depth_checker.rs), [type depth](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity-types/src/types/signatures.rs), [block inclusion of failures](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/clarity.rs).

## Post-conditions (transaction level)

- Modes: Allow, Deny, and Originator (epoch 3.4+, SIP-040: deny-mode applies only to the origin account's outflows).
- NFT conditions: sent, not sent, may send (3.4+).
- Epoch 4.0 adds Staking and PoX post-conditions (SIP-045).
- Conditions can name standard *and contract* principals.
- The origin is fixed for the transaction and is unchanged by `as-contract?`.
- Contracts cannot read post-conditions, and contract-to-contract calls inside a transaction are covered only by the transaction's own conditions.

## Semantics every skill relies on

- `uint`/`int` are 128-bit; overflow, underflow, division by zero, negative `to-uint` and `pow` overflow abort the transaction.
- A public function returning `err` rolls back its writes and events; a caller can handle a callee's `err` and continue; private-function errors roll back nothing by themselves.
- Read-only functions cannot write, cannot call non-read-only functions, and cannot make dynamic (trait) calls. Read-only results are code output, not proofs.
- `tx-sender` is the origin until `as-contract?`/`as-contract` switches it; `contract-caller` is the immediate caller.
- Traits are structural, except a trait-typed parameter inside your own trait, which is compared by identity ([nested traits](../security/SKILL.md#calls-traits-recursion)).
- Re-entering an *active function* aborts; calling a *different* function of a contract on the stack is allowed.
- Contracts are immutable at their principal, but registries, roles, signer sets and token semantics behind them change.
- Bitcoin settlement, signer processing and redemption queues are asynchronous and cannot be made atomic by a Clarity transaction.

## Recall corrections

Models often recall these rules wrong. Check the target language, epoch and deployed dependencies before applying one. To verify or cite a rule, read its full entry in [references/recall-corrections.md](references/recall-corrections.md).

- **M01 Recursion tracks functions, not contracts:** Re-entering an active function aborts; a different function of a contract on the stack can run and observe intermediate state.
- **M02 Native FT/NFT primitives do not authenticate owners:** Wrappers authorize callers; native `stx-transfer?` checks its sender against the effective `tx-sender`.
- **M03 `is-standard` checks network address versions:** Matching contract principals return `true`; it proves no wallet identity, trust or key control.
- **M04 Name current time exactly:** Use `stacks-block-time` in Clarity 4+; current-block info lookup returns `none`.
- **M05 `as-contract?` semantics:** No body expression may be response-typed; allowances are evaluated before the body, outflows are checked at scope exit, and violations roll back the scope.
- **M06 Errors and rollback have boundaries:** A private `err` alone reverts nothing; a caller handling a public callee's `err` can return `ok` and commit its own changes.
- **M07 Separate size and depth limits:** Stack depth, value size, serialization bounds and deployment size are distinct.
- **M08 Epoch changes affect old contracts:** Epoch 3.4 disables `at-block` even in existing Clarity 1–4 contracts; resolve function, version and epoch gates.
- **M09 Five execution dimensions; other limits are separate:** Refresh `/v2/pox`; SDK 3.26.0 reports older read limits, and the 25%-of-remaining block soft limit is miner policy.
- **M10 SIP-006 covers costs; voting is disabled:** Epoch 4.0 selects native Rust costs_5; filenames do not prove activation.
- **M11 sBTC ownership differs from spendable balance:** Check `get-balance-available`, not `get-balance`, before any transfer or repayment.
- **M12 Compose actual roles and payloads:** Read the deployed source and the [protocol recipe](../protocols/SKILL.md); recalled addresses and callback names are not evidence.
- **M13 Hash chain identifiers in the correct order:** `index_block_id = SHA512/256(block_hash_bytes || consensus_hash_bytes)`, not a truncated SHA-512.
- **M14 Separate SIP clauses from security design:** SIP-009/010 do not prescribe caller authentication; the implementation must authorize the sender.
- **M15 Verify incident causes:** Confirm the public report, affected commit, deployed source and transaction result before attributing an incident.

## References

- [recall corrections](references/recall-corrections.md): the full M01–M15 entries, most with their sources.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
- `stacks-core-targeted`: [01a60adcb6](https://github.com/stacks-network/stacks-core/tree/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7).
- `sbtc`: [eb507946c6](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17).
