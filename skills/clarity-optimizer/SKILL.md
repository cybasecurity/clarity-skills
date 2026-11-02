---
name: clarity-optimizer
description: "Cut Clarity execution costs: cost dimensions, block and tenure budgets, Clarinet cost reports and safe rewrites. Use when a transaction is too expensive or hits a block limit."
license: MIT
compatibility: "Python 3.10+ for the bundled scripts."
allowed-tools: "Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/compare_costs.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/inspect_costs.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Optimizer

Optimize the measured limiting dimension; preserve authority, rounding, state, errors and consumed events.

## Key distinctions

- Execution has five dimensions: runtime, read count/bytes, write count/bytes. Memory, stack and transaction size are separate bounds.
- Nakamoto blocks share tenure capacity. Higher fees do not buy extra execution budget.
- Fewer reads can increase runtime; shorter expressions are not proof of improvement.
- Source bytes, including whitespace and deployment-only code, spend runtime/read budget on later contract loads.
- `costs-*.clar` evaluates schedule formulas. It cannot read the caller's consumed or remaining budget.
- Epoch 4.0 uses native `costs_5.rs`; the still-callable `costs-4` contract returns an older schedule. There is no deployed `costs-5` on mainnet or testnet.
- Simulator limits can lag the network. The default 25%-of-remaining block soft limit is configurable miner policy.

## Budget and the binding dimension

- The budget is five independent counters. In Nakamoto the `/v2/pox` block limit is the budget of a whole **tenure**. Default miners stop adding contract calls to a block once it passes **25% of what remains** (`tenure_cost_limit_per_block_percentage`, default 25), but the call that crosses it is still included.
- A transaction that overflows a tenure less than 20% used is dropped as too big; one that overflows a fuller tenure waits for a later one. Both rules are miner policy, not consensus ceilings ([resource limits](../clarity-epochs/SKILL.md#resource-limits)): size transactions with headroom for the target miner and remaining tenure budget.

| Dimension | Tenure limit (epoch 4.0) | Block soft limit in a fresh tenure (25%) | What spends it |
|---|---:|---:|---|
| runtime | 5,000,000,000 | 1,250,000,000 | evaluation, hashing, contract loading (grows with size) |
| read count | 30,000 | 7,500 | every `map-get?`, `var-get`, balance read and map or var write, **3 per `contract-call?`** |
| read bytes | 200,000,000 | 50,000,000 | stored value sizes, **full callee size per `contract-call?`** |
| write count | 15,000 | 3,750 | every `map-set`/`insert`/`delete`, `var-set`, token movement |
| write bytes | 15,000,000 | 3,750,000 | stored value sizes written, deployed contract size |

- Epochs 2.1–3.4 have 15,000 reads and 100,000,000 read bytes; the other limits are the same.
- **Epoch 4.0 changed what matters:** `costs_5` recalibrated runtime at 1 unit per 80,000 CPU instructions. `map-get?` went from `n + 1025` to `44` runtime and `secp256k1-verify` from 8,349 to 38, but per-item `map` and `fold` work fell far less: function application and argument checks keep their costs_3 formulas. Read and write counts did not change.
- These changes make storage counts and large-contract read bytes important profiling candidates.
- On epochs 2.1–3.4 (costs_3 and costs_4), runtime from list processing, hashing and large `let`s can still bind.

## Measure and compare

First move for "my transaction hits a budget limit" or "make it cheaper":

1. Run the public entry with Clarigen/SDK `trackCosts: true` and read `receipt.costs`.
2. Divide each `total` by the target network's `/v2/pox` limit; the largest ratio is the binding dimension. At epoch 4.0 the receipt's `limit`, which `compare_costs.py` also divides by, still has 15,000 reads and 100,000,000 read bytes.
3. Pick a [transformation](#transformations-by-dimension) for that dimension.
4. Re-measure on a fresh, identical fixture.
5. Keep only changes that lower the binding dimension without breaking tests.

Call shapes (default to Clarigen for project tests; use a current compatible CLI/SDK and inspect the project's scripts):

- Clarigen's `txOk`, `txErr` and `tx` wrappers retain the SDK receipt, including `costs` when tracking is enabled. Generate types first and configure SDK cost tracking in the test environment:

```ts
// Fragment: target and sender come from the project's generated factory/accounts.
const receipt = txOk(target.operation(1000n), sender);
if (!receipt.costs) throw new Error('Cost tracking was not enabled');
console.log(JSON.stringify(receipt.costs, null, 2));
```

- SDK directly, for an isolated measurement or a wrapper gap:

```ts
import { initSimnet } from '@stacks/clarinet-sdk';
import { Cl } from '@stacks/transactions';
const simnet = await initSimnet('./Clarinet.toml', true,
  { trackCosts: true, trackCoverage: false });
const sender = simnet.getAccounts().get('wallet_1')!;
const receipt = simnet.callPublicFn('target', 'operation', [Cl.uint(1000n)], sender);
if (!receipt.costs) throw new Error('Cost tracking was not enabled');
console.log(JSON.stringify(receipt.costs, null, 2));
```

- `receipt.costs.total` and `.limit` have `runtime`, `readCount`, `readLength`, `writeCount`, `writeLength`, plus `memory` and `memory_limit` at the costs root.
- Null costs are missing measurement, not zero cost. SDK 3.26 defaults to free cost tracking when omitted, which can hide cost-triggered aborts and budget overruns; enable tracking even for semantic regression tests. See [environment fidelity](../clarity-environments/SKILL.md).
- Set the target epoch **before deployment/setup** where analysis or boot state depends on it; a later `setEpoch` only changes subsequent execution.
- For whole-suite reports, `npx vitest run -- --costs` writes `costs-reports.json` ([coverage and costs](../clarity-testing/SKILL.md#coverage-costs-and-properties)).

Fixtures:

- Record language version, epoch, SDK/VM revision, source revisions and fixture state with each result.
- Start baseline and candidate from equivalent fresh state. Baseline complete public transactions: wrappers, oracle verification, token transfers, prints and callbacks. Helpers measured with private calls are diagnostic only.
- Include maximum list/buffer sizes and state, near-limit state, empty and failing paths, and asset/debt values near arithmetic boundaries. A failing operation can consume budget despite state rollback.
- Establish a minimal public/read-only-call baseline to separate contract loading from business logic; repeat with exact release bytes.

Compare:

- Write each measurement from the receipt (`total`/`limit`, each with the five fields), then run `python3 <optimizer>/scripts/compare_costs.py before.json after.json` (`<optimizer>` is this skill's directory):

```ts
// Fragment: receipt comes from the measured call above.
import { writeFileSync } from 'node:fs';
writeFileSync('before.json', JSON.stringify({
  context: { epoch: '4.0', clarity: 6, sdk: '3.26.0', fixture: 'deposit-1000' },
  costs: { total: receipt.costs!.total, limit: receipt.costs!.limit },
}));
```

- Resulting file shape (values illustrate the schema, not a measured transaction):

```json
{"context":{"epoch":"4.0","clarity":6,"sdk":"3.26.0","fixture":"deposit-1000"},"costs":{"total":{"runtime":100,"readCount":1,"readLength":100,"writeCount":1,"writeLength":100},"limit":{"runtime":5000000000,"readCount":15000,"readLength":100000000,"writeCount":15000,"writeLength":15000000}}}
```

- Both records must have the same context and limits. `context.clarity` is a free label but must match; keep contract revision labels outside `context`, since baseline and candidate necessarily differ. The helper reports all dimensions, deltas, utilization, and the limiting dimension.
- Verify outputs, balances, storage, events, errors, authorization and rollback, including arithmetic boundaries. Never remove a safety check to save cost.
- Report every dimension's absolute/percentage change, active-budget utilization, limiting dimension and unmeasured paths. Label estimates separately.

Interpret capacity:

- Use the current node's `/v2/pox` epoch limits and version-matched consensus source. The SDK reports 15,000 reads / 100,000,000 read bytes even at epoch 4.0, while live epoch-4.0 limits are 30,000 / 200,000,000: keep the simulator limits in raw records and judge capacity against `/v2/pox`.
- Dividing the tenure budget by one call's cost is arithmetic, not a TPS figure: blocks share the budget, tenure extensions reset it and other transactions compete for it.
- Transaction fees and execution costs are different quantities. The simulator may use generous/default limits or omit real mempool conditions: report those differences.
- Deployment analysis and serialization costs are separate from subsequent function costs; contract loading/dependency size can affect calls.

Sources and trackers: [cost dispatch](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/costs/mod.rs), [SDK](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarinet-sdk), [SIP-044](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-044), [SIP-034](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-034). Check both [Clarigen issues](https://github.com/hstove/clarigen/issues) and [Clarinet issues](https://github.com/stx-labs/clarinet/issues) for receipt/epoch/cost-tracking differences.

## Transformations by dimension

Per-operation charges ([cost table](references/cost-table.md)) are not transaction totals: measure before and after. Cache across writes/callbacks only after proving stability; read [snapshot/cache invalidation](../clarity-security/references/state-and-accounting.md#cache-validity), including mutations within one block.

The [Clarity Book cost chapter](https://book.clarity-lang.org/ch12-00-runtime-cost-analysis.html) remains useful for a minimal-call baseline, fewer repeated cross-contract loads and separating bulky setup. Its numeric limits, tooling examples and optimization rankings require current-version measurements.

### Read count

| Change | Saves | Proof obligation |
|---|---|---|
| Read a map entry / var once and bind it with `let` | 1 read per repeat | Nothing between the reads changes it (no intervening write, no external call that could) |
| Store fields read together in one tuple value | 1 read per extra field map | Read bytes grow with the tuple; writes of one field rewrite the whole value |
| Fewer `contract-call?` hops (inline a tiny helper contract, call the protocol's bundled entry point) | 3 reads + callee size per hop | Same authorization, events and error behavior; the callee may be shared code you must not fork |
| Avoid `get-balance`/getter calls whose value you already have from a return value | 3+ reads per call | The returned value is the same quantity (sBTC `get-balance` includes locked units) |
| Replace "check then write" pairs with `map-insert` (returns `false` if present) | 1 read | Assert the boolean; keep the same error |
| Constants instead of data vars for values that never change | 1 read per use | Truly immutable for the life of the contract; governance can never need it |
| Paginate/bound list-driven loops | reads per item left out | Partial progress semantics are explicit and replay-safe |

### Read bytes

- `contract-call?` charges the callee's whole stored size each call. Calling a 60 KB contract ten times costs ~600 KB of read bytes and 30 reads before any logic runs. Keep hot-path contracts small (split admin/rarely used code out), and avoid calling a large contract for a trivial read.
- Stored values are read whole. A data var holding a `(list 500 uint)` or a fat tuple charges its full size on every `var-get`. When calls touch only a few items, index them in a map (`{index: uint} → item`); when calls use the whole list, one read of it can be cheaper than one read per item. Measure the binding dimension.
- Strings and buffers in storage cost their bytes on every read. Store hashes or IDs where the full value is not needed on-chain.

### Write count and bytes

- Each `map-set`/`var-set` is a write, and so is each FT/STX/NFT movement (`ft-transfer?` = 2 writes, `stx-transfer?` = 1). Batch accounting updates into one entry where the data model allows.
- Do not write unchanged values; skip the write when the computed value equals the stored one, if that read is already paid for.
- Deploy cost: `cost_contract_storage` charges the source size as write bytes ([source size](#source-size-and-recurring-load-costs)).

### Runtime (binding on old epochs or heavy computation)

- Prefer native operations over hand-written loops (`fold` over a 200-item list costs per item).
- Clarity 6: variadic `(concat a b c d)` is cheaper than nested binary `concat` chains.
- Verify an oracle payload's signatures once per transaction and reuse the verified values within the contract, or pass them only to consumers that authenticate the caller as the verifier; a consumer that accepts price arguments from any caller must verify the payload itself. Keep each consumer's freshness and feed checks.
- `to-consensus-buff?` + `sha256` over large tuples costs per byte; hash once and reuse.

## Never trade away the invariant

- Never cut trait identity, signatures, price freshness/confidence, `try!` propagation, slippage minima, health checks, or exact `as-contract?` allowances for savings.
- Do not reorder an external call ahead of authentication to reuse its output.
- `(/ (* a b) d)` and `(* (/ a d) b)` are different numbers. Reducing precision is a product decision, not an optimization.
- Preserve event names/fields for indexers unless versioning the schema.

## Switch-style dispatch

- Prefer the scholar's [nested `if` chain](../clarity-scholar/references/style.md#switch-style-dispatch) over repeated `(asserts! (not case?) result)` dispatch.
- With eight cases at epoch 4.0, `asserts!` dispatch costs 23 more runtime than the `if` chain for case 1, 72 for case 8 and 103 for an unknown case; storage counts are equal. Neither pattern evaluates unselected actions.
- This is a control-flow difference, not a guaranteed transaction saving. Re-measure the actual entry point, case distribution, nesting limits and source-size load cost.

## Filtering with per-call context

- Clarity has no lambda closures. Pass operation context in a [`fold` accumulator](../clarity-scholar/SKILL.md#iteration-without-loops), or let a named `filter` predicate read stored state.
- Context/output `fold`: no helper storage reads/writes, supports read-only per-call arguments and trait references. A growing result list increases argument/type-checking and append work.
- Helper-variable `filter`: can use much less runtime, but each predicate visit reads the helper. Setting it first adds **one read and one write**, even for an empty list. An already-correct persisted policy avoids setup, not the per-item reads.
- Before choosing between the two on cost, read the [measured fixture](references/measurements.md#filtering-fixture) (350 items at epochs 2.4 and 4.0) and its Bitflow source examples.
- Before epoch 3.3, callback argument charges use declared maximum type sizes; from 3.3 they use actual values ([VM argument charging](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/callables.rs#L202-L231)). Include the accumulator's list bound in historical measurements.
- Set scratch context before every helper-filter invocation; it is contract state, not a captured local. A read-only function cannot perform that setup write; reading existing policy is allowed.
- Prefer the smaller **binding budget dimension**, not runtime alone. A cheaper filter does not justify replacing a multi-action fold with a boolean filter.

## Repeated reads and address constants

- Binding a repeated map read with `let` performs one read instead of two, but the binding can cost more runtime than the saved read: at epoch 4.0 the [example](#example-binding-a-repeated-read) adds about 200 runtime units. That trade helps a read-bound path; a runtime-bound path may need the opposite choice. Measure the real entry point.
- Re-measure historical optimizations under the active schedule; measurements under costs_3 do not establish savings under costs_5.
- Use [supported address constants](../clarity-scholar/references/authority.md#fixed-contract-addresses) for readability and repeated identities, after checking their epoch, read-only and dependency limits. A once-used alias costs more runtime than the literal; each further use saves about one runtime unit and one read byte per source byte removed.

### Example: binding a repeated read

```clarity
;; id: repeated-read
(define-map positions principal {collateral: uint, rewards: uint})

(define-read-only (total-before (owner principal))
	(+
		(get collateral (default-to {collateral: u0, rewards: u0} (map-get? positions owner)))
		(get rewards (default-to {collateral: u0, rewards: u0} (map-get? positions owner)))))

(define-read-only (total-after (owner principal))
	(let ((position (default-to {collateral: u0, rewards: u0} (map-get? positions owner))))
		(+ (get collateral position) (get rewards position))))
```

- `total-after` performs one map read instead of two.

## Source size and recurring load costs

- Runtime is a deterministic meter, not elapsed time or only the instructions in the selected function. Ordinary contract entry charges `LoadContract`, including transaction entry and repeated `contract-call?` calls; local function calls do not add another contract load.
- Load size `n` is source bytes, including comments/whitespace/unused initialization code, plus the memory size of evaluated constants. Contract caching does not remove the metered charge.
- `cost_load_contract` (Costs5 delegates to Costs4 then Costs3): **runtime `n + 80`, read bytes `n + 1`, read count `3`**. These are load components, not complete call costs. Removing `k` source bytes saves `k` runtime units and `k` read bytes per ordinary load, other behavior and constant sizes unchanged.
- Publication also charges `ContractStorage` on source length `s` (runtime `11*s + 7165`, write bytes `s + 1`, one write) after parsing and analysis, before top-level code runs.
- One tab is one byte, so replacing four spaces saves three bytes; a single space is also one byte. Keep the project's [formatting policy](../clarity-scholar/references/style.md#formatting-and-function-comments): this byte difference does not override it. Measure actual output bytes; formatters may expand tabs before publication.
- Test and hash the exact final artifact. Whitespace changes source hashes and signed deployment bytes even when execution behavior is equivalent. Never rename public functions, tuple fields or event fields solely for size without checking consumers.
- Top-level setup runs once, but its source remains chargeable on later calls; unused helper bodies remain too, and large computed constants add load data. Large initialization is permitted if publication, analysis, execution and memory limits fit: a tradeoff, not a prohibition.
- Move bulky setup data/orchestration to scripts or a separate setup/proposal contract when recurring savings justify the additional interface and calls. Preserve authenticated, bounded initialization and finalization; see [deployment-time execution](../clarity-deployment/SKILL.md#deployment-time-execution). Splitting frequently used code adds cross-contract loads and changes caller context: benchmark the complete path.
- Sources: [load/publication charge sites](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/contexts.rs), [stored sizes](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/database/clarity_db.rs), [Costs5 delegation](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/costs/costs_5.rs), [effective load/storage formulas](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/costs/costs_3.rs).
- To estimate what a whitespace, comment or retained-initialization change saves, read the [measured examples](references/measurements.md#measured-examples).
- [Extreme source compaction](references/measurements.md#extreme-source-compaction) is **explicit opt-in only**: read it only when the user asks for it, and do not recommend or apply it during ordinary optimization.

## References

- [Cost formulas and cost contracts](references/cost-formulas.md): read before estimating a formula by hand, choosing an epoch's schedule, extracting formulas from a `stacks-core` checkout, or calling a deployed `costs-*.clar` contract.
- [cost table](references/cost-table.md): generated effective formula of every cost function under costs_3, costs_4 and costs_5. Open it to estimate one operation's charge.
- [Versions](../clarity-epochs/SKILL.md#resource-limits): historical limits and schedule activation. [Recall corrections](../clarity-epochs/SKILL.md#recall-corrections): common cost and limit mistakes.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `bitflow-dlmm`: [b4d3694c86](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0).
- `stacks-core-targeted`: [01a60adcb6](https://github.com/stacks-network/stacks-core/tree/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
