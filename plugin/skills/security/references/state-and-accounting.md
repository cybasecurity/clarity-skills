# Clarity security: state and accounting

## State and accounting

### Snapshots and writes

- A `let` value is a snapshot, not a reference to storage. `merge` builds a new tuple; `map-set` replaces the whole stored tuple and returns `true`.
- Read → accrue/update/callback → merge the old tuple can erase the intervening update, including fields untouched by the final patch.
- After a mutating call, use its authoritative returned state or read again. Check every later write and calculation using earlier locals, including bad-debt settlement after repayment.
- Prefer one calculated next-state tuple and one write when no intervening effect is required. Removing a read is unsafe if the value can change.

```clarity
;; fragment
;; old was read BEFORE refresh-position changed storage.
(refresh-position account)
;; Unsafe: overwrites refreshed fields with old values.
(map-set positions account (merge old {amount: next-amount}))
;; Instead merge from refreshed state, or have refresh-position return it.
```

### Cache validity

- A block-height tag alone proves neither freshness within the block nor completeness across dependencies.
- Test two transactions in one block and multiple calls in one transaction. Deposits, repayments, fees, configuration changes and callbacks may invalidate cached ratios without advancing the clock.
- Separate caches valid solely for time-based accrual from values dependent on mutable balances, prices or configuration. Include those dependencies in invalidation or recompute them.
- Populate required indexes before pricing dependent shares; test both cold and warm paths. A prior transaction must not be required merely to make liquidation executable.
- Keep views and execution consistent: previews may calculate pending accrual without writing, but must include fee-share dilution and the same rounding/configuration as settlement. Document deliberately stale getters.

### Packed registries and parallel lists

- Clarity integers have 128 bits. `bit-shift-left`/`bit-shift-right` reduce the shift count modulo 128; left shifts discard high bits. Arithmetic overflow checks do not protect bitmap IDs.
- Validate IDs before shifting, including domain offsets: two 64-bit domains require IDs below 64 in each domain. ID 128 aliases ID 0 in `(bit-shift-left u1 id)`.
- Bound packed fields before truncating/slicing. Prove encode/decode round trips at zero, maximum and one beyond; check signed bin IDs, sentinels, endian order and field overlap.
- Keep forward/reverse maps, masks, bucket lists and counters consistent on insertion, update, removal and migration. Reject duplicate identities even when their numeric IDs differ; verify hardcoded ID-to-principal assumptions against initialization order.
- Handle the `false` results of `map-insert` (existing key) and `map-delete` (absent key) explicitly when uniqueness/existence matters.
- Compute capacity from the smallest internal buffer/list/accumulator, not just the public parameter type. Include headers and length prefixes; test every supported cardinality for unrolled parsers and the final partial batch.
- Multi-sequence `map` is positional, not a key join. Validate equal lengths when inputs must correspond; match signer keys to authorized weights rather than zipping a signer subset against a full roster.
- From epoch 4.0, iteration stops at the shortest sequence; earlier VM paths have the off-by-one in the [`map` row](../SKILL.md#responses-and-control-flow). Reproduce historical behavior in its epoch, and never use that discrepancy as input validation.

### Amounts and checkpoints

- Label raw assets, scaled debt, shares, indexes, prices and percentage scales separately. They can all be `uint` while representing incompatible units.
- Add new debt using the current index; preserve corresponding market/vault scaled deltas. Repeated scale → unscale conversions can leave residual debt or erase debt in only one ledger.
- Reconcile liquid funds, receivables, accrued fees, claim liabilities and share supply. Accrued interest is not necessarily cash available for withdrawal.
- Settle old-rate accrual before changing rates/fees or ownership when that is the intended policy. Check whether pausing freezes accrual, payouts or both; do not silently charge a new rate retroactively.
- Reward checkpointing must be idempotent with no new accrual. A getter returning saved + new rewards must not be added to saved rewards again.
- During zero-stake periods, advance time/checkpoints according to the reward policy without granting later entrants historical rewards. Keep liabilities per pool when balances are shared.
- Test quote and execution at ±1 native unit, low-decimal assets, zero supply/assets/debt and complete insolvency. Bound intermediate products even when final results fit.
- Reordering divisions changes rounding: `floor(a*k) + floor(b*k)` need not equal `floor((a+b)*k)`. An inverse quote must cover the execution path's independently rounded fees.
- Test all-debt-repaid/full-exit paths separately from partial repayment and liquidation. A zero denominator or mandatory zero-value transfer can make the last position impossible to close ([A27](patterns.md#a27-zero-and-self-native-transfers-abort-whole-flows)).
- For shared queues, test a user who sets an impossible payout limit and never cancels, and a request too small to pay anything (1 share). Preserve other users' settlement paths unless blocking FIFO is an explicit requirement.

### Disabled assets and repair paths

- Define what each flag means: block new exposure, stop transfers, exclude valuation, disable liquidation or revoke a role. Do not infer all effects from an `enabled` name.
- Disabling new borrowing must not silently erase existing debt from health/accounting. Retain enough registry data to decode existing positions and settle claims.
- Disabled collateral policy is protocol-specific. Apply it consistently to valuation, withdrawal, seizure, risk-group selection and bad-debt recognition; neither blanket exclusion nor blanket seizure is universally correct.
- Adding collateral or repaying can change an asset mask and select a worse risk group. Check transitions and authorization even for operations that appear only beneficial; avoid needlessly blocking partial repairs of unhealthy positions.
- For pause/unpause and cap changes, test repayment, withdrawal and liquidation together. Assess any grace period against solvency; do not prescribe a universal delay.
- Test cyclic deposit/withdraw and borrow/repay against rate limits. Distinguish gross volume, net outflow and time-weighted exposure; inflow credits can enable bypass, while gross-only caps can enable cheap denial of service.

Sources: [VM function documentation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs), [arithmetic](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/arithmetic.rs), [sequence iteration and epoch dispatch](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/sequences.rs), [Stacks function reference](https://docs.stacks.co/reference/clarity/functions). Verify the target revision/epoch.
