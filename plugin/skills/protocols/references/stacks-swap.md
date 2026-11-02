# Stacks Swap calls

Exact Stacks Swap router call shapes, multi-hop and split routes, Stacking DAO conversion adapters and test obligations. Apply the [rules for every protocol call](../SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../SKILL.md#addresses-and-freshness) first.

## Stacks Swap

Zest Protocol's aggregator ([official overview](https://docs.zestprotocol.com/stacks/swap), [official contracts](https://docs.zestprotocol.com/stacks/swap/contracts), [selected addresses](addresses/stacks-swap.md)). Routers compose DEX/protocol adapters (Bitflow DLMM/XYK/stable, Velar, ALEX, Arkadiko, Stacking DAO conversions). Inspect the deployed source/ABI and canonical successful publication. Import implementations through Clarinet requirements; do not recreate router code or substitute a mock for production integration.

- Stacks Swap is not the default venue: choose it or a direct Bitflow call as [choosing a swap venue](../SKILL.md#choosing-a-swap-venue) says. Its quote service compares pools and can split or combine legs; the on-chain router executes the supplied route and does not search for a price. A quote is not an execution guarantee: keep meaningful limits and verify actual custody changes.
- Router families expose different signatures: resolve the quote's exact deployment and method; do not infer a contract or function from a name suffix or a documentation example.
- `zr-d-0` function `r-d` (one DLMM hop) takes, in order: `a0` DLMM adapter `<swap-trait-dlmm>`, `p0` DLMM pool `<dlmm-pool-trait>`, `xy0` direction (`true` = x to y), `is-stx-in`, `is-stx-out`, `t-in`, `t-out` (`<sip010-trait>`), `amount-in`, `min-out`, `deadline`, `skim-amount`, `max-skim`, `recipient`.
- The router pulls `amount-in` from **`tx-sender`** and sends the net output (after skim) to `recipient`. A contract swapping its own funds runs the call inside `as-contract?` with `with-ft` for the input and sets `recipient` to the intended holder.
- The DLMM adapter derives the direction from the input token versus the pool's `x-token` and ignores `xy0`; still pass the matching value. It calls the Bitflow router with minimum `u0`: the protection is the route's `min-out`, applied to the measured net delivery after skim.
- **Deadline:** `deadline` is an inclusive **Stacks block height** checked against `stacks-block-height` (Bitflow's DLMM router takes seconds instead; never pass one unit to the other). Take it as a function argument chosen by the transaction signer (tip height plus a bounded allowance, computed off-chain), with a name that states the unit, such as `deadline-height`. `(+ stacks-block-height u10)` inside the call always passes. The height unit is the router's requirement; it does not change the clock your own schedules use.
- `skim-amount` and `max-skim` are absolute output-token units, not basis points; `min-out` applies after skim. Official docs state no additional Zest fee for standard swaps; keep both zero unless a fee is explicitly intended.
- Fix or authenticate router, adapter, pool, token pair, direction, native-STX flags, amounts, recipient and limits; trait compatibility alone does not approve an adapter. For swaps an operator triggers, floor `min-out` from a verified oracle price where one exists for the pair; otherwise tell the developer the swap has no independent price floor.
- Native STX: STX allowances and the route's wrapper trait. Bitflow's `token-stx-v-1-2` differs from Zest's wSTX ([wrapper identities](../../assets/SKILL.md#stx-through-a-token-interface-zest-wstx)).
- Errors: `u1000` deadline passed, `u1001` skim over max, `u1002` insufficient output, `u1004` zero amount, `u1007` both sides STX.

```clarity
;; fragment: USDCx -> sBTC from a contract's own USDCx; pool x = sBTC, y = USDCx
(try! (as-contract? ((with-ft 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx "usdcx-token" amount-in))
  (try! (contract-call? 'SP3EWCDA3V8HCP64CSETSNYXZ25WC4AJ95EC0ZEST.zr-d-0 r-d
    'SP3EWCDA3V8HCP64CSETSNYXZ25WC4AJ95EC0ZEST.dlmm-adapter
    'SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10
    false false false                                 ;; xy0 (y -> x), is-stx-in, is-stx-out
    'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx      ;; t-in
    'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token ;; t-out
    amount-in min-out deadline-height u0 u0 recipient))))
;; sBTC -> USDCx: allowance on sbtc-token "sbtc-token", flags true false false, tokens swapped
```

### Stacks Swap multi-hop and split routes

- `r-dd` composes two DLMM hops; `r-dt`/`r-td` combine DLMM with a generic adapter. Verify the additional intermediate token interfaces and minimums in the exact ABI.
- Generic adapters (`bitflow-adapter`, `velar-adapter`, ...) use a `uint` pool ID in the route functions that take `swap-trait` arguments; do not pass a principal there.
- `split-router-v1.swap` requires exactly two path slots and at most four hops **across both paths**, despite the nested ABI maxima. Check zero-path rules, amount sums, hop continuity and output identity in the body.
- Preserve each hop's input/output identity and native flags. Intermediate values belong to the operation; unrelated pre-existing balances are not quoted proceeds.
- Bound route length and measure the complete caller graph, including nested adapter/protocol costs.

### Stacking DAO conversion adapters

- `stacking-dao-receipt-adapter*` converts stSTX/stSTXbtc through its bound protocol contract. Adapter `-3` binds conversion v5, while Stacking DAO's docs name v4. Different versions are separate deployments; verify quote selection and the actual bound conversion contract.
- `stacking-dao-stbtc-receipt-adapter` calls the bound stBTC core's `deposit` or `withdraw-idle`. The withdrawal depends on idle liquidity and returns the actual net sBTC output; it does not make queued redemptions atomic.
- Receipt IDs in these adapters are sponsor-scoped: unsponsored calls require `u0`; sponsored calls require a positive unused ID. Successful use is recorded; replay fails. Preserve these rules when composing multiple hops.
- Conversion availability, fees, pauses and authorization remain external state. A deployed adapter does not establish a currently executable route.

### Stacks Swap test obligations

- Exercise contract-owned inputs through actual public router paths, not a contract principal spoofed as transaction sender.
- Check height deadline boundaries, direction/native-flag mismatches, wrong adapters/pools/tokens, intermediate and final minimums, skim bounds, input/output deltas and unchanged unrelated balances.
- Cover the cases your route has: empty liquidity and partial delivery for every route; late-hop failure for multi-hop and split routes; paused conversions and sponsor receipt replay for Stacking DAO adapters; and rollback of any earlier steps in the same transaction.
- Record the selected route, source hashes, quote/state tip and measured costs. Keep local economic mocks separate from real-dependency execution evidence.
