---
name: security
description: "Load with clarity:scholar when writing or changing a contract that holds funds or has admin roles. Covers tx-sender vs contract-caller, as-contract? allowances, trait validation, signatures, arithmetic and rollback. Use for access control, custody or fixing a vulnerability."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Security

Preserve the intended trust and ownership model while making each sensitive effect explicitly authorized.

## Key distinctions

- Inherited `tx-sender` can forward a victim's authority through an untrusted contract ([A01](references/patterns.md#a01-sender-authority-forwarded-through-an-attacker)).
- Asset postconditions do not protect arbitrary state, including NFT listings changed through callbacks ([A01](references/patterns.md#a01-sender-authority-forwarded-through-an-attacker)).
- Requiring direct calls everywhere can break legitimate routers and multisigs.
- Native FT/NFT operations do not authenticate the supplied owner; native STX has different sender checks ([native assets](#native-assets)).
- Traits establish interfaces, not trusted implementation, economic identity or approved role.
- `as-contract?` protects its dynamic scope; caller-authorized token pulls elsewhere remain possible.
- Recursion restrictions do not prevent every callback or transient-accounting attack.
- A private function returning `err` rolls back nothing; only the public function's final response decides ([responses and control flow](#responses-and-control-flow)).

## Implement or repair

- Establish language version, execution epoch, native assets and actor roles.
- Trace wallet → router → token and each callback. Choose sender, immediate caller or explicit signed delegation according to the intended authorization.
- When downstream contracts need the user's `tx-sender`, apply an explicit [entry-point policy](references/authorization.md#sender-preservation) and retain that context through trusted calls.
- Check every `<trait>` argument with `(asserts! (is-eq (contract-of t) <stored or constant principal for that role>) ERR)` before calling or crediting it, with one allowlist per role (asset, market, oracle, callback, governance) ([A02](references/patterns.md#a02-trait-confusion--wrong-role-contract)).
- Privileged setters check `contract-caller` against the admin principal (`tx-sender` against the DAO under an ExecutorDAO-style core), print an event naming the change and validate their input. Roles that move funds or report value (rebalancer, adapter, venue, oracle) are sensitive: fix them, or change them only behind a timelock (at least 24 hours recommended, 48 for upgrades and custodial changes). A guardian's [instant pause](../governance/SKILL.md#immediate-actions) is the exception: it stops actions with no delay and cannot move funds or change roles. A contract-only role must reject wallets: require the `name` that `principal-destruct?` returns to be `some` (it is `none` for wallets), since `is-standard` also accepts wallets ([A06](references/patterns.md#a06-bad-network-principals--unusable-roles)).
- Add persistent callback locks only for a concrete reachable path and invariant; use [callback guard criteria](references/pitfalls.md#callback-guards).
- Signed authorizations ([rules](references/authorization.md#signed-authorizations)): put chain ID, contract, operation, arguments, signer and a nonce or expiry in the digest; compare the recovered key with the stored signer, or call `secp256k1-verify` with the stored key; consume a signer-scoped nonce or the digest, never the signature bytes or their hash (high-S twins and the ignored final byte defeat that).
- Capture original actors before changing context; scope allowances to exact assets and bounded gross outflows ([A04](references/patterns.md#a04-broad-asset-allowances)).
- Make reward hooks and batch transfers compatible with explicit wallet bounds; enforce intended receipts on-chain ([A24](references/patterns.md#a24-automatic-rewards-and-aggregate-postconditions)).
- Guard before computing: `let` bindings run before the body's `asserts!` ([A28](references/patterns.md#a28-let-bindings-run-before-the-bodys-guards)). Native transfers of amount 0 or to self return errors that abort a `try!` flow ([A27](references/patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows)).
- Share vaults: a 1:1 first mint plus a direct donation lets the first depositor take later deposits; use virtual shares and virtual assets in both deposit and redeem math, seeded dead shares, or internally tracked assets; reject 0-share mints and take `min-shares` ([A29](references/patterns.md#a29-first-deposit-and-donation-share-inflation)).
- Propagate responses deliberately; test handled callee errors and late failures against committed state/events ([A18](references/patterns.md#a18-response-handling-in-batches)).
- Bound uint128 intermediates; prefer [additive range guards](../scholar/references/arithmetic-and-time.md#additive-range-checks) when their sums provably fit. Define rounding and test dust, maximums and repeated operations ([A11](references/patterns.md#a11-uint128-intermediates-and-rounding-direction)).
- Treat prints as interfaces: preserve required ordering/units and authenticate emitter/canonical execution in consumers ([A16](references/patterns.md#a16-prints-are-protocol-interfaces)).
- Check the [native behavior tables](#native-behavior-pitfalls), then the relevant [security patterns](#security-patterns-a01-a29).
- For replaceable implementations or privileged registries, use [upgrade and migration checks](../upgrades/SKILL.md), including timelocked code/role changes and legacy exits.
- For mutable tuples, caches, packed registries or lending/reward ledgers, apply [state and accounting](references/state-and-accounting.md#state-and-accounting).
- Test malicious traits, contract-mediated callers, wrong roles, boundary values and rollback. A trait-compatible mock is not proof of a real dependency's behavior.
- Explain the changed invariant and observable effects. Do not turn a targeted fix into an unsolicited full audit.
- Keep normative SIP compliance separate from additional security policy.

## Native behavior pitfalls

Check [VM documentation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs), implementation and target version. Resolve epoch-wide changes through [versions](../epochs/SKILL.md).

### Native assets

| Function | Pitfall |
|---|---|
| `stx-transfer?` / `stx-burn?` | `sender` must equal the current `tx-sender`, otherwise `(err u4)`. A contract can spend inherited user STX with `(stx-transfer? amt tx-sender to)`; wallets should bound outflows with postconditions. Contract-owned spending needs its sender scope and, in Clarity 4+, `with-stx`. |
| `ft-transfer?` / `nft-transfer?` / `ft-burn?` / `nft-burn?` | **No sender check at all.** The defining contract can move or burn anyone's balance; every public path that reaches them needs its own owner check. |
| zero amounts | `stx-transfer?`/`ft-transfer?` → `(err u3)`, `ft-mint?`/`ft-burn?` → `(err u1)`. A fee or rounded output of 0 aborts a flow that `try!`s it ([A27](references/patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows)). |
| self-transfer | `(err u2)` when sender = recipient (STX, FT, NFT). Self-liquidation, a fee recipient who is also a user, or a vault paying itself abort. |
| `ft-mint?` over a supply cap | `define-fungible-token name cap`: exceeding the cap is a **runtime abort** (`SupplyOverflow`), not an err value. Callers cannot catch it. |
| `nft-mint?` | `(err u1)` if the ID exists. |
| `stx-get-balance` | Returns **spendable** STX only (unlocked, plus locks whose unlock height has passed); stacked STX is invisible. Use `stx-account` (`{locked, unlock-height, unlocked}`). sBTC differs: [A08](references/patterns.md#a08-sbtc-total-is-not-transferable-balance). |
| Low error codes | Native `u1`–`u4` propagate through `try!` and collide with application codes. Use higher documented ranges for new custom errors ([A17](references/patterns.md#a17-local-error-namespaces)). |

### Execution context

| Name | Pitfall |
|---|---|
| `tx-sender` | The origin, unchanged across nested `contract-call?`s until `as-contract?` switches it. Authorization on it trusts every contract in the call path. |
| `contract-caller` | The immediate caller. Use it when the designated caller owns the admin/role authority. Trace signer → multisig → executor → proposal → target, including sender scopes; the target does not necessarily see the multisig as its caller. Some governance paths deliberately authenticate inherited executor context. |
| `as-contract` | Clarity 1–3 only. Switches both principals and grants unlimited authority over the contract's assets to everything the body calls. |
| `as-contract?` | Clarity 4+: `(as-contract? ((with-ft <token-contract> "<token-name>" amount) (with-stx amount)) (try! ...))`. Inside the body `tx-sender` **and** `contract-caller` are both the contract itself. It runs the body, **then** checks the contract's outflows: `(err index)` for the first violated allowance, `(err u128)` for an asset with no allowance; the body is reverted. Allowance expressions are evaluated before the body, in the outer context. **No** body expression may be a response (wrap calls in `try!`/`unwrap!`). Allowances are **ceilings**, not exact spends. Burns count as outflows, including a callee burning the contract's tokens (a protocol's withdraw or redeem burning its LP or vault shares): allow that token too. Callees still see `tx-sender` = the contract, and non-asset side effects are unrestricted. |
| `with-ft` | Names the token contract **and** the `define-fungible-token` name; `"*"` = all FTs of that contract. Does not cover STX moved by a wrapper that calls `stx-transfer?` (needs `with-stx`). |
| `with-nft` | `(with-nft contract asset-name (list id ...))`, at most 128 IDs. `"*"` as the asset name covers every NFT class the contract defines, and the ID list still limits which tokens may leave, so a caller-supplied collection is scoped with `(with-nft (contract-of nft) "*" (list token-id))`. Element types are not type-checked: a wrong-typed ID never matches. |
| `with-stacking` → `with-staking`, plus `with-pox` | Clarity 4–5: `with-stacking` caps the **total** locked amount (increase calls need the new total). Clarity 6+: `with-staking`, the same allowance renamed, plus `with-pox` (no amount) for position-altering PoX calls. `with-stx` never covers locks. |
| `with-all-assets-unsafe` | Removes every outflow check. Around a call to a caller-supplied trait it is equivalent to legacy `as-contract`. |
| `tx-sponsor?` | `none` when unsponsored. Logic paying/crediting sponsors needs single-use receipts. |
| `define-constant` | Evaluated once in the deploy transaction: `tx-sender` = deployer, heights = deploy block (each contract of a suite gets its own), `contract-call?` results frozen. |

### Calls, traits, recursion

| Topic | Pitfall |
|---|---|
| Recursion | Rejected at analysis ("interdependent functions"). Loops are `fold`/`map`/`filter` over bounded lists. |
| Re-entrancy | Runtime rejects calling a function **already on the call stack** (`contract:function`) and a contract dynamically calling itself. A callee *may* call a **different** function of a contract that is mid-execution, so cross-function and read-only re-entrancy through trait callbacks is possible. |
| Call targets | `contract-call?` needs a literal principal, a constant (works at epoch 4.0 in public functions and the private helpers they call; a read-only function that calls through a constant, directly or through a private helper, fails analysis with "detected a writing operation", so use the literal there; see [versions](../epochs/SKILL.md) for older epochs), or a trait value received as an argument. A principal read from storage cannot be called. That is why contracts take `<trait>` arguments and must validate `contract-of`. |
| `impl-trait` | Publication analysis checks declared trait methods/signatures, not authority or behavior. Structural implementations can work without it. A node's mempool checks contract arguments against the whole trait (in any list, only the first element), and deployment checks literals in source, but the VM checks only the called function at dispatch, and a miner can include a transaction without the mempool check. Stub functions pass every check. Local trait copies have distinct identities; verify canonical trait/types. |
| Runtime trait args | `contract-of` extracts identity without validating the whole ABI. Without an explicit implementation, dispatch checks the invoked method; a successful handshake does not validate other methods. |
| Trait-typed parameters in your trait | When your own trait declares a method whose parameter is itself a trait (a router trait whose `swap` takes `<pool-trait>`), dispatch compares that nested trait by **identity**: a target typed with the protocol's trait fails `RuntimeCheck(BadTraitImplementation)` against a byte-identical local copy. Deploy and `clarinet check` succeed, and mocks that share your copy hide it. Call fixed protocol contracts statically, or `use-trait` the protocol's own trait principals (declared as requirements) inside your trait. |
| Read-only functions | Cannot write, cannot call non-read-only functions, and cannot make dynamic (trait) calls at all: a read-only quote through a caller-supplied `<trait>` will not type-check. |
| Static references | A literal `.contract` is bound at deploy; proxies/upgrades that keep literal references keep calling v1. |

### Responses and control flow

| Construct | Pitfall |
|---|---|
| `try!` / `unwrap!` / `asserts!` | Return from the **enclosing function** (inside a `fold`/`map` callback: the callback). The thrown value can be `(ok ...)`: `(asserts! cond (ok true))` is a silent early success that commits prior writes; `(unwrap! (parse ...) (ok partial))` turns a parse failure into a successful partial result. |
| `unwrap-panic`, overflow, underflow, `/ 0`, `to-uint` of a negative, `pow` overflow | Runtime abort: no error code, not catchable by callers, the transaction is still mined and pays its fee. On user paths, use `unwrap!` with a real error. |
| `let` bindings | Evaluated in order **before** the body: a guard in the body cannot protect a binding ([A28](references/patterns.md#a28-let-bindings-run-before-the-bodys-guards)). |
| Unchecked responses | The analyzer rejects an unchecked response as an intermediate `begin` expression, but accepts one bound in `let` and a list of responses from `map`. `(begin (map f xs) (ok true))` silently ignores failures. |
| `map` | Returns a list of results; errors stay inside the list. With several sequences and one empty, epochs before 4.0 had an off-by-one that called the function with too few arguments: an abort, or spurious results from a variadic function such as `+` (fixed from 4.0). |
| `fold` | Always visits every element (no break). Carry failure in the accumulator: `(try! prior)` first. Epoch 4.1 widens the result type to cover both the initial value and the function's return. |
| `map-insert` / `map-delete` | Return `false` (not an error) when the key exists / is absent. Unasserted, duplicates and removals become silent no-ops. `map-set` always overwrites. |
| `default-to` getters | Hide "never registered": a setter that reads through one creates half-initialized records. |
| Public `err` | Rolls back the whole public call's writes and events. A **private** function returning `err` rolls back nothing by itself; only the enclosing public function's final result decides. |
| `print` arguments | Evaluated eagerly: a division by zero inside an event payload aborts the state change it describes. |

Read [references/pitfalls.md](references/pitfalls.md) when adding a callback lock ([callback guards](references/pitfalls.md#callback-guards)) or handling numbers, buffers, strings, clocks, signatures or principal checks.

## Security patterns (A01-A29)

Read [references/patterns.md](references/patterns.md) before applying or reporting a pattern: most entries give what goes wrong, the fix and what to test.

### Authority and dynamic contracts

- [A01](references/patterns.md#a01-sender-authority-forwarded-through-an-attacker): inherited `tx-sender` forwards a victim's authority through untrusted contracts, beyond what postconditions cover; check `contract-caller` or explicit delegation.
- [A02](references/patterns.md#a02-trait-confusion--wrong-role-contract): a trait is an interface only; check `(contract-of t)` against that role's allowlist for every trait argument.
- [A03](references/patterns.md#a03-allowance-bypass-outside-as-contract): a token accepting `contract-caller == sender` debits its caller with no `as-contract?` scope; audit every outgoing call.
- [A04](references/patterns.md#a04-broad-asset-allowances): allow the exact asset, token name and bounded outflow; no `with-all-assets-unsafe` or wildcards for a known asset.
- [A05](references/patterns.md#a05-approval-based-on-the-wrong-deployment): a mined deploy can abort; require a successful deploy and matching deployed source or `contract-hash?`.
- [A06](references/patterns.md#a06-bad-network-principals--unusable-roles): `is-standard` is a network check that contracts pass; validate persisted role and recipient principals.
- [A07](references/patterns.md#a07-deployment-order-and-initialization-hazards): the top-level deployer is not the runtime caller; authenticate one-time, ordered initialization.

### Tokens, clocks and accounting

- [A08](references/patterns.md#a08-sbtc-total-is-not-transferable-balance): sBTC `get-balance` includes locked units; use `get-balance-available` for liquidity and repayment.
- [A09](references/patterns.md#a09-wstx-is-not-one-universal-token): wSTX wrappers differ; a native-STX wrapper needs sender context and `with-stx`.
- [A10](references/patterns.md#a10-stale-or-fictitious-now): previous-block time is not now; use the target version's clock.
- [A11](references/patterns.md#a11-uint128-intermediates-and-rounding-direction): `a*b` must fit even when `a*b/d` would; round shares and payouts to preserve solvency.
- [A12](references/patterns.md#a12-receipt-tokens-vs-actual-asset-movements): never count collateral twice through aliases or receipt tokens; use actual returned amounts.
- [A13](references/patterns.md#a13-flashloan-context-and-transient-balances): balances during a flash-loan callback exclude the lent principal; never price from them.

### Oracles, serialization and external consumers

- [A14](references/patterns.md#a14-pyth-data-and-units): check feed ID, freshness, exponent, confidence and sign; Lazer times are microseconds.
- [A15](references/patterns.md#a15-buffers-slicing-and-partial-validation): `(buff N)` is a maximum; check exact lengths and trailing bytes before slicing.
- [A16](references/patterns.md#a16-prints-are-protocol-interfaces): consumers check emitter, success, canonical block and event index, not tuple shape.
- [A17](references/patterns.md#a17-local-error-namespaces): native `u1`–`u4` collide with low codes; use a higher range such as `u1000`–`u1099`.
- [A18](references/patterns.md#a18-response-handling-in-batches): `map` keeps errors in its list and `fold` continues; choose all-or-nothing or partial.
- [A19](references/patterns.md#a19-execution-budget-as-a-liveness-boundary): exits and liquidations must fit the execution budget at maximum supported state.

### PoX and asynchronous flows

- [A20](references/patterns.md#a20-wrong-pox-generation-and-clock): resolve the live PoX contract (PoX-5, not `.pox-4`); the allowance name follows your contract's Clarity version.
- [A21](references/patterns.md#a21-reward-weights-and-ownership-across-cycles): settle historical rewards before changing balance, delegation or signer manager.
- [A22](references/patterns.md#a22-async-withdrawal-state-vs-synchronous-success): an accepted withdrawal request is not settlement; track requests and pending liabilities.
- [A23](references/patterns.md#a23-canonical-bitcoin-identifiers-and-replay-state): one canonical byte order per Bitcoin outpoint; migrate replay state across upgrades.

### Payouts, state and guards

- [A24](references/patterns.md#a24-automatic-rewards-and-aggregate-postconditions): postconditions bound gross sender outflow, not receipts; enforce minimum output on-chain.
- [A25](references/patterns.md#a25-stale-tuples-and-incomplete-caches): `map-set` of an old tuple erases newer fields; block-height caches miss same-block changes.
- [A26](references/patterns.md#a26-packed-registries-hide-capacity-and-identity-errors): shift counts wrap modulo 128; bound bitmap IDs before shifting.
- [A27](references/patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows): zero-amount and self transfers return errors that abort a `try!` flow; skip those legs.
- [A28](references/patterns.md#a28-let-bindings-run-before-the-bodys-guards): `let` bindings run before the body's `asserts!`; guard first, then compute.
- [A29](references/patterns.md#a29-first-deposit-and-donation-share-inflation): virtual shares and assets in both directions (or dead shares, or internally tracked assets), reject 0-share mints, take `min-shares`.

## Read when needed

- [Versions](../epochs/SKILL.md): exact allowance, clock and keyword boundaries.
- [Model corrections](../epochs/SKILL.md#recall-corrections): authority/rollback errors.
- Read [references/authorization.md](references/authorization.md) when downstream contracts need the user's `tx-sender` ([sender preservation](references/authorization.md#sender-preservation): guard `(asserts! (is-eq contract-caller tx-sender) ERR)` at the entry) or code accepts signatures ([signed authorizations](references/authorization.md#signed-authorizations)).
- Read [references/state-and-accounting.md](references/state-and-accounting.md) when code merges stored tuples, caches values, packs registries, zips lists, keeps lending or reward ledgers, or disables assets.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `stacks-core-release`: [10474cdec9](https://github.com/stacks-network/stacks-core/tree/10474cdec9f9c0bdf05841b58cffc89cdad87a9b).
- `openzeppelin-contracts`: [b7f748eae2](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/b7f748eae2341b9e8e8f85cf966e94476813d168).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
