---
name: clarity-scholar
description: "Write, build or refactor Clarity (.clar) contracts: syntax, types, responses, errors, traits, loops and layout. Use before writing or editing Clarity code, fixing compile errors, or answering how Clarity code behaves: what an expression returns, what aborts or rolls back, what the VM checks."
license: MIT
compatibility: "Optional: Python 3.10+ for scripts/lookup_function.py. Examples assume Clarinet 3.26.0 (Clarity 6 at epoch 4.0)."
allowed-tools: "Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/lookup_function.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Scholar

Make authority, units and failure paths explicit while preserving the requested behavior.

Writing or changing contract code: also load `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- `is-standard` checks network compatibility, not account versus contract. Unwrap `principal-destruct?` for the current network: its `name` is `some` for a contract principal and `none` for a standard account. `contract-of` takes a trait value and returns a principal, not an optional or a principal-kind check; see [authority checks](references/authority.md#authority-and-execution-context).
- Current time is `stacks-block-time` in Clarity 4+; previous-block timestamps lag execution.
- No `as-contract?` body expression may be response-typed. Handle its outer response and capture actors before switching context.
- `begin` rejects unchecked intermediate responses, but `let` bindings and response lists can hide errors.
- A fitting quotient does not prevent an intermediate uint128 multiplication from overflowing.
- Epoch changes can affect old contracts; retaining a language version does not preserve every historical feature.

## Write or refactor

1. `clarinet contract new NAME` (or `contracts new`) creates the contract and manifest entry. Clarinet 3.26.0 defaults to Clarity 6 / epoch 4.0; use an older version only for interoperability. Unscheduled epoch 4.1 rejects version-pinned deployments ([versions](../clarity-epochs/SKILL.md#current-network-and-versions)).
2. Follow [contract layout](references/style.md#contract-layout); run `clarinet check` until clean.
3. Format with the project's formatter if it has one; otherwise `clarinet format --in-place --file contracts/NAME.clar`, then `clarinet format --check` on the same files.
4. Add [Clarigen/Vitest tests](../clarity-testing/SKILL.md) for every public function and error path; run `npm test`. Clarigen is the default typed client; Clarinet remains the execution layer.

For changes to existing code:

- Check [language, epoch and tool support](../clarity-epochs/SKILL.md#version-specific-behavior). Preserve intended ABI, errors, assets, roles, invariants, dependencies and storage compatibility.
- For future logic replacement, prefer separate token ledgers and stable custody/accounting ([upgrade architecture](../clarity-upgrades/SKILL.md#durable-state-and-replaceable-logic)).
- Choose [failure behavior](#responses-choose-the-failure-behavior) deliberately; propagate atomic-batch errors, define rounding and bound intermediates.
- Preserve [tuple snapshots, cache validity and registry invariants](../clarity-security/references/state-and-accounting.md#state-and-accounting); locals do not refresh after writes.
- Add a persistent lock only for a reachable callback that can break an invariant ([criteria](../clarity-security/references/pitfalls.md#callback-guards)).
- Wallets constrain aggregate sends; contracts enforce intended receipts ([postconditions](../clarity-wallets/SKILL.md#post-conditions)).
- Apply [native pitfalls](../clarity-security/SKILL.md#native-behavior-pitfalls) and [recall corrections](../clarity-epochs/SKILL.md#recall-corrections) to their stated targets. Standards require the normative SIP and deployed trait, not invented ERC-20 approvals or vault APIs.
- Separate style from behavior changes; test observable behavior. Shorter expressions are not necessarily cheaper: measure all five cost dimensions.

## Syntax

Examples in this skill run on Clarity 4–6 at epoch 4.0 unless marked. Omit their `;; id:` labels in project code. Check [version-specific behavior](../clarity-epochs/SKILL.md#version-specific-behavior) before porting; look up exact signatures with the [lookup script](#exact-language-lookup).

Read [syntax tables and a complete contract](references/syntax.md) for literals, definitions, control flow and trait syntax. Keep these distinctions:

- `u42` is `uint`, `42` is `int`; keywords such as `tx-sender` take no `()`.
- Definitions are top-level; a function has one body expression; public functions return a response.
- Optional `match` takes four arguments, response `match` five; `fold` reducers take element, then accumulator.

### Unlike general Lisp

- `(function arg ...)` calls; atoms stand alone. Parentheses do not merely group values.
- No `eval`, macros, lambdas, first-class functions, recursion or unbounded loops. `map`/`filter`/`fold` require literal function names.
- Parameters/storage declare types; expression/return types are inferred before deploy. Branch types must agree, lists are homogeneous and sequences are bounded. Integers are 128-bit, and overflow aborts.
- `'` introduces a principal; `;;` starts a comment. No `//`, quote/backquote code forms, JavaScript property access, mutation operators, `return` or semicolon separators.
- Conditions must be booleans, not `none`, responses or integers. `if` needs both branches; `let` supports several body expressions. Tuple labels and definition names are literal identifiers, not strings.

### Names that no longer exist

A name outside its version range fails analysis on deploy.

- `as-contract` (Clarity 1–3): use `as-contract?` with explicit allowances (Clarity 4+); `current-contract` for the contract's own principal.
- `block-height` (Clarity 1–2): `stacks-block-height` (every Stacks block) or `tenure-height` (Clarity 3+); `burn-block-height` for Bitcoin.
- `get-block-info?` (Clarity 1–2): `get-stacks-block-info?`, `get-tenure-info?` (Clarity 3+); `stacks-block-time` for the current block (Clarity 4+).
- `at-block` (Clarity 1–4): nothing equivalent; existing callers throw from epoch 3.4.
- `with-stacking` (Clarity 4–5): `with-staking` (Clarity 6+). Clarity 6 also adds `with-pox`, with no amount, for position-changing PoX calls such as `unstake`; it does not cover locking.

## Layout and style

For new files or restyling, read [style and layout](references/style.md): trait-only contracts, mocks in `contracts/mock/`, declaration order and the withdraw example. Use the project formatter (else `clarinet format` on owned files), a `;;` summary above each function, brace tuples for values/types, and nested `if` dispatch ending in an explicit error.

## Names, units, errors

- Use kebab-case for functions, parameters and storage names; **new constants use `SCREAMING_SNAKE_CASE`**, including errors and address aliases; in an existing project, keep its constant style. Current Clarinet's [constant-case lint](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarity-repl/src/analysis/lints/case_const.rs) flags hyphens (a style note by default).
- Parameters and `let` bindings cannot shadow contract-level variables/constants. Use distinct names; unrelated functions may reuse parameter names.
- Natives whose names end in `?` return an optional or response (`map-get?`, `stx-transfer?`), except `contract-call?`, which returns what the callee returns. Follow that convention for your own helpers, and use `get-...`/`is-...` for getters and booleans.
- Put units in names: `amount-ustx`, `price-e8`, `rate-bps`, `expires-at` (seconds), `unlock-burn-height`. `uint` has no implicit scale.
- Define a commented `ERR_...` constant per distinct failure, so callers and tests can tell failures apart (for example missing versus unauthorized). Prefer a higher local range such as `u1000`–`u1099` to avoid native/boot collisions. Ranges are not globally reserved: document module prefixes, distinguish forwarded errors, preserve public ABIs and standard conventions (SIP-010 transfer codes `u1`–`u4`). A forwarded `(err u1)` can originate in any callee.
- Public functions must return a response. Keep each response branch type compatible across paths; the analyzer must infer a common type. Trait return bounds are maxima, not exact lengths; see [compatible return types](../clarity-sip-compliance/SKILL.md#sip-010-fungible-tokens).
- Default privileged roles to data vars initialized with `tx-sender`, with authenticated setters and events naming actor, previous and new authority. Use [reachable ownership handoff](../clarity-governance/SKILL.md#two-step-ownership); immutable administration requires an explicit design choice.
- Remove redundant single-expression `begin`, nested `let` and `match` branches that only rebuild the original response. [The book's style suggestions](https://book.clarity-lang.org/ch13-01-coding-style.html) explain these; measure cost claims against current tooling.

## Responses: choose the failure behavior

| Need | Use |
|---|---|
| Propagate a response-returning callee's error unchanged | `(try! (contract-call? ...))` |
| Replace a missing value / error with a local error | `(unwrap! (map-get? m k) ERR_NOT_FOUND)` |
| Guard a precondition | `(asserts! cond ERR_...)` |
| Act differently on success and failure | `(match resp v (...) e (...))` |
| A value whose absence is a bug you have proved impossible | `unwrap-panic` (aborts the whole transaction, no error code) |

- Bind a plain tuple/value returned by a read-only function directly; `try!` requires a response or optional. Check the ABI before unwrapping.
- `try!`, `unwrap!`, `asserts!` return from the **enclosing function**. Inside a `fold`/`map` callback that means the callback, not your public function.
- A public function that returns `err` rolls back all of its writes and events; one that catches a callee error and returns `ok` keeps its own writes.
- The analyzer rejects an unchecked response used as an intermediate `begin` expression, but not one bound in `let`, returned inside a list from `map`, or discarded via `match`. Do not rely on it to catch ignored failures.

## Guard before computing

- `let` evaluates bindings in order, before its body, so an assertion in the body is too late for later bindings. Bind the guard first, as `remaining` below does: failure returns `ERR_INSUFFICIENT` before the subtraction; computing `left` first would abort on underflow, bypassing a later guard.
- The guard binding is `true` on success; no `try!` is needed. Use descriptive placeholders ending in `_`, such as `amount-check_` or `claims-capacity-ok_`, to mark intentionally unused results for the default linter. Avoid opaque `p1`/`p2` names.
- Put authorization, range and denominator checks before dependent arithmetic, writes or external calls. Validate the guard's own arithmetic too.
- A guard in a `fold`/`map` callback exits only that callback; [propagate batch failures](#iteration-without-loops).

```clarity
;; id: let-guard
(define-constant ERR_INSUFFICIENT (err u1100))

(define-read-only (remaining (balance uint) (amount uint))
	(let ((amount-check_ (asserts! (<= amount balance) ERR_INSUFFICIENT)) (left (- balance amount)))
		(ok left)))
```

- Upstream example: [Bitflow's bound check before a call](https://github.com/BitflowFinance/bitflow-dlmm/blob/b4d3694c863fb737574b2830acaa33a02f399bc0/clarity/contracts/dlmm-liquidity-router-v-1-1.clar#L151-L155).

## Iteration without loops

- No recursion, no `while`, no built-in `every`. Use bounded `fold` for an all-items predicate.
- Iterate over a bounded list with `map`, `filter` or `fold`. To repeat N times, fold over a constant index list.
- For filtering with per-call context, compare a pure context/output `fold` with a stored-helper `filter`: fewer reads can cost much more runtime ([cost tradeoff](../clarity-optimizer/SKILL.md#filtering-with-per-call-context)).
- For atomic batches, thread a response through `fold`; stop work after the first error:

```clarity
;; id: atomic-batch
(define-constant ERR_DUPLICATE (err u1001))

(define-map seen uint bool)

(define-public (record-many (ids (list 100 uint)))
	(fold record-one ids (ok true)))

(define-private (record-one (id uint) (prior (response bool uint)))
	(begin
		(try! prior)
		(asserts! (map-insert seen id true) ERR_DUPLICATE)
		(ok true)))
```

- A late duplicate returns `err`, so the public function rolls back the earlier insertions.
- `fold` still visits every element (it never breaks early): the `try! prior` makes later visits cheap no-ops.
- In contrast, `(ok (map do-thing items))` returns `ok` even when some items failed: it is a partial-success API, and the caller gets a list of responses.
- `map-insert` returns `false` (not an error) if the key exists; `map-set` silently overwrites. Use `map-insert` with an assert for create-once records (claims, nonces, IDs).
- `var-set` and `map-set` return write-success `true`, even when storing `false`; they do not return the stored value.
- Bound everything a user controls: list arguments (`(list 20 ...)`), buffers (`(buff 34)`), strings.
- Never grow an unbounded list in a data var (`append` + `as-max-len?` caps it, and each read costs the whole list). Use a map keyed by an incrementing index instead.

## Authority, traits and dependencies

Read [references/authority.md](references/authority.md) before writing privileged functions, `as-contract?` custody, trait calls or address constants:

- [Authority and execution context](references/authority.md#authority-and-execution-context): admin checks use `contract-caller` (DAO-executed setters check `tx-sender` against the DAO); capture actors before `as-contract?`; list explicit allowances (`with-ft` names contract and token) and `try!` the result; `current-contract` is the contract's own principal.
- [Traits and dynamic calls](references/authority.md#traits-and-dynamic-calls): take traits as arguments; check `contract-of` against a stored principal per role; `impl-trait` checks signatures only.
- Trait checks have distinct stages ([VM rules](../clarity-security/SKILL.md#calls-traits-recursion)):
  - Contract literals in source and `impl-trait`: whole-trait check at deployment.
  - Node mempool: whole-trait check on transaction arguments (in any list, only the first element). Simnet has no mempool, so a partial mock that works there can still be rejected by a node.
  - Runtime trait values, including transaction arguments and forwarded/nested values: check the invoked method at dispatch; no `impl-trait` required.
  - A trait-typed parameter inside a router trait: nested trait **identity** matters at dispatch. A byte-identical local copy can deploy and pass `clarinet check`, then fail with `BadTraitImplementation` on the real call. Use the protocol's trait or a static call.
- [Fixed contract addresses](references/authority.md#fixed-contract-addresses): calls through address constants need epoch 3.4+, and fail at top level (simnet misses this) and in read-only paths.

## Arithmetic

- `uint`/`int` are 128-bit. Overflow, underflow and division by zero **abort** the transaction (no wrap, no error code).
- Order operations for precision and bound the intermediate. Floor and ceil helpers, each guarding the denominator first; the ceil form avoids the `(n + d - 1)` overflow at the top of the range:

```clarity
;; id: mul-div
(define-constant ERR_ZERO_DENOMINATOR (err u1300))

;; floor(a*b/d): a*b must fit in 128 bits, or this aborts.
(define-read-only (mul-div-down (a uint) (b uint) (d uint))
	(begin
		(asserts! (> d u0) ERR_ZERO_DENOMINATOR)
		(ok (/ (* a b) d))))

;; ceil(a*b/d) without the (n + d - 1) overflow at the top of the range.
(define-read-only (mul-div-up (a uint) (b uint) (d uint))
	(let ((denominator-check_ (asserts! (> d u0) ERR_ZERO_DENOMINATOR)) (n (* a b)))
		(ok (+ (/ n d) (if (> (mod n d) u0) u1 u0)))))
```

- Choose rounding per operation to preserve solvency. Typical vaults floor deposit shares/redeem assets and ceil withdrawal shares/mint assets; verify debt conventions separately.
- `(/ (* a b) d)` and `(* (/ a d) b)` differ: dividing first truncates.
- `pow` overflows quickly; prefer fixed-point helpers with documented bounds.
- Clarity has no 256-bit type: a Solidity `mulDiv` does not port unchanged.
- Read [additive range checks](references/arithmetic-and-time.md#additive-range-checks) when guarding a cap: prefer `amount + used <= cap` once operands are bounded.

## Time

- Clarity 4+: `stacks-block-time` is the current block's timestamp in seconds.
- `(get-stacks-block-info? time (- stacks-block-height u1))` is the **previous** block's time. Older versions have no current timestamp at all.
- Handle zero elapsed time: calls within one Stacks block share its timestamp. Distinct Stacks blocks must have increasing timestamps.
- Read [time detail](references/arithmetic-and-time.md#time) when writing deadlines, PoX schedules or [a configurable period length](references/arithmetic-and-time.md#epochs-whose-length-can-change).

## Strings, buffers, serialization

- `(buff 34)` / `(string-ascii 32)` are maxima. Check exact lengths with `len` before slicing or indexing. `slice?`, `element-at?` and `as-max-len?` return optionals.
- `concat` takes exactly two arguments before Clarity 6. `as-max-len?` is a checked cast, not truncation.
- `buff-to-uint-be`/`-le` and `buff-to-int-be`/`-le` accept at most 16 bytes. Short inputs are **zero-padded, not sign-extended**: `(buff-to-int-be 0xffffffff)` returns `4294967295`, not `-1` ([conversion rules](references/functions.md#buff-to-int-be)).
- `to-consensus-buff?` gives the canonical serialization for hashing and SIP-018 signing; apply [signature validation and replay rules](../clarity-security/references/authorization.md#signed-authorizations) to the chosen scheme. Tuple fields serialize in sorted key order, not declaration order.
- `int-to-ascii` (C2+), `to-ascii?` (C4+) for display strings. Strings cost bytes on every read and write.

## Events

- `print` one tuple per state-changing action, after the change succeeds: `{event: "withdraw", owner: ..., amount: ..., id: ...}`.
- Keep names and fields stable; indexers depend on them.
- Prints are discarded when their context rolls back: a transaction whose top-level result is `err`, a public function that returns `err` (even when its caller handles the error), a violated `as-contract?` or `restrict-assets?` scope and any read-only function, even one that a public function calls. Print from the public function or a private helper it calls.
- Anyone can print an identical tuple from another contract, so consumers must filter by emitting contract.

## Upgradability

- Code and literal dependency principals are immutable.
- Authorized registries/DAOs (`is-dao-or-extension`) or trait arguments checked against stored role principals can select replaceable logic. State and custody do not move automatically.
- Use [upgrades](../clarity-upgrades/SKILL.md) for scope, timelocks, state/token migrations and overlapping versions.

## Read-only functions

- `define-read-only` cannot write, can only call other read-only functions (including read-only functions of other contracts by literal principal), and cannot make dynamic trait calls.
- Read-only code must name another contract by its literal principal. A call through a contract-principal constant fails analysis with "detected a writing operation", even when the target is read-only and even through a private helper. In Clarity 2+, public functions and the private helpers they call can use the constant from epoch 3.4.
- Off-chain calls via `/v2/contracts/call-read` are free; on-chain they still consume budget.
- A read-only getter of an external contract can still lie: it is code, not a proof.

## Exact language lookup

- Run `python3 <scholar>/scripts/lookup_function.py 'as-contract?'` (`<scholar>` is this skill's directory; exact name, quoted). It prints the matching rows of the [version-specific behavior](../clarity-epochs/SKILL.md#version-specific-behavior) table before the quoted VM text; apply them first. Unknown names exit 2: search the index in `references/functions.md`. Avoid loading the whole catalog.
- Before using an unfamiliar form, check its signature and example this way. Compile for the target version and fix diagnostics before claiming completion.
- Read [references/lookup.md](references/lookup.md) for known VM-doc discrepancies and sources to cross-check, and to study [deployed contracts](references/lookup.md#deployed-contracts-as-study-material).

## References

- [Functions](references/functions.md): generated VM catalog, indexed by name, version and signature. Prefer the lookup script; topic references are linked where needed above.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarity-deployed-contracts`: [45a7af6028](https://github.com/boomcrypto/clarity-deployed-contracts/tree/45a7af60288ae72eb36592a9c428e41034c04367).
- `bitflow-dlmm`: [b4d3694c86](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `granite`: [2d44a2df94](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b).
- `hermetica`: [5e13e431f6](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0).
- `sbtc`: [eb507946c6](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
- `bips`: [5aadddb511](https://github.com/bitcoin/bips/tree/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793).
