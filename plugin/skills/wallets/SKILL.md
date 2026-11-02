---
name: wallets
description: "Connect Stacks wallets (Leather, Xverse, Ledger) and call contracts from apps with @stacks/connect: contract calls, post-conditions, message signing. Use for frontend or dapp wallet integration."
license: MIT
compatibility: "Browser apps with @stacks/connect 8.2.7 and @stacks/transactions 7.6.0; Leather, Xverse or Ledger."
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Wallets

## Key distinctions

- Use `@stacks/connect` 8 `connect()` and `request()` for new integrations. `UserSession`, `showConnect`, `openContractCall` and `@stacks/connect-react` are legacy.
- Validate C32 checksums, network and principal shape. Contract IDs require exactly `address.name`, not a bare account; a postcondition builder returning an object does not prove validity. Native multisig uses `SM`/`SN`; address length varies.
- A cached address or `isConnected()` is not proof of account ownership, current wallet network or transaction approval.
- Connect 8 uses `contract: "ADDRESS.name"`, `functionArgs` and lowercase `txid`. Legacy callbacks and direct wallet APIs differ.
- `cvToString` prints Clarity syntax. Use `Cl.serialize` for wire hex, or let Connect serialize `Cl` values.
- Wallet, Ledger app, transport and node support are independent. A consensus-valid transaction can exceed the signer's capacity: check device model, app version, serialized transaction size, post-condition count and Clarity payload support.
- A deployment request's `clarityVersion` can be rewritten by a wallet. Inspect the payload and verify the deployed language version.
- STX/FT postconditions count gross outflows per principal/asset, not net spend or recipient receipts.
- Wallet signing/broadcast is separate from successful execution: verify a successful mined receipt and apply the app's confirmation policy.

## Choose the interface

| Need | Start here |
| --- | --- |
| Browser dapp supporting several Stacks wallets | [`@stacks/connect`](https://github.com/stx-labs/connect) |
| Clarity values, post-conditions, unsigned transaction construction | [`@stacks/transactions`](https://github.com/stx-labs/stacks.js/tree/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions) |
| Xverse-specific Stacks, Bitcoin or mobile behavior | [`sats-connect`](https://docs.xverse.app/sats-connect), including its own response envelope |
| Mobile pairing | Connect's optional WalletConnect provider; verify the selected wallet's supported chain/methods |
| Ledger signing transport | [`@zondax/ledger-stacks`](https://github.com/Zondax/ledger-stacks-js), plus [device checks](#ledger-and-hardware-signing) |
| Native multisig signing | [Governance](../governance/SKILL.md); inspect [`stx-labs/multisig-cli`](https://github.com/stx-labs/multisig-cli) for Ledger signing workflows |

- Connect 8.2.7's selector includes [Leather](https://leather.io), [Xverse](https://www.xverse.app), [Asigna](https://www.asigna.io/) and [Fordefi](https://www.fordefi.com).
- Use the wallet's official website for downloads. Follow current documentation links rather than copying browser-store identifiers from old tutorials.
- Current protocol contracts/addresses belong in [protocols](../protocols/SKILL.md), not wallet configuration examples.

## Connect and call

```ts
// fragment: Connect 8.2.7 contract call with a Deny post-condition (imports from @stacks/connect, @stacks/transactions)
const { addresses } = await connect({ network });
const account = addresses.find(({ address }) => validateStacksAddress(address) &&
  (network === 'mainnet' ? /^S[PM]/.test(address) : /^S[TN]/.test(address)));
if (!account) throw new Error('No Stacks account for the intended network');
const result = await request('stx_callContract', {
  contract, functionName: 'deposit', functionArgs: [Cl.uint(amount)], network, // contract: `${string}.${string}`
  address: account.address, postConditionMode: 'deny',
  postConditions: [Pc.principal(account.address).willSendEq(amount).ustx()],
});
if (!result.txid) throw new Error('Wallet returned no broadcast transaction ID');
return result.txid; // track canonical execution separately
```

- Call `connect()`/`request()` only from user events, in client code, not during rendering or server-side rendering. `connect()` opens the wallet selector; existing sessions can request fresh addresses with `request('stx_getAddresses', { network })` where supported.
- Select the Stacks address by chain and intended account, never a fixed index in a mixed BTC/STX address array. If several eligible Stacks accounts come back, choose explicitly (the fragment takes the first).
- Use checksum-aware decoding before network/version and principal-shape checks. `validateStacksAddress` checks the address component only; validate contract names separately. C32 addresses vary in length (`ST000000000000000000002AMW42H` is valid), and `SM`/`SN` are native multisig accounts, not contract principals. Decoding proves neither ownership nor authorization.
- `address` is a recommendation; wallets may ignore it. Confirm origin, network and intended account in the wallet and the returned transaction.
- `amount` is micro-STX for STX; FT amounts use the asset's base units. Keep integers as `bigint` or decimal strings, including values above JavaScript's safe integer range.
- The example ABI is `(define-public (deposit (amount uint)) ...)` transferring exactly `amount` from its transaction sender. A `deny` call needs a condition for every outgoing principal/asset (see [post-conditions](#post-conditions)). Use the deployed ABI, the actual token asset name and the current [protocol registry](../protocols/SKILL.md); a token contract name is not necessarily its asset name.

## New dapp: install, button, status

`npm install @stacks/connect@8.2.7 @stacks/transactions@7.6.0` and keep one deduped `@stacks/transactions` (`npm ls @stacks/transactions`). Pin packages in the project lockfile.

- API bases: mainnet `https://api.hiro.so`, testnet `https://api.testnet.hiro.so`, devnet `http://localhost:3999` (`clarinet devnet start`).
- Disable the button while a request is in flight (one request per click), catch wallet rejection or failure and do not auto-retry. Re-enable it in `finally` only if no txid came back; once one does, show the transaction as pending, because another click can send a second one. A Leather multisig account returns `status: 'proposed'` and a `proposalId` instead of a txid: check `status` before the txid check in [Connect and call](#connect-and-call), keep the button disabled and show the proposal as awaiting co-signers.
- Poll `/extended/v3/transactions/{tx_id}`: v3 returns the canonical mined record or the mempool record and has no `canonical` flag. Read the [status poller](references/examples.md#transaction-status-poller) before writing your own.
- Report success only for `status: "success"` with `block.height` and `block.index_hash`. Mined records can also be `abort_by_response`, `abort_by_post_condition` or `problematic_skipped` (epoch 4.0): failures, not pending.
- A 404 is normal right after broadcast and after a drop: v3 never reports `dropped_*` (the deprecated `/extended/v1/tx/{tx_id}` still does). No 404, timeout or lookup error proves failure: a dropped transaction can reappear or still be mined, so resume lookup and never automatically re-sign.
- Keep the txid and returned block identity, recheck them for reorgs and apply the app's confirmation policy before irreversible effects. Sources: [v3 lookup](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/v3/transactions.ts), [canonical query](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/v3/pg-store-v3.ts), [v1 dropped lookup](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/controllers/db-controller.ts).
- Test the same code against devnet ([devnet runbook](../environments/SKILL.md#run-devnet)); the wallet must support a custom node, so for automated checks use the scripted flow in [clarity:deployment](../deployment/SKILL.md#release-script-rules). Test the actual supported wallet/device combination, including rejection, account/network changes, large values, post-conditions, sponsorship and pending transactions where used.
- Pending, dropped, reverted and canonical-success evidence: [clarity:apis](../apis/SKILL.md).

## Post-conditions

- Standard STX/FT amount conditions constrain the **total sent by one principal for one native asset** in the whole transaction. They do not identify recipients, individual calls or net balance changes. This aggregate-outflow rule applies in every coverage mode; `Originator` changes coverage, not amount semantics.
- Incoming transfers do not offset outgoing ones: a wallet that sends 100 and receives a 40 refund sent 100, so constrain wallet sent = 100, not 60, and in `Deny` mode also cover the refunding principal's 40. STX amount checks include STX burned; fees are separate.
- Two conditions on the same principal and asset constrain the same total: a reward contract paying Alice 3 and Bob 7 of one FT sent 10, so conditions for 3 and 7 both fail; they do not select separate payouts. Use one condition for 10.
- Even sent = 10 does not prove Alice received 3. Enforce recipient and minimum output in the contract; for a balance-delta check, select the actual spendable asset and account for other movements within the measured scope.
- Use the native asset the call moves, not a token symbol or interface name. A wrapper whose `transfer` calls `stx-transfer?`, such as [Zest wSTX](../assets/SKILL.md#stx-through-a-token-interface-zest-wstx), moves STX: an FT condition on the wrapper sees nothing sent, even if it declares an FT. Write STX conditions in the micro-STX it moves, which differs from the call amount when the wrapper rescales it.
- FT and NFT identity is `address.contract-name::asset-name`. Require exactly one dot in the contract ID, a valid address and contract name and the actual declared asset name; reject bare accounts and extra components ([FT recipe](#build-an-ft-condition)).
- An NFT condition also names the key's exact Clarity value, never a recipient. A wrong name, key type or key value matches nothing, so `willSendAsset()` aborts and `willNotSendAsset()` passes, protecting nothing. A burn counts as a send. When a call may or may not move the NFT, use `willMaybeSendAsset()` (SIP-040 `MAY SEND`, epoch 3.4+): it passes either way and still covers the NFT in `Deny` and `Originator` mode.
- An SFT that keeps balances only in a map is invisible to post-conditions: tell the developer. A SIP-013 mirrored SFT burns the sender's tag NFT (SIP key `{token-id: uint, owner: principal}`) on transfer, so pair the FT amount condition with `willSendAsset()` on that tag. The tag condition binds the ID; without it `Deny` mode aborts, as does `Originator` mode when the sender is the origin. If the contract also burns an existing recipient's tag, as SIP-013's example does, `Deny` mode needs `Pc.principal(recipient).willMaybeSendAsset()` on that tag, because that burn is the recipient's send. Read the [SFT helpers](../sip-compliance/references/sft-post-conditions.md#client-conditions) before writing these conditions.

### Build an FT condition

- After validating inputs and aggregating outflows, pass `address.contract` and the native token name separately (`Pc.principal(sender).willSendEq(amount).ft(contractId, assetName)`). Do not append the token name to the contract ID.

```js
import { Pc } from '@stacks/transactions';

export function ftOutflow(sender, amount, token) {
  return Pc.principal(sender).willSendEq(amount)
    .ft(token.contractId, token.assetName);
}
```

- Assert `condition.asset` equals `token.contractId + '::' + token.assetName`, along with sender, amount, comparator and coverage mode. A contract name can differ from its native token name.
- With Stacks.js 7, serialize via `postConditionToHex(condition)` and decode via `Pc.fromHex(hex)`; assert the complete round trip matches the intended condition. Successful construction alone is insufficient.

### Choose coverage deliberately

| Mode | Uncovered outflows | Explicit conditions |
|---|---|---|
| `Deny` | Rejected for every sending principal | All must pass |
| `Originator` | Rejected only for the transaction origin account | All must pass, including conditions on contracts |
| `Allow` | Permitted | All supplied conditions still must pass |

- `Originator` is available from epoch 3.4 (SIP-040). Its origin is fixed by transaction authorization, including sponsorship; `as-contract?` does not change it. It does not protect a user's vault/contract principal or guarantee incoming assets; constrain those principals explicitly. Verify node, SDK, wallet and device support before using it.
- For complex routes, `Originator` can protect origin outflows without enumerating every contract movement; preserve protocol authorization and scoped allowances.
- Use `Deny` when the required flows can be bounded. Never silently fall back to `Allow`, remove conditions or widen amounts until signing succeeds.
- Stakes and unstakes need [Staking/PoX conditions](../staking/SKILL.md), not STX ones.

### Design predictable reward flows

- Automatic reward harvests inside token transfers, swaps or deposits can add outflows to several recipients from the same reward contract, and pending rewards, fees and configuration can change before inclusion. Enumerate `(sender, asset, total)` across the whole call graph (both endpoints' hooks, routers, fees, refunds), or settle entitlement into storage and pay through an explicit claim.
- Known batches remain usable with aggregate bounds.
- When settling accrued entitlement into storage on ownership change, preserve the prior owner's rewards, checkpoint exactly once and clear paid entitlement; test repeated saves/claims and migrations.
- Separate claims cost another transaction and lose atomic settlement with the original action. Keep atomic composition where required and enforce recipient, min-output, max-input, fee and deadline bounds on-chain.
- A frontend preflight is advisory and can become stale. Stacks transaction postconditions are not arbitrary before/after assertions over contract state; see [state-only authority abuse](../security/references/patterns.md#a01-sender-authority-forwarded-through-an-attacker).

### Test the signed policy

- Test no rewards, rewards for either/both endpoints, changing rewards between quote and execution, multiple payouts, refund round trips and wrong recipients with unchanged gross totals.
- Submit the intended mode and conditions explicitly in tests: simnet disables checks when both are omitted ([simulator traps](../environments/SKILL.md#simulator-traps)).
- Assert committed balances, entitlement, events and rollback. Test the actual wallet's request encoding and displayed limits separately.

Sources: [released node's condition evaluator](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/crates/stacks-transactions/src/lib.rs), [asset accumulation](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity-types/src/effects/asset_map.rs), [SIP-040](../epochs/SKILL.md#epochs-and-clarity-versions), [postcondition documentation](https://docs.stacks.co/learn/transactions/post-conditions).

## Messages, deployments and sessions

- Plain text signature: `request('stx_signMessage', { message })` uses a wallet-specific prefix and is not for contracts; bind it to your own challenge (for example a nonce). SIP-018 structured data: `request('stx_signStructuredMessage', { message: Cl.tuple(...), domain: Cl.tuple({ name, version, 'chain-id' }) })` with `chain-id` mainnet `u1`, testnet `u2147483648`; results carry `signature` and `publicKey`. Use SIP-018 structured signatures when the protocol requires them. Examples: [mobile, sessions and messages](references/examples.md#mobile-sessions-and-messages).
- For backend authentication, verify a wallet signature over a server-issued, single-use challenge bound to the intended domain and expiration. For contract-verified SIP-018 messages, verify the exact domain, chain, schema and replay protection ([security](../security/SKILL.md)).
- Deployment: `request('stx_deployContract', { name, clarityCode, clarityVersion, network, postConditionMode: 'deny', postConditions: [] })` ([deployment request](references/examples.md#deployment-request)). `name` is the contract name, not `ADDRESS.name`; the signing origin's address deploys. An empty list is only right when deployment performs no asset outflows.
- Wallet methods can broadcast immediately; do not assume `broadcast: false` works in every provider. For pre-broadcast payload inspection, use a supported sign-only flow and verify its actual behavior. Confirm the signed payload's contract name, source, language version, origin, chain ID, nonce, fee, sponsorship and post-conditions.
- Leather emits an **unversioned** deployment when `clarityVersion` is omitted or equals `6`, so the node's epoch default selects the language ([implementation](https://github.com/leather-io/mono/blob/c7f03715845889e62bcd52d88caa792400915ed1/packages/stacks/src/transactions/generate-unsigned-transaction.ts)). A request for 6 is not a permanent wire-level pin: check the wallet release and the deployed version. Ordering and initialization: [clarity:deployment](../deployment/SKILL.md).
- Mobile: `connect({ walletConnect: { projectId, networks: [WalletConnect.Networks.Stacks] } })`; `walletConnectProjectId` is deprecated in 8.2.7. WalletConnect is a connection protocol, not a wallet; a Bitcoin-capable mobile connection does not establish Stacks support. Test the in-app browser and external pairing independently.
- Connect 8 caches every connected address, across networks, and exposes no portable account/network event listener; check provider-specific events and capabilities separately. Re-query after wallet, account or network changes and before building an action. `disconnect()` clears local state and ends a WalletConnect session; it does not undo signed transactions or revoke contract permissions.
- Read [references/examples.md](references/examples.md) when writing these requests: complete deployment, message-signing and WalletConnect examples.

Sources: [Connect request/type source](https://github.com/stx-labs/connect/tree/096c3fa5a1160cfbd0fcc9c9ffecea1227d25b7e/packages/connect/src), [Xverse calls](https://docs.xverse.app/sats-connect/stacks-methods/stx_callcontract), [Leather RPC source](https://github.com/leather-io/mono/tree/c7f03715845889e62bcd52d88caa792400915ed1/packages/rpc/src/methods/stacks).

## Compatibility traps

- Connect 8 call/deploy results use `txid` and optionally `transaction`; legacy callbacks use `txId`/`txRaw`; direct Sats Connect wraps responses in `status`, `result` or `error`.
- Let Connect serialize `Cl` and `Pc` objects. Direct APIs may require hex via `Cl.serialize(value)` and `postConditionToHex(condition)`.
- For STX through a token interface, pass the wrapper the target contract or protocol requires, since it rejects others; otherwise use [Zest wSTX](../assets/SKILL.md#stx-through-a-token-interface-zest-wstx).
- Current Xverse docs support post-conditions for calls and deployments; do not repeat older tables claiming otherwise, and test the installed wallet.
- Connect's BTC `sendTransfer` adapter strips `network` for Xverse/Fordefi. Its `signPsbt` adapter can drop inputs without addresses, `network` and `allowedSighash`; Leather receives signing indexes rather than the full input mapping. Inspect the final request when those fields matter.
- SIP-030 method definitions do not guarantee implementation: a connection does not prove `stx_transferSip10Ft`, sign-only, sponsorship or multisig support. Connect 8.2.7's selector (Leather, Xverse, Asigna, Fordefi) does not imply every RPC method.
- Sponsorship: coordinate origin and sponsor nonce/signature stages explicitly and preserve the origin-signed fields.
- Native multisig must preserve pubkey order, threshold and the selected signing mode. A contract multisig approves contract state transitions instead; they are not interchangeable ([clarity:governance](../governance/SKILL.md)).

## Ledger and hardware signing

- Record wallet version, Ledger model/firmware, Stacks app version, JS transport version, Clarity version, network and serialized transaction bytes. Distinguish node rejection, transport failure, device parsing/display rejection and invalid signature; `Data invalid` alone does not identify the cause.
- Count serialized **transaction bytes**, including auth and post-conditions, not source or hex length: UTF-8 source bytes, hex characters and transaction bytes are different sizes. Rehearse the exact signing path on the intended device before fixing an immutable deployer identity.
- A chain-valid contract can exceed hardware limits. Consult [versions](../epochs/SKILL.md) for consensus bounds; never treat a device limit as one.
- Do not downgrade Clarity or remove post-conditions to make a device accept a transaction. Choose a supported signer/release path, or deliberately redesign and retest the protocol.
- Splitting a contract changes dependencies, principals, authorization and deployment order. Whitespace reduction also changes the exact source hash. Treat either as a reviewed release change.
- Read [references/ledger.md](references/ledger.md) before a hardware wallet signs a deployment, a versioned or multisig payload, or many post-conditions. Ledger does not reject every `VersionedSmartContract`.

## Lookup

- [Connect source and issues](https://github.com/stx-labs/connect), [current wallet support](https://docs.stacks.co/stacks-connect/wallet-support).
- [Leather docs](https://leather.gitbook.io/developers/), [current source and issues](https://github.com/leather-io/mono). The former extension repo is archived.
- [Xverse Sats Connect docs](https://docs.xverse.app/sats-connect), [SDK source and issues](https://github.com/secretkeylabs/sats-connect).
- [Stacks.js source and issues](https://github.com/stx-labs/stacks.js), [Ledger device app](https://github.com/Zondax/ledger-stacks), [Ledger JS client](https://github.com/Zondax/ledger-stacks-js).
- Route Bitcoin proof work to [clarity:bitcoin-proofs](../bitcoin-proofs/SKILL.md).

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `stacks-connect`: [096c3fa5a1](https://github.com/stx-labs/connect/tree/096c3fa5a1160cfbd0fcc9c9ffecea1227d25b7e).
- `stacks-js-wallets`: [e6084a5214](https://github.com/stx-labs/stacks.js/tree/e6084a52140b2ad010a9d1a0f1b87d527c3a8870).
- `sats-connect`: [2e196801c0](https://github.com/secretkeylabs/sats-connect/tree/2e196801c053335d50f6abb5fb1b94da48eedc15).
- `leather-mono`: [c7f0371584](https://github.com/leather-io/mono/tree/c7f03715845889e62bcd52d88caa792400915ed1).
- `ledger-stacks`: [3f9bc89ce7](https://github.com/Zondax/ledger-stacks/tree/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d).
- `ledgerhq-stacks`: [3be06bebde](https://github.com/LedgerHQ/app-stacks/tree/3be06bebdef4b7b9bf858759cc096fe5474ab8b3).
- `stacks-multisig-cli`: [47bdc291a5](https://github.com/stx-labs/multisig-cli/tree/47bdc291a52d85bace44502ca7bd42b0e9967b6f).
- `stacks-core-release`: [10474cdec9](https://github.com/stacks-network/stacks-core/tree/10474cdec9f9c0bdf05841b58cffc89cdad87a9b).
- `stacks-blockchain-api`: [ee0c0ac5be](https://github.com/hirosystems/stacks-blockchain-api/tree/ee0c0ac5bee51b206c67e83e581fab457c34a622).
