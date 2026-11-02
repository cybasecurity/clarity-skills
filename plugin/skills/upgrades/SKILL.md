---
name: upgrades
description: "Make a Clarity protocol upgradable or migrate a deployed one: stable custody with replaceable logic, registries, timelocked cutovers, state migration. Use for upgrades, v2 logic, proxies or migrations."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Upgrades

Preserve asset identity, authoritative accounting and users' enforceable claims across immutable contract versions.

Writing or changing contract code: also load `clarity:scholar` and `clarity:security`, and finish with the [build checklist](../start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- **A deployed contract cannot be made upgradable in place:** Clarity has no proxy or `delegatecall`, and code and storage are fixed per principal. "Make my contract upgradable" means deploying a new state contract plus a replaceable logic contract and moving users over, or accepting immutability. Follow [make a contract upgradable](#make-a-contract-upgradable).
- **Bind activation to the exact staged candidate:** The recommended default takes it as `(target <logic-trait>)`, calls a readiness method on it before the delay starts (a contract without the method aborts the schedule, since runtime trait checks cannot be caught; one built for another state contract returns an error), and stages `(contract-of target)` with its source/configuration identity and scope. Activation compares the exact staged principal after the [timelock](#timelocked-cutover) and rechecks compatibility; no alternate setter may bypass the delay. A `principal`-typed registry or setter is also valid when it stages the exact principal behind the same delay and reviewers verify the candidate's deployed source and ABI during it; it only loses the early readiness check.
- Deploying v2 creates a new principal and storage. A registry change neither copies state/custody nor rewrites literal calls or constants.
- Stable custody alone is insufficient: shares, debt, indexes, queues and fees must remain authoritative and compatible, or need migration too. The stable contracts themselves remain immutable.
- Traits specify interfaces, not authorization. `contract-of` only returns the principal, and dispatch checks at most the method it calls. Bind the exact approved principal, then verify deployed source/ABI and funded operations before retiring old logic. See [trait checks](../security/SKILL.md#calls-traits-recursion).

## Workflow

1. Design first: apply [durable state and replaceable logic](#durable-state-and-replaceable-logic) and the [migration rules](references/migration.md). Record replaceable logic, immutable dependencies, asset identity, authoritative state and every role/setter.
2. Rehearse the exact staged graph with populated old state, working successor operations and user exits ([rehearsal assertions](#rehearsal-assertions)). Transfer operational roles before cutover and prove the revoked deployer stays revoked. Use the existing project's public test tooling and preserve regression coverage. Update existing fixtures or deployment expectations only when the intended graph change requires it; explain the change and run the affected suite. Keep authorization, accounting and rollback assertions intact; fix implementation regressions instead of deleting, skipping or weakening tests. Leave explicitly frozen tests unchanged and report any conflict. Add new lifecycle cases for the upgrade.
3. Write the release files (Clarinet plan or release script) into the project, then read them back. Reconcile state, and record which cutover steps can resume after a partial run and what cannot be rolled back.
4. Check the release files against the [release plan rules](#release-plan): explicit schedule and activation calls after the publish, and reviewed source hashes to compare during the delay. Reading a plan does not replace step 2.

## Durable state and replaceable logic

- For protocols planning upgrades, keep native FT/NFT definitions in a stable contract (the state contract or a dedicated token contract beside it), never in a logic contract, and custody/accounting in the state contract. Replace logic contracts, routers or strategies through explicit permissions.
- Define the native asset identity as contract principal plus token name. Moving `define-fungible-token` creates a different asset even if name, symbol and decimals match. A forwarding facade is not the asset: allowances and post-conditions must name the defining contract ([ledger split](references/migration.md#split-a-token-ledger-from-its-logic)).
- Give each logic contract only required mint, burn, state-write or transfer powers. Check the immediate caller at privileged boundaries; bind dynamic trait arguments to approved principals. See [authority](../security/SKILL.md).
- A registry that lets governance authorize arbitrary withdrawals or minting gives governance those powers. A trait or timelock does not remove that trust.
- Keep conservation, withdrawal reservations and other permanent safety rules in the stable layer where feasible. Replacing the logic contract cannot repair an immutable bug there; design an explicit, authorized migration/exit route where required.
- Keep storage schema, units, asset IDs and read APIs compatible across logic versions. A new logic contract must understand existing state before it is enabled.
- Do not add a mutable target to every dependency by default. Stable static dependencies are simpler; a target stored as `principal` is not itself a callable trait reference. Use a checked trait parameter for dynamic calls, or let replaceable logic contracts call the state contract directly.
- A two-step account-owner acceptance flow needs an executable acceptance route when the new owner is a contract; see [two-step ownership](../governance/SKILL.md#two-step-ownership).
- Protocol layouts that separate state from logic: [source examples](references/source-examples.md#source-examples).

## Make a contract upgradable

Build the layout in this order. Pass the step 8 rehearsal before deploying to mainnet or moving any user.

1. Decide what stays durable: asset definitions, custody, the authoritative ledgers (balances, shares, debt, indexes, queues, accrued fees) and permanent safety rules such as conservation and withdrawal reservations ([durable state](#durable-state-and-replaceable-logic)). Rules that may change, such as pricing, fee rates, limits and strategies, become replaceable logic. For a deployed contract, either keep it immutable and fix issues by migration, or deploy this layout and move its users (step 7). Whatever stays in logic is lost or migrated at every replacement; whatever goes into the state contract can never be fixed.
2. Write the state contract with the switch from steps 4 to 6 in it. Deploy it before any logic contract and never redeploy it.
   - It holds custody and the authoritative ledgers, and exposes only narrow privileged methods, such as taking a deposit, paying out or writing one record. Gate each on `(is-eq contract-caller (var-get logic))`: a `tx-sender` gate would trust every contract in the user's call path.
   - Assets move inside it, so replacing logic moves nothing. `tx-sender` is still the user there, so it pulls deposits directly and pays out of its own custody inside `as-contract?`.
   - Native `ft-transfer?` and `ft-burn?` check neither `tx-sender` nor `contract-caller` ([native operations](../assets/SKILL.md#native-operations)). A method that moves any holder's balance hands that power to every logic contract governance ever activates.
   - It defines the tokens, or a stable token contract beside it does. That token contract's mint and burn accept only the active logic: it reads the state contract's `logic`, or activation sets its minter. A minter setter of its own is a second switch that can skip the delay or leave the old logic minting.
   - If holders or other contracts can transfer a token, its SIP-010 functions, `get-total-supply` included, live in the defining contract. Allowances and post-conditions name that contract, and a token defined in a logic contract changes identity with every version ([ledger split](references/migration.md#split-a-token-ledger-from-its-logic)).
3. Put the business rules in versioned logic contracts. Each version is a new principal that calls the state contract by static `contract-call?`, so the state contract must exist first. Each also answers a readiness probe naming the state contract it was built for (`get-state-contract`), so a candidate built for another state contract is refused before the delay starts. Users call the active logic contract for protocol actions such as deposits and withdrawals; transfers of an open token still go to its defining contract. Assets or records a logic contract holds stay at its principal when it is replaced, and the next version cannot reach them. A router in front calls the logic contract and is never the trusted caller itself, or the staged switch stops covering what it calls.
4. Store the active logic and one staged change in the state contract: `logic` as a `principal` that starts as the deployer (`tx-sender`), and `pending` as `{ target, at }`, with read-only getters for UIs, indexers and tests. Or use `logic` as `(optional principal)`, `none` until bootstrap, and gate on `(is-eq (some contract-caller) (var-get logic))`. Restaging overwrites `pending` with a fresh `at`: a target that inherits an earlier `at` skips the delay.
5. Change logic only through governance: schedule, then activate once the [timelock](#timelocked-cutover) has passed. Schedule takes `(target <logic-trait>)`, probes it before the delay starts and stores `(contract-of target)` with `at` = `stacks-block-time` plus the delay. Activate requires that same principal once `at` has passed, probes again, sets `logic` and clears `pending`. Cancel drops it. Any other setter, or activating a principal other than the staged one, bypasses the delay. Compare governance with `contract-caller` for a multisig that calls directly; an ExecutorDAO-style DAO runs proposals with `tx-sender` = the DAO, so compare `tx-sender` there. Replace governance itself behind the same delay, after rehearsing that the new principal can call these functions: a wrong one leaves nobody able to change the state contract.
6. Bootstrap the first logic contract once, before any deposit: a one-shot init (governance only, refused once a logic contract is set) with the same probe and no delay, since nothing is at stake yet. The check compares `logic` with a `DEPLOYER` constant set to `tx-sender` at deploy, or uses `is-none` for the optional form. An init that can run again is an instant switch around the timelock. Until bootstrap the deployer passes the logic gate and can write records that survive bootstrap. That is acceptable only while the deployer is governance, which could install any logic through the init anyway, so bootstrap before handing governance over. When governance starts as another principal, such as a DAO, use the optional form.
7. Move users off an existing deployment. It keeps its code, custody and ledger, and a new contract gains no access to them. Users withdraw and re-deposit (a borrower repays first), or the old contract's own authority moves assets while a one-shot, caller-gated, duplicate-safe import registers each position, debts included; close import authority afterwards ([migration](references/migration.md)). A replayable import credits claims twice, and collateral imported without its debt can be withdrawn free.
8. Rehearse the switch with funded state: deposit through v1, publish v2 later, schedule it, fail an early activation, pass the delay, activate, then prove v1 is rejected while balances and exits work through v2. Also reject a second init, an unauthorized scheduler, an unrelated contract and a logic contract built for another state contract ([rehearsal assertions](#rehearsal-assertions)). An empty-state test passes even when v2 cannot read v1's records.

Worked example with names, error codes, the staged-switch fragment and the test sequence: [upgradable vault](references/vault-example.md).

## When replacement requires migration

Before moving state, custody or token claims to a new contract, read [references/migration.md](references/migration.md): the token approaches (version chain, pause and migrate, holder swap), the ledger-split rule and the state checklist.

- **Same state contract and ledger:** change authorized logic; preserve all state and native asset identity. Update callers pinned to old facades and test their transfer semantics/postconditions.
- **New custody or state:** import records, indexes and reservations, then transfer assets through reachable old-contract authority. Fresh deployment does not grant access to another principal's holdings/maps.
- **New token ledger:** define conversion, consume old claims exactly once, and reconcile both versions until migration completes. Native `ft-burn?`, `ft-mint?` and `ft-transfer?` accept only a token the calling contract defines. The new contract therefore calls the old version's own burn as an approved `contract-caller`, or each holder converts through a transfer the old version gives them ([approaches](references/migration.md#choose-an-approach)). See [legacy-token compatibility](references/migration.md#legacy-token-compatibility).
- **New trait version:** old literal trait references remain bound. Preserve the old ABI through an adapter or migrate its callers; test actual language/epoch compatibility with [epochs](../epochs/SKILL.md).

## Timelocked cutover

- Recommend a delay before installing new code. Cover implementation pointers, trusted-registry entries, mint/burn/logic roles, migration targets/sources and equivalent grants that can replace behavior indirectly.
- Bind the staged action to its target, parameters, relevant source/configuration identity, activation time and proposal/request ID. Replacing a pending target must start a fresh delay; execute only the approved action.
- Prevent bypass through an alternate direct setter, a new upgrader role, timelock reduction or an unrestricted executor. Apply the same delay to security-relevant delay reductions, or document the explicit exception.
- Use `stacks-block-time` seconds in Clarity 4+ for wall-clock delays; [older clocks](../epochs/SKILL.md) need explicit semantics. A delay's length is protocol policy: recommend at least 48 hours (172800 s) for a custodial vault, longer when users need more time to exit; document any shorter choice.
- Allow cancellation according to policy; recheck compatibility, permissions and dependent constraints at execution. Activation must not rely solely on checks made when scheduling.
- Keep pausing an [immediate action](../governance/SKILL.md#immediate-actions) that cannot install code. Immediate installation of arbitrary code is a timelock bypass to disclose.
- A timelock provides notice, not a guaranteed exit: withdrawals may be locked or illiquid. Evaluate users' actual exit time and liquidity when selecting the delay.
- Use [governance transitions](../governance/SKILL.md#signer-and-proposal-transitions) for pending approvals and membership changes, and [immediate actions](../governance/SKILL.md#immediate-actions) for pause and cancellation.

## Rehearsal assertions

- Seed old state with debt, unclaimed fees/rewards, queued exits, partial approvals and third-party holders. Execute the real governance/caller chain through [deployment](../deployment/SKILL.md).
- Check unauthorized source/target, a malicious trait-compatible replacement, before/exact/after timelock, replaced requests, duplicate imports, ID gaps/collisions and late failure rollback.
- Prove the new logic contract can operate on old records and users can repay, claim and exit. Test pending requests created before cutover and calls arriving during each staged transition.
- Check aggregate backing, old/new supply conservation, unmigrated balance inclusion, no duplicate redemption, reserved liquidity, old-role revocation and required legacy permissions.
- Exercise future creation, not only imported records. Update SDKs, routers, indexers and contract templates pinned to the old version; verify canonical deployment/source and emitted migration events.
- When owner or manager roles transfer before cutover, assert that former role holders lose authority and pending nominations follow the declared policy.

## Release plan

Keep the project's release format: a [Clarinet plan](../deployment/SKILL.md#clarinet-plans) or a [release script](../deployment/SKILL.md#release-script-rules). Order, Clarity versions and fees follow [deployment](../deployment/SKILL.md).

- **Publishing v2 switches nothing:** The state contract keeps using v1 until governance schedules v2 and, after the delay, activates it. List both calls as explicit steps after v2's publish, sent through the real governance caller chain; under a multisig or DAO they are proposals ([governance](../governance/SKILL.md)). A plan that only publishes is not an upgrade.
- **The delay splits the release:** A Clarinet plan has no step that waits, and the schedule call needs v2 already published. Publish and schedule in one run, then activate in a later run once the delay has passed on chain.
- **Hash the reviewed bytes:** Record the SHA-256 of each contract's exact source as published, after any remapping. The staged principal holds whatever was published, not necessarily the reviewed file. During the delay, hash the candidate's deployed source and compare ([deployed source check](../deployment/SKILL.md#verify-the-release)); on a mismatch, cancel the staged change.

## Design or migrate

- Name what stays immutable; a policy switch does not imply replaceable execution or accounting.
- For ongoing upgrades, rehearse a fresh v3 published after funded v1; initial contracts cannot statically call unpublished replacements. An immutable v1/v2 allowlist or dispatcher supports only its precommitted generations; state that limit when intentional.
- Trace cutover calls with `contract-caller`: a timelock calling an owner-only setter needs that capability; the owner's `tx-sender` does not grant it.
- Do not recreate a token merely to replace its logic contract.
- Use the [migration and cutover checks](references/migration.md) for old balances, liabilities, fees, pending exits, replay protection and contract-held replacement tokens.
- Define old entrypoints and privileges after cutover. Remove obsolete mint/borrow/admin powers while retaining explicitly required repayment, claim or conversion paths.
- Use [governance](../governance/SKILL.md) for approval, signer transitions and owner handoff; [deployment](../deployment/SKILL.md) for release artifacts, initialization and transaction orchestration; [testing](../testing/SKILL.md) for typed regressions.
- Inspect upstream and deployed sources before reusing a pattern, starting from the [source examples](references/source-examples.md). Repository code and historical audit outcomes do not prove a migration ran on-chain or that today's roles match.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`. Pins do not renew deployment or mutable-state evidence.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `zest-v1`: [3564bc3890](https://github.com/Zest-Protocol/zest-contracts/tree/3564bc38906e464ec4de774122bb9bbaee20ddc6).
- `hermetica`: [5e13e431f6](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0).
- `stackingdao`: [125c73dc10](https://github.com/StackingDAO/stackingdao-smart-contracts/tree/125c73dc109988730156f4d0434ff01654480fc7).
- `stackingdao-legacy`: [a8d7d2a2dc](https://github.com/StackingDAO/contracts/tree/a8d7d2a2dcffa0b4759bc8411f9d1369fc44b736).
- `bitflow-dlmm`: [b4d3694c86](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0).
