# Upgradable vault example

A worked example of [make a contract upgradable](../../clarity-upgrades/SKILL.md#make-a-contract-upgradable): an STX vault split into the state contract `vault-state` and the logic contracts `vault-logic-vN`.

Keep an existing project's contract, function and error names; the rules hold whatever the names.

## Runbook

A deployed vault cannot be upgraded in place: its code and storage are fixed at its principal, and there is no proxy. Pick one:

- **Accept immutability:** keep the existing vault and fix issues by migration.
- **Build the upgradable layout and migrate users to it:** deploy `vault-state` plus `vault-logic-v1`, then move the old vault's users and assets across (step 4).

1. Inventory the old vault: asset(s), share ledger, debt/indexes, fees, queues, roles ([state checklist](migration.md#state-custody-and-authority)).
2. Split it. The state contract `vault-state` holds custody and the share token (`define-fungible-token` lives here, never in a logic contract), exposes only narrow methods over them, and is never redeployed. The logic contract `vault-logic-vN` holds the business rules (pricing, fees, limits) and reaches state only through those methods, which check `contract-caller` is the active logic contract. Users deposit and withdraw through the logic contract; share transfers, if enabled, call `vault-state` directly.
3. The state contract stores the active `logic` and a staged `pending` change with an activation time. Only `governance` (a multisig or DAO contract, see [governance](../../clarity-governance/SKILL.md)) can stage and activate, using `contract-caller` (a multisig contract calling directly). If `governance` is an ExecutorDAO-style DAO, proposals arrive with `tx-sender` = the DAO and `contract-caller` = the proposal; compare `tx-sender` instead. Activation must name the staged target and wait the delay (48 hours for a custodial vault).
4. Move existing users: either users withdraw from the old vault and deposit into the new one, or the old vault's authority transfers assets while a one-shot import (caller-gated, duplicate-safe) registers shares. Close import authority when done. For the first route see [holder swap](migration.md#holder-swap): it needs no privileged burn of holders' shares. For the second see [pause and migrate](migration.md#pause-and-migrate) and the [state checklist](migration.md#state-custody-and-authority).
5. Rehearse a cutover to logic v2 with funded state: early activation fails, the old logic contract is rejected afterwards, user shares and exits still work.

## State contract: vault-state

What it stores:

- `vault-state` is deployed once; only its `logic` pointer changes. It defines the share token (`define-fungible-token vault-share`) and holds custody.
- `governance` (data var, initialized to the deployer's `tx-sender`), `logic` `(optional principal)` (`none` until bootstrap) and `pending` `(optional { target: principal, at: uint })`. Read-only `get-logic`, `get-pending` and `get-shares (who)` serve UIs, indexers and tests.
- Or type `logic` as a `principal` that starts as the deployer ([step 4](../../clarity-upgrades/SKILL.md#make-a-contract-upgradable)). Then no `some` wraps `contract-caller` or the new target, and `init-logic` compares `logic` with a `DEPLOYER` constant instead of using `is-none`.
- The readiness trait a candidate must answer before it can be scheduled: `(define-trait logic-trait ((get-state-contract () (response principal uint))))`.
- Shares move only through `credit` and `debit`. If shares are to be transferable, implement [SIP-010](../../clarity-sip-compliance/SKILL.md#sip-010-fungible-tokens) (`transfer`, `get-balance`, `get-total-supply` and the metadata getters) in `vault-state` next to `define-fungible-token vault-share`; logic contracts still reach shares only through `credit` and `debit`. Allowances and post-conditions name the asset `<deployer>.vault-state::vault-share`: a facade or logic contract offered as the token matches nothing there, and replacing it breaks callers pinned to it ([ledger split](migration.md#split-a-token-ledger-from-its-logic)).
- A contract redeeming through the logic contract allows `(with-ft .vault-state "vault-share" shares)`, since `debit` burns its shares; one from another deployer spells out the full principal, because `.vault-state` resolves against its own deployer. A user's post-conditions bound the STX sent on deposit and the shares burned on withdrawal. Under `Deny` a withdrawal also needs one on the STX `vault-state` pays out, since every sending principal is checked ([coverage](../../clarity-wallets/SKILL.md#choose-coverage-deliberately)). None covers minted shares.

Who may change it:

- Stage, activate and cancel: only governance, `(is-eq contract-caller (var-get governance))` (under an ExecutorDAO-style DAO compare `tx-sender`, as in runbook step 3). Replace `governance` only through a governance proposal that waits out the [timelock](../../clarity-governance/SKILL.md#immediate-actions), like a code change. Rehearse that the new governance can call these functions first: a wrong principal leaves no one able to change the state contract. Without a setter `governance` stays the deployer, so add one behind the same delay before handing the state contract to a multisig or DAO.
- Ledger methods: only the active logic contract, `(is-eq (some contract-caller) (var-get logic))`. A router or UI in front of the logic contracts must not be the principal the state contract trusts; it trusts the one active logic contract as `contract-caller`.

The staged transition:

- `init-logic (target <logic-trait>)`: one-shot bootstrap of the first logic contract (governance only; `ERR_ALREADY_INIT` once one is set); no delay because nothing is deposited yet; probed like any candidate.
- `schedule-logic (target <logic-trait>)`: governance only. Readiness probe before the delay starts: `(asserts! (is-eq (try! (contract-call? target get-state-contract)) current-contract) ERR_NOT_READY)`. A contract without `get-state-contract` aborts the call (a runtime trait check cannot be caught); a logic contract built for another state contract returns `ERR_NOT_READY`. The probe checks one method, not the whole ABI: test the candidate's operations before scheduling. Stores `{ target: (contract-of target), at: (+ stacks-block-time DELAY_SECONDS) }`; restaging restarts the delay.
- `activate-logic (target <logic-trait>)`: requires a pending change (`ERR_NO_PENDING`), governance, `(contract-of target)` equal to the staged target (`ERR_TARGET_MISMATCH`), `stacks-block-time` at or past `at` (`ERR_TIMELOCK`), and rechecks readiness at execution; then sets `logic` and clears `pending`.
- `cancel-logic`: governance only; drops the staged change.
- `DELAY_SECONDS u172800` (48 hours; Clarity 4+ `stacks-block-time` is in seconds). Print an event for init, schedule and activation. Example error codes: `u90001` unauthorized, `u90002` no pending, `u90003` timelock, `u90004` target mismatch, `u90005` already initialized, `u90006` not ready.
- Ledger: `credit` and `debit` move funds in the state contract itself. Inside it `tx-sender` is still the user and `contract-caller` is the logic contract, so `credit` pulls the deposit from `tx-sender` and `debit` pays out of the state contract's custody inside `as-contract?` with an exact `with-stx` allowance (`with-ft` in a token vault). Assets never pass through the logic contract, so replacing it moves nothing. Here shares mint and burn 1:1 with STX. In a priced vault the logic contract passes the share amount and `vault-state` bounds it by custody and supply, so a faulty logic version cannot mint unbacked shares or pay out more than they are worth ([share inflation](../../clarity-security/references/patterns.md#a29-first-deposit-and-donation-share-inflation)).

```clarity
;; fragment: staged switch in vault-state (event prints omitted)
(define-public (schedule-logic (target <logic-trait>))
  (let ((at (+ stacks-block-time DELAY_SECONDS)))
    (try! (only-governance))
    (asserts! (is-eq (try! (contract-call? target get-state-contract)) current-contract) ERR_NOT_READY)
    (ok (var-set pending (some { target: (contract-of target), at: at })))))
(define-public (activate-logic (target <logic-trait>))
  (let ((staged (unwrap! (var-get pending) ERR_NO_PENDING)))
    (try! (only-governance))
    (asserts! (is-eq (contract-of target) (get target staged)) ERR_TARGET_MISMATCH)
    (asserts! (>= stacks-block-time (get at staged)) ERR_TIMELOCK)
    (asserts! (is-eq (try! (contract-call? target get-state-contract)) current-contract) ERR_NOT_READY)
    (var-set logic (some (contract-of target)))
    (ok (var-set pending none))))
```

## Logic contract: vault-logic-vN

- A separate contract that users call to deposit and withdraw; each version is a new principal. It calls the state contract by static `contract-call?` (`(contract-call? .vault-state credit amount)`, `(contract-call? .vault-state debit amount)`), so the state contract must be deployed first.
- It answers the probe with `(define-read-only (get-state-contract) (ok .vault-state))`, can expose `(define-read-only (get-version) u1)`, and rejects a zero deposit (`ERR_ZERO_AMOUNT`, `u91001`) before calling the state contract.
- Put tokens and custody in the stable contract from the first deployment whenever upgrades are planned; they cannot be separated later.

## Tests

Assert this sequence: an unrelated contract rejected at init, a second init rejected after the first (`ERR_ALREADY_INIT`), unauthorized scheduler rejected, an unrelated contract and a logic contract built for another state contract both rejected at scheduling, early activation rejected, mine past the delay, activation of a different target rejected, activation succeeds, old logic contract rejected, shares survive the switch.
