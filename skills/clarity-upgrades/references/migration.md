# State and token migration

Rules for moving state, custody and token claims to new contracts. Choose the case first in [when replacement requires migration](../../clarity-upgrades/SKILL.md#when-replacement-requires-migration), and rehearse with the [rehearsal assertions](../../clarity-upgrades/SKILL.md#rehearsal-assertions).

## Legacy-token compatibility

Native `ft-burn?`, `ft-mint?` and `ft-transfer?` accept only a token the calling contract defines ([burn check](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/analysis/type_checker/v2_1/natives/assets.rs#L309-L330)). A new version moves old balances only through the old contract's own functions, so read their gates first:

- Approved callers checked on [`contract-caller`](../../clarity-security/SKILL.md#execution-context): the owner approves the new version or a migrator. With an owner check on `tx-sender`, a contract the owner calls can approve itself; on `contract-caller`, the owner must send each approval.
- A transfer only the holder can make: use a [holder swap](#holder-swap).
- Neither: old balances cannot move, so the new version must keep honoring them as claims.

Give a token that may be replaced a gated `burn` in its first version. Each old-token burn or pull is the holder's [outflow](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/assets.rs#L1071-L1085): under `Deny` a transaction needs a sent condition for each holder and old token it moves, and under `Originator` only for the origin's. Use `willSendLte` where the move may not happen. A contract holder needs a `with-ft` per old token in `as-contract?`.

### Choose an approach

| Approach | Use when | Costs and failures |
|---|---|---|
| Version chain: the newest version reads old balances and moves an account's balance on its next action | Only your protocol moves the old token | Every read walks every version; idle holders never move |
| Pause and migrate: freeze, list holders, burn and mint in batches | You can stop every writer, burn any holder's balance and move any backing the new token needs | No exits while frozen; an unlisted holder keeps a balance nothing reads |
| Holder swap: each holder trades in the old token | Holders can transfer or redeem it, but pause and migrate cannot run | Idle holders keep the old token |

### Version chain

Each version reads its predecessor and pulls an account's old balance up on the next protocol action. For example, in Zest v1's stSTX z-token (v1 `zststx`, v2 `zststx-v1-0`, v3 `zststx-v1-2`, [sources](source-examples.md#concrete-migration-sources)), reads nest but writes go straight from v3 to the version holding the balance:

```text
read:   v3 --get-principal-balance--> v2 --get-principal-balance--> v1
        total = v3 own + v2 own + v1 own

write:  pool --cumulate-balance--> v3   mints the old amount + interest
        v3 --burn--> v1                 if v1 holds it   (v3 approved on v1)
        v3 --burn--> v2                 else if v2 does  (v3 approved on v2)
```

- Add only the predecessor's read: it already includes the older ones, which would count twice.
- Burn and mint each old version's own amount (its read minus its predecessor's), all versions in one call. A chained read used as the burn fails with `(err u1)` when an older version also holds a balance, and as the mint counts that balance twice. Moving only the oldest non-empty version, as Zest's v1 token's third version (`zststx-v1-2`) does, is safe only while each version moves an account's old balance before crediting it; otherwise a cut strands the second old balance.
- Move old balances inside the newest version's own burn and transfer, not in a separate call: a caller that skips that call debits a balance still held in an old version and gets `(err u1)`.
- Each upgrade, per asset, in one transaction: approve the new version on every older one, and revoke the previous version and old protocol contracts. A missing approval reverts every move of an affected balance; an unrevoked one keeps writing balances the chain counts.
- Never pause or retire an old version that still holds balances: its read and burn run inside the newest version's calls, so an error there reverts them.
- Each version adds a nested `contract-call?`, and every call loads the callee's source. Measure the costliest path at the deepest chain against the [resource limits](../../clarity-epochs/SKILL.md#resource-limits) before adding a version; near them, cut over with a pause and migrate.
- Sum every version's own supply wherever supply prices shares, the newest `get-total-supply` included: `zststx-v1-2` counts only its own ledger, so it omits unmoved balances.

### Pause and migrate

1. Stop every writer of the old token and every protocol action that moves it (a pause, or revoked approvals), or balances move to unlisted holders mid-run. Until the last batch, also keep closed the new version and every action that reads its balances, such as liquidations in other markets: unmoved holders read zero there and can be liquidated.
2. List holders off chain from mint, transfer and burn events ([discovery](../../clarity-apis/references/positions-and-proofs.md#discover-positions-then-value-them)): Clarity cannot enumerate them.
3. Gate the migrator to the operator, or anyone can migrate a holder you meant to skip. Approve it through each token's owner check ([gates](#legacy-token-compatibility)). With instant approvals and a `tx-sender` owner check, each batch contract can approve itself and revoke in the same call, so no approval outlives its batch. Under a `contract-caller` owner check or timelocked approvals, each new batch contract would need its own approval, so approve one migrator that takes holders as an argument and revoke it after the last batch.
4. Per holder, in one call: burn the live old balance, mint it at a defined ratio and rounding, and re-key records keyed by the old token's principal, or the new balance loses what they held, such as an interest index or a collateral flag. Live balances make a re-run a no-op.
5. Skip zero balances, since [zero burns and mints](../../clarity-assets/SKILL.md#native-operations) return `(err u1)`, and `try!` each result through `fold` so one failure rolls back the batch: `(ok (map ...))` keeps a burn whose mint failed ([iteration](../../clarity-scholar/SKILL.md#iteration-without-loops)).
6. Size batches from one measured batch, usually by reads. A batch must fit the tenure budget left when it is mined: a large one waits for a tenure with room, and one that overflows a tenure under 20% used is dropped as too big ([resource limits](../../clarity-epochs/SKILL.md#resource-limits)).
7. Publish every batch contract, or the one migrator, before the freeze, then call them back to back, since exits stop while frozen. Re-list holders after the freeze and add a batch for any new one. A batch that runs at deploy instead needs `unwrap-panic` on its top-level call: a top-level `err` does not [abort the deploy](../../clarity-deployment/SKILL.md#failures-must-actually-abort).
8. Skip contract holders whose code cannot use the new token, since a contract calls only what its code names, and reopen only the old exit they call.
9. Done means each old version's `get-total-supply` is zero apart from skipped holders, and new supply and custody match what was burned. Keep a self-migration entry for missed holders, revoke every other approval, then reopen.

See [example migrations](source-examples.md#concrete-migration-sources).

### Holder swap

The swap `try!`s the old token's own `transfer` with `tx-sender` as sender, then mints the converted amount in the same call, so a failed pull mints nothing. A `transfer` checking only `contract-caller` rejects the pull, and send-then-claim is unsafe: a contract cannot tell who sent it a token. Never send pulled tokens back out, since each is a consumed claim. For vault shares, skip the pull: in one call the swap redeems the holder's shares at the old vault and deposits the proceeds into the new one, with `tx-sender` still the holder, so the backing moves and the new shares mint to the holder. Inside `as-contract?` both calls would act for the swap contract, which would keep the new shares.

### Split a token ledger from its logic

The asset is `<defining contract>::<token name>`: [allowances](../../clarity-security/SKILL.md#execution-context) (`with-ft`, `"*"` included) and [post-conditions](../../clarity-wallets/SKILL.md#post-conditions) match only that contract. For a token others can transfer, a split works when that contract is stable and keeps `transfer`, `get-balance`, `get-total-supply` and the metadata getters: the state contract, as in [Granite](../../clarity-protocols/references/granite.md#granite), or a token contract beside it (Zest v2 `zvstBTC`). Replaceable logic reaches the token only through mint and burn, behind a timelocked pointer. A deployed token cannot be split later; its definition cannot move.

- A facade or logic contract offered as the token matches nothing in allowances and post-conditions (`(err u128)` in `as-contract?`), and replacing it breaks pinned callers.
- A ledger only the logic contract can reach suits a token only protocol contracts move (Zest v1 `zststx-token`).
- Per-transfer rules belong in the defining contract from its first deployment: a stored principal cannot be called, and SIP-010 `transfer` takes no trait.

## State, custody and authority

- Inventory every field, including nonces, replay markers and NFT listings, with its owner contract, units and clock. Take map keys from events: maps cannot be enumerated.
- Convert saved heights when the new logic reads another clock (burn height, Stacks height or `stacks-block-time`), or elapsed time and interest come out wrong.
- Checkpoint indexes, and settle or import fees and queued exits, before retiring the old writer: new logic inherits none of them.
- Mark each imported record consumed in the same call, and close import authority after: a replayed import credits the claim twice.
- Reconcile backing before reopening: new custody covers the new supply, old custody every claim left on the old token.
