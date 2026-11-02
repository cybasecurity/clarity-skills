# Bitflow calls

Exact Bitflow DLMM and stable swap call shapes, pools and test fixtures. Providing DLMM liquidity from a contract (per-bin shares, the tag NFT allowance, valuation, pool migration) is in [DLMM liquidity positions](../../ecosystem/references/positions.md#bitflow-dlmm-liquidity-sbtcusdcx-pool-dlmm-pool-sbtc-usdcx-v-1-bps-10). Apply the [rules for every protocol call](../SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../SKILL.md#addresses-and-freshness) first.

## Bitflow

Resolve [current cores, routers and pools](addresses/bitflow.md); older address docs lag the app/API. Choose between a direct call and Stacks Swap as [choosing a swap venue](../SKILL.md#choosing-a-swap-venue) says. A larger version suffix does not prove readiness or an upgrade: match each deployed ABI and body independently.

- DLMM router `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2` binds `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1`. `swap-x-for-y-simple-multi (pool-trait x-token-trait y-token-trait x-amount min-dy deadline-time)` and `swap-y-for-x-simple-multi (pool-trait x-token-trait y-token-trait y-amount min-dx deadline-time)` return `(ok {in: uint, out: uint})`; `in` can be below the input when liquidity ends; the check is `out >= min`.
- **Orientation:** Read it from the pool's `get-pool` (`x-token`, `y-token`), not from its name. `dlmm-pool-sbtc-usdcx-v-1-bps-10` reports x = `sbtc-token`, y = `usdcx`, so USDCx to sBTC is `swap-y-for-x-simple-multi`. Wrong trait order fails the pool's token check.
- **Payer and recipient:** Both are `tx-sender`, which supplies the input and receives the output. A contract swapping its own funds runs the call in `as-contract?` with an allowance for the input (`with-stx` for the `token-stx-v-1-2` wrapper), captures the beneficiary outside the scope and transfers only the intended output.
- **Deadline:** `deadline-time` is an optional **timestamp in seconds** compared to `stacks-block-time` (`none` skips it), chosen by the transaction signer.
- **Call the router statically:** A router trait of your own must `use-trait` the router's own traits, `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-trait-v-1-1` and `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.sip-010-trait-ft-standard-v-1-1` (not the `SM1793...` SIP-010 copy in the registry); a local copy fails `BadTraitImplementation` at runtime against the real router.
- Bin bounds (`max-steps` in the `simple-range` forms, `max-unfavorable-bins` in `swap-multi`) cap cost and drift, not the final price; keep `min-*` meaningful.
- Stable swap core `SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-core-v-1-4`: `swap-x-for-y (pool-trait x-token-trait y-token-trait x-amount min-dy)` and `swap-y-for-x (... y-amount min-dx)`; swapper `tx-sender`; `min-dy` must be greater than zero and the output at least `min-dy` (equality passes). STX pools use `token-stx-v-1-2`, not Zest's wSTX.
- On a mainnet fork the pool's `pool-transfer` asserts `(is-standard recipient)`: a contract deployed by the default `ST...` simnet deployer fails with `err u3003`. Set `use_mainnet_wallets = true` ([dependencies](../../testing/SKILL.md#dependencies-and-fixtures)); swapping from a contract works on mainnet.

### Bitflow DLMM router: other forms

`dlmm-swap-router-v-1-1` under the `SP1PFR4V...` deployer binds the same `dlmm-core-v-1-1` as `dlmm-swap-router-v-1-2`, but takes no `deadline-time`, has no `simple-range` forms and walks up to 350 bins; the excerpt below is v-1-2. Pools are passed as a `dlmm-pool-trait-v-1-1` argument, and each swap needs the pool's own x and y token traits.

```clarity
;; fragment: interface excerpt; resolve the exact deployment before calling
;; Bounded walk: swap-x-for-y-simple-range-multi / swap-y-for-x-simple-range-multi add `max-steps`
;; (1..319) before deadline-time. The plain `-simple-multi` forms use 319.
;; Multi-pool: swap-multi (swaps (list 319 {amount, expected-bin-id, min-received, pool-trait,
;;   x-for-y, x-token-trait, y-token-trait}) max-unfavorable-bins deadline-time)
;; Same pool pair: swap-x-for-y-same-multi / swap-y-for-x-same-multi
```

- `max-unfavorable-bins` in `swap-multi` and the `same` forms caps how many swaps may land in bins worse than `expected-bin-id`.

### Bitflow stable swap pools

- Call the core that a pool reports in `get-pool` (`core-address`); a pool's version suffix does not identify its core. `stableswap-pool-stx-ststx-v-1-4` (x = `token-stx-v-1-2`, y = stSTX) reports `stableswap-core-v-1-4`. `stableswap-pool-sbtc-pbtc-v-1-1` (x = sBTC, y = pBTC) reports `stableswap-core-v-1-2` and accepts transfers and balance updates only from it, so a swap through `stableswap-core-v-1-4` fails.

### Bitflow test fixtures

- Repository: [bitflow-dlmm](https://github.com/BitflowFinance/bitflow-dlmm) `clarity/contracts/` holds `dlmm-core-v-1-1`, the pool trait and router v-1-1 (documented in `docs/dlmm-swap-router-v-1-1.md`), not router v-1-2. [bitflow](https://github.com/BitflowFinance/bitflow) `contracts/stableswap.clar` is an older stable swap with another interface, not `stableswap-core-v-1-4`. Test against the deployed contracts.
- Add `[[project.requirements]]` for the router, `dlmm-core-v-1-1`, `dlmm-pool-trait-v-1-1`, the pool, the SIP-010 trait it imports, and both tokens (sBTC is provided by simnet; do not add it). Pools hold real liquidity only with `repl.remote_data` at a pinned height; a freshly deployed local pool starts empty.
- Test min-out failure, empty liquidity, wrong pool/token order, fee/decimal boundaries, deadline boundaries and maximum route cost.
