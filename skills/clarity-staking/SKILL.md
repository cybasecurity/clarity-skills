---
name: clarity-staking
description: "Stack STX through PoX from Clarity: stake and unstake, signers, reward cycles, delegation, with-staking/with-pox allowances, liquid staking (stSTX). Use for contracts or tools that stake STX."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Staking

Keep protocol generation, burnchain clocks, signer rights and historical entitlements explicit.

Writing or changing contract code: also load `clarity-scholar` and `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- Use the word staking for PoX participation, but keep exact names: PoX-4 `stack-stx`, PoX-5 `stake` and `unstake` ([names by generation](#pox-generations)), and the protocol name Stacking DAO. Allowance names follow the Clarity version, not the PoX generation: a Clarity 4 or 5 contract stakes into PoX-5 with `with-stacking`.
- The newest PoX source file is not activation evidence. Mainnet uses PoX-5; resolve `/v2/pox` for the target.
- STX, stSTX, stSTXbtc, stBTC, sBTC and hBTC represent different assets and rights: distinguish them by principal, native asset identifier, decimals and economic rights; names are not identities.

## PoX generations

- Read the active PoX boot contract from `/v2/pox` (`contract_id`; mainnet: PoX-5), then its delegation, signer authorization, reward-cycle and unlock rules. Resolve boot identities with [system addresses](../clarity-system-integration/references/addresses.md).
- Mainnet: active `SP000000000000000000002Q6VF78.pox-5`. Epoch 4.0 deployed it at burn height 960,230, inside cycle 140, and cycle 141 is the first whose signer and reward set it controls. Cycles span 2,100 burn blocks with a 100-block prepare phase. Cycles and unlocks follow `burn-block-height`, not Stacks blocks or wall time.
- PoX-5's `SIGNER_SET_MIN_USTX` is 50,000 STX delegated to a signer for signer-set eligibility. It is not a universal minimum for each participant.

| Generation | Integration model |
|---|---|
| Legacy PoX-4 | `stack-stx`/delegation APIs, signer authorization IDs and Bitcoin reward addresses; miner rewards paid on Bitcoin |
| PoX-5 | `stake`/`stake-update`/`unstake`, registered signer managers/key grants, sBTC reward accounting and claims; Bitcoin withdrawal is a separate step |

| Concept | PoX-4 (legacy) | PoX-5 |
|---|---|---|
| Lock / delegate STX | `stack-stx`, `delegate-stx` (+ `delegate-stack-stx`, `stack-increase`) | `stake`, `stake-update` |
| Exit | lock expires at the cycle boundary | lock also expires at the cycle boundary; `unstake` (STX) moves the unlock to the next boundary, and `unstake-sbtc` withdraws bonded sBTC |

- An STX-only `unstake` schedules unlocking at a cycle boundary, rather than immediately transferring STX.
- PoX-5 also supports bonded STX with L1 BTC or custodied sBTC; use its specific bond/rollover/exit rules.
- PoX-5 has no PoX-4 authorization IDs, delegation expiry or Bitcoin reward addresses, and `pox-4` call shapes do not map onto it. From epoch 4.0 every `pox-4` call that is not read-only, including `delegate-stx` and `stack-stx`, aborts with a `DefunctPoxContract` runtime error ([locking dispatch](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/pox-locking/src/lib.rs#L169-L182)). PoX-5 has no `delegate-stx`: a staker joins a pool with `stake`, naming the pool's signer manager.
- Sources: [PoX-5 source](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/chainstate/stacks/boot/pox-5.clar), [SIP-045](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-045). Verify actual deployed source and activation before use.

## Allowances and postconditions

| Clarity version | Allowance for locking STX | Allowance for position changes |
|---|---|---|
| 4, 5 | `with-stacking amount` | none: an unstake-type call by the scope's owner makes `as-contract?` or `restrict-assets?` return `(err u128)`, unless `as-contract?` uses `with-all-assets-unsafe` |
| 6+ | `with-staking amount` (same allowance, renamed) | `with-pox` (no amount) covers `unstake`, `unstake-sbtc`, `update-bond-registration`, `announce-l1-early-exit` |

- Allowance amounts are **totals** the active PoX contract may lock, not increases: a stake update or `stack-increase` needs an allowance for the new total. A scope adds up the totals its calls record: a `stake` of 100 STX then an update to 110 STX in one scope needs an allowance of 210 STX.
- `with-pox` does not cover locking (that is `with-staking`). A call to a `with-pox` function counts even when it returns `(err ...)`, so omit the allowance to forbid touching the position inside a scope.
- `with-stx` and STX post-conditions see transfers and burns, never locks. Cover a lock or position change with the allowances above and the [transaction post-conditions](#transaction-post-conditions) below ([versions](../clarity-epochs/SKILL.md)).
- For reward-bearing token transfers, inspect whether hooks pay both endpoints or save entitlement for later claims. Apply [aggregate postcondition and reward-checkpoint checks](../clarity-wallets/SKILL.md#post-conditions); do not assume one transfer means one asset movement.

### Transaction post-conditions

Epoch 4.0 adds two transaction post-condition types for PoX-5 (SIP-045 section 3.4.3; the SDK and Ledger app label them SIP-044).

| Type | Builder (`@stacks/transactions` 7.6.0) | Covers |
|---|---|---|
| Staking `0x03` | `Pc.principal(p).willSendEq(total).ustxToLock()` or another `willSend*` comparator | the micro-STX lock that `stake`, `stake-update` or `register-for-bond` records for `p` |
| PoX `0x04` | `Pc.principal(p).willPerformPox()`, `.willNotPerformPox()` or `.mayPerformPox()` | `p` calling `unstake`, `unstake-sbtc`, `update-bond-registration` or `announce-l1-early-exit` |

- `Deny` aborts the transaction when a principal stakes or makes one of those calls without a condition of that type on it. `Originator` does so for the origin only, and `Allow` permits it. Listed conditions must pass in every mode.
- Abort reasons: `Post-condition check failure: <n> STX was staked by <principal> but not checked` (`<n>` in micro-STX) and `... <principal> performed a PoX action but it was not checked`. A failed condition reads `... on STX staked by <principal>: <amount> SentLe <staked>` (comparators print as `Sent*`, as for transfers) or `... on PoX action by <principal>: NotPerformed performed=true`.
- The staking amount is the total lock each call records, summed per principal over the transaction, not the increase. A `stake-update` adding 10 STX to 100 STX records 110 STX, an extension alone records the whole lock, and a `stake` of 100 STX then that update in one transaction records 210 STX. Use `willSendEq` for a known total and `willSendLte` for a cap.
- STX conditions count transfers and burns, never locks. On a stake, `willSendEq(amount).ustx()` fails (sent 0) and `willSendLte(amount).ustx()` leaves the stake unchecked. A PoX condition does not cover a stake, and a staking condition does not cover an unstake.
- The staking total and the PoX action both belong to the `tx-sender` of the call into pox-5. A PoX attempt counts even when pox-5 returns `(err ...)`, so `willPerformPox()` proves an attempt, not success: check the call result. `willNotPerformPox()` aborts even a failed attempt. If a calling contract then returns an err, the attempt rolls back with it.
- PoX-5 has no contract-caller allow list; SIP-045 relies on these conditions instead. Any contract the user calls can stake, update or unstake for the user, since the user stays `tx-sender`. In `Deny` mode, list only the intended action so that anything else aborts. In `Allow` mode, `willSendEq(0).ustxToLock()` and `willNotPerformPox()` on the user forbid any stake or PoX action by the user.
- Cover the other movements as usual. The staker sends sBTC into bond custody, and pox-5 itself sends sBTC refunds and `unstake-sbtc` payouts, so `Deny` mode also needs an FT condition on the pox-5 contract ([sBTC identity](../clarity-assets/SKILL.md#sbtc)). The signer manager's `validate-stake!` runs with the staker as `tx-sender`, so cover anything it moves. A contract acting on its own position needs the allowance above and, in `Deny` mode, a condition on the contract principal.
- Before epoch 4.0, nodes reject a transaction that carries either type (`Staking/Pox post-condition is not supported before Stacks 4.0`), so read `current_epoch` from the target's `/v2/pox`. `@stacks/transactions` 7.5.0 added the builders, and `postConditionToHex` and `Pc.fromHex` round-trip them. Connect 8.2.7 serializes them; 8.2.6 throws on these objects. Test the installed wallet and device ([Ledger notes](../clarity-wallets/references/ledger.md#other-confirmed-corner-cases)).
- Clarinet SDK 3.26.0 simnet enforces both types at epoch 4.0 with the same reasons and rejects them at earlier epochs. Pass the mode and conditions explicitly ([simulator traps](../clarity-environments/SKILL.md#simulator-traps)).

```ts
// fragment: PoX-5 stake-update in Deny mode (imports from @stacks/connect, @stacks/transactions)
// poxId: contract_id from /v2/pox; staked: get-staker-info amount-ustx, in micro-STX
const newTotal = staked + increase; // the node records the new total lock, not the increase
const { txid } = await request('stx_callContract', {
  contract: poxId, functionName: 'stake-update', // new and old manager, extra cycles, increase, calldata
  functionArgs: [Cl.principal(manager), Cl.principal(manager), Cl.uint(0), Cl.uint(increase), Cl.none()],
  network, address: staker, postConditionMode: 'deny',
  postConditions: [Pc.principal(staker).willSendEq(newTotal).ustxToLock()],
});
```

- An intended `unstake` in `Deny` mode takes `Pc.principal(staker).willPerformPox()`, or `mayPerformPox()` when the call may not run; never `willNotPerformPox()`.
- `stake` takes the signer manager, `amount-ustx`, `num-cycles`, `start-burn-ht` and optional calldata. Pass a burn height in the current cycle, such as `/v2/info` `burn_block_height`; a height in another cycle fails with `(err u24)`. In `Deny` mode it takes `Pc.principal(staker).willSendEq(amount).ustxToLock()`.
- In the prepare phase, `stake`, `stake-update`, `register-for-bond`, `update-bond-registration`, `announce-l1-early-exit` and `unstake-sbtc` fail with `(err u47)`, and `unstake` with `(err u28)`. The transaction is still mined and pays its fee, so before the wallet signs, check that pox-5's read-only `is-in-prepare-phase` is false for `current-pox-reward-cycle` ([stake](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/chainstate/stacks/boot/pox-5.clar#L976-L1086), [unstake](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/chainstate/stacks/boot/pox-5.clar#L1424-L1441), [prepare phase](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/chainstate/stacks/boot/pox-5.clar#L2945-L2960)).
- Sources: [SIP-045](https://github.com/stacksgov/sips/blob/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-045/sip-045-pox-5-bitcoin-staking.md#L524-L555), [epoch check](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/crates/stacks-transactions/src/lib.rs#L110-L141), [condition evaluator](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/crates/stacks-transactions/src/lib.rs#L221-L498), [lock and action records](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/pox-locking/src/pox_5.rs#L360-L594), [per-principal sums](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity-types/src/effects/asset_map.rs#L216-L306), [allowance check](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity/src/vm/functions/post_conditions.rs#L661-L679), [SDK builders](https://github.com/stx-labs/stacks.js/blob/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions/src/pc.ts#L185-L285), [Connect serializer](https://github.com/stx-labs/connect/blob/096c3fa5a1160cfbd0fcc9c9ffecea1227d25b7e/packages/connect/src/request.ts#L518-L567).

## PoX-5 signer managers

- A signer manager implements PoX-5's `signer-manager-trait`, whose only function is the `validate-stake!` callback. It must assert there that `contract-caller` is the active PoX contract; otherwise anyone can call it directly and redirect another staker's reward destination.
- Trace signer-key grants, manager registration, reward claims, fee snapshots and old-manager entitlements after switching signers.
- Account separately for pending withdrawals, rejected refunds, accepted fee refunds and unclaimed rewards. Fee sweeps must preserve staker liabilities.
- Reference implementations: [STX Labs signer-managers](https://github.com/stx-labs/signer-managers) collects implementations of PoX-5's `signer-manager-trait`. Its [basic manager](https://github.com/stx-labs/signer-managers/tree/c9e023542184fd532c7a7620d59d5f16a5a6d840/basic) supports sBTC reward claims, optional Bitcoin withdrawals and admin-set fees. Treat it as reference code; verify deployment and configuration separately.
- Reuse its [Clarigen tests and PoX helpers](https://github.com/stx-labs/signer-managers/tree/c9e023542184fd532c7a7620d59d5f16a5a6d840/basic/tests) as test designs. Its extraction script supplies SDK boot source to Clarigen; tests call simnet's boot instance. Check SDK/epoch support and target-network bindings before adapting the harness.

## Liquid staking: Stacking DAO

- Stacking DAO's STX core is `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-dao-core-stx-v2`; stSTX is `...ststx-token`, the withdrawal NFT `...ststx-withdraw-nft-v4`. Addresses: [Stacking DAO registry](../clarity-protocols/references/addresses/stackingdao.md).

```clarity
;; fragment: interface excerpt; resolve the exact deployment before calling
;; Deposit STX, receive stSTX at the current ratio (ok ststx-amount)
(contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-dao-core-stx-v2 deposit stx-amount min-shares-out)
;; Queue a withdrawal: stSTX moves to the core, a withdrawal NFT is minted (ok nft-id)
(contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-dao-core-stx-v2 init-withdraw ststx-amount)
;; After the unlock burn height: burn the NFT and receive STX (ok {stx-user, stx-fee})
(contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-dao-core-stx-v2 withdraw nft-id)
;; Instant exit from idle liquidity only, with a fee (ok {stx-user, stx-fee})
(contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stacking-dao-core-stx-v2 withdraw-idle ststx-amount)
```

- The ratio is `data-stx-v2` `get-stx-per-ststx` (STX per stSTX, 6 decimals); to price stSTX, see [liquid staking ratios](../clarity-oracles/SKILL.md#liquid-staking-ratios).
- These functions act on **`tx-sender`**, not `contract-caller`: STX is taken from `tx-sender`, stSTX is minted to `tx-sender`, and the NFT owner must equal `tx-sender`. A contract that holds the STX, stSTX or withdrawal NFT must make the call in its own `as-contract?` scope. `deposit` needs `with-stx`, and `init-withdraw` and `withdraw-idle` need `with-ft` on `ststx-token` (token name `ststx`). `withdraw` burns the NFT, so it needs `with-nft` on `ststx-withdraw-nft-v4` (token name `withdraw-nft`) listing the NFT id.
- `withdraw` requires `burn-block-height >= unlock-burn-height` of the NFT, which `init-withdraw` sets to the burn height plus a governed cooldown, at least 2,100 blocks on mainnet ([cooldown](https://github.com/StackingDAO/stackingdao-smart-contracts/blob/125c73dc109988730156f4d0434ff01654480fc7/mainnet/contracts/withdrawals/withdraw-data-stx-v2.clar#L19-L31)); `withdraw-idle` fails with an insufficient-idle error when the reserve lacks liquid STX, and charges `withdraw-idle-fee` unless fee-exempt. Queued withdrawals cannot finance atomic repayment.
- The stSTXbtc and stBTC cores have separate contracts and ABIs (`stacking-dao-core-ststxbtc-v2`, `stacking-dao-core-stbtc-v1`); read each before use.
- Each liquid staking protocol adds its own custody, share accounting and withdrawal schedule, and these change between versions. Before generating calls, read its current core, staker and strategy contracts and their mutable configuration.

## Historical reward entitlements

- Settle historical rewards against historical entitlement before changing balance, delegation, signer manager or exclusions.
- Handle queued withdrawals and pending rewards in share price; do not apply current weights to prior-cycle rewards.
- Reconcile available funds, locked principal, withdrawal reserves, pending rewards and queued liabilities.

## Integrate and test

- Resolve the active PoX contract and read its source. Record the cycle and prepare-phase lengths, the burn height, signer-key grants, reward destinations and who may call each function.
- Separate native STX transfers from locks, and use the allowance and post-condition type each operation needs.
- In your own wrapper, check callers per operation rather than with one global list.
- Test cycle and prepare-phase boundaries, joining and leaving near a boundary, lock expiry, caller checks, revoked signer-key grants, direct calls to manager callbacks, reward-claim and withdrawal destinations, late funding, signer changes and strategy migration.
- Use Clarigen for typed tests, and a devnet or pinned simulation for boot transitions and timing. Record the synthetic time and state each test assumes.

## References

- [Versions](../clarity-epochs/SKILL.md): allowance evolution and epoch behavior.
- [Model corrections](../clarity-epochs/SKILL.md#recall-corrections): context and PoX gaps.
- Load `clarity-system-integration` for boot identities and `clarity-apis` for node reads.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `stackingdao`: [125c73dc10](https://github.com/StackingDAO/stackingdao-smart-contracts/tree/125c73dc109988730156f4d0434ff01654480fc7).
- `signer-managers`: [c9e0235421](https://github.com/stx-labs/signer-managers/tree/c9e023542184fd532c7a7620d59d5f16a5a6d840).
- `stacks-core-release`: [10474cdec9](https://github.com/stacks-network/stacks-core/tree/10474cdec9f9c0bdf05841b58cffc89cdad87a9b).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
- `stacks-js-wallets`: [e6084a5214](https://github.com/stx-labs/stacks.js/tree/e6084a52140b2ad010a9d1a0f1b87d527c3a8870).
- `stacks-connect`: [096c3fa5a1](https://github.com/stx-labs/connect/tree/096c3fa5a1160cfbd0fcc9c9ffecea1227d25b7e).
