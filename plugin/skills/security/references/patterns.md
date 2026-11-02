# Clarity security patterns

## Security patterns (A01-A29)

- Treat each pattern as a hypothesis for the target and trace its actual call graph. Reassess historical recommendations for newer epochs.
- Most entries give what goes wrong, the fix and what to test; A01 lists public write-ups and A27 a deployable vulnerable/fixed example.
- Distinguish language behavior, integration constraints, and accounting bugs made consequential by Clarity execution. Require reachable impact; API ergonomics/style recommendations alone are not vulnerabilities.
- Reports can be superseded or overbroad. Fixed historical findings support regressions, not claims of current vulnerabilities.

### Authority and dynamic contracts

#### A01: Sender authority forwarded through an attacker

- Wrong: at a privileged contract C, `tx-sender == admin` still holds on the path admin → untrusted B → C. If a contract A calls B inside legacy `as-contract`, B can impersonate A to C. Allowing `tx-sender == owner` **or** `contract-caller == owner` still accepts inherited owner authority.
- Example: NFT purchase → untrusted commission callback → another collection's listing/approval function. The callback creates cheap listings under the buyer's identity; later purchases cause the loss. Asset postconditions do not constrain listing, approval or admin state: assert stored prices, commission contracts and authority changes, even when no unexpected asset leaves during the initiating transaction.
- Fix: for contract-only roles, compare `contract-caller` to the designated contract; for deliberate user delegation, require explicit authorization binding the intended action, recipient and nonce. When trusted downstream calls need the user's sender, use an authenticated [entry policy](authorization.md#sender-preservation) rather than switching the payer to the contract. A blanket direct-call requirement can break legitimate multisigs/routers.
- Test: direct, trusted-router, arbitrary-router and changed-sender paths.
- Write-ups: [Setzeus on sender forwarding](https://www.setzeus.com/community-blog-posts/clarity-carefully-tx-sender) and [100proof's NFT callback analysis](https://100proof.org/a-questionable-design-choice.html). Historical examples require target-specific reachability checks.

#### A02: Trait confusion / wrong-role contract

- Wrong: traits specify interfaces only. Commission approval does not imply staking approval.
- Fix: validate `(contract-of value)` against the intended role/asset, not protocol-wide approval, supplied symbols or self-reported underlying tokens. Check every trait parameter, including both sides of a swap, a reserve, oracle, callback and governance proposal.
- Test: malicious contracts with matching ABIs; swapping two allowed roles; unrelated deployed targets; partial implementations that pass a readiness method but omit another operation (see [runtime trait args](../SKILL.md#calls-traits-recursion)).

#### A03: Allowance bypass outside `as-contract?`

- Wrong: a token accepting `contract-caller == sender` can debit its caller without an `as-contract?` wrapper. Restricted wrappers protect only their dynamic scope, not unrelated transfers.
- Converse: contract-funded payouts can fail for sender-only tokens.
- Fix: audit every outgoing call. Use the [per-asset authorization matrix](../../assets/SKILL.md#transfer-authorization), including treasury/rescue paths and helper-induced context changes.
- Test: downstream contracts that pull funds from their immediate caller.

#### A04: Broad asset allowances

- Wrong: `with-all-assets-unsafe`, wildcard FT names, overlarge limits, and both STX/FT allowances granted for one known asset widen the impact of a malicious dependency.
- Fix: identify native asset class, exact token name, maximum principal/fee outflow, and whether outflows are required. Every body expression must be non-response-typed; deliberately unwrap/propagate inner calls and handle the wrapper's response. Allowance expressions execute before the body; capture original actors outside. `restrict-assets?` bounds an explicitly chosen principal's outflows without switching context; read its target-version semantics.
- Test: failure after a transfer, and verify rollback.

#### A05: Approval based on the wrong deployment

- Wrong: deployment transaction inclusion proves neither success nor deployed-code identity. A deploy transaction can be mined without effect (v3 `status` `abort_by_response`, `abort_by_post_condition` or `problematic_skipped`): it creates no contract, yet its source stays visible in the transaction, and a later successful deploy of different code can reuse the same `<deployer>.<name>`.
- Fix: verify before trusting an address, never because "a deploy transaction with this source exists":
  1. `GET https://api.hiro.so/extended/v3/transactions/0x<txid>` (an unprefixed txid gets a 302 redirect) and require `status == "success"`, a mined `block.index_hash`, `type == "smart_contract"` and `smart_contract.contract_id` equal to the `<deployer>.<name>` you audited. v3 returns only the canonical mined record or a pending one, and has no `canonical` field. `GET /extended/v3/smart-contracts/<deployer>.<name>` names the successful deployment's `tx_id`, or answers 404 when none succeeded.
  2. `GET https://api.hiro.so/v2/contracts/source/<deployer>/<name>` and compare the returned `source` byte for byte with the audited source.
  3. Clarity 4+: compare `(contract-hash? .name)` (or the contract principal passed in) with the hash of the audited deployment. `contract-hash?` can help establish deployed-code identity; it does not prove benign behavior or immutable dependencies.

#### A06: Bad network principals / unusable roles

- Wrong: `is-standard` checks compatibility with the current network, including contract principals. It does **not** mean EOA, trustworthiness, an existing contract, or a private key known to someone.
- Fix: validate persisted authority/fee/recipient principals when foreign-network values would strand authority or funds. Omit redundant checks only when a later mandatory operation rejects the same value and propagates failure; preserve intentional error distinctions.
- Test: nominee acceptance in a two-step transfer demonstrates an authorized acceptance path; two calls by the old owner do not prove the nominee can act.

#### A07: Deployment-order and initialization hazards

- Wrong: top-level deployer identity differs from runtime caller identity. Cycles and absent external contracts prevent deployment (forward local references can work).
- Fix: inspect [dependency-sorted initializers](../../deployment/SKILL.md#deployment-time-execution), external dependencies and unchecked responses. Require initialization authentication, one-time behavior, and atomic deployment ordering where required.
- Test: immutable registry bindings initialize to the intended network/version.

### Tokens, clocks and accounting

#### A08: sBTC total is not transferable balance

- Wrong: sBTC's `get-balance` sums available and withdrawal-locked FTs; `get-balance-available` returns transferable units. Total supply likewise includes locked tokens. A transfer can correctly fail despite a positive total.
- Fix: do not infer liquidity, repay capacity, lending collateral backing or reward eligibility from an incompatible balance view. Do not alter external-token semantics in mocks to force passing integrations.
- Test: pending withdrawal, rejection/unlock, completion/burn, and donations.

#### A09: wSTX is not one universal token

- Wrong: some SIP-010 wrappers transfer native STX without an FT ledger; they require sender context and `with-stx`, not `with-ft` for the wrapper principal. Other wrappers custody/mint FTs. ALEX's fixed-decimal wrappers can scale micro-STX to 8-decimal units and introduce minimum transferable amounts/dust.
- Fix: use and audit the exact wrapper the target contract or protocol registers or checks, and verify its implementation and scales. New work uses Zest's wSTX where nothing requires another wrapper ([wSTX](../../assets/SKILL.md#stx-through-a-token-interface-zest-wstx)); that does not make other implementations equivalent.
- Test: wrappers with different decimals, zero/dust amounts, sender-only authorization, and post-conditions on the actual asset.

#### A10: Stale or fictitious 'now'

- Wrong: prior-block time is not current-block time. Consecutive operations can share timestamps; long gaps invalidate average-cadence assumptions. Clarity 1/2 `block-height` changes meaning after Nakamoto.
- Fix: use the target-version clock ([time and blocks](pitfalls.md#time-and-blocks)); do not treat previous-block time plus a fixed offset as current time.
- Test: exact expiry, same-block accrual, long pauses, future oracle timestamps, and negative-time subtraction.

#### A11: UInt128 intermediates and rounding direction

- Wrong: for `floor(a*b/d)`, both the quotient and `a*b` must fit unless using verified wider/decomposed arithmetic. `(x + d - 1)/d` can overflow.
- Fix: derive the domain of every product, exponent, scale and denominator. Apply [additive guard criteria](../../scholar/references/arithmetic-and-time.md#additive-range-checks): check both subtraction underflow and replacement-sum overflow (subtraction alone is not a vulnerability). Use quotient/remainder for ceilings where equivalent.
- Round assets paid and shares minted to preserve solvency: typical share vaults floor deposit shares and redeem assets, ceil shares burned for an asset withdrawal and assets charged for exact shares; verify the protocol's convention.
- Test: low decimals, largest configured caps, fee near 100%, one-unit amounts, repeated dust cycles, and frequent accrual.

#### A12: Receipt tokens vs actual asset movements

- Wrong: SIP-010-shaped getters/transfer wrappers can obscure economic identity. Public burns bypassing vault bookkeeping can desynchronize supply/accounting.
- Fix: do not double count the same collateral through aliases, duplicate asset entries, or both underlying and receipt tokens. For repayment/redemption, use actual returned amounts/state, not requests.

#### A13: Flashloan context and transient balances

- Wrong: balance during the callback excludes the lent principal. Clarity's call-cycle restrictions do not by themselves prove cross-contract accounting is safe.
- Fix: snapshot lender accounting deliberately. Do not price deposits from transient balance, book principal as fees, or assume the callback recipient is the repayment payer.
- Test: whitelist, fee ceiling rounding, zero-fee transfers, caller- versus sender-authorized tokens, and paused paths.

### Oracles, serialization and external consumers

#### A14: Pyth data and units

- Fix: verify feed ID, publisher/signature trust, freshness (including future values), exponent, positive price, confidence interval, and signed-to-unsigned conversion bounds.
- Units: Pyth Lazer envelope/feed timestamps use microseconds; legacy Core publish time and Clarity block time use seconds. Apply the [unit and migration rules](../../oracles/SKILL.md#timestamp-units). Wormhole/Pyth Core VAA/PNAU formats are not Lazer payloads.
- Test: sparse, duplicate and out-of-order feeds; reject silent omissions.

#### A15: Buffers, slicing, and partial validation

- Wrong: a `(buff N)` is a maximum size, not an exact size; fixed lists also specify maxima. `as-max-len?` is a checked cast, not a truncation function.
- Fix: require the exact lengths the protocol needs before indexing/slicing; verify endianness and two's-complement signed fields. Check property counts, trailing bytes, duplicate fields, unsupported channel IDs, recovery ID, and zero-valued data.
- Test: historical deserialization/type bugs require epoch-matched tests ([versions](../../epochs/SKILL.md)).

#### A16: Prints are protocol interfaces

- Wrong: missing admin/config prints impede monitoring; misleading prints can break bridges. Attackers can emit identical tuple shapes from other contracts.
- Fix (emitter): print structured action/version/actor/asset/amount/request-ID data with correct units and actor identity, following required standards.
- Fix (consumer): check emitting contract, committed transaction result, canonical block, topic/schema, and event index. Deduplicate by event identity, not transaction ID alone; one transaction can contain multiple valid burns/withdrawals. Bound payload sizes and page receipt streams.

#### A17: Local error namespaces

- Wrong: a forwarded `(err u1)` is not globally unique: it can originate from token, oracle, state, or caller code. Low values overlap native and boot/system errors. Signed `1` and unsigned `u1` differ, and some errors include a batch/allowance index, so literal constants do not enumerate the whole family.
- Fix: for new custom errors, prefer a documented higher range, such as `u1000`–`u1099`, or contract/module prefixes. This is a debugging convention, not a consensus reservation or global uniqueness guarantee. Retain provenance when wrapping, and preserve the error type as well as its value; preserve native/SIP conventions and existing public error ABIs. A caller that branches on errors must know their origin.
- Review duplicate constants within a contract; equal codes across independent contracts need not be vulnerable.

#### A18: Response handling in batches

- Wrong: `map` can collect responses without propagating their errors. A `fold` ignoring its previous error can resume after failure. A caller handling a public callee error can return `ok` and commit its own state.
- Fix: specify all-or-nothing or partial semantics.
- Test: failure at first/middle/last element; verify state and event outcomes.

#### A19: Execution budget as a liveness boundary

- Wrong: read-heavy cross-contract calls, repeated registry resolution, oracle verification, oversized lists/buffers and nested expression frames can make valid actions unexecutable. Worst-case external traits can exhaust caller budgets.
- Fix: separate per-input costs, aggregate transaction costs, memory, call stack and deployment-analysis constraints. Prove exits/liquidations remain usable at maximum supported state.
- Limits: call stack depth 64 before epoch 3.4 and 128 from 3.4. A default miner stops adding contract calls to a block once it passes 25% of the remaining tenure budget, but includes the call that crosses it; a call that overflows a tenure less than 20% used is dropped as too big. Value sizes and per-epoch block limits are in [versions](../../epochs/SKILL.md#resource-limits).
- Test: measure with `initSimnet(manifest, true, {trackCosts: true, trackCoverage: false})` and compare `receipt.costs` with the `/v2/pox` limits (the simulator can report older read limits; see versions). Test the deepest chain of `<trait>` callbacks at the maximum list size.

### PoX and asynchronous flows

#### A20: Wrong PoX generation and clock

- Wrong: assuming `.pox-4`; mainnet uses PoX-5. PoX-4 authorization IDs/reward addresses are not PoX-5's interface ([generation-specific rules](../../staking/SKILL.md#pox-generations)).
- Fix: resolve the live boot contract. Validate cycle/prepare-phase boundaries and the selected generation's signer authorization, manager callbacks, reward destination and caller permissions. Distinguish native STX spent from STX locked/staked; use the `with-stacking`, `with-staking` or `with-pox` allowance for the selected operation/version. The allowance name follows the contract's Clarity version, not the PoX generation: a Clarity 4 or 5 contract stakes into PoX-5 with `with-stacking`.
- For callback authority, fee snapshots and withdrawal liabilities, use the [PoX-5 signer-manager checks](../../staking/SKILL.md#pox-5-signer-managers).

#### A21: Reward weights and ownership across cycles

- Fix: settle historical rewards against historical entitlement before changing balance, delegation, signer manager or exclusions. Handle queued withdrawals and pending rewards in share price; do not apply current weights to prior-cycle rewards.
- Test: switching signer pools, joining/leaving near boundaries, late funding, and migration.

#### A22: Async withdrawal state vs synchronous success

- Wrong: accepted requests do not establish Bitcoin settlement or asset delivery. An attempted "flashloan → peg-out → redeem → repay" cannot finish atomically.
- Fix: maintain request IDs, partial completion, fees, cancellation, rejected requests and resumed settlement. Reserve accounting must distinguish available, locked, allocated and pending liabilities.
- Check [request/rejection cost asymmetry](../../bitcoin-proofs/SKILL.md#who-pays-for-failure): a cheap or underfunded request can force repeated operator-paid work on another chain.

#### A23: Canonical Bitcoin identifiers and replay state

- Wrong: a `(buff 32)` alone does not distinguish raw/internal/display byte order, so aliases of one outpoint can be accepted as different collateral.
- Fix: bind Bitcoin transaction ID, output index, network and verified owner using one canonical byte/serialization convention. Bind the Clarity-minted owner to the owner authenticated by the Bitcoin proof. Migrate used-nonce/outpoint state with bridge implementation upgrades so immutable old contracts do not leave the new implementation replayable. Apply current Bitcoin helpers only with version-matched byte-order/proof rules.
- Review [bridge reservations and inscription identity](../../bitcoin-proofs/SKILL.md#bridge-boundaries): cross-direction replay-map poisoning, utility-UTXO reuse, full inscription indexes and metadata/collection mapping.

### Payouts, state and guards

#### A24: Automatic rewards and aggregate postconditions

- Wrong: reward hooks or batched payouts can mix several recipients' transfers under one sender/asset total; incoming funds do not reduce that gross amount. A passing sender condition does not prove the user's expected receipt.
- Fix: check on-chain recipient/min-output constraints and the exact wallet policy. Review [flow design, coverage modes and reward checkpoints](../../wallets/SKILL.md#post-conditions). Current `Originator` mode eases coverage but does not add recipient guarantees.
- Test: both endpoints' pending rewards, stale quotes, refunds, unchanged totals sent to the wrong recipient, and save/claim replay. Batching alone is not a vulnerability.

#### A25: Stale tuples and incomplete caches

- Wrong: a later `map-set` from an old tuple can erase new fields; a block-height cache can miss another mutation in the same block.
- Fix: trace reads across accrual, repayments and callbacks; apply [state and accounting](state-and-accounting.md#state-and-accounting).
- Test: cold and warm paths, multiple transactions per block, and repeated calls without new accrual.

#### A26: Packed registries hide capacity and identity errors

- Fix: bound bitmap IDs before shifting, maintain forward/reverse indexes and derive capacity from the narrowest internal container. Validate positional lists before `map`; a signer subset is not a positional match to the full roster.
- Detail (shift modulo 128, domain offsets, round trips, capacity): [packed registries](state-and-accounting.md#packed-registries-and-parallel-lists).

#### A27: Zero and self native transfers abort whole flows

- Wrong: `stx-transfer?` and `ft-transfer?` return `(err u3)` for amount 0 and `(err u2)` when sender equals recipient; `ft-mint?`/`ft-burn?` return `(err u1)` for 0. A `try!` turns that into an abort of the whole transaction.
- Typical triggers: a fee that rounds to 0, the last repayment or a fully paid position, self-liquidation, a fee recipient that is also the user, a vault paying itself.
- Fix: skip the leg when the amount is 0 or the parties are equal, or reject the input deliberately: `(if (and (> amount u0) (not (is-eq tx-sender to))) (stx-transfer? amount tx-sender to) (ok true))`.
- Test: 0, 1 and dust amounts, and recipient equal to sender.

Vulnerable and fixed versions (deployable):

```clarity
(define-constant FEE_RECIPIENT 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM)

;; Vulnerable: fee rounds to 0 for small amounts, so (err u3) aborts the payment.
(define-public (pay-vulnerable (amount uint) (fee-bps uint) (to principal))
	(let ((fee (/ (* amount fee-bps) u10000)))
		(try! (stx-transfer? fee tx-sender FEE_RECIPIENT))
		(stx-transfer? (- amount fee) tx-sender to)))

;; Fixed: skip legs that cannot execute.
(define-private (send (amount uint) (to principal))
	(if (and (> amount u0) (not (is-eq tx-sender to)))
		(stx-transfer? amount tx-sender to)
		(ok true)))

(define-public (pay (amount uint) (fee-bps uint) (to principal))
	(let ((fee (/ (* amount fee-bps) u10000)))
		(try! (send fee FEE_RECIPIENT))
		(send (- amount fee) to)))
```

#### A28: `let` bindings run before the body's guards

- Wrong: bindings evaluate in order before the body. A `/`, `-`, `unwrap-panic` or contract call in a binding runs before the `asserts!` meant to guard it, so a bad input hits a runtime abort (no error code, uncatchable) instead of the intended `err`. A value read in a binding is a snapshot taken before any state change in the body; returning or emitting it afterwards reports stale state.
- Fix: put guards first (`begin` with `asserts!`, then `let`), or nest a second `let` after the guard; read state after the changes it must reflect.
- Test: an input that fails the guard returns the guard's error, not a runtime abort; returned or printed values reflect the state after the change.

```clarity
;; fragment
;; Vulnerable: (- bal amount) aborts with an underflow before the guard can return
;; ERR_INSUFFICIENT_BALANCE, and snapshot is read before total changes.
(let ((bal (default-to u0 (map-get? balances tx-sender)))
      (remaining (- bal amount))
      (snapshot (var-get total)))
  (asserts! (>= bal amount) ERR_INSUFFICIENT_BALANCE) ...)
;; Fixed: guard first, then compute; read state after it changed.
(let ((caller tx-sender) (bal (default-to u0 (map-get? balances tx-sender))))
  (asserts! (>= bal amount) ERR_INSUFFICIENT_BALANCE)
  (map-set balances caller (- bal amount))
  (var-set total (- (var-get total) amount))
  (try! (as-contract? ((with-stx amount)) (try! (stx-transfer? amount tx-sender caller))))
  (ok (var-get total)))
```

#### A29: First-deposit and donation share inflation

- Wrong: with `shares = amount * supply / assets`, a 1:1 mint into an empty vault, and `assets` read from the live balance, an attacker deposits 1 unit, then transfers a large amount directly to the vault. The next deposit rounds down to 0 or 1 share, and the attacker's share captures part of it. For example, after a 1-unit deposit and a 10,000-unit donation, a 15,000 deposit mints 1 share worth 12,500. A deposit that rounds to 0 shares does not silently donate: `ft-mint?` of 0 returns `(err u1)`, so a `try!`ed mint aborts it (griefing rather than theft).
- The same rounding hands any assets left after supply returns to 0 (dust, late yield) to the next depositor.
- Fix: use virtual shares and assets in **both** directions (deposit and redeem math), reject deposits that mint 0 shares (and redemptions that pay 0), and take a caller-supplied `min-shares`. With `VIRTUAL_SHARES` = 1,000,000 the attacker loses far more than the victim, whose loss stays small unless the donation is on the order of `VIRTUAL_SHARES` times the deposit. The ratio `VIRTUAL_SHARES / VIRTUAL_ASSETS` is the initial number of shares per asset unit (10^6 below), so give the share token the asset's decimals plus 6 or pick a smaller offset, and check the uint128 bound on `amount * (supply + VIRTUAL_SHARES)`. Alternatives: seeded dead shares (minted at initialization to a holder that never redeems) or internally tracked assets (direct transfers ignored; yield then needs explicit booking).
- Test: the donation sequence against the real valuation path (including deployed positions and queued shares), and a deposit after a full exit.

```clarity
;; fragment
(define-constant VIRTUAL_SHARES u1000000)
(define-constant VIRTUAL_ASSETS u1)
(define-read-only (preview-deposit (amount uint))
  (/ (* amount (+ (ft-get-supply share) VIRTUAL_SHARES)) (+ (total-assets) VIRTUAL_ASSETS)))
(define-read-only (preview-redeem (shares uint))
  (/ (* shares (+ (total-assets) VIRTUAL_ASSETS)) (+ (ft-get-supply share) VIRTUAL_SHARES)))
;; deposit (amount, min-shares): shares = (preview-deposit amount), checked before transfer and mint
(asserts! (> shares u0) ERR_ZERO_SHARES)
(asserts! (>= shares min-shares) ERR_SLIPPAGE)
;; redeem (shares): assets = (preview-redeem shares); (asserts! (> assets u0) ERR_ZERO_SHARES),
;; then burn the caller's shares and pay inside (as-contract? ((with-stx assets)) ...)
```
