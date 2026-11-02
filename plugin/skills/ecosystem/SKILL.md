---
name: ecosystem
description: "Compose one Clarity contract across Stacks protocols: flash loan, liquidation and swap flows, vault strategies into Zest, Granite or Hermetica, atomicity. Use when a contract calls two or more protocols."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Ecosystem

Never write a protocol call or an oracle interface from memory or prose: use the call shapes in this skill and the skills it links, and verify each deployment. [clarity:protocols](../protocols/SKILL.md) selects and verifies each dependency and holds the full interfaces (flash loans, liquidations, Bitflow, USDCx); this skill holds the rules for holding protocol positions, valuing a multi-protocol vault, ordering a flash-loan flow and testing on a mainnet fork.

Writing or changing contract code: also load `clarity:scholar` and `clarity:security`, and finish with the [build checklist](../start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- Callback, initiator, asset receiver and repayment payer can be different principals.
- Verify each lender's callback, payer and repayment semantics; do not assume an EVM interface.
- Check caller constraints, timing guards and runtime payload validation; ABI bounds alone do not establish accepted inputs.
- Owned balances can include locked funds; queued redemption cannot finance atomic repayment.
- An authorized current implementation can disable deposits while permitting withdrawals. Preserve that refusal; a governance override in a fixture does not prove the integration is available.
- A target that requires `contract-caller == tx-sender` rejects an unscoped router preserving the wallet sender. A scoped adapter acts on its own funds and position; it does not impersonate the wallet. A new helper changes `contract-caller`; its sender scope cannot authorize another contract's funds.
- Upgraded protocol wrappers may retain the native ledger or introduce a new token; inspect [upgrade architecture and compatibility](../upgrades/SKILL.md#durable-state-and-replaceable-logic) before changing addresses.
- Repository HEAD, a trait match and a submitted deployment payload do not prove the live implementation or permissions.
- Trait checks are structural and prove nothing about behavior: `impl-trait` and trait identity are not required (mainnet routers take the sBTC token, which has no `impl-trait`, through their own SIP-010 trait copies), and a contract with stub functions passes every check. Bind each role to its expected principal. [Trait arguments](../system-integration/SKILL.md#execution-model) says which check runs where, and why a partial mock that passes in simnet is rejected at broadcast unless it sits later in a list. A trait-typed parameter inside your own trait is compared by identity ([nested traits](../security/SKILL.md#calls-traits-recursion)).

## Establish feasibility

Build the requested operation's call graph and asset ledger before implementing its adapters.

- Record for every edge: caller contract/function, callee function, sender context, incoming/outgoing native asset, amount/fee scale, destination, authority, and expected response.
- Apply the [transfer authorization matrix](../assets/SKILL.md#transfer-authorization) to every asset and payment leg: inspect deployed guards and prove both user-funded and contract-funded paths through the complete call graph. Check each target's [entry policy](../security/references/authorization.md#sender-preservation).
- Compare payload bounds at every interface (oracle update, callback `data`, list maxima). If oracle data exceeds callback capacity, use authenticated operation state and a bounded session identifier.
- For automation, establish [position discovery and fresh valuation](../apis/references/positions-and-proofs.md#discover-positions-then-value-them), including contract-owned borrowers.
- Identify all functions already active on the stack at each edge, then prove the exact graph in the target VM rather than inferring feasibility from the trait.
- A viable structure may use one authorized orchestration contract with separate callback functions, or separate adapters when graph/permission constraints require it. Do not add contracts mechanically.
- Enforce a clean isolated account model or explicit per-operation accounting.

## Position contracts

By default, hold each protocol position in a small contract that serves exactly one owner contract (your vault or strategy); it isolates each position's balances and allowances. A vault may instead call a protocol directly from its own `as-contract?` scope when it accounts for each position explicitly; the allowance, payout and valuation rules below apply to that scope too. A position contract follows these rules:

- **One owner:** The owner starts as the deployer, `(define-data-var owner principal tx-sender)`, which hands it to the vault with an owner-only setter as a deployment step. After that, change it only through timelocked governance, never an open setter.
- **Owner-only:** Every public function asserts `(is-eq contract-caller (var-get owner))` and rejects a zero amount.
- **Exact allowances:** Each protocol call runs in the position's own `as-contract?` scope with a `with-ft` allowance for exactly what the protocol pulls, including the share token it burns or escrows on exit: Zest `v0-vault-*` `"zft"`, Granite `state-v1` `"lp-token"`, Hermetica `token-hbtc` `"hBTC"`, a Bitflow DLMM pool's `"pool-token"` plus its `"pool-token-id"` tag NFT.
- **Payouts only to the owner:** Read the owner before entering the scope and pass it as the protocol's `recipient`, or forward the proceeds to it.
- **Read-only values:** Expose a shares view such as `get-shares` (shares the position holds) and a value view such as `get-value` (underlying units at the protocol's current conversion, accrued interest included). The owner converts with a verified oracle price and counts only positions it recorded.
- Print an event for each owner change, supply and exit.

The vault pushes the funds and calls the position in one `as-contract?` scope whose allowance covers the pushed amount:

```clarity
;; fragment: inside your vault
(try! (as-contract? ((with-ft 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx "usdcx-token" amount))
  (try! (contract-call? 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx transfer amount current-contract .zest-position none))
  (try! (contract-call? .zest-position supply amount min-shares))))
```

## What differs between protocols

Supply, exit and valuation calls differ between protocols in ways that break a position when assumed. Check each point in the deployed source. [references/positions.md](references/positions.md) has verified calls for Zest vaults, Granite LP, Hermetica hBTC, Bitflow DLMM liquidity and swaps from a contract; [clarity:protocols](../protocols/SKILL.md) holds the full interfaces.

- A deposit may return the shares minted (Zest, Hermetica) or only `(ok true)` (Granite). When it returns no count, measure the share balance before and after.
- When a deposit or exit takes no minimum argument (Granite, Hermetica deposit), check the returned or measured amount against your own minimum in the same transaction.
- Shares may be a token your contract holds (Zest z-tokens, hBTC), a balance inside protocol state (Granite `state-v1`), or per-bin balances (Bitflow DLMM: a `pool-token` FT plus a `pool-token-id` tag NFT per bin, which the pool burns and re-mints on every withdrawal and every add to a bin you already hold). Exit burns or escrows them, so the `as-contract?` scope needs a `with-ft` for the share token and a `with-nft` for a tag; a missing one returns `(err u128)`, the code for an outflow no allowance covers ([exact allowances](#position-contracts)).
- An exit pays a `recipient` argument (Zest, Granite) or the caller (Bitflow DLMM withdrawals pay `tx-sender`); forward the caller's proceeds to the owner.
- An exit may settle at once but only up to idle liquidity (a lending market while funds are borrowed) or a rate limit (Granite withdrawal caps), or be queued (Hermetica: request, funding and cooldown, then claim). When anyone may complete a claim, treat a missing claim as completed, and never `try!` across a list of claims.
- Governance can disable deposits, pause or cap supply, and a vault can refuse deposits while a flash loan on it is open. Read the flag first (Hermetica `check-is-deposit-enabled`), and decide whether a refused deposit is held, routed elsewhere or reverts the operation.
- A protocol can move a pool to a new core contract: Bitflow admins can migrate a DLMM pool after a cooldown they set (currently 14 days, at least 7), after which the old core and its routers reject the pool (`u1060`). A position that hardcodes them can no longer exit; take the core as a `<dlmm-core-trait>` argument checked against the `core-address` the pool reports (`get-pool`).
- A pool may check the recipient with `is-standard`, which fails on a mainnet fork for a contract deployed by a testnet (`ST...`) deployer. Deadlines may be Stacks block heights (Stacks Swap) or seconds (Bitflow).

## Vault composition rules

### Allocate

1. Group destinations by the asset each one takes. Swap once per asset pair rather than once per destination, with `min-out` for the whole amount, then split the amount actually received by the planned proportions. Choose the venue as [choosing a swap venue](../protocols/SKILL.md#choosing-a-swap-venue) says.
2. Deposit each slice from an `as-contract?` scope with a `with-ft` allowance of exactly that slice. Where the deposit takes no minimum, check the measured shares against a minimum the caller supplies.
3. Record shares per position, whether a token the vault holds or a balance in protocol state ([what differs](#what-differs-between-protocols)).
4. Key minimum outputs and obligations by native asset identity (and pool/bin ID for SFT shares). Aggregate slippage across routes only when outputs share the economic unit and recipient; enforce the net amounts received, fees included.

### Value

- Value every position at what it is worth now, in the vault's unit: the protocol's share-to-asset conversion (Zest `convert-to-assets`, Granite `utility` `get-market-state` totals, Hermetica `preview-redeem`, including accrued interest, fees and rounding), times a fresh verified oracle price for assets other than the vault's unit.
- **Never carry cost basis:** After a swap, book the amount received, not the amount spent. Holders who exit before an unwind would leave price losses (or take gains) from the rest. A stored total may lag execution; later entrants must not capture earlier holders' unrecognized yield.
- **Value exits net and round toward the vault:** Subtract any exit or redemption fee the protocol charges (check the deployed source), and round each conversion down for assets the vault holds and up for amounts it owes. A gross or rounded-up value overstates NAV, and the next depositor pays for it.
- **Value only positions the strategy recorded:** Count the shares it received from its own deposits. Reading live share balances lets anyone donate dust shares, adding a leg that needs a fresh price and blocks every deposit and exit without one.
- **Never use a DEX pool's spot or active-bin price:** It can be moved within the same transaction. Recommend a verified oracle price. A price a keeper or admin passes in is a trust assumption: use it only when the design needs it, bounded as [oracles](../oracles/SKILL.md) describes, and tell the developer which party it trusts.
- Pyth stores no live price on chain: Pyth Core's Stacks feeds stopped updating (yet still return their stale values), and a Lazer instance only verifies a signed update inside the transaction that carries it, so it has no price to read without one. Each protocol verifies through its own Lazer instance (Zest and Granite run their own); deploy yours as [Lazer instance for your protocol](../oracles/SKILL.md#deploy-a-lazer-instance-for-your-protocol) describes. DIA's push oracle does store BTC/USD, set by one updater key ([DIA](../oracles/SKILL.md#dia-usdhusd)).
- Take a price only from your Lazer instance's `verify-price-feeds(update, decoder, (some max-age))` (the decoder must be the instance's configured one), then require the configured feed ID and exponent (feed 1 BTC/USD at -8), a positive price before any uint conversion, a minimum publisher count, `confidence * 10000 <= price * max-bps`, and a per-feed timestamp no later than the envelope's and within `max-age` (microseconds: divide by 1,000,000). Exact checks and fragment: [price checks](../oracles/SKILL.md#lazer-price-checks). Pick one pattern:
  - **Update per call:** Every function that uses the share price (deposit, claim, rebalance) takes the Lazer update as an argument, as Zest's and Granite's markets do, and verifies it in the same transaction.
  - **Verified mark:** Anyone may store `{price, timestamp}` by calling a function that verifies a newer signed update (replays and older updates refused); readers reject a mark older than a documented maximum age. The keeper chooses when, never the price; an admin price override, if any, is bounded and timelocked.
  - Staleness halts what depends on it: a stale mark blocks deposits and claims priced from it. If deposits must stay open, take the update per call.
- Bound or reject a stale or unavailable price with an error instead of `unwrap-panic`, which would block every deposit and claim.
- Count a pending redemption once, as receipt shares, a claim or returned cash according to its lifecycle. Separate NAV from immediately spendable liquidity and from unsecured capital with no repayment claim.

### Liquidity and share minting

- Keep enough of the vault's asset idle for matured withdrawal requests (or support partial claims) before deploying funds; otherwise a request can expire unpaid. When liquidity is short, settle matured requests in request order (FIFO) or pro rata, never in an order the caller picks; otherwise the first caller or a keeper decides who exits. A FIFO head that cannot settle blocks everyone behind it: refuse requests below a minimum size, close a request whose payout rounds to 0, and never require a non-zero payment to advance the head. Protocol exits can be queued or liquidity-bound ([what differs](#what-differs-between-protocols)).
- Capital that is out (lent, deployed, released to an operator, in transit) counts at what it can still return: outstanding debt, a recorded claim, or the verified value of the positions it bought, never the amount released when the operator need not return it. Write it down only when it cannot come back; pricing deposits as if it were gone hands its return to new depositors. It never blocks deposits or claims: settle claims from the liquid balance, partially when short. No `unwrap-panic` on a path that deposits, claims or exits.
- Mint vault shares against the current valuation, reject 0-share mints and take a caller-supplied `min-shares`. A valuation that reads live balances is open to the first-deposit donation attack: defend it with virtual shares and assets, seeded dead shares or internally tracked assets ([A29](../security/references/patterns.md#a29-first-deposit-and-donation-share-inflation)).

### Allowance scope

- A contract that deposits, swaps, repays, redeems or queues a withdrawal with its own assets (for example `request-redeem`, which escrows its shares) makes that call inside `as-contract?`, with an allowance for everything that leaves. Protocols pull from `tx-sender` or `contract-caller` ([position calls](references/positions.md)); without the scope `tx-sender` is still the user, so the pull from your contract fails on mainnet even when a mock that books shares in a map passes.
- `as-contract?` is not an ERC-20 approval; it bounds asset outflows during a sender-context scope.
- Use `with-ft` with the exact token contract, native asset name and intended gross outflow, or `with-stx` for native STX.
- Allowance expressions evaluate before the body: reserve quantities and fee bounds before entering the scope. Changing a variable inside the body does not increase the allowance.
- A nested `as-contract?` still counts against every enclosing scope: an outer scope must allow the sum of all outflows beneath it.
- Burns are outflows. Exiting a position whose shares the protocol burns or escrows needs a `with-ft` allowance for the share token as well as for anything sent out. Test exits against the real share token: a mock that books shares in a map hides this.
- A callback can reach other contracts under inherited sender authority. Use the smallest practical scope and verified dynamic targets; never `with-all-assets-unsafe` to make a composition pass. A missing allowance can be a correct refusal of an unaccounted outflow.

## Flash-loan liquidation

Read [references/flash-loans.md](references/flash-loans.md) before building a flash-loan liquidation: which lender to pick for the debt token of the position being liquidated, and the call order of one orchestration contract that is also the lender callback, with a Zest liquidation as the worked example.

### Flash-loan rules

- Start the outer loan under the sender and allowance context its repayment needs: the contract that owes repayment must be able to authorize the token pull through the full call chain.
- Reserve **every** loan's principal and rounded fee in its own asset; a large balance in another asset does not repay it. An explicit transfer to a lender is not repayment if the lender later also pulls the debt; treat the lender's success as necessary evidence.
- Deposit profit after the lender returns, so repayment funds are not locked in shares; if a design deposits inside a callback, prove the remaining repayment reserves separately. Count as profit only this operation's balance change (after minus before), not the contract's whole balance, which can include funds reserved for other obligations; for sBTC, read `get-balance-available`, since `get-balance` includes locked units that cannot move.
- The VM detects repeated active **function identifiers**; not every return to a different function in the same contract is forbidden, and application guards can be stricter. Re-entering a lender or vault operation that is still active can fail even through a different route, and a liquidation may internally call that same vault's accrual and repayment paths. With a Zest sBTC loan against a position whose debt is sBTC, the vault is both lender and debt vault: it guards `deposit` and `flashloan` during a loan but not `system-repay`. Prove the exact graph in simnet against the real market.
- If one provider is sufficient, avoid a second fee and call graph. Nest two loans only when the complete graph is valid; unwind in reverse order.
- Pass a same-contract callback as a trait argument checked with `(is-eq (contract-of cb) current-contract)`: a literal of the contract's own name does not resolve at deployment.
- Oracle data: match the protocol's exact verifier and payload format; current Lazer consumers take the signed update in the call ([oracles](../oracles/SKILL.md)). A Lazer instance can charge a per-verification fee in STX from `tx-sender` (currently 0 on the Zest and Granite instances): read `get-fee`, and allow it with `with-stx` when verifying inside `as-contract?`.

## Integrate

- Establish language version, epoch, target network and each deployment. Use the [protocol registry](../protocols/references/addresses.md) with its [freshness rules](../protocols/SKILL.md#addresses-and-freshness) and [source/ABI evidence](../apis/SKILL.md#read-state-and-transactions).
- Select capabilities in [clarity:protocols](../protocols/SKILL.md). For swaps, choose a direct Bitflow call or Stacks Swap as [choosing a swap venue](../protocols/SKILL.md#choosing-a-swap-venue) says, comparing live output and execution cost.
- Record mutable registries, whitelists, pauses, fees, liquidity, oracle configuration, native asset names and decimals.
- Build the actor/asset ledger, the active-function graph and the per-asset transfer authorization check before writing adapters ([establish feasibility](#establish-feasibility)).
- In each lender callback, assert `contract-caller` is the expected lender endpoint and that an operation your entry point stored is active.
- Reserve each debt and rounded fee in its own spendable asset, and deposit only this operation's surplus.
- Preserve narrow allowance scopes and actual token authorization. Prove synchronous feasibility separately from queued settlement.
- Default to Clarigen for typed integration tests. Follow [dependency fixtures](../testing/SKILL.md#dependencies-and-fixtures) and verify the real parser/token behavior; run every leg at least once against the real contracts on a pinned fork.
- Read [references/testing.md](references/testing.md) before writing the fork setup (requirements, pinned `initial_height`, `use_mainnet_wallets = true`, funding from a real holder) or the integration tests, whose scenarios for the entire operation it lists.
- Deliver implementation, deployment evidence, permissions, tests and measured costs. Identify any unsupported leg precisely rather than fabricating an interface. State whether the result has only simulator coverage or also a pinned devnet/remote-state run; do not call it production-ready while deployment identity, permission or real-oracle behavior is unverified.

## References

- [sBTC](../assets/SKILL.md#sbtc), [Pyth fixtures](../oracles/SKILL.md#signed-fixtures), [staking](../staking/SKILL.md): load only for those legs.
- [Stacks primer](../system-integration/SKILL.md): platform context when needed.
- [Versions](../epochs/SKILL.md) and [model corrections](../epochs/SKILL.md#recall-corrections): resolve compatibility or recall gaps.
- Use the focused assets, oracles, staking, testing and APIs skills for deeper work. Ordinary integrations do not require every audit/compliance workflow.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
