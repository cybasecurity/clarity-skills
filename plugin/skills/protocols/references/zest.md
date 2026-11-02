# Zest v2 calls

Exact Zest v2 vault, flash-loan and market call shapes, deployed-body checks and test fixtures. Apply the [rules for every protocol call](../SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../SKILL.md#addresses-and-freshness) first.

## Zest v2

Market `SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-8-market` and seven vaults under the same deployer ([addresses](addresses/zest.md)). `v0-vault-usdc` holds USDCx; its name alone does not identify the asset.

| Vault `v0-vault-*` | Underlying (debt asset) | Decimals |
|---|---|---|
| `sbtc` | `SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token` (asset `"sbtc-token"`) | 8 |
| `stx` | `SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.wstx` (native STX: `with-stx`) | 6 |
| `usdc` | `SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx` (asset `"usdcx-token"`) | 6 |
| `usdh` | `SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1` | 8 |
| `ststx` | `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststx-token` | 6 |
| `ststxbtc` | `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.ststxbtc-token-v2` | 6 |
| `stbtc` | `SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.stbtc-token` | 8 |

Vault calls (same shape on every vault; deposit and redeem return `(response uint uint)`):

- `deposit (amount uint) (min-out uint) (recipient principal)` returns the shares minted. The payer is `contract-caller`; the vault pulls the underlying under the caller's `tx-sender` context, so a contract deposits inside its own `as-contract?` with `with-ft` for the underlying (`with-stx` for the wSTX vault). `min-out` is the minimum shares (reverts below it). Pause and supply cap apply.
- `redeem (amount uint) (min-out uint) (recipient principal)` burns `amount` shares from `contract-caller` (allowance `(with-ft '<vault> "zft" amount)`) and pays the underlying to `recipient`; `min-out` is the minimum underlying. Liquidity left after borrows limits it.
- Value of held shares: the vault's `get-balance` (z-tokens), then `convert-to-assets shares` (accrued interest included).
- `flashloan (amount uint) (funds-receiver (optional principal)) (fc <flash-callback>) (data (optional (buff 4096)))`. Funds go to `funds-receiver` (default `contract-caller`; it must pass `is-standard`); the vault calls `callback(amount, fee, data)`, then pulls `amount + fee` (fee rounded up) from the **funds-provider, the `contract-caller` of `flashloan`**. A receiver changes the destination, not the repayment source.
- Only funds-providers with `can-flashloan` can borrow. The default is `{can-flashloan: false, fee-exempt: false}`, so a new contract needs a DAO grant (`set-flashloan-permissions`) before it can borrow on mainnet; `fee-exempt` is a separate permission.
- While a loan is open, `deposit` and a second `flashloan` on the same vault fail (`ERR-REENTRANCY`); `system-repay` is not guarded.
- Callback trait `'SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.vault-traits.flash-callback`: `(callback (uint uint (optional (buff 4096))) (response bool uint))`, arguments (amount, fee, data). Bind the expected vault caller, amount, data/session and permitted operation; arbitrary callers must not trigger liquidation or spend allowances.
- An 8,192-byte Lazer update does not fit the 4,096-byte `data`: keep it in authenticated operation state and pass a bounded session identifier.

Market calls:

- `liquidate (borrower principal) (collateral-ft <ft-trait>) (debt-ft <ft-trait>) (debt-amount uint) (min-collateral-expected uint) (collateral-receiver (optional principal)) (price-feeds (optional (list 3 (buff 8192))))` returns `(ok {debt: uint, collateral: uint})`: use those actual amounts. `collateral-ft` is the collateral's **z-token vault contract**; `debt-ft` is the **underlying token** repaid. Collateral positions are vault shares.
- The market requires `contract-caller == tx-sender` (debt token paid from `tx-sender`): an adapter calls `liquidate` inside its own `as-contract?` scope, and needs no second scope when it already runs in one (as in a flash-loan callback it started). `collateral-add` checks the same; inspect each method. Liquidation is rejected when the borrower's last borrow is in the current Stacks block; seed test state in an earlier block.
- `liquidate-redeem` also redeems the seized shares to the underlying for `receiver`; `supply-collateral-add` deposits underlying and adds the shares as collateral in one call.
- Zest types token arguments with its own `ft-trait` (`SP1A27...ft-trait`, the same seven functions as SIP-010); trait references match by shape, so a SIP-010 value passes.
- `price-feeds`: `none` verifies nothing; `(some (list update))` must hold **exactly one** Lazer update despite the ABI maximum of three, and it must include every required configured feed (pinned parser: IDs 1/7/45, channels 3/4, at least three publishers, confidence and per-feed timestamps required). These are version-specific facts, not a permanent feed registry, and the local-testing parser and helper differ ([local helpers](#zest-test-fixtures)). Supply one whenever a position asset is priced from Pyth. Oracle fees can require native STX from the sender.
- Pass fresh feeds and a meaningful `min-collateral-expected`. Choose the exact market/vault pair: "borrow sBTC" does not imply every liquidation consumes sBTC debt or returns sBTC collateral.
- For STX, use Zest's registered wSTX (six decimals, STX allowances and postconditions; [wSTX](../../assets/SKILL.md#stx-through-a-token-interface-zest-wstx)).

```clarity
;; fragment: deposit into and exit from a Zest vault with a contract's own funds (USDCx vault)
(try! (as-contract? ((with-ft 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx "usdcx-token" amount))
  (try! (contract-call? 'SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc deposit amount min-shares current-contract))))
(try! (as-contract? ((with-ft 'SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc "zft" shares))
  (try! (contract-call? 'SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc redeem shares min-assets recipient))))
```

### Zest deployed-body checks

- Read the body to confirm debt payer (`contract-caller`), collateral receiver default, accrual ordering, asset configuration and oracle routing.
- The market's `contract-caller == tx-sender` requirement during liquidation is an [authenticated entry policy](../../security/references/authorization.md#sender-preservation): it prevents an unscoped intermediary borrowing the user's sender authority while retaining it for the market's downstream calls.

### Zest test fixtures

- Repository: `mainnet/contracts/` for deployed sources, `local-testing/` (Clarinet project with Clarigen types and `contracts/mocks`) for a runnable harness. The local market differs from the deployed v0-8 market, so assert production behavior against the deployed requirements.
- To test against deployed Zest, add `[[project.requirements]] contract_id` entries for the deployer's contracts the market references: `ft-trait`, `market-trait-v7`, `vault-traits`, `v0-assets`, `v0-egroup`, `v0-market-vault`, `v0-8-market`, every `v0-vault-*`, `wstx`, `dao-executor`, `pyth-lazer-oracle`, `pyth-lazer-decoder-v1`, plus `SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle` and the Stacking DAO `data-stx-v2` and `data-stbtc-v1` ratio sources. The vaults' underlying tokens (USDCx, USDh, stSTX family) are further requirements. Do not add sBTC as a requirement; simnet provides it from epoch 3.0. Use `repl.remote_data` with a pinned height when live state matters.
- A vault position needs only the contracts it calls directly as requirements (`v0-vault-usdc` and `usdcx`); keep only the requirements your contracts call.
- Lazer fixtures: `pyth-lazer-helpers.ts` uses local feed IDs and omits per-feed update timestamps, and the local parser accepts fields the deployed market rejects; extend the encoder and verify against the [deployed market source](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/market/v0-8-market.clar). `pyth-helpers.ts` is the legacy Core/Wormhole path, unsuitable for new Lazer integrations.
