# Granite calls

Exact Granite lender, flash-loan, borrower and liquidation call shapes, withdrawal caps, oracle path and test fixtures. Apply the [rules for every protocol call](../SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../SKILL.md#addresses-and-freshness) first.

## Granite

Granite lends USDCx; sBTC and other collateral go into a borrower position and are never lent ([addresses](addresses/granite.md)).

- Logic (`borrower-v1`, `liquidity-provider-v1`, `liquidator-v1`, `flash-loan-v1`): `SPSX722NK9V3A8D3CVQT0CDY4EBQ3E9FSDDE61FT`.
- State: `SP3M2BYF7RGF8WKW5FVDNJ6WR8D7AR9BHDXAKPXZE.state-v1`. Loan asset: `SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx`.
- Callback trait for `flash-loan`: `SP3M2BYF7RGF8WKW5FVDNJ6WR8D7AR9BHDXAKPXZE.trait-flash-loan-v1.flash-loan`. It lives under the old deployer while the logic sits under the current one: use it exactly. The repository's `.mock-usdc` is a test dependency, not production identity.
- Deprecated: the aeUSDC market closes by 2026-11-03 ([announcement](https://x.com/GraniteBTC/status/2115575726975922272)). An open position exits through `SP119QJ4NVE3RQP8RXJVW5EXAV3XD4CJZWRCEEAAR` `borrower-v1` (`repay`, then `remove-collateral`) or `liquidity-provider-v1` (`redeem`), with state `SP35E2BBMDT2Y1HB0NTK139YBGYV3PAPK3WA8BRNA.state-v1`, and reopens in USDCx.

Lender calls (`liquidity-provider-v1`):

- `deposit (assets uint) (recipient principal)` returns `(ok true)`: no minimum argument and no share count. It pulls `assets` from `contract-caller` under its `tx-sender` (contracts call it inside `as-contract?` with `with-ft` for the loan asset) and credits LP shares to `recipient`. Measure minted shares from `state-v1` `get-balance` before and after; require more than zero and at least the caller's minimum. It fails with `(err u116)` when the deposit would take `state-v1` total assets above its asset cap.
- `withdraw (assets uint) (recipient principal)` and `redeem (shares uint) (recipient principal)` debit `contract-caller` and pay `recipient`. The debit is `state-v1` burning the caller's `lp-token`: allowance `(with-ft '<state-v1> "lp-token" shares)`, or the scope returns `(err u128)`. No slippage argument: measure the recipient's balance change against a minimum. Both draw on the LP [withdrawal cap](#granite-withdrawal-caps).
- Value: held shares times `total-assets` over `total-lp-shares`, rounded down, both from `get-market-state` on the read-only USDCx utility `SPDMQABVKKDVZ25MYCQ0ZW90QWERMZFWT02QP1Q4.utility`. Its `total-assets` includes interest since the last accrual; `state-v1` `convert-to-assets` uses the stored total, which omits it, and rounds up. Exit liquidity can be lower while funds are borrowed.

```clarity
;; fragment: Granite USDCx LP; get-shares reads state-v1 get-balance of current-contract
(let ((before (get-shares)))
  (try! (as-contract? ((with-ft 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx "usdcx-token" amount))
    (try! (contract-call? 'SPSX722NK9V3A8D3CVQT0CDY4EBQ3E9FSDDE61FT.liquidity-provider-v1 deposit amount current-contract))))
  (let ((minted (- (get-shares) before)))
    (asserts! (and (> minted u0) (>= minted min-shares)) ERR_SLIPPAGE)
    (ok minted)))
;; exit: state-v1 burns this contract's LP shares
(try! (as-contract? ((with-ft 'SP3M2BYF7RGF8WKW5FVDNJ6WR8D7AR9BHDXAKPXZE.state-v1 "lp-token" shares))
  (try! (contract-call? 'SPSX722NK9V3A8D3CVQT0CDY4EBQ3E9FSDDE61FT.liquidity-provider-v1 redeem shares recipient))))
```

Flash loan (`flash-loan-v1`, per market):

- `flash-loan amount callback data` with `data` up to `(optional (buff 20480))`. The endpoint checks that the **callback contract** is allowed (`is-contract-allowed`; governance may set `allow-any`). Funds go to the immediate caller of `flash-loan`; the callback receives `(amount, fee, data)` with the fee rounded up (`divide-round-up`); afterwards the principal is pulled from the caller (`transfer-from`) and the fee is transferred from the caller to governance. Callback address and asset receiver are distinct roles.
- Callback method: `(on-granite-flash-loan (uint uint (optional (buff 20480))) (response bool uint))`.
- Principal and fee are pulled from the original caller using its `tx-sender`, so a contract that calls `flash-loan` runs inside `as-contract?` with a `with-ft` allowance for the loan asset covering `amount + fee`. Inside the callback, `tx-sender` is that initiating contract and `contract-caller` is the Granite flash-loan contract: authenticate that caller and the active operation before spending. Read `get-fee` live.
- The flash loan itself reads no oracle. Granite and Zest differ in callback names, buffer limits, permissions and receiver behavior; they are not interchangeable EIP-3156 interfaces.

Borrower and liquidation calls:

- `borrower-v1.add-collateral (collateral <token-trait>) (amount uint) (maybe-user (optional principal))`: with `none` the position owner is `contract-caller`; with `(some user)` that user must equal `tx-sender`. Only collaterals with a nonzero max LTV in `state-v1` are accepted.
- `borrow (update (buff 8192)) (amount uint) (maybe-user (optional principal))`, `repay (amount uint) (on-behalf-of (optional principal))`, `remove-collateral (update (buff 8192)) (collateral <token-trait>) (amount uint) (maybe-user (optional principal))`.
- `liquidator-v1.liquidate-collateral (update (buff 8192)) (collateral <token-trait>) (user principal) (liquidator-repay-amount uint) (min-collateral-expected uint)` credits the liquidator as `contract-caller`, repays in the loan asset, and enforces a minimum block gap after the borrow plus `min-collateral-expected`.

### Granite withdrawal caps

- `withdraw` and `redeem` fail with `(err u120002)` above the LP bucket, `borrow` with `(err u120003)` above the debt bucket and `remove-collateral` with `(err u120004)` above that collateral's bucket. The buckets live in the logic deployer's `withdrawal-caps-v1`, not the older `SP3M2BY...` one.
- All users draw on the same buckets, so a position's own shares or LTV do not guarantee the call. Each bucket refills toward a governed fraction (`cap-factor`) of a `state-v1` amount: its USDCx balance (LP), its borrowable balance (debt) or its balance of that collateral. `deposit`, `repay` and `add-collateral` add their amounts at once; a `cap-factor` of zero means no cap. Liquidations and flash loans are not capped.
- Read the amount left as `new-bucket` from `SPDMQABVKKDVZ25MYCQ0ZW90QWERMZFWT02QP1Q4.utility` with inflow `u0`: `get-market-withdrawal-caps u0` returns `lp` and `debt`; `get-collateral-withdrawal-caps` takes the token, that token's `get-balance` of `state-v1` and `u0`. A result whose `cap-factor` is `u0` is uncapped, so ignore its `new-bucket`. Read off chain, it is an estimate that time and other users' calls change.
- `withdraw` is checked on exactly its `assets` and burns the shares rounded up, so the `lp-token` allowance must cover them; `redeem` is checked on its shares' value after interest accrues. To exit an exact amount near the bucket, use `withdraw`. Exit a larger position in parts.

### Granite oracle path

- Borrowing, removing collateral and liquidating take a required Pyth Lazer `update (buff 8192)`; removing collateral needs one even from a position without debt. The live USDCx market's `borrower-v1` and `liquidator-v1` (deployer `SPSX722...`) call the same-deployer `.pyth-adapter-v1`, whose `verify-update` calls `verify-price-feeds(update, decoder, none)` on Granite's own instance `SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-oracle` ([addresses](addresses/pyth-lazer.md)), so the instance's governed stale-price threshold applies. The adapter divides the envelope timestamp by 1,000,000, then requires for each token its feed (sBTC: feed 1 BTC/USD; USDCx: feed 7 USDC/USD), a positive price, an exponent within [-18, 11], an envelope time at most 300 s (`time-delta`) before and 60 s after the previous block time plus 5 s, and, when present, confidence within the token's ratio (sBTC 5%, USDCx 1%). Feed ids and limits change only through the market's governance (multisig plus a 21,600-block timelock). Verify the instance's pause state, signer, fee and decoder before relying on it. Lazer payload rules: [clarity:oracles](../../oracles/SKILL.md).
- The registry row labelled "historical `pyth-adapter-v1` (Pyth Core)" under `SP3M2BY...` is a legacy adapter that still calls Pyth Core (`pyth-oracle-v4`, `pyth-storage-v4`, `pyth-pnau-decoder-v3`, `wormhole-core-v4`). Their stored prices stop at the Core shutdown (last BTC/USD publish 2026-08-21), the live borrower and liquidator do not call them, and they return `(err u80002)` (stale price). Never route a borrow or liquidation through them.

### Granite test fixtures

- Repository `contracts/test/` has `mock-flash-loan-callback.clar` (callback skeleton implementing `trait-flash-loan-v1`) and `mock-liquidator-with-flash-loan.clar`; `contracts/traits` holds the traits. They use `.mock-usdc`, so keep them for unit tests of your callback logic only.
- The pinned repository is newer than the deployed USDCx logic: its `borrower-v1`, `liquidator-v1` and `withdrawal-caps-v1` differ from the deployed contracts, and its `withdrawal-caps-v1` ships with every cap off. Test against the deployed contracts, not repository source.
- To run against deployed Granite, declare `[[project.requirements]]` for the chosen deployer's `borrower-v1`, `flash-loan-v1`, `liquidity-provider-v1`, `liquidator-v1`, `pyth-adapter-v1`, `withdrawal-caps-v1`, `staking-v1`, `linear-kinked-ir-v1`, the market's `state-v1`, `constants-v1/v2`, `math-v1`, `staking-reward-v1`, the callback trait contract, the loan token and the Lazer oracle/decoder. Use `repl.remote_data` with a pinned height for live balances and whitelist state; with only synthetic mocks you have not proved the callback is allowed.
- An LP position that only deposits and redeems needs only the contracts it calls directly as requirements: `liquidity-provider-v1`, `state-v1` and `usdcx`, plus `SPDMQABVKKDVZ25MYCQ0ZW90QWERMZFWT02QP1Q4.utility` when it reads the market state or caps.
- State allowlisting alone does not prove callback permission, unpaused execution or liquidity; apply the [freshness rules](../SKILL.md#addresses-and-freshness).
