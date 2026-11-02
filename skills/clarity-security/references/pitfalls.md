# More native behavior pitfalls

Check [VM documentation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs), implementation and target version. Resolve epoch-wide changes through [versions](../../clarity-epochs/SKILL.md).

### Callback guards

- Before adding a persistent `busy` lock, identify a reachable callback, the entry point it can access and the invariant it can violate. External calls alone do not justify a lock.
- The VM blocks active-function recursion; a different function can remain callable. Trace exact dependencies, caller checks and transient state before choosing a repair.
- Prefer appropriate authorization and safe state ordering. If a shared lock is needed, test the violating callback, legitimate composition and rollback; include affected read-only consumers in the review.
- Locks add storage reads/writes and cleanup paths. Remove unsupported guards without removing authorization bundled into their helpers.

### Numbers, buffers, strings

| Topic | Pitfall |
|---|---|
| `uint`/`int` | 128-bit. `a*b` must fit even if `a*b/d` would; Curve-style invariants with 18-decimal tokens overflow quickly. No 256-bit type. |
| `buff-to-int-be` / `-le` | ≤ 16 bytes; shorter input is **zero-padded, not sign-extended**: `(buff-to-int-be 0xffffffff)` = `4294967295`. Sign-extend signed wire fields with shifts. |
| Comparisons | `<`, `>`, `<=`, `>=` compare buffers and strings lexicographically (Clarity 2+). Do not convert hashes to `uint` to order them (lossy past 16 bytes). |
| `(buff N)`, `(string-ascii N)`, `(list N T)` | `N` is a maximum. Check exact lengths of hashes, txids, keys, IDs with `len`. |
| `concat` | Two arguments before Clarity 6. The result's max length is the sum of the inputs' maxima, so storing it into a narrower field needs `as-max-len?` (a checked cast that returns `none`, not truncation). |
| `as-max-len?` + `unwrap-panic` in folds | An undersized accumulator bound makes growth abort when the checked cast returns `none`; it does not truncate the list. |
| `element-at` / `index-of` | Clarity 2+ adds `element-at?`/`index-of?` aliases; both spellings work. |
| `to-consensus-buff?` | Returns an optional (none if too large). Use for hashing/signing (SIP-018), not JSON text. |

### Time and blocks

| Name | Pitfall |
|---|---|
| `block-height` | Clarity 1–2 only; after Nakamoto it is the **tenure** height. Does not exist in Clarity 3+. |
| `stacks-block-height` | Advances every few seconds with variable cadence. N blocks is not a duration. |
| `burn-block-height` | ~10 minutes per block; many Stacks blocks share one. Interest accrued per burn block is zero inside a tenure. |
| `get-stacks-block-info? time` / `get-block-info? time` | Past blocks only; `(- stacks-block-height u1)` is the *previous* block's time (lags, sometimes by 25+ minutes after Bitcoin stalls). |
| `stacks-block-time` | Clarity 4+: the current block's timestamp. Miner-chosen within consensus bounds (strictly increasing, may run up to ~15 s ahead), so do not rely on sub-15-second precision. |
| `at-block` | Throws for existing contracts from epoch 3.4; new contracts cannot use it. |
| Mixed clocks after upgrades | State written in burn heights and later compared with Stacks heights (or seconds) underflows and aborts every accrual. |

### Cryptography and principals

| Name | Pitfall |
|---|---|
| `secp256k1-recover?` / `secp256k1-verify` | Recovery accepts high-S; verification rejects it but ignores a permitted recovery byte. Neither makes signatures unique or authorizes the recovered key: apply the [signed-authorization rules](authorization.md#signed-authorizations). Recovery returns a 33-byte compressed key; `secp256k1-decompress?` exists from Clarity 6. |
| `secp256r1-verify` | Clarity 4 hashes `message-hash` again (double SHA-256); Clarity 5+ uses it directly. NIST P-256, not the Bitcoin curve. |
| `principal-of?` | Clarity 1 contracts return a **testnet** principal on mainnet forever (the fix applies only to Clarity 2+, per `special_principal_of`). The VM doc note says "fixed in 2.1", which is true only for newer contracts. |
| `is-standard` | True when the principal's version matches the current network, including **contract** principals. It is not an "is a wallet" check. |
| `principal-construct?` | Other-network version bytes return an `err`. `0x16`/`0x14` = mainnet single-/multi-sig, `0x1a`/`0x15` = testnet. |
| `is-in-mainnet` | Easy to invert in a guard. Plain simnet, devnet and testnet run only the testnet branch; a [mainnet fork](../../clarity-testing/SKILL.md#mainnet-forks) runs the mainnet branch, so test both. |
