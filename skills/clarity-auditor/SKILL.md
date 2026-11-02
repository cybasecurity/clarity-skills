---
name: clarity-auditor
description: "Audit or security-review Clarity contracts: threat model, Clarity-specific checks, simnet PoC exploits, severity and findings. Use for any request to review, audit or find issues in .clar code."
license: MIT
allowed-tools: "Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/clarity-scholar/scripts/lookup_function.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Auditor

Establish reachable impact and affected versions; historical findings are hypotheses for the current target. Load only the relevant pattern families.

## Key distinctions

- Recursion protection tracks active functions; callbacks into another function of an active contract can execute.
- Native FT/NFT primitives check assets and balances, not permission to act for the owner.
- A trait argument proves only that the called method has the trait's signature. It proves no approved role or trusted code: check the role's allowlist and the deployed source.
- Private `err` does not itself roll back writes. A caller handling a public callee's error can commit its own state.
- Source submitted in a failed deployment is not the code deployed at that principal.

## Clarity pass (run on every target; record file:line or "none")

Each line: what to look for -> pattern. Load `clarity-security` with this skill: each ID below links to its entry in the [security patterns](../clarity-security/references/patterns.md#security-patterns-a01-a29).

1. `tx-sender` in authorization checks on privileged paths -> [A01](../clarity-security/references/patterns.md#a01-sender-authority-forwarded-through-an-attacker); contract roles compare `contract-caller`, except setters reached through an ExecutorDAO-style proposal, where `tx-sender` = the DAO is the intended check.
2. `as-contract`, `as-contract?`, `restrict-assets?`, `with-all-assets-unsafe`, wildcard or oversized allowances around a caller-supplied `<trait>` call -> [A03](../clarity-security/references/patterns.md#a03-allowance-bypass-outside-as-contract), [A04](../clarity-security/references/patterns.md#a04-broad-asset-allowances).
3. Every `<trait>` argument: is `(contract-of t)` compared to a stored or constant principal for that role? -> [A02](../clarity-security/references/patterns.md#a02-trait-confusion--wrong-role-contract).
4. Public paths reaching `ft-transfer?`, `nft-transfer?`, `ft-burn?`, `nft-burn?` (no sender check in the VM) -> owner check present? [native assets](../clarity-security/SKILL.md#native-assets).
5. `stx-transfer?`/`ft-transfer?`/`ft-mint?` under `try!` where the amount can be 0 (fee rounding, last repayment) or sender equals recipient -> [A27](../clarity-security/references/patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows).
6. `let` bindings with `/`, `-`, `unwrap-panic` or a contract call that precede an `asserts!`; values read before a state change -> [A28](../clarity-security/references/patterns.md#a28-let-bindings-run-before-the-bodys-guards).
7. `map`, `fold`, `filter` over responses; `asserts!`/`unwrap!` thrown values of `(ok ...)` -> [A18](../clarity-security/references/patterns.md#a18-response-handling-in-batches).
8. `(/ (* a b) d)`, `pow`, ceil division `(/ (+ n (- d u1)) d)`, rounding direction -> [A11](../clarity-security/references/patterns.md#a11-uint128-intermediates-and-rounding-direction). Share mint `amount * supply / assets` with a 1:1 empty-vault branch and a live-balance `assets` -> [A29](../clarity-security/references/patterns.md#a29-first-deposit-and-donation-share-inflation).
9. `get-balance`, `stx-get-balance`, wSTX or sBTC balance used as liquidity -> [A08](../clarity-security/references/patterns.md#a08-sbtc-total-is-not-transferable-balance), [A09](../clarity-security/references/patterns.md#a09-wstx-is-not-one-universal-token).
10. `block-height`, `burn-block-height`, block time, `at-block` comparisons -> [A10](../clarity-security/references/patterns.md#a10-stale-or-fictitious-now).
11. `print` consumed off-chain or by a bridge -> [A16](../clarity-security/references/patterns.md#a16-prints-are-protocol-interfaces). Forwarded `(err uN)` -> [A17](../clarity-security/references/patterns.md#a17-local-error-namespaces).
12. PoX/staking calls and allowances -> [A20](../clarity-security/references/patterns.md#a20-wrong-pox-generation-and-clock), [A21](../clarity-security/references/patterns.md#a21-reward-weights-and-ownership-across-cycles).
13. Any approved deployed address -> [A05](../clarity-security/references/patterns.md#a05-approval-based-on-the-wrong-deployment). Network principals, initializers -> [A06](../clarity-security/references/patterns.md#a06-bad-network-principals--unusable-roles), [A07](../clarity-security/references/patterns.md#a07-deployment-order-and-initialization-hazards).
14. Worst-case list sizes, trait callback chains, exits at maximum state -> [A19](../clarity-security/references/patterns.md#a19-execution-budget-as-a-liveness-boundary).
15. Batch payouts, caches, packed registries -> [A24](../clarity-security/references/patterns.md#a24-automatic-rewards-and-aggregate-postconditions), [A25](../clarity-security/references/patterns.md#a25-stale-tuples-and-incomplete-caches), [A26](../clarity-security/references/patterns.md#a26-packed-registries-hide-capacity-and-identity-errors).
16. Receipt or wrapper tokens counted as collateral, balances read inside a flash-loan callback -> [A12](../clarity-security/references/patterns.md#a12-receipt-tokens-vs-actual-asset-movements), [A13](../clarity-security/references/patterns.md#a13-flashloan-context-and-transient-balances).
17. Oracle prices and timestamps, `slice?` and `(buff N)` parsing -> [A14](../clarity-security/references/patterns.md#a14-pyth-data-and-units), [A15](../clarity-security/references/patterns.md#a15-buffers-slicing-and-partial-validation).
18. Withdrawal requests, Bitcoin txids and outpoints -> [A22](../clarity-security/references/patterns.md#a22-async-withdrawal-state-vs-synchronous-success), [A23](../clarity-security/references/patterns.md#a23-canonical-bitcoin-identifiers-and-replay-state).

## Solidity reflexes that are not findings in Clarity

| Reflex | In Clarity | Check instead |
|---|---|---|
| Reentrancy | The VM blocks active-function recursion; a missing lock is not a finding by itself | A different function reachable from a callback and the invariant it breaks ([callback guards](../clarity-security/references/pitfalls.md#callback-guards)) |
| Integer overflow wraps | Overflow, underflow and `/ 0` abort the transaction | Intermediates that make valid users abort (A11); guard order (A28) |
| Unchecked return value | The analyzer rejects an unchecked response in `begin` | Responses dropped by `map`/`fold`, `(ok ...)` thrown by `asserts!` (A18) |
| `tx.origin` is bad, `msg.sender` is good | `tx-sender` is the origin-like value and is the one that is forwarded | `tx-sender` vs `contract-caller` per path (A01) |
| `selfdestruct`, proxies, `delegatecall` | None exist | Registry or role swaps that replace code in effect ([upgrades](../clarity-upgrades/SKILL.md#timelocked-cutover)) |
| Uninitialized storage | A var gets its initial value at definition; a missing map key reads as `none` | `default-to` hiding "never registered" ([pitfalls](../clarity-security/SKILL.md#responses-and-control-flow)) |

## Review

- Record language version, executing epoch, tool support, deployment and source revision. Inventory public entry points, dynamic traits, privileged state, native assets and print consumers.
- Trace authority, allowances, callbacks and transient balances to committed effects; check earlier aborts and the rollback boundary before claiming persistence. Call the target through an attacker contract or router, not only directly from a wallet.
- Asset postconditions do not protect arbitrary state (listings, approvals, roles); assert state, events and balances. Mocks prove only modeled behavior.
- Also review [state/cache/registry invariants](../clarity-security/references/state-and-accounting.md#state-and-accounting), [position discovery and valuation](../clarity-apis/references/positions-and-proofs.md#discover-positions-then-value-them) for liquidators/indexers, and, for upgrades, [cutover, legacy claims and timelock bypasses](../clarity-upgrades/SKILL.md#timelocked-cutover).
- Use the [test matrix](../clarity-testing/SKILL.md#test-matrix) and the [proof-of-concept steps](#proof-of-concept). Check exact SIP clauses separately; a security recommendation is not a normative requirement.
- Separate confirmed issues, hypotheses, fixed history, accepted trust, style and recommendations. Reassess historical severity for this target.

Finding template (the default; follow a format the engagement requests):

```markdown
### <ID>: <title>
Severity: <Likelihood x Impact per matrix> | Status: confirmed / hypothesis / fixed-history
Root cause: <file:line, commit/version, language version, epoch>
Preconditions: <who calls what, state required>
PoC: <test name, call sequence, observed delta>
Impact: <assets or state, who is hurt>
Fix: <change preserving the intended authority model>; regression test <name>
Assumptions: <unresolved>
```

## Proof of concept

- Use a reachable transaction sequence to demonstrate runtime impact whenever the target can be simulated. A static proof or compiler rejection can establish other findings; state that evidence and any simulation limitation.
- Caller/trait/allowance findings often need a **contract in the middle** (an attacker contract, router, or malicious implementation), because a direct wallet call does not exercise the disputed boundary.
- Run PoCs only in a project you are authorized to execute (the user's own repository or a scratch copy). Do not install or run dependencies of a repository downloaded only for reading.
- Harness: default to Clarigen for the target protocol's generated calls and response assertions. To deploy attacker variants dynamically without regenerating types (or in projects without Clarigen), use the raw SDK: `initSimnet('Clarinet.toml')` (in a vitest-environment-clarinet project use the global `simnet`), `simnet.setEpoch('4.0')` for a scratch run (a project manifest normally pins it), an attacker account from `simnet.getAccounts().get('wallet_2')`, `simnet.deployContract(name, source, { clarityVersion: 4 }, attacker)`. A standalone script runs as `node poc.mjs` next to a `Clarinet.toml` and a `settings/Devnet.toml` that defines the deployer and wallet accounts. It needs `@stacks/clarinet-sdk` and `@stacks/transactions`, prints a line on success and throws on any failed assertion.
- When tool behavior differs, check the current [Clarigen](https://github.com/hstove/clarigen/issues) and [Clarinet](https://github.com/stx-labs/clarinet/issues) issue trackers.

Steps for every PoC:

1. **Arrange** real state through public functions (deposits, borrows, oracle updates), not `callPrivateFn` or direct storage edits. Move clocks with `mineEmptyStacksBlocks`/`mineEmptyBurnBlocks`. Deploy the target before any contract whose analysis references it.
2. **Act** through the contract graph the attacker can actually build: deploy the attacker/malicious-trait contract **from the attacker's account**, then have the right principal call it (victim, admin, keeper).
3. **Assert** the impact in assets (`getAssetsMap`), storage (`getMapEntry`, `getDataVar`) and events. A wrong return value alone is not impact.
4. **Contrast:** run the same sequence against the fixed code (or the intended trusted path) and show it fails with the expected error. Include a control showing the attacker cannot do it directly.

```js
// fragment: A01 PoC. VAULT's withdraw-to checks (is-eq tx-sender ADMIN), then pays inside as-contract?.
const BAIT = `(define-public (claim-airdrop)
  (contract-call? '${admin}.vault withdraw-to u1000000 '${attacker}))`;
simnet.deployContract('vault', VAULT, { clarityVersion: 4 }, admin);
simnet.deployContract('bait', BAIT, { clarityVersion: 4 }, attacker); // after the vault, from the attacker
// Control (after the admin deposited): the attacker cannot withdraw directly.
assert.deepEqual(simnet.callPublicFn(`${admin}.vault`, 'withdraw-to',
  [Cl.uint(1_000_000), Cl.principal(attacker)], attacker).result, Cl.error(Cl.uint(100)));
// Act: the admin calls the untrusted contract. Assert the asset delta, not only the response.
const stx = (who) => simnet.getAssetsMap().get('STX').get(who);
const before = stx(attacker);
const r = simnet.callPublicFn(`${attacker}.bait`, 'claim-airdrop', [], admin);
assert.deepEqual(r.result, Cl.ok(Cl.bool(true)));
assert.equal(stx(attacker) - before, 1_000_000n);
```

### Building blocks

| Need | Construct |
|---|---|
| Malicious trait implementation | Deploy a contract with the trait's exact signatures that lies: `get-balance` returns a huge number, `transfer` returns `(ok true)` without moving anything, a callback re-enters a *different* function of the target. |
| Context switch | Clarity 4 attacker: `(as-contract? ((with-all-assets-unsafe)) (try! (contract-call? ...)))` makes the attacker contract itself the `tx-sender`. Legacy targets: deploy the attacker with `clarityVersion: 3` and use `as-contract`. |
| Victim calls attacker | `callPublicFn('<attacker>.bait', ..., victim)`: the attacker contract now runs with `tx-sender = victim`. |
| Same-block conditions | Several `callPublicFn` calls without mining run in successive blocks in simnet; `simnet.mineBlock([tx.callPublicFn(...), ...])` puts calls in **one** block. |
| Time | `mineEmptyStacksBlocks(n)` advances Stacks height only (epoch 3.0+); `mineEmptyBurnBlocks(n)` advances burn height and the simulated Stacks tip. `mineEmptyBlocks` aliases burn-block mining in SDK 3.26.0. |
| Big numbers | `Cl.uint(2n ** 127n)`; SDK 3.26.0 runtime failures can throw for both public and read-only calls. Capture the specific VM category and verify rollback; a node receipt represents the abort differently. See [runtime assertions](../clarity-testing/references/helpers-and-assertions.md#separate-contract-errors-from-runtime-failures). |
| Event spoofing | Deploy an unrelated contract that prints the same tuple shape and show the consumer cannot tell them apart without checking the emitter. |
| Costs / DoS | `initSimnet(manifest, true, { trackCosts: true, trackCoverage: false })` and inspect `receipt.costs.total` against the active tenure budget (simnet's `receipt.costs.limit` shows older read limits) and the target miner's block policy ([resource limits](../clarity-epochs/SKILL.md#resource-limits)). |

### Real dependencies

- Use `[[project.requirements]]` to pull the real deployed contracts (SIP traits, a protocol's deployed contract; `sbtc-token` is already a simnet boot contract) into simnet instead of hand-written mocks, so the authorization and asset semantics are the real ones. Seed protocol state through its public functions.
- When a dependency needs off-chain inputs (Pyth/Lazer signed payloads, Bitcoin proofs), use the protocol's own test fixtures and a test signer, and say so in the report.
- Mock PoCs establish only adapter behavior.

### Writing it up

- State the Clarity version and epoch of the run, the SDK version, the exact call sequence (who calls what, through which contract), the observed asset/state delta, and the contrasting failing run.
- Keep the PoC minimal: one attacker contract and the fewest steps that show the impact.

## Risk classification

Use the severity scale and report format the engagement specifies (contest rules, a bug-bounty table, the client's template). Without one, use this matrix and the template above.

- Rate demonstrated impact and realistic likelihood separately; state the assumptions supporting each.

| Likelihood / Impact | High | Medium | Low |
|---|---|---|---|
| High | Critical | High | Medium |
| Medium | High | Medium | Low |
| Low | Medium | Low | Low |

- Impact: **High** = significant asset loss or harm to a group of users; **Medium** = small funds loss or affected protocol functionality; **Low** = less critical unexpected behavior.
- Likelihood: **High** = direct attack with low cost relative to damage; **Medium** = conditionally incentivized but reasonably likely; **Low** = many/unlikely assumptions or little/no incentive.
- Actions: **Critical/High must fix**; **Medium should fix**; **Low could fix**.
- **Informational:** style, operations, cost, documentation, standards or design recommendations with minimal functional/security impact. Review them, but classify any demonstrated vulnerability by the engagement's scale (this matrix by default).

## Read when needed

- [Native behavior pitfalls](../clarity-security/SKILL.md#native-behavior-pitfalls): native assets, responses, serialization and cryptography.
- [Signed authorizations](../clarity-security/references/authorization.md#signed-authorizations): high-S, recovery IDs, signer binding and replay; require reachable impact before classifying malleability as a vulnerability.
- [Bitcoin bridge boundaries](../clarity-bitcoin-proofs/SKILL.md#bridge-boundaries): UTXO reservations, accepted script encodings, NFT identity and cross-chain rejection costs.
- [Versions](../clarity-epochs/SKILL.md): activation and historical bugs.
- [Recall corrections](../clarity-epochs/SKILL.md#recall-corrections): common model errors.
- `python3 <skills>/clarity-scholar/scripts/lookup_function.py 'as-contract?'` (`<skills>` is the directory holding the skill folders): retrieve one exact entry; cross-check current VM behavior.
- Never mechanically replace `tx-sender`, remove context scopes, ban traits or add `is-standard` everywhere; preserve the intended authority model.
- For requested stateful/property fuzzing, use [Rendezvous guidance](../clarity-fuzzing/SKILL.md); require exercised checks and a reachable clean-state reproduction.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
