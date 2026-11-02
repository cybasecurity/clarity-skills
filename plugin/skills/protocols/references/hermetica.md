# Hermetica calls

Exact Hermetica hBTC vault call shapes, redemption-claim rules and test fixtures. Apply the [rules for every protocol call](../SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../SKILL.md#addresses-and-freshness) first.

## Hermetica

Vault `SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1-2`; asset `SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token` (8 decimals, **sBTC only**); shares `SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.token-hbtc` (asset `"hBTC"`). HQ membership authorizes vault v1.2 and rejects v1/v1.1; documentation still links v1 ([addresses](addresses/hermetica.md)). The pinned current source is `vault-v1-2.clar`; `deprecated/vault-v1.clar` remains for history.

- **Deposits can be disabled:** `state-hbtc-v1` `check-is-deposit-enabled` currently returns `(err u102005)` (`ERR_DEPOSIT_DISABLED`), so every `deposit` fails. Read it before integrating. In a multi-venue allocation, decide whether a refused hBTC leg is held, rerouted or reverts the whole allocation. Also read the deposit cap, `min-deposit` and the soft blacklist through `state-hbtc-v1`.
- `deposit (assets uint) (affiliate (optional (buff 64)))` returns `(ok shares)`. Payer, share owner and blacklist subject are all `contract-caller`; the vault moves sBTC with `transfer assets contract-caller reserve`, so a contract deposits inside its own `as-contract?` with `(with-ft '<sbtc-token> "sbtc-token" assets)`. There is no minimum argument: check the returned shares against your minimum (the outer `err` rolls the deposit back). Forward the shares if the beneficiary is someone else.
- `request-redeem (shares uint) (is-express bool)` returns a claim id; the claim `user` is `contract-caller`, and its hBTC moves into the vault (allowance `(with-ft '<token-hbtc> "hBTC" shares)`).
- `cancel-redeem (claim-id uint)` returns the hBTC of an unfunded claim; express claims cannot be cancelled (`(err u103009)`). `redeem (claim-id uint)` pays the sBTC to the claim's `user` regardless of who calls it, once the claim is funded (`ERR_NOT_FUNDED`) and its cooldown (`stacks-block-time`) has passed. Also `redeem-peg-out (claim-id btc-recipient max-fee)` and `*-many` variants.
- **A tracked claim can disappear:** Anyone may redeem a funded, cooled-down claim (the sBTC still goes to its `user`), and the vault then deletes it (`map-delete claims`); a later `redeem` or `cancel-redeem` on that id fails in `get-claim`. Read `get-claim` first, treat a missing claim as completed, and never `try!` across a list of claims, where one stale id blocks every other unwind.
- Value: `preview-redeem` of the held shares. hBTC is not one-for-one with sBTC. A queued claim cannot finance an atomic flash-loan repayment. Check ownership of both minted shares and queued claims, the affiliate encoding and the deployed version.

### Hermetica prices

- No production Hermetica contract accepts a Pyth Lazer update. USDh minting (`SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-v1-2`) takes an optional Pyth Core payload per call and checks it with Pyth Core v4 `decode-price-feeds` inside the transaction, without storing it. Pyth Core stopped publishing on Stacks (last BTC/USD price 2026-08-21), so oracle-priced sBTC minting has no fresh payload. Assets configured with feed id `0x00` (USDCx) are priced at a fixed $1 with no oracle.
- hBTC's share price uses no oracle: it is sBTC accounting, moved only by the rewarder's bounded reward updates.
- Hermetica's Lazer contracts exist only on a test deployer (`SP6XGBDAD800GGY6XF48AC27467W9PEHA6EPBGKJ`). Recheck before relying on either path.

### Hermetica test fixtures

- Repository `mainnet/contracts/hbtc/protocol/` (`vault-v1-2.clar`, state, reserve, controller) and its `Clarinet.toml`, which declares the deployed contracts as `[[project.requirements]]` and a pinned `repl.remote_data` height. Declare the Hermetica contracts your code calls from `SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D` (for a deposit, `vault-hbtc-v1-2`; add `state-hbtc-v1` or `token-hbtc` if you call them) as requirements with a pinned `repl.remote_data` height, and add others only if `clarinet check` or the fork run reports them missing; sBTC is provided by simnet.
- Resolve the exact dependency set in the [hBTC registry](addresses/hermetica.md) and verify live HQ membership and configuration before use.
