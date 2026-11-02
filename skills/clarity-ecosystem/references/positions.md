# Protocol position calls

Verified calls for holding a position in each protocol from a [position contract](../../clarity-ecosystem/SKILL.md#position-contracts) or a vault's own `as-contract?` scope. For a protocol not listed here, check the points in [what differs between protocols](../../clarity-ecosystem/SKILL.md#what-differs-between-protocols).

## Zest vault (`v0-vault-usdc`; same shape on every `v0-vault-*`)

- Supply: `deposit (amount uint) (min-out uint) (recipient principal)` returns the shares minted. Zest pulls the underlying from `contract-caller` under its `tx-sender` context: allowance `(with-ft <underlying> "<asset>" amount)` (USDCx `"usdcx-token"`, sBTC `"sbtc-token"`), `recipient` = `current-contract`, `min-out` = the owner's minimum shares (Zest reverts below it).
- Exit: `redeem (amount uint) (min-out uint) (recipient principal)` burns the position's z-tokens: allowance `(with-ft '<vault> "zft" shares)`; `min-out` = minimum underlying; `recipient` = the owner. Liquidity left after borrows limits it.
- Value: the vault's `get-balance current-contract`, then `convert-to-assets`.
- Retarget by replacing the vault and underlying literals everywhere (read-only code cannot call through a constant); the sBTC vault is `SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-sbtc` with `sbtc-token` and asset `"sbtc-token"`.
- `deposit` fails on pause, supply cap, share slippage and while a flash loan on the same vault is open; `redeem` fails on pause and slippage.

## Granite LP (USDCx market)

- Supply: `liquidity-provider-v1` `deposit (assets uint) (recipient principal)` returns `(ok true)`: no minimum argument and no share count. It pulls from `contract-caller` under its `tx-sender`: allowance `(with-ft '<usdcx> "usdcx-token" amount)`. Measure minted shares from `state-v1` `get-balance current-contract` before and after; require more than zero and at least `min-shares`. Fails with `(err u116)` above the market's asset cap.
- Exit: `redeem (shares uint) (recipient principal)` burns the caller's `lp-token` in `state-v1`: allowance `(with-ft 'SP3M2BYF7RGF8WKW5FVDNJ6WR8D7AR9BHDXAKPXZE.state-v1 "lp-token" shares)`, or the scope returns `(err u128)` and the position cannot exit. No minimum: measure the owner's USDCx balance before and after and compare with `min-assets`.
- Exits also fail with `(err u120002)` above the market's LP withdrawal bucket, which all lenders share and which refills over a governed window. `redeem` is checked on the shares' value after interest accrues; to exit an exact amount, call `withdraw (assets uint) (recipient principal)` with `assets` at most `lp.new-bucket` (no limit while `lp.cap-factor` is `u0`) ([withdrawal caps](../../clarity-protocols/references/granite.md#granite-withdrawal-caps)); it burns the shares rounded up, so the `lp-token` allowance must cover them. Decide whether the remainder waits for a later call or the operation reverts, and tell the developer which.
- Value: held shares times `total-assets` over `total-lp-shares`, rounded down, from `SPDMQABVKKDVZ25MYCQ0ZW90QWERMZFWT02QP1Q4.utility` `get-market-state`; `state-v1` `convert-to-assets` omits interest since the last accrual and rounds up. Exit liquidity can be lower while funds are borrowed.
- Lenders earn yield on the market's borrowable asset, USDCx; sBTC enters Granite only as borrower collateral (`borrower-v1.add-collateral`), which earns nothing.

## Hermetica hBTC (`vault-hbtc-v1-2`, sBTC only)

- Read `state-hbtc-v1` `check-is-deposit-enabled` first: it returns `(err u102005)` (`ERR_DEPOSIT_DISABLED`) while governance has deposits disabled, as they currently are. Decide whether a refused deposit is held, routed elsewhere or reverts the operation, and tell the developer which.
- Supply: `deposit (assets uint) (affiliate (optional (buff 64)))` with `none` returns the shares; sBTC moves from `contract-caller`: allowance `(with-ft 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token "sbtc-token" amount)`. No minimum argument: check the returned shares against `min-shares`. Deposit cap, `min-deposit` and the soft blacklist also apply.
- Exit is asynchronous: `request-redeem (shares uint) (is-express bool)` moves hBTC into the vault (allowance `(with-ft 'SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.token-hbtc "hBTC" shares)`) and returns a claim id whose user is the position; `cancel-redeem claim-id` returns the shares of an unfunded claim, but not of an express claim (`(err u103009)`); `redeem claim-id` pays sBTC to the claim's user once it is funded and its cooldown has passed. Neither moves assets out of the position, so neither needs an `as-contract?` scope.
- Anyone may redeem a funded claim (the sBTC still comes to the position), and the vault then deletes it: read `get-claim` first, treat a missing claim as completed, then forward the spendable sBTC (`get-balance-available`) to the owner under a `with-ft` allowance for that amount. Never `try!` across a list of claims.
- Value: `preview-redeem` of the held shares; the owner tracks queued claims itself and counts each once. hBTC is not one-for-one with sBTC.

```clarity
;; fragment: Hermetica collect; a missing claim was already redeemed by someone else
(if (is-ok (contract-call? 'SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1-2 get-claim claim-id))
  (begin (try! (contract-call? 'SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1-2 redeem claim-id)) true)
  false)
```

## Bitflow DLMM liquidity (sBTC/USDCx pool `dlmm-pool-sbtc-usdcx-v-1-bps-10`)

- Router `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2`, bound to core `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1`. Supply: `add-liquidity-multi (positions (list 333 {pool-trait, x-token-trait, y-token-trait, bin-id: int, x-amount: uint, y-amount: uint, min-dlp: uint, max-x-liquidity-fee: uint, max-y-liquidity-fee: uint})) (deadline-time (optional uint))` returns the shares minted per entry. Exit: `withdraw-liquidity-multi (positions (list 326 {pool-trait, x-token-trait, y-token-trait, bin-id: int, amount: uint, min-x-amount: uint, min-y-amount: uint})) (deadline-time (optional uint))` returns `{x-amount, y-amount}` per entry. The `relative` forms take `active-bin-id-offset` instead of `bin-id`. `deadline-time` is seconds (`u5009`). Here x is sBTC and y is USDCx.
- Bin ids in calls are signed, -500 to 500 (`u5007` outside). The pool's token id is the bin id + 500. x may go only into bins at or above the active bin (`u1020`), y only at or below it (`u1021`): `get-active-bin-id` on the pool.
- The pool contract is the SIP-013 share token: `pool-token` (one FT summed over bins) and `pool-token-id`, a tag NFT `{token-id, owner}` that the pool burns and re-mints on every mint, burn and transfer. Read a bin's shares with the pool's `get-balance (token-id uint) (user principal)` and the bins held with `get-user-bins`.
- Supply allowances: the core pulls the inputs from `tx-sender`, so the position adds inside `as-contract?` with `with-ft` for each input (`"sbtc-token"`, `"usdcx-token"`) and `with-nft '<pool> "pool-token-id"` for every bin it already holds; always listing the target bins is harmless. `min-dlp` is the minimum shares and must be above zero (`u1027`, `u1024`). Adding to the active bin charges a fee on the imbalanced side, capped by `max-x-liquidity-fee`/`max-y-liquidity-fee` (`u1030`/`u1031`). The first deposit into an empty bin needs at least `minimum-bin-shares` (currently 10,000) and gives `minimum-burnt-shares` (currently 1,000) to a burn address.
- Exit allowances: `with-ft '<pool> "pool-token" amount` and the tag `with-nft` for each bin withdrawn; neither alone works. Proceeds go to `tx-sender`, with no recipient argument, so forward them to the owner. `min-x-amount + min-y-amount` must be above zero (`u1002`). Withdrawal works per bin, for any part of the balance, and still works while the pool is disabled; adds and swaps need it enabled (`u1010`).
- One `with-nft` lists at most 128 ids; several `with-nft` entries for the same asset add up.
- Value: for each bin in `get-user-bins`, the position's shares `s` from `get-balance` and `{x-balance, y-balance, bin-shares}` from `get-bin-balances` give `s * x-balance / bin-shares` sBTC and `s * y-balance / bin-shares` USDCx, exactly what withdrawing would pay at that state. Bins above the active bin hold only sBTC, bins below only USDCx, and every swap changes the split. Value both sides with a verified oracle price, never the bin price.
- Bitflow admins can migrate a pool to a new core after `core-migration-cooldown` (currently 1,209,600 s); afterwards core v-1-1 and the routers return `u1060` for it. The core trait `dlmm-core-trait-v-1-1` declares `add-liquidity`, `withdraw-liquidity` and `move-liquidity`, so an exit that takes `(core <dlmm-core-trait>)` and asserts `(contract-of core)` equals the pool's `get-pool` `core-address` survives a migration.
- On a fork, use `use_mainnet_wallets = true`: the pool checks mint, burn and transfer principals with `is-standard` (`u3003`).

```clarity
;; fragment: withdraw part of one bin; the pool pays tx-sender (this position), which then forwards to the owner
(as-contract? ((with-ft 'SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10 "pool-token" amount)
               (with-nft 'SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10 "pool-token-id" (list {token-id: (to-uint (+ bin-id 500)), owner: current-contract})))
  (try! (contract-call? 'SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2 withdraw-liquidity-multi
    (list {pool-trait: 'SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10,
           x-token-trait: 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token,
           y-token-trait: 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx,
           bin-id: bin-id, amount: amount, min-x-amount: min-x, min-y-amount: min-y})
    none)))
```

## Swaps from a contract (Stacks Swap through a Bitflow DLMM pool)

A swap holds no position, but a contract that converts between assets swaps from its own scope. The example is the sBTC/USDCx pool.

- Call `r-d` on `SP3EWCDA3V8HCP64CSETSNYXZ25WC4AJ95EC0ZEST.zr-d-0` with `SP3EWCDA3V8HCP64CSETSNYXZ25WC4AJ95EC0ZEST.dlmm-adapter` and `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10` (x = sBTC, y = USDCx). USDCx to sBTC passes `false false false` (y to x, no STX on either side), sBTC to USDCx `true false false`; skim `u0 u0`. Argument order: [Stacks Swap](../../clarity-protocols/references/stacks-swap.md#stacks-swap).
- The router pulls the input from `tx-sender`: the owner transfers the input to the position, which swaps inside `as-contract?` with `with-ft` for the input amount and sets `recipient` to the owner, so the output goes straight there.
- `min-out` and `deadline-height` (a Stacks block height, not seconds) are function arguments chosen by the transaction signer. An owner that lets an operator trigger swaps also floors `min-out` from a verified price.
- Through Stacks Swap the pool pays the adapter, not your contract, so the pool's `is-standard` check applies only to a direct Bitflow call, which fails on a fork when your contract has an `ST...` deployer (`err u3003`).
- The alternative is to call the same pool directly through Bitflow's DLMM router ([Bitflow](../../clarity-protocols/references/bitflow.md#bitflow), deadline in seconds). [Choosing a swap venue](../../clarity-protocols/SKILL.md#choosing-a-swap-venue) says which to pick.
