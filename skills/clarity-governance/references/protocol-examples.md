# Governance protocol examples

Upstream and protocol-specific detail for [clarity-governance](../../clarity-governance/SKILL.md).

## Proposal-contract DAO

- Upstream uses legacy `as-contract`, `block-height` and older Clarinet configuration. Adapt to the target version/epoch; its block-to-day estimates and console commands are historical examples.
- Upstream `execute(proposal, sender)` invokes the proposal trait's `execute(principal) -> (response bool uint)` in the DAO's sending context and records execution by proposal principal. Sources: [core](https://github.com/MarvinJanssen/executor-dao/blob/4676718828455a694a6593d251cb2e968f346c8c/contracts/executor-dao.clar), [proposal trait](https://github.com/MarvinJanssen/executor-dao/blob/4676718828455a694a6593d251cb2e968f346c8c/contracts/traits/proposal-trait.clar), [extensions](https://github.com/MarvinJanssen/executor-dao/tree/4676718828455a694a6593d251cb2e968f346c8c/contracts/extensions).

### Zest v2 adaptation

- Use Zest as an implementation example of this architecture. Its ABI, multisig policy and upgrade controls are not ExecutorDAO defaults.
- Pinned flow: register the proposal principal with `dao-multisig.propose` → collect approvals → satisfy expiry/timelock rules → `execute(id, script)` → `dao-executor.execute-proposal(script)` → proposal `execute`.
- Zest's proposal `execute` takes no arguments; do not substitute upstream's sender-argument trait.
- `execute` binds `contract-of script` to the stored principal and marks the proposal executed before the external call. Propagated failure must roll back this state with the failed operation.
- The proposer counts as an initial approval. Verify duplicate approvals, removed signers and the relationship between stored approvals and the current threshold.
- Its timelock uses `stacks-block-time`. A separate implementation update has its own delay and second execution step.
- The executor intentionally uses `as-contract?` with broad asset authority. This is a privileged governance trust boundary; do not copy it into an ordinary user adapter.
- A proposal may intentionally rely on inherited executor `tx-sender` at downstream admin gates. Trace the whole call graph instead of replacing every check with `contract-caller`.
- Verify deployed proposal source, successful deployment, exact roles, action invariants, maximum costs and emitted configuration events before approval.

Sources: [Zest DAO contracts](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/dao), [mainnet initialization proposal](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/proposals/mainnet/v0-init.clar).

## Granite action governance

- Pinned Granite exposes `initiate-proposal-to-*`, `approve`, `deny`, `close` and `execute`; exact arguments differ by action.
- Granite uses `stacks-block-height` for `expires-at` and `execute-at`. Comments estimating days from four-second blocks are approximations, not time guarantees.
- Guardians pause a market at once with [`guardian-pause-market`](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/contracts/governance-v1.clar). Actions in the `time-locked` map wait `TIME_LOCKED_PERIOD` (`u21600` blocks); market unpause and guardian removal are not in it, so those proposals execute on approval.

Sources: [Granite governance](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/contracts/governance-v1.clar), [meta-governance](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/contracts/meta-governance-v1.clar), [governance tests](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/tests/governance.test.ts).

## Hermetica hBTC example

Sources: [HQ](https://github.com/hermetica-fi/hermetica-contracts/blob/5e13e431f69dd840fe297791fa2a73d9993a27e0/mainnet/contracts/hbtc/protocol/hq-v1.clar), [state](https://github.com/hermetica-fi/hermetica-contracts/blob/5e13e431f69dd840fe297791fa2a73d9993a27e0/mainnet/contracts/hbtc/protocol/state-v1.clar). Check the [current repository](https://github.com/hermetica-fi/hermetica-contracts) and deployed source before integration.

| Change | Request/cancel | Completion |
|---|---|---|
| Owner | Current owner | Named nominee calls `claim-owner` after maturity |
| Timelock duration | Current owner | Anyone calls `confirm-new-timelock` after maturity |
| Guardian/trader/rewarder/manager/fee-setter/protocol role | Current owner | Anyone confirms the stored add/remove request after maturity |
| Staged state parameters, assets and external integrations | Current owner | Anyone confirms the stored request after maturity; some fees also have an execution window |

- hBTC gates administrative authority through `contract-caller`. Pending entries bind action type, target and values; confirmation cannot substitute a new payload.
- Deadlines use `stacks-block-time` in seconds. The current delay is captured when scheduling, including a change to the delay itself. Changing the delay does not rewrite existing deadlines.
- HQ allows one pending owner/duration change; role/state maps reject a second request for the same key. Cancel before replacing. Map confirmation deletes the request; repeat execution fails.
- Owner cancellation does not require the delay to expire. Owner handoff does not automatically invalidate other pending requests: define whether these survive and who must cancel them.
- Test permissionless confirmation (it executes only previously authorized data) as an intentional negative control during audits.
- Direct actions remain: owner protocol toggles, guardian disable, deposit caps and some fee/settings updates. Inventory actual setters rather than assuming every change is delayed.
- A contract nominee must have an executable route that makes it the immediate caller of `claim-owner`; `is-standard` accepts contract principals too.
- Older [USDh HQ](https://github.com/hermetica-fi/hermetica-contracts/blob/5e13e431f69dd840fe297791fa2a73d9993a27e0/mainnet/contracts/usdh/protocol/hq-v1.clar) differs: owner requests and activates after a burn-height delay, using `tx-sender`. Do not apply hBTC's nominee-claim semantics to it.
