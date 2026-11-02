# Contract layout and style

Layout, formatting and branch-style rules for [clarity-scholar](../../clarity-scholar/SKILL.md#layout-and-style).

## Contract layout

- By default, put protocol-owned `define-trait` declarations in trait-only contracts under `contracts/traits/` or `contracts/<module>/traits/`, so a trait's identity does not depend on replaceable logic; keep an existing project's layout. Keep `use-trait` and `impl-trait` in their consumers/implementations; retain external dependency layouts. Inline `define-trait` in the snippets here is single-file illustration.
- By default, keep mock contracts in `contracts/mock/` and test suites in `tests/`; follow the project's existing layout.
- Directories do not namespace contracts. Set filesystem paths in `Clarinet.toml`, reference traits by contract/trait name (`.vault-traits.vault-trait`), and preserve those names when moving files. Update affected tooling paths and regenerate clients/plans as needed.
- By default, use this declaration order for new contracts unless the project already differs: header comments → `use-trait`/`impl-trait` → error constants → other constants → address constants → FT/NFT declarations → data vars → maps → public functions → read-only functions → private functions → deployment initialization.
- Keep FT/NFT declarations at top level, outside functions. This layout is a project convention, not a VM visibility-order requirement.
- For distinct logical modules in one contract, repeat this internal layout per labeled module. These are not separately deployed inner contracts. Preserve deliberate initialization/dependency ordering and upstream formatting.
- Keep function comments attached and separate definitions using the project's formatting scheme.
- Upstream layout example: [sBTC token](https://github.com/stacks-sbtc/sbtc/blob/eb507946c65bdf4dde72469ea8cb2481fa276a17/contracts/contracts/sbtc-token.clar). Trait folders: [Granite's shared traits](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b/contracts/traits), [Hermetica's module traits](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0/mainnet/contracts/hbtc/traits).
- Rules for deposit and withdraw functions (the fragment below shows withdraw):
  - Bind the actor once (`(let ((owner tx-sender)) ...)`) **before** any context switch.
  - Pull deposits into the contract with `(stx-transfer? amount owner current-contract)`.
  - Withdraw in this order: guard the balance, write the new balance and total, make the outflow bounded by `with-stx` with its response propagated by `try!`, then print an event carrying the actor and amount.
  - A direct native-STX outflow has no callback and rolls back on failure. For external calls, ordering can still matter: Clarity blocks reentry into an active function, but another function of the same contract may be called and observe intermediate state.

```clarity
;; fragment
;; Withdraw recorded STX using a bounded contract-owned transfer.
(define-public (withdraw (amount uint))
	(let ((owner tx-sender) (balance (default-to u0 (map-get? deposits owner))))
		(asserts! (<= amount balance) ERR_INSUFFICIENT)
		(map-set deposits owner (- balance amount))
		(var-set total-deposits (- (var-get total-deposits) amount))
		(try! (as-contract? ((with-stx amount)) (try! (stx-transfer? amount tx-sender owner))))
		(print {event: "withdraw", owner: owner, amount: amount})
		(ok amount)))
```

## Formatting and function comments

- Preserve an existing project's formatter configuration and established style. For new or unconfigured projects, use Clarinet's default formatter without indentation/width overrides: `clarinet format --in-place`; validate with `clarinet format --check`.
- Format only project-owned code. If the manifest includes upstream/submodule contracts, target owned files with `--file PATH`; leave dependency and generated sources unchanged.
- Let the selected formatter determine indentation, line breaks and closing-parenthesis placement. Snippets here (tab-indented for compactness) illustrate semantics only; the formatter's output is authoritative.
- By default, put a `;;` summary immediately above every authored production public, read-only and private function, unless the project already differs. Aim for one short line: purpose plus relevant authority, units, bounds, timing or side effects. Avoid merely repeating the name.
- Keep comments accurate as behavior changes. Preserve useful security notes; use extra lines only when needed for clarity. Mock comments are optional; keep upstream/generated sources under their own documentation workflow.

## Tuple style

- Use brace tuples for new values **and types**, and convert legacy tuple forms when restyling; in a targeted fix, follow the surrounding code. Both spellings have the same tuple semantics; braces do not change field names, bounds or ABI.
- Legacy `(tuple (amount u1) (active true))` becomes `{amount: u1, active: true}`; type `(tuple (amount uint) (active bool))` becomes `{amount: uint, active: bool}` (example below).
- Convert tuple forms only. Function parameters `(amount uint)`, call arguments and `let` pairs `(name expression)` keep their parentheses.
- Preserve field expressions and their evaluation order, nested types, sequence bounds and optional/response wrappers. Do not turn a field into a function call or reorder side effects while restyling.
- Do not wrap a single value in a one-field tuple (Clarinet `unnecessary_tuple` lint) unless it is an argument of `merge`; use the plain value as the map key.

```clarity
;; id: brace-tuples
(define-map records principal {amount: uint, active: bool})

(define-public (store (row {amount: uint, active: bool}))
	(begin
		(map-set records tx-sender row)
		(ok {amount: (get amount row), active: (get active row)})))

(define-read-only (load (who principal))
	(map-get? records who))
```

## Switch-style dispatch

- Clarity has no `switch`/`cond`. Prefer a nested `if` chain for a small, fixed set of cases; align each case at the same indentation (`dispatch` below).
- Only the selected branch executes. Return an explicit error for unknown cases; keep branch return types compatible.
- Avoid dispatch via repeated `(asserts! (not case?) result)`: it returns `result` from the enclosing function when the case matches, including an `ok` result. It works, but disguises selection as failure handling and costs more runtime ([dispatch costs](../../clarity-optimizer/SKILL.md#switch-style-dispatch)).
- For many cases, measure worst-case depth and cost; a trait argument needs [role-specific identity checks](authority.md#traits-and-dynamic-calls), not a fabricated dynamic call from a stored principal.

```clarity
;; id: switch-dispatch
(define-constant ERR_UNKNOWN_ACTION (err u1100))

(define-public (dispatch (action uint))
	(if (is-eq action u1) (ok u10)
	(if (is-eq action u2) (ok u20)
	(if (is-eq action u3) (ok u30)
	ERR_UNKNOWN_ACTION))))
```

- Upstream examples: [Zest nested `if`](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/market/v0-8-market.clar#L186-L194), [Granite early-return dispatch](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/contracts/governance-v1.clar#L341-L360).
