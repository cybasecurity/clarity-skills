# Flash-loan liquidation

Lender selection and call order for a [flash-loan liquidation](../../clarity-ecosystem/SKILL.md#flash-loan-liquidation); apply the [flash-loan rules](../../clarity-ecosystem/SKILL.md#flash-loan-rules) to every flow.

### Who lends what

| Source | Lends / accepts | Repay asset | Pull context |
|---|---|---|---|
| Zest `v0-vault-<x>.flashloan` | that vault's underlying: sBTC, wSTX, USDCx, USDh, stSTX, stSTXbtc, stBTC | same underlying, `amount` + rounded-up fee | `tx-sender`-based transfer from the `contract-caller` of `flashloan` (needs `can-flashloan`) |
| Granite `flash-loan-v1` | USDCx | same asset, `amount` + rounded-up fee | pulled from the `contract-caller` of `flash-loan` with its `tx-sender` |
| Hermetica `vault-hbtc-v1-2` | not a lender; deposit sink for **sBTC only** | n/a | sBTC pulled from `contract-caller` |
| Zest `v0-8-market.liquidate` | repays the position's **debt token** (underlying), seizes **vault shares** (z-token) of the collateral | debt token from `tx-sender`, which must equal `contract-caller` | `liquidate-redeem` redeems seized shares to the underlying for a `receiver` |

Pick the lender from the debt token of the Zest position being liquidated:

| Zest position debt | Collateral seized | Lender | Swaps |
|---|---|---|---|
| USDCx | sBTC (via `liquidate-redeem`) | Granite USDCx market or Zest `v0-vault-usdc` | sBTC to USDCx for `amount + fee` |
| sBTC | USDCx, stSTX or other | Zest `v0-vault-sbtc` (no swap before liquidation) | collateral to sBTC for `amount + fee` |
| sBTC | any | Granite (lends USDCx only) | USDCx to sBTC before liquidating, then collateral to USDCx for repayment |
| other (stSTX, USDh, ...) | any | that token's Zest vault | collateral to the borrowed token |

### Call order

In one orchestration contract `X` that is also the lender callback (separate callback contracts follow the same order):

1. `X.run(...)`: authenticate the caller or apply a keeper policy. Bind borrower, `collateral-ft`, `debt-ft`, amounts, `min-collateral`, `min-profit`, beneficiary and the swap deadline (a Stacks block height for Stacks Swap, seconds for Bitflow) into operation state. Carry the Lazer update (up to 8,192 bytes) in Granite's 20,480-byte `data`, or keep it in operation state for Zest, whose `data` holds only 4,096 bytes.
2. Compute `repay = amount + ceil(amount * fee)` in the lender asset. Open `as-contract?` with allowances for the **sum of every outflow in the whole operation** (repayment plus liquidation debt token plus swap inputs).
3. Lender: Zest `v0-vault-<x>.flashloan amount (some X) X data` (X needs `can-flashloan`) or Granite `<market>.flash-loan-v1.flash-loan amount X data` (Granite governance must allow X as a callback). Funds arrive at `X`.
4. Callback (`contract-caller` is the lender endpoint, `tx-sender` is `X`): assert the caller is the expected endpoint and that an operation `run` stored is active; take every parameter from that stored operation or validate `data` against it. A public callback that trusts `data` lets anyone run your swaps under your allowances.
5. If the lender asset is not the debt token, swap it through Bitflow or Stacks Swap ([choosing a swap venue](../../clarity-protocols/SKILL.md#choosing-a-swap-venue)), with min-out for the exact debt amount.
6. `v0-8-market.liquidate borrower collateral-ft debt-ft debt-amount min-collateral (some X) (some (list update))`, or `liquidate-redeem` for the underlying. The market requires `contract-caller == tx-sender`: both are `X` when the callback calls it, so no second scope is needed (a separate callback contract opens its own). The borrow must be older than the current Stacks block. Use the returned `{debt, collateral}` (`{debt, underlying}` from `liquidate-redeem`).
7. Swap only enough of the received collateral to cover the shortfall in the lender asset; assert `balance >= repay` at the end of the callback.
8. The callback returns `(ok true)`; the lender pulls `repay` from `X`. After the lender call returns, compute the surplus from balance deltas and deliver it as step 1 bound it: forward it to the beneficiary, or swap and deposit it when the strategy calls for that (for example Hermetica `deposit` under `(with-ft sbtc-token "sbtc-token" surplus)` after `check-is-deposit-enabled`, with a minimum-shares check, then forward the shares).
9. Any error reverts the whole transaction, including the lender's transfer and earlier legs.
