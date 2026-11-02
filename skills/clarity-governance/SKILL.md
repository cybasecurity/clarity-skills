---
name: clarity-governance
description: "Governance and admin control for Clarity protocols on Stacks: DAO proposals, multisigs, timelocks and 2-step ownership. Use for DAOs, proposals, multisigs, admin roles or owner transfer."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Governance

Separate the representation of an approved action from the mechanism that authorizes it.

Writing or changing contract code: also load `clarity-scholar` and `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- A native Stacks multisig is a standard principal with transaction-level signature rules; it is not a Clarity multisig contract.
- A trait-compatible proposal is executable code, not evidence of an approved or safe action.
- Current membership, historical approvals, threshold changes and timelocks must have explicit semantics.
- A timelock in Stacks blocks is not an exact wall-clock duration.

## Default decision rule

- **Protocol holding user funds:** contract-owned M-of-N approval plus a timelock on sensitive changes: code and upgrades, roles, and anything touching prices, oracles, tokens or custody; the protocol defines what else counts. Recommend at least 24 hours for operational changes and at least 48 hours (172800 s) for upgrades and custodial changes, counted from the approval that makes the action executable; lengthen it when users need more time to exit. It must also have an instant pause that a guardian or keeper can trigger with no delay; pausing and cancelling a pending proposal are the only [immediate actions](#immediate-actions).
- **Fixed, short action list:** [action-based governance](#action-based-governance) or timelocked setters (set fee, change role, switch logic contract).
- **Open-ended actions:** the [proposal-contract executor](#proposal-contract-dao), with the multisig and timelock as its extension.
- **Native multisig:** good for deployer and operational keys (deployment, pause). As a long-term owner, pair it with an on-chain timelock or staged administration and plan an ownership transfer for every signer change: changing keys or threshold derives a new principal, and native authorization adds no delay ([comparison](#contract-multisig-versus-native-multisig)).
- **Token voting:** only when holder voting is a product requirement. Never count votes from current-block balances, or a flash loan can borrow, vote and repay in one transaction; use balances recorded before the proposal opened.
- **Ownership of any single role:** nominate then accept, with events; for roles that move funds or report value, acceptance completes only after the protocol timelock ([two-step ownership](#two-step-ownership)).

## Choose and implement

- Provide role setters and [reachable ownership handoff](#two-step-ownership): prefer nominee acceptance for accounts; contract nominees need an executable acceptance/admin route or an explicitly authorized direct handoff.
- For account-only nominees, check `(is-none (get name (unwrap! (principal-destruct? p) ERR)))` as in the fragment below; `is-standard` also accepts contracts. Allow contract administrators when the policy requires them.
- Bind target contracts, assets, parameters, proposal identity, network/domain and replay state to the approval.
- Trace signer → governance → executor → proposal → target. Distinguish `tx-sender`, `contract-caller` and deliberate executor context.
- Define proposal creation, duplicate approval handling, eligibility, threshold snapshots/current rules, cancellation, expiry, execution-once and emergency powers.
- Confirm actual deployed proposal source and successful deployment. A source payload in a failed transaction is insufficient ([A05](../clarity-security/references/patterns.md#a05-approval-based-on-the-wrong-deployment)).
- Treat broad executor asset authority as an explicit governance trust decision, never a generic integration workaround.
- Test direct and routed signers, malicious proposals, wrong-role traits, repeated execution, removed members, threshold changes, exact timelock boundaries, failed legs and emitted events ([test cases](#governance-test-cases)).
- Rehearse initialization and authority handoff through the deployment workflow. Test fixtures must not become production signer/threshold defaults.

## Proposal-contract DAO

ExecutorDAO pattern ([Marvin Janssen's ExecutorDAO](https://github.com/MarvinJanssen/executor-dao)):

- Each action is a new immutable contract implementing the proposal trait's `execute` function. The core executes proposals and tracks enabled extensions; extensions supply submission, voting, emergency execution and other policies. The core does not mandate one voting or multisig model.
- A proposal can coordinate several privileged operations atomically when they fit one transaction's budget. New action combinations need not be pre-enumerated, but approved code gets the executor's effective authority.
- The privileged check accepts the DAO sending context or an enabled immediate extension caller. Enabling an extension grants it the DAO's authority.
- Read [upstream notes](references/protocol-examples.md#proposal-contract-dao) before reusing ExecutorDAO source (legacy `as-contract`, `block-height`), and the [Zest v2 adaptation](references/protocol-examples.md#zest-v2-adaptation) before integrating or reviewing Zest.

Minimal Clarity 4 layout: a core, a multisig-plus-timelock extension and one proposal contract per action. Deploy the core and extension, then the first proposal, then call `construct` once.

Core (`dao-core`):

- Proposal trait: `(define-trait proposal-trait ((execute (principal) (response bool uint))))`.
- State: `executive` (data var, the deployer until `construct`), `executed-proposals` (proposal principal → `stacks-block-height` of execution), `extensions` (principal → bool). Read-only `is-extension` and `executed-at`.
- `is-self-or-extension`: `(or (is-eq tx-sender current-contract) (is-extension contract-caller))`, the DAO itself (inside a proposal) or an enabled extension.
- `run` executes a proposal once (`map-insert` into `executed-proposals`, else `ERR_ALREADY_EXECUTED`), prints, then calls its `execute` inside `as-contract?`, so the DAO is `tx-sender` and `contract-caller` of the proposal. `with-all-assets-unsafe` gives proposals the DAO's full asset authority: use `()` if they never move the core's assets.
- `set-extension (extension, enabled)` is reachable only through a proposal or another extension, and prints. `execute (proposal, sender)` is the entry point for extensions. `construct (proposal)` is the one-time bootstrap by the deployer: it hands `executive` to `current-contract` and runs the first proposal, which installs the extensions.

```clarity
;; fragment: ExecutorDAO-style core, adapted to Clarity 4
(define-trait proposal-trait ((execute (principal) (response bool uint))))
;; The DAO itself (inside a proposal) or an enabled extension.
(define-private (is-self-or-extension)
  (ok (asserts! (or (is-eq tx-sender current-contract) (is-extension contract-caller)) ERR_UNAUTHORIZED)))
;; Run a proposal once, with the DAO as tx-sender and contract-caller of the proposal.
(define-private (run (proposal <proposal-trait>) (sender principal))
  (begin
    (asserts! (map-insert executed-proposals (contract-of proposal) stacks-block-height) ERR_ALREADY_EXECUTED)
    (as-contract? ((with-all-assets-unsafe)) ;; narrow this when proposals never move assets
      (try! (contract-call? proposal execute sender)))))
;; construct: (asserts! (is-eq tx-sender (var-get executive)) ERR_UNAUTHORIZED),
;; then (var-set executive current-contract) and run the first proposal.
```

Multisig extension (`dao-multisig`):

- State: `members` (principal → bool), `proposals` (id → `{ script, mature-at, approvals, executed }`, `mature-at` `u0` = not yet approved), `approved` (`{ id, member }` → bool), `next-id`. Example policy: `THRESHOLD u2`, `DELAY_SECONDS u172800` (48 hours, the upgrade minimum above).
- `set-member` checks `(is-eq tx-sender .dao-core)`: membership changes arrive as DAO proposals, where `tx-sender` is the DAO (a deliberate executor context). Everything else uses `contract-caller`.
- `propose (script <proposal-trait>)`: a member registers the proposal principal; the proposer counts as the first approval.
- `approve (id)`: member only, not executed, one approval per member (`map-insert` into `approved`, else `ERR_ALREADY_APPROVED`). The approval that reaches the threshold starts the review window.
- `execute (id, script)`: anyone may execute a matured, approved proposal. The stored script principal is binding; it marks the proposal executed before calling `(contract-call? .dao-core execute script tx-sender)`.
- `cancel (id)`: members approve a cancellation the same way; the approval that reaches the threshold closes the pending proposal at once ([immediate actions](#immediate-actions)).
- Changing `THRESHOLD`, the delay or the member set policy is itself a proposal (or a new extension), subject to the same delay.

```clarity
;; fragment: multisig extension
;; approve: reject a duplicate, then the approval that reaches THRESHOLD starts the delay
(asserts! (map-insert approved { id: id, member: contract-caller } true) ERR_ALREADY_APPROVED)
(merge p { approvals: approvals,
  mature-at: (if (and (is-eq (get mature-at p) u0) (>= approvals THRESHOLD)) (+ stacks-block-time DELAY_SECONDS) (get mature-at p)) })
;; execute: anyone, once, with the stored script, after the delay
(define-public (execute (id uint) (script <proposal-trait>))
  (let ((p (unwrap! (map-get? proposals id) ERR_NOT_FOUND)))
    (asserts! (is-eq (contract-of script) (get script p)) ERR_WRONG_SCRIPT)
    (asserts! (not (get executed p)) ERR_EXECUTED)
    (asserts! (and (>= (get approvals p) THRESHOLD) (> (get mature-at p) u0)) ERR_THRESHOLD)
    (asserts! (>= stacks-block-time (get mature-at p)) ERR_TIMELOCK)
    (map-set proposals id (merge p { executed: true }))
    (contract-call? .dao-core execute script tx-sender)))
```

Proposal contracts:

- A proposal is an ordinary contract implementing the trait, deployed, approved and executed once. The first one installs the multisig; later proposals call your protocol's setters.
- Those setters must accept the DAO as caller: `tx-sender` is the DAO and `contract-caller` is the proposal contract, so downstream admin checks compare `tx-sender` with the DAO.

```clarity
;; fragment: installs the multisig; add every signer (at least THRESHOLD)
(impl-trait .dao-core.proposal-trait)
(define-public (execute (sender principal))
  (begin
    (try! (contract-call? .dao-core set-extension .dao-multisig true))
    (try! (contract-call? .dao-multisig set-member sender true))
    (ok true)))
```

- Test: non-member propose, duplicate approval, below threshold, early execution, wrong script, repeat execution, removed member.

## Action-based governance

- A persistent contract stores proposal IDs, action codes, typed parameter data, approvals/denials, expiry and execution state. A dispatcher executes a finite set of supported operations when the selected threshold and timelock policy pass.
- This narrows the available actions and avoids a contract deployment per proposal. New action kinds can require a governance implementation change.
- Approval can immediately execute an eligible action or schedule it for later, depending on its configured timelock. Do not assume every approval is a pure vote.
- Proposal/member-count snapshots, current membership checks and threshold arithmetic must agree. Test member removal/addition, duplicate votes, small signer sets and threshold boundary rounding.
- Guardian pause roles differ from governance members ([immediate actions](#immediate-actions)).
- Bind proposal ID to nonce/action/parameters; test that one approved ID cannot be reused with different payloads.
- Read [Granite action governance](references/protocol-examples.md#granite-action-governance) before integrating or reviewing Granite.

## Contract multisig versus native multisig

| Property | Clarity contract multisig | Native Stacks multisig principal |
|---|---|---|
| Identity | `deployer.contract-name` | Standard address starting `SM` (mainnet) or `SN` (testnet) |
| Threshold enforcement | Contract code and stored membership/proposals | Transaction authorization signature condition |
| Approval flow | Often multiple approval transactions plus execution | Multiple signatures authorize one transaction origin |
| Policies | Can implement timelocks, role limits, cancellation, spend rules | Native authorization alone supplies no DAO timelock or action policy |
| Signer changes | Contract can retain identity while changing membership | Threshold or key-set changes derive a different principal; plan authority migration |
| Call context | Immediate caller can be the multisig/executor contract; sender depends on context scopes | The signed transaction origin is the native multisig principal; routing still changes immediate caller |
| Deployments | A contract is not a top-level transaction signer; it governs calls by execution | A native multisig can sign a deployment, producing contracts under its `SM` or `SN` address |

- `is-standard` does not identify single-sig versus multisig or contract identity. `SM`/`SN` are P2SH version bytes, also used by P2SH-wrapped single keys: `(get version (unwrap-panic (principal-destruct? p)))` of `0x14` (mainnet) or `0x15` (testnet) shows a script-hash address, not proof of a multisig. Inspect intended principal type and verified authorization design.
- Clarity does not expose the full native multisig's pubkey/signature configuration through the principal alone.
- A contract multisig can include a native multisig principal as a member; these layers then enforce distinct thresholds.
- Read [native multisig transactions](references/native-multisig.md#native-multisig-transactions) when building or signing one: every signer keeps the same public-key order and reviews the same payload; non-signing keys are appended with `appendOrigin`.

## Two-step ownership

- Initialize privileged roles in data vars, commonly `tx-sender` for the deployer. Provide authenticated replacement/removal as appropriate; immutable authority requires an explicit design reason.
- For standard-principal owners, prefer current-owner nomination followed by nominee acceptance. Test old-owner revocation and rejection of repeated acceptance.
- Contract nominees need a real authorized entry point that calls the target's acceptance function, so the nominee is the immediate caller of `accept-owner`. A simulated contract principal supplied as transaction sender does not prove reachability.
- If the intended contract cannot accept ownership, use an explicitly authorized direct contract-owner setter or extend its governance route. Verify it can perform later administration too.
- Restrict account-nomination/direct-contract setters to their intended principal kinds and networks with `principal-destruct?` (wrong-network principals fail there); `is-standard` does not distinguish these kinds.
- Use `contract-caller` for the owner and nominee checks, so a malicious intermediary cannot act through the owner's `tx-sender`. Under an ExecutorDAO-style owner the DAO arrives as `tx-sender`; compare that with the DAO as in [proposal contracts](#proposal-contract-dao).
- Clear stale nominations on completed handoff; let the owner cancel an unaccepted nomination. Emit actor, previous and new authority using the project's event schema. Test unauthorized calls, contract routes, replacement/cancellation policy and revocation.

```clarity
;; fragment: two-step ownership for a standard-account owner (owner, pending-owner data vars)
(define-public (nominate-owner (nominee principal))
  (let ((parts (unwrap! (principal-destruct? nominee) ERR_NOT_ACCOUNT)))
    (asserts! (is-eq contract-caller (var-get owner)) ERR_UNAUTHORIZED)
    (asserts! (is-none (get name parts)) ERR_NOT_ACCOUNT) ;; drop to allow contract nominees
    (print { event: "owner-nominated", owner: (var-get owner), nominee: nominee })
    (ok (var-set pending-owner (some nominee)))))
(define-public (accept-owner)
  (let ((previous (var-get owner)))
    (asserts! (is-eq (some contract-caller) (var-get pending-owner)) ERR_UNAUTHORIZED)
    (var-set owner contract-caller)
    (var-set pending-owner none)
    (print { event: "owner-changed", previous: previous, owner: contract-caller })
    (ok true)))
```

## Staged administration

- Prefer staged changes for sensitive authority/configuration: authorize and bind the payload, expose a review window, then execute the stored action.
- Separate two protections: a timelock provides time to react; nominee acceptance proves the new authority can act. Two calls by the same owner provide no independent approval.
- Changes outside the protocol's sensitive set need no staging.
- Permissionless confirmation executes previously authorized data; it does not grant permission to choose new settings.
- Reject unauthorized requests/cancellation, premature execution, mismatched payloads and repeated execution.
- Test cancellation followed by replacement, same-key duplicates, independent keys, and owner transfer with pending actions.
- Test nominee reachability and old-owner revocation through the real call chain; simnet sender strings do not prove wallet/multisig signing capability.
- Keep delay reductions subject to the existing delay and above the coded minimum. Test exact clock boundaries, the immediate actions and monitoring events.
- Recheck dependent constraints at execution or prove they remain invariant while requests are pending.
- Read the [Hermetica hBTC example](references/protocol-examples.md#hermetica-hbtc-example) for a worked request, delay and confirmation design, or before integrating Hermetica.

## Immediate actions

Two actions skip the timelock, because each can only stop something. Every other sensitive change waits for it, and its minimum delay is a constant in code that no proposal can lower.

- Guardian pause: guardians (or keepers) can only pause, and do it at once. Pair them with automated monitoring that triggers the pause, such as Hypernative. A compromised guardian can only pause: the protocol stays paused until governance replaces the guardian and unpauses, two timelocked proposals that run in parallel.
- Cancellation: the governing multisig closes any pending proposal as soon as its threshold approves. If an attacker reaches the threshold while the team still holds enough keys, the team cancels each malicious proposal during its delay, and users exit meanwhile.
- One multisig governs everything else through the timelock: damaging operations, guardian changes, member and threshold changes, and migration to a new multisig.
- Unpause through the timelock by default, at least 24 hours, so a malicious unpause can be cancelled. A faster unpause is the project's choice to disclose ([Granite](references/protocol-examples.md#granite-action-governance) unpauses on approval).
- Do not pause during a multisig compromise: users could not exit, and the team would have to cancel the attacker's proposals indefinitely. No design survives the guardians and the multisig compromised together; disclose that residual risk.
- Any other path around the delay (an urgent flag, emergency execution, an instant delay cut) is a timelock bypass: disclose it as a trust exception, and report it in reviews.

## Signer and proposal transitions

- Enforce unique members and a reachable, nonzero threshold at bootstrap and every update. Respect list/buffer capacities and any weighted-vote rules.
- Count approvals by signer identity, not signature count. A valid signer subset need not occupy the same list indexes as the full roster; each weight must come from the authorized roster.
- Specify whether pending proposals retain snapshot membership/thresholds or use current configuration. Test removal, re-addition, threshold changes and expiry before execution.
- Preserve action/parameter binding, execution-once state and cancellation through implementation changes. Test that authorized governance can actually reach every required setter through its complete call chain.
- Recheck dependent configuration at execution; another approved action may have changed it since scheduling.
- For contract replacement, state/custody migration and old-token compatibility, use [Clarity Upgrades](../clarity-upgrades/SKILL.md). Recommend timelocks for code upgrades and equivalent registry/role grants; pausing stays an [immediate action](#immediate-actions).

## Governance test cases

- Initialization exactly once by the intended authority; signer membership and threshold match the approved deployment policy.
- Missing/duplicate approval; expired/cancelled/already-executed proposal; wrong script principal or changed action data.
- Membership/threshold changes before execution; signer forwarding through an untrusted contract.
- Just before, at and after maturity/expiry with the actual clock.
- Guardian pauses at once and can do nothing else; cancellation at the threshold takes effect at once; unpause, guardian and member changes wait for the delay; a delay below the coded minimum is rejected.
- Failed middle action rolls back the intended transaction; separately submitted transactions remain independently committed.
- Narrow asset movement, expected admin events, preserved error provenance, post-upgrade replay protection and continuing control of treasury/registries.

## Read when needed

- [Versions](../clarity-epochs/SKILL.md): context scopes and clocks.
- [Security patterns](../clarity-security/SKILL.md#security-patterns-a01-a29): authority, role confusion and deployed-source evidence.
- [Protocol examples](references/protocol-examples.md) (ExecutorDAO upstream, Zest, Granite, Hermetica).

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`. Review dates do not renew live evidence.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `executor-dao`: [4676718828](https://github.com/MarvinJanssen/executor-dao/tree/4676718828455a694a6593d251cb2e968f346c8c).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `granite`: [2d44a2df94](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b).
- `hermetica`: [5e13e431f6](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
- `stacks-js-wallets`: [e6084a5214](https://github.com/stx-labs/stacks.js/tree/e6084a52140b2ad010a9d1a0f1b87d527c3a8870).
