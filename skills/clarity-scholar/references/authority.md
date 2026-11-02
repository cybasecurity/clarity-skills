# Authority, traits and fixed dependencies

Privileged-call, custody and dependency rules for [clarity-scholar](../../clarity-scholar/SKILL.md#authority-traits-and-dependencies).

## Authority and execution context

- `is-standard` accepts network-compatible contract principals too. It cannot enforce a non-contract administrator policy. When policy requires a current-network account, check the decoded optional contract name:

```clarity
(define-read-only (is-local-account (who principal))
	(match (principal-destruct? who) parts (is-none (get name parts)) failure false))

(define-read-only (is-local-contract (who principal))
	(match (principal-destruct? who) parts (is-some (get name parts)) failure false))
```

- `is-local-account` accepts native multisig accounts and rejects contract principals and other-network accounts. It proves neither key control nor signing ability.
- `is-local-contract` instead requires a current-network contract principal. Neither helper proves deployment, source identity or role authorization. Apply it only when that restriction is intended; governance contracts can be valid administrators under other policies.
- `tx-sender` = origin of the transaction (or the contract inside `as-contract?`); `contract-caller` = the immediate caller.
  - Admin checks should use `contract-caller` so an admin who calls a malicious contract does not lend it admin rights. Exception: under an ExecutorDAO-style core, proposals reach setters with `tx-sender` = the DAO and `contract-caller` = the proposal, so those setters check `tx-sender` against the DAO ([governance](../../clarity-governance/SKILL.md#proposal-contract-dao)).
  - User-facing "my funds" APIs often use `tx-sender` deliberately so routers can act for users; apply [wallet outflow bounds and on-chain receipt checks](../../clarity-wallets/SKILL.md#post-conditions).
- When downstream calls need the user's sender context, authenticate the public entry point without switching it: see [user entry points and phishing](../../clarity-security/references/authorization.md#sender-preservation). A sender/caller equality guard deliberately rejects unscoped intermediary contracts.
- Capture actors in `let` before `as-contract?`; inside it both become the contract.
- `current-contract` (Clarity 4+) is the contract's own principal. Do not use `(as-contract tx-sender)` for that in new code.
- `as-contract?` (Clarity 4+) takes explicit allowances: `with-stx`, `with-ft`, `with-nft`, `with-stacking` (Clarity 4–5; `with-staking` from Clarity 6), `with-pox` (Clarity 6+, no amount, for position-changing PoX calls such as `unstake`) and `with-all-assets-unsafe`.
  - Allowance expressions are evaluated before the body. **No** body expression may be a response: wrap each call in `try!`/`unwrap!`.
  - Violations revert the body and return `(err index)` (`u128` = asset with no allowance), so always `try!` or check its result.

```clarity
;; id: bounded-payout
;; Contract must already hold the STX. Admin authorization uses contract-caller.

(define-constant ERR_NOT_OWNER (err u1002))

(define-data-var owner principal tx-sender)

(define-public (pay-stx (amount uint) (recipient principal))
	(begin
		(asserts! (is-eq contract-caller (var-get owner)) ERR_NOT_OWNER)
		(as-contract? ((with-stx amount)) (try! (stx-transfer? amount tx-sender recipient)))))
```

- For FTs the allowance names the token contract **and** its `define-fungible-token` name: `(with-ft 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token "sbtc-token" amount)`.
- A wrapper that moves native STX behind a SIP-010 interface needs `with-stx`, not `with-ft`.
- `ft-transfer?` already checks balance, zero amount and `sender == recipient`; avoid duplicating those checks unless custom errors are required. It does **not** reject a user transferring to `current-contract`. Keep distinct custody/escrow policy guards and explicit sender authorization.
- Focused authority snippets here omit handoff endpoints; a complete protocol needs a reachable authority handoff ([two-step ownership](../../clarity-governance/SKILL.md#two-step-ownership) or a DAO path) unless administration is deliberately immutable.

## Traits and dynamic calls

- Define small traits; reference them with `use-trait` and take them as **arguments**.
- A contract cannot call a principal it read from storage. Callers pass a trait value, and you check it against what you stored:

```clarity
;; id: trait-allowlist

(define-trait price-source ((get-price () (response uint uint))))

(define-constant ERR_NOT_OWNER (err u1200))
(define-constant ERR_UNKNOWN_SOURCE (err u1201))

(define-data-var owner principal tx-sender)
(define-data-var approved-source principal tx-sender)

(define-public (set-source (source principal))
	(begin
		(asserts! (is-eq contract-caller (var-get owner)) ERR_NOT_OWNER)
		(ok (var-set approved-source source))))

(define-public (read-price (source <price-source>))
	(begin
		;; Bind the exact role identity; dispatch below checks the invoked method.
		(asserts! (is-eq (contract-of source) (var-get approved-source)) ERR_UNKNOWN_SOURCE)
		(contract-call? source get-price)))
```

- `impl-trait` only asks the analyzer to check signatures. It proves nothing about behavior.
- Where the trait check happens depends on where the value comes from. A value supplied at run time (a transaction argument, a forwarded value, or one inside a list, optional or tuple) is checked only for the function called, when it is called; no `impl-trait` is needed. A contract literal anywhere in source, and `impl-trait`, are checked against the whole trait at deployment. A node's mempool checks transaction arguments against the whole trait (in any list, only the first element), so a partial mock that passes in simnet is rejected at broadcast unless it sits later in a list ([bad trait arguments](../../clarity-testing/references/troubleshooting.md#errors-from-a-bad-trait-argument)).
- Re-entering a function that is still executing aborts the transaction, but a callback may call a *different* public function of the same contract: guard the state those functions read ([callback guards](../../clarity-security/references/pitfalls.md#callback-guards)).
- Keep separate allowlists per role (asset vs oracle vs strategy) so a contract approved for one role cannot be passed in another.

## Fixed contract addresses

- Put supported fixed dependencies last among constants, e.g. `(define-constant USDCX 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx)`. An alias selects an immutable dependency; it is not an upgrade setter.
- Calls through contract-principal constants require Clarity 2+ and execution epoch 3.4+; in earlier epochs they pass analysis but fail at run time. On the node they also fail in top-level (deployment-time) expressions, although simnet runs them.
- In read-only code, analysis rejects calls through a constant ("detected a writing operation"), even for a read-only target and through a private helper ([read-only checker](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/analysis/read_only_checker/mod.rs)). Keep the literal principal there; compile the exact graph.
- Clarinet 3.26.0's dependency detector can miss trait-argument dependencies behind constant call targets. Retain explicit literal targets/arguments where needed; regenerate and inspect the graph rather than inserting dummy calls or silently patching order.
- Aliases can reduce repeated source bytes, but add stored constant data and lookup work; a once-used alias costs more. Measure all five cost dimensions; see [optimizer](../../clarity-optimizer/SKILL.md#repeated-reads-and-address-constants).
