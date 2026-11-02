# Test design

Caller-context tests, case selection per surface and generated inputs.

## Drive public functions through attacker contracts

- Test through **contracts**, not only wallets: deploy a small caller/attacker contract to create the `contract-caller`/`tx-sender` context a router, callback or malicious contract would. `callPrivateFn` and storage patches skip the public boundary.
- Arrange real state through public functions (deposits, borrows, oracle updates), not private calls or direct storage edits.
- Generated builders also dispatch private functions (through `callPrivateFn`); that proves nothing about public reachability.
- Deploy fixtures dynamically with `simnet.deployContract(name, source, { clarityVersion: 4 }, sender)`: the target first (the attacker's analysis needs it), then the attacker **from the attacker's account**.
- When a victim or admin calls the attacker contract, it runs with `tx-sender` = that caller. A Clarity 4 attacker that calls through `(as-contract? ((with-all-assets-unsafe)) (try! (contract-call? ...)))` becomes `tx-sender` itself; for legacy targets deploy it with `clarityVersion: 3` and `as-contract`.
- Malicious trait implementations keep the trait's exact signatures and lie: `get-balance` returns a huge number, `transfer` returns `(ok true)` without moving anything, a callback re-enters a different function. Also test wrong dependency principals. Event spoofing: an unrelated contract prints the same tuple.
- Assert the asset delta, not only the response, and contrast with the control (direct call refused, fixed code or trusted path fails with the expected error).

```ts
// fragment: admin -> attacker's bait -> vault (raw SDK, sources as strings)
simnet.deployContract('vault', VAULT, { clarityVersion: 4 }, admin);
simnet.deployContract('bait', BAIT, { clarityVersion: 4 }, attacker); // after the target
const stx = (who: string) => simnet.getAssetsMap().get('STX')!.get(who)!;
const before = stx(attacker);
const r = simnet.callPublicFn(`${attacker}.bait`, 'claim-airdrop', [], admin); // bait runs with tx-sender = admin
expect(r.result).toBeOk(Cl.bool(true));
expect(stx(attacker) - before).toBe(1_000_000n);
```

Case selection per surface: [test matrix](#test-matrix); write-up: [PoC construction](../../auditor/SKILL.md#proof-of-concept).

## Test matrix

Choose rows relevant to the reviewed behavior, rather than adding generic tests for every helper.

| Surface | Required contrasting cases | Observe |
|---|---|---|
| Authority | Direct EOA; contract admin; allowed router; arbitrary router; sender changed by `as-contract?` | Actor, storage, authorized outflow, exact error origin |
| Trait | Correct implementation; malicious ABI match; wrong allowed role; incorrect underlying; same symbol | Principal checks before privilege or balance credit |
| Allowance | Exact outflow; one unit excessive; wrong asset; STX wrapper; caller-authorized pull; callback error | All relevant balances and rollback |
| Token | Zero; self-transfer; maximum; dust; 6/8/low decimals; locked sBTC; sender-only token | Native asset transfer, response, memo/event shape/order |
| Math | Zero/one; max allowed config; near 2^128 - 1; reciprocal round trip; repeated tiny calls | Solvency invariant and intermediate overflow |
| Oracle | Valid signed payload; wrong signer; wrong feed/channel; stale/future; wide confidence; negative/zero price; malformed lengths | Parser rejection and correct units; no price default to zero |
| Time | Same Stacks block; next Stacks block in same tenure; next burn block; long gap; exact boundary | Interest, deadlines, expiry, no unsigned subtraction abort |
| Batches | Empty; one; maximum; duplicate/reordered; middle failure | Atomicity, accumulator errors, no silently dropped feed/event |
| Postconditions | Split payouts; incoming refunds; automatic rewards for both endpoints; stale quote; wrong recipient with same total; Deny/Originator | Gross outflows by sender/asset, explicit coverage, on-chain receipt bounds and rollback; [rules](../../wallets/SKILL.md#post-conditions) |
| Resources | Largest supported portfolio/path; hostile trait; all oracle signatures; cold reads; near stack depth | Five costs, memory, executable liquidation/exit |
| Bridge/events | Two withdrawals/burns in one tx; unrelated contract prints matching tuple; reverted tx; reorg; pagination boundary | Idempotent event identity and committed canonical execution |
| PoX | Prepare/reward boundary; signer migration; partial pending withdrawals; old/new contract | Correct locked principal, cycle entitlement, allowance type |
| Upgrade | Populated old state; old/new dependencies; timelock boundaries/bypass; role and token migration; source hash mismatch | No stale approvals, duplicate claims or inaccessible funds; reconcile custody, liabilities, fees and indexes; [cutover assertions](../../upgrades/SKILL.md#rehearsal-assertions) |
| State/cache | Read → mutate → merge; cold/warm cache; two mutations in one block; repeated checkpoint without accrual | Updated fields persist; previews and settlement agree; no duplicate rewards |
| Registry/packing | Empty/full; ID 127/128; domain boundary; duplicate key; unequal lists; every parser cardinality | No bitmap alias, silently unprocessed entry, inconsistent reverse map or unreachable capacity |
| Asset lifecycle | Enabled/disabled debt/collateral; partial repair; final exit; zero assets/supply; complete loss | Policy-consistent valuation, claims and executable recovery paths |

- Use a version-matched simnet for contract semantics and devnet/replay for node/epoch/bridge behavior that simnet does not model.
- A simulator test cannot prove a distributed signer liveness fix. State that limit explicitly.

## Properties and generated inputs

- Use bigint for financial quantities; cover zero/dust/max inputs, uint128 intermediate overflow, rounding (ten small deposits need not equal one large one: specify the bound and who gets the remainder), empty/maximal collections and time boundaries. Use fixed boundary cases and seeded bigint generators; never `Math.random()` or `Number` over uint128 ranges.
- Derive invariants from accounting, fees and rounding. Test quote-versus-execution bounds, empty liquidity, dependency errors and rollback.
- Save seed, inputs and sequence for every generated failure, and turn it into a fixed regression. Replace skipped failures with a tracked reason and a regression for the intended behavior.
- For Rendezvous campaigns (setup, private `test-*` functions, stateful invariants, generated inputs, saved-failure replay) use [clarity:fuzzing](../../fuzzing/SKILL.md); keep Clarigen for typed tests and deterministic regressions. A fuzz run's exit status alone does not establish that its intended properties were checked.
