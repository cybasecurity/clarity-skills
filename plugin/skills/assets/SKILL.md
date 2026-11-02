---
name: assets
description: "Handle assets in Clarity: STX, SIP-010 tokens, SIP-009 NFTs, sBTC (available vs locked), custody, transfers, burns and post-conditions. Use whenever a contract moves, holds or accounts for tokens."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Assets

Identify the asset actually moved before choosing authorization, allowances or postconditions.

Writing or changing contract code: also load `clarity:scholar` and `clarity:security`, and finish with the [build checklist](../start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- A ticker or SIP-010-shaped wrapper does not establish native asset identity.
- Some wSTX contracts move native STX; others custody STX and mint an FT.
- Native FT/NFT primitives do not authorize callers on behalf of supplied owners.
- sBTC `get-balance` includes withdrawal-locked units. Repayment needs available units.
- Postconditions are transaction-level client constraints; contracts cannot inspect or set them.
- Bitcoin settlement and queued vault redemption cannot complete within an atomic flash loan.

## Native operations

- `ft-transfer?`, `nft-transfer?`, `ft-burn?` and `nft-burn?` do not look at `tx-sender` or `contract-caller`: the VM lets the defining contract move or burn any holder's balance. Every public path that reaches one of them needs its own owner/role check, including privileged mint/burn branches.
- Only `stx-transfer?`, `stx-transfer-memo?` and `stx-burn?` check authorization: `sender` must equal the effective `tx-sender`, otherwise `(err u4)`. Inherited user context can authorize spending; wallets should bound outflows. Contract-owned spending needs its own sender scope and, in Clarity 4+, a `with-stx` allowance.

| Operation | Behavior to preserve |
|---|---|
| Zero amounts | STX/FT transfer returns `(err u3)`; FT mint/burn returns `(err u1)`. Skip zero fee/output legs when policy permits; `try!` otherwise propagates failure |
| Self-transfer | STX/FT/NFT transfer returns `(err u2)`; test self-liquidation, fee recipients and vault self-payments |
| Insufficient funds | STX/FT transfer `(err u1)`; NFT transfer `(err u1)` when `sender` does not own the ID, `(err u3)` when the ID does not exist |
| FT supply cap | Exceeding `define-fungible-token`'s cap aborts with `SupplyOverflow`; this is not a catchable `err` |
| NFT mint | An existing ID returns `(err u1)` |
| `stx-get-balance` | Spendable STX, including expired locks; `stx-account` exposes `{locked, unlock-height, unlocked}`. Staking locks funds in place |
| Errors | Native `u1`–`u4` and boot errors overlap application codes. Prefer documented higher ranges for new custom errors; preserve native/SIP conventions and existing ABIs. Retain provenance when forwarding or mapping |

- Contract-owned outflows in Clarity 4+ (`as-contract` does not exist there): `(try! (as-contract? ((with-stx amount)) (try! (stx-transfer? amount tx-sender recipient))))`; for a native FT, `(as-contract? ((with-ft <token-contract> "<token-name>" amount)) (try! ...))`. List only the assets that leave; no body expression may return a response.
- Match `with-stx`, `with-ft`, `with-nft` and staking/PoX allowances to the actual operation and target version ([versions](../epochs/SKILL.md)).

## Accounts and identities

- Standard principals start with `SP` (single-signature) or `SM` (multisig) on mainnet and `ST` or `SN` on testnet. A contract principal appends `.name`; deployable names are 1–40 bytes. Successfully deployed code is immutable.
- STX has six decimals: one STX = 1,000,000 micro-STX.
- Native FT/NFT identity is contract principal plus declared asset name, such as `SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token::sbtc-token`. Symbols are not unique.
- Map-only balances are contract state, outside native asset/postcondition tracking.
- Record network, contract principal, native asset name/class, decimals, ownership rights and actual source for every asset you integrate. Resolve deployed identities through the [system](../system-integration/references/addresses.md) and [protocol](../protocols/references/addresses.md) registries.

## Transfer authorization

- A shared SIP-010 interface does not imply shared authorization. Check every integrated asset, including treasury fees, rescue transfers, rewards and flash-loan repayment.
- Clarity has `tx-sender` and `contract-caller`; there is no `contract-sender` keyword.
- Pin network, deployed source and native asset identity. Follow public `transfer` through private helpers, delegated contracts and native primitives.
- Record the exact predicate: `sender == tx-sender`, `sender == contract-caller`, either, explicit delegation, or a privileged exception. Inspect branches that mint/burn instead of transferring, plus pause, migration, blacklist and available-balance checks. A private helper's predicate may not describe every public path.
- For each call edge, record origin, current `tx-sender`, immediate `contract-caller`, supplied `sender`, recipient and asset owner. Recompute after every helper, callback or sender scope.
- Verify both ingress and egress. A successful user deposit does not establish that the contract can withdraw, repay or distribute the same asset.
- Resolve authorization separately from asset allowances and transaction postconditions. None substitutes for the others.

### Call-context matrix

`U`: user, `V`: contract owning funds, `H`: helper, `T`: token. Assume sufficient funds, a different recipient, no extra restrictions or privileged exceptions. Columns evaluate only the named authorization predicate. `V scope` means V executes its call inside its own `as-contract?` with adequate allowances, or legacy `as-contract` where supported.

| Call path | Token `sender` | Token `tx-sender` | Token `contract-caller` | Sender-only | Caller-only | Either |
|---|---|---|---|---|---|---|
| `U → T` | U | U | U | Pass | Pass | Pass |
| `U → V → T` | U | U | V | Pass | Fail | Pass |
| `U → V → T` | V | U | V | Fail | Pass | Pass |
| `U → V → H → T` | V | U | H | Fail | Fail | Fail |
| `U → V scope → T` | V | V | V | Pass | Pass | Pass |
| `U → V scope → H → T` | V | V | H | Pass | Fail | Pass |
| `U → V → H scope → T` | V | H | H | Fail | Fail | Fail |

- A sender-only token is not inherently broken or SIP-incompatible. Its owning contract must establish the required sender context.
- Scoping a helper makes **the helper** the sender; it cannot impersonate the owning vault. Adding a helper can also break caller-only authorization.
- For Clarity 4+, use narrowly bounded `as-contract?` in the owning contract, authenticate the requested operation first, capture the original beneficiary outside the scope, and propagate errors.
- Match `with-ft` to the native FT or `with-stx` to native STX. For STX wrappers such as Zest wSTX, the underlying `stx-transfer?` requires `sender == tx-sender`, even if an outer wrapper accepts `contract-caller`.
- Do not weaken a token guard, broaden allowances or rely on inherited user authority merely to make a composition pass.
- An either-identity guard still accepts forwarded `tx-sender` authority. Caller-authorized outflows can also occur outside a restricted scope; review every reachable outgoing call.

### Concrete source examples

These identify implementations, not current protocol support or operational state; refresh the selected deployment and mutable roles before integrating.

| Contract | Effective path to check |
|---|---|
| [ststx-token](https://explorer.hiro.so/txid/SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststx-token?chain=mainnet&tab=overview) | `transfer` requires `sender == tx-sender` |
| [sbtc-token](https://explorer.hiro.so/txid/SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token?chain=mainnet&tab=overview) | `transfer` accepts sender or caller; check [available balance](#sbtc) separately |
| [usdh-token-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1?chain=mainnet&tab=overview) | `transfer` accepts sender or caller after `is-not-migrated`; verify migration state and intended version |

- Sources: [Clarity caller keywords](https://docs.stacks.co/reference/clarity/keywords), deployed contracts above. Fetch deployed source as in [deployed source and ABI](../apis/SKILL.md#deployed-source-and-abi).

## sBTC

- sBTC is a signer-controlled, BTC-backed SIP-010 token with 8 decimals. Mainnet identity: `SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token::sbtc-token`; resolve other networks through the [protocol address registry](../protocols/references/addresses.md) and its freshness rules.
- `get-balance(owner)` adds unlocked and withdrawal-locked units. Use `get-balance-available(owner)` for spendable liquidity and immediate repayment, `get-balance-locked(owner)` for pending locked units. Total ownership differs from available repayment funds.
- `transfer` accepts `sender` equal to `tx-sender` or `contract-caller`; inspect that exact implementation when composing calls.
- A SIP-010 `transfer` moves sBTC on Stacks synchronously. Deposit minting and Bitcoin withdrawals are asynchronous and need external processing; submitting a request is not Bitcoin settlement, and no fixed completion time is guaranteed.
- Verify the registry-controlled protocol contracts, request IDs, event provenance, maximum fees, recipient encoding and status progression. Read [sBTC settlement](../bitcoin-proofs/SKILL.md#sbtc-settlement) for Bitcoin deposit and withdrawal scripts and for what acceptance or rejection of a withdrawal does.
- Transaction postconditions must name the actual native asset, not just a UI ticker.
- Test pending withdrawals, rejection/unlock, completion/burn and donations; keep mocks faithful.
- Source: [sBTC contracts](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17/contracts/contracts), pinned in the [reference baseline](#reference-baseline).

## STX through a token interface: Zest wSTX

- When STX must pass through a SIP-010 interface and nothing you call requires another wrapper, use Zest's wSTX ([registry entry](../protocols/references/addresses/zest.md)) so your integrations converge on one wrapper. This is the package's interoperability rule, not a Stacks standard or a guarantee that a protocol accepts it.
- A pool, market, vault or router that registers or checks another wrapper needs that wrapper for its own calls, because a different principal fails its token check or registry lookup. Use it there only, and tell the developer ([protocol wrappers](../protocols/SKILL.md#protocol-discovery)).
- Use native STX operations when no token interface is needed.
- Existing deployments keep their configured wrapper and version; do not replace a v1 principal with v2 by ticker alone.
- `transfer(amount, sender, recipient, memo)` calls `stx-transfer?`: it moves native STX directly, with no separate FT balance, wrapping deposit or redemption step. Amounts use six decimals (one STX is `u1000000`).
- The native transfer requires `sender == tx-sender`. Passing the adapter as `sender` is insufficient unless its sender context is active.
- A contract spending its own STX through wSTX needs its sender scope and, for Clarity 4+, a bounded `with-stx` allowance. A `with-ft` allowance for `.wstx` cannot authorize native STX.
- Client postconditions constrain STX outflows from the actual sending principal. Do not invent a `.wstx::wstx` FT identifier.
- `get-balance(who)` is the holder's whole spendable STX and `get-total-supply` is `stx-liquid-supply`, not tokens held for a protocol. Vaults track deposited amounts in their own state instead of reading `get-balance` of the vault or the user.
- An optional memo prints only after a successful transfer. Test zero/self-transfer failures, caller context, fees and gross STX outflows.
- Other wrappers can have different principals, custody STX and mint an FT, or rescale amounts; use the wrapper the target contract or protocol requires ([protocol wrappers](../protocols/SKILL.md#protocol-discovery)) and test dust and minimum transferable units.
- Zest's market types its token arguments as Zest's SIP-010-shaped `ft-trait`, which `wstx` implements. Trait references match by shape, so SIP-010-typed code can pass `.wstx` where `<ft-trait>` is expected. Read [Zest v2 calls](../protocols/references/zest.md#zest-v2) for call shapes and Clarinet requirements.
- Sources: [Zest deployment table](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/README.md), [wrapper source counterpart](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/local-testing/contracts/utility/token/wstx.clar).

## Custody and accounting

- Distinguish total ownership, liquidity, backing, receipt shares and pending liabilities. Avoid double counting underlying assets, receipt tokens, duplicate registry entries or wrapper aliases.
- Check actual transferred/returned amounts; burns outside vault bookkeeping can desynchronize supply.
- Bound uint128 intermediates, fee scales and denominators; choose operation-specific rounding. Use [rounding checks](../security/references/patterns.md#a11-uint128-intermediates-and-rounding-direction) for low decimals, caps, one-unit amounts and repeated dust cycles.
- [Bitcoin settlement](../bitcoin-proofs/SKILL.md#sbtc-settlement) and queued vault redemption cannot fund synchronous flash-loan repayment. Track request IDs, partial completion, fees, cancellations, rejected requests and pending liabilities separately.
- USDCx has separate token and bridge contracts, and its bridge settles asynchronously. Its three balance getters return the same value, so do not apply sBTC's locked-balance formula. Use the [USDCx recipe](../protocols/references/usdcx.md#usdcx) for transfers or bridging.
- For Bitcoin deposit scripts, inclusion proofs or withdrawal settlement, use `clarity:bitcoin-proofs`; ordinary token transfers remain here.
- Writing a SIP-010 token or SIP-009 NFT: follow [SIP compliance](../sip-compliance/SKILL.md#sip-010-fungible-tokens), then apply the transfer-authorization checks here. SIP compliance covers normative clauses; asset authorization remains a security obligation independently.
- Token replacement: use [legacy-token compatibility](../upgrades/references/migration.md#legacy-token-compatibility); conserve claims across versions and prove contract holders can transfer/redeem the replacement.

## Transactions and postconditions

- Origin accounts have sequential nonces; origin or sponsor pays fees in micro-STX. Higher fees do not buy execution budget.
- Versioned deployment payloads pin a language; unversioned payloads select the executing epoch's default.
- Successful top-level `ok` commits contract effects. A returned `err`, runtime abort or postcondition failure rolls back contract state/assets/events; included transactions still consume nonce and fees. A caller can handle a public callee's `err` and commit its own effects.
- Contracts cannot inspect or set transaction postconditions. Clients attach them, including conditions on contract principals; use [gross outflows, coverage modes and reward-flow rules](../wallets/SKILL.md#post-conditions).
- Constrain every intended outflow from the user and the user's contracts in the actual native asset. `Deny` also needs coverage for other sending principals; `Originator` covers unlisted origin outflows only. Node/wallet support and staking/PoX conditions are version-dependent ([versions](../epochs/SKILL.md)).
- Test client transactions through a transaction-capable environment, not only direct contract calls.

## Supply-preserving retirement (null principal)

- To remove tokens from circulation while keeping them in total supply, or to lock permanent minimum shares, transfer them to the network's null standard principal. Native burns (`stx-burn?`, `ft-burn?`, `nft-burn?`, an SFT burn method) reduce supply; recoverable treasury balances do not establish permanent retirement.
- Mainnet `SP000000000000000000002Q6VF78`, testnet `ST000000000000000000002AMW42H`. The payload is 20 zero bytes; do not use an empty buffer, a zero string of the wrong length, or EVM `0x0`. `.pox-5` or any appended contract name is a different principal, not the null recipient.
- Minimum liquidity: mint/transfer the locked share amount to the null principal, give the first depositor only the remainder, and keep those shares in the supply denominator. Burning them instead reduces the denominator and does not create the same invariant.
- A null-principal balance is not automatically immutable: FT/SFT implementations may expose administrative transfer/burn or migration powers. Inspect them before claiming permanent locking.
- Null addresses are a deliberate retirement destination, not a default for user withdrawals or protocol repayments.
- Test unchanged total supply after transfer, increased null balance, decreased sender balance, inability to redeem the locked shares through public paths, correct aggregate/per-ID SFT accounting, and initialization exactly once.

### Construct the network-correct principal

```clarity
;; clarity 4
;; id: null-principal
;; principal-construct? and is-in-mainnet require Clarity 2+.
(define-constant NULL_PRINCIPAL (unwrap-panic (principal-construct? (if is-in-mainnet 0x16 0x1a) 0x0000000000000000000000000000000000000000)))

(define-read-only (get-null-principal)
	NULL_PRINCIPAL)
```

- Version `0x16` (22) is mainnet single-signature, `0x1a` (26) testnet single-signature.
- Off-chain equivalent with `c32check`:

```ts
import { c32address } from 'c32check';
const mainnetNull = c32address(22, '00'.repeat(20));
const testnetNull = c32address(26, '00'.repeat(20));
```

### Transfer the actual asset

- STX: `(stx-transfer? amount tx-sender NULL_PRINCIPAL)` transfers owned native STX; an owning contract needs the appropriate sender context and `with-stx` allowance.
- Native FT: an authorized path in its defining contract can use `(ft-transfer? token amount owner NULL_PRINCIPAL)`.
- External FT/SIP-010: call its actual `transfer` interface with the null recipient and preserve sender authorization, memo and postconditions.
- SFT: use the implementation's transfer method with the exact token/bin ID and quantity. SIP-013 has multiple transfer interfaces; do not assume one universal signature.
- NFT: transferring an ID to the null principal preserves existence; `nft-burn?` destroys it. Verify the token's actual interface and admin powers.
- Apply normal amount, identity and error checks; zero transfers may return errors.
- Sources: [principal-construct?](https://docs.stacks.co/reference/clarity/functions#principal-construct), [VM principals](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/principals.rs), [native asset operations](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/assets.rs).

## Tests

- Exercise each supported asset through the real deposit, withdrawal, repayment, liquidation, fee and rescue paths that use it.
- Cover wallet, owning contract, helper and callback contexts from the [matrix](#call-context-matrix); assert the actual payer and recipient balance deltas.
- Test unauthorized callers, forged `sender`, altered recipient, missing/insufficient allowances and token rejection. Confirm accounting and transfers roll back together.
- Test zero and dust transfers, hostile callers, wrong tokens, fees and late rollback. Test native STX and locked, migrated or paused assets against their actual implementation.
- Test against pinned real contracts where authorized (Clarigen by default, or the project's harness); otherwise use faithful, explicitly limited fixtures. Keep sender-only fixtures sender-only.
- Start contract-owned payments through a wallet's call into that contract. Passing its principal as the simulator transaction sender bypasses the context transition being tested.
- A passing generic SIP-010 mock does not establish compatibility with every listed asset. Deposit success does not prove withdrawal or repayment works.

## References

- [Model corrections](../epochs/SKILL.md#recall-corrections): native authorization and locked balance mistakes.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `sbtc`: [eb507946c6](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
