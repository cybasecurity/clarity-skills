---
name: oracles
description: "Read prices in Clarity: Pyth Lazer signed feeds, DIA, staleness and confidence checks, test fixtures, migrating from Pyth Core. Use for any price feed or oracle."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Oracles

Use [Stacks Pyth Lazer](https://github.com/stx-labs/stacks-pyth-lazer) (Pyth Pro) for new Pyth integrations, and read a price only from a signed update that a Lazer instance verifies, with the checks below. Call the instance's real `verify-price-feeds`; do not invent a Pyth trait, a stored-price getter or other functions the verifier lacks. Your own adapter over the verified result is fine if it keeps every check below. Pyth Core no longer supports Stacks, as Pyth's [unsupported-chains page](https://docs.pyth.network/pro/no-longer-supported) states; prices stored in the Stacks Core contracts stopped updating. Keep the old [Core/Wormhole bridge](https://github.com/stx-labs/stacks-pyth-bridge) and its examples for legacy audits and migration. Upgraded Core remains available on other chains; its automatic-upgrade guidance does not establish Stacks compatibility.

Writing or changing contract code: also load `clarity:scholar` and `clarity:security`, and finish with the [build checklist](../start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- Lazer accepts different payloads from Core/Wormhole VAAs. Do not send Core VAAs/PNAU bundles to Lazer or reuse old feed identifiers without remapping.
- The current Stacks implementation returns verified feeds within the transaction and persists none, so a Lazer instance has no price to read without a signed update. Pyth Core's storage stopped updating (BTC/USD last published 2026-08-21), yet its `get-price` still returns the stale value without an error. DIA's pushed keys are live stored prices ([DIA](#dia-usdhusd)).
- Valid signatures do not establish the requested feed, positive price, confidence, channel or freshness.
- Lazer envelope and per-feed timestamps use microseconds; legacy Core used seconds; verifier age limits remain seconds ([units](#timestamp-units)).
- A local fixture parser can accept fields its mainnet consumer rejects.
- Relayer names and README examples can describe obsolete storage interfaces: the [stx-labs relayer](https://github.com/stx-labs/stacks-pyth-lazer-relayer) calls `verify-and-update-price-feeds` and reads `pyth-lazer-storage.get-price`, both absent now. Match executable source and ABI.

## Lazer consumer rules

The [current oracle source](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/contracts/pyth-lazer-oracle.clar) and [decoder](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/contracts/pyth-lazer-decoder-v1.clar) define the interface.

- Call the instance's `verify-price-feeds` with the signed update (`(buff 8192)`), the decoder contract and an optional `max-age` in seconds (`none` uses the governance configuration). `max-age` replaces that threshold rather than tightening it: `(some u86400)` accepts a day-old update even where governance set 7,200 s, so enforce your own freshness on the per-feed timestamp. The result carries the envelope `timestamp` (microseconds), its `channel` and `price-feeds`, a list of feed tuples.
- The current implementation accepts an `evm` envelope: secp256k1 over `keccak256(payload)`. The verifier checks signature, trusted signer and envelope age; it does not apply your feed, channel, duplicate, future-time or per-feed freshness policy.
- **Decoder:** Pass the instance's configured decoder: `verify-price-feeds` rejects any other (`ERR_INVALID_DECODER`), and only the oracle may call the decoder's verification. Governance can rotate the decoder, so take it as a `<decoder-trait>` argument rather than a constant that stops every read after a rotation.
- Each feed tuple is `{feed-id: uint, price: (optional int), exponent: (optional int), publisher-count: (optional uint), confidence: (optional uint), best-bid: (optional int), best-ask: (optional int), funding-rate: (optional int), funding-timestamp: (optional uint), funding-rate-interval: (optional uint), market-session: (optional uint), ema-price: (optional int), ema-confidence: (optional uint), feed-update-timestamp: (optional uint)}`. A successful decode may leave optional properties empty: require price, exponent, confidence, publisher count and per-feed timestamp.
- **Instance:** The documented model is one governed instance per consumer, not a public shared oracle; check current upstream service/access terms. Zest v2 (`SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-oracle`) and Granite (`SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-oracle`) each run their own ([addresses](../protocols/references/addresses/pyth-lazer.md)). Anyone can call `verify-price-feeds` on any instance, but its governance decides which signers it trusts and can replace them at once, even while the instance is paused, and so sign any price. Calling another protocol's instance makes its governance your price authority; deploy your own ([deploy your own instance](#deploy-a-lazer-instance-for-your-protocol)).
- Verify signer rotation/expiry, fees charged to `tx-sender`, pause state and decoder governance at the target deployment; include oracle fees and caller authority in the full call graph.

## Lazer price checks

After `verify-price-feeds` succeeds, require all of these for the feed you use:

- The configured feed ID is present (select it from `price-feeds`; missing is an error). Feed 1 is BTC/USD, 7 USDC/USD and 45 STX/USD, each at exponent -8.
- The exponent equals the configured one, and the price is present and **positive**; convert the signed price to uint only after that guard.
- `publisher-count` at least a configured minimum.
- Confidence within a bound of the price: `confidence * 10000 <= price * max-bps`.
- The per-feed `feed-update-timestamp` is no later than the envelope `timestamp` (a fresh envelope can carry a stale feed) and fresh: `feed-time-us / 1000000 + max-age >= stacks-block-time`.

```clarity
;; fragment: verify one Lazer feed inside the transaction that uses its price
(let ((decoded (try! (contract-call? .pyth-lazer-oracle verify-price-feeds
          update .pyth-lazer-decoder-v1 (some MAX_AGE))))
      (feed (unwrap! (element-at? (filter is-feed (get price-feeds decoded)) u0) ERR_FEED_MISSING))
      (price (unwrap! (get price feed) ERR_BAD_PRICE))
      (confidence (unwrap! (get confidence feed) ERR_WIDE_CONFIDENCE))
      (feed-time-us (unwrap! (get feed-update-timestamp feed) ERR_FEED_STALE)))
  (asserts! (is-eq (get exponent feed) (some EXPONENT)) ERR_BAD_EXPONENT)
  (asserts! (> price 0) ERR_BAD_PRICE)
  (asserts! (>= (default-to u0 (get publisher-count feed)) MIN_PUBLISHERS) ERR_LOW_PUBLISHERS)
  (asserts! (<= feed-time-us (get timestamp decoded)) ERR_FEED_STALE)
  (asserts! (>= (+ (/ feed-time-us u1000000) MAX_AGE) stacks-block-time) ERR_FEED_STALE)
  (asserts! (<= (* confidence u10000) (* (to-uint price) MAX_CONF_BPS)) ERR_WIDE_CONFIDENCE)
  (ok {price: (to-uint price), time: (/ feed-time-us u1000000)}))
```

`is-feed` is a private predicate over the feed tuple above that compares `feed-id` with the configured ID. Choose and document your own bounds, such as `MIN_PUBLISHERS u3`, `MAX_CONF_BPS u100` (1%), `MAX_AGE u60` seconds and, for a mark, `MAX_MARK_AGE u900` seconds. The fragment calls your own instance, deployed beside the consumer ([deploy your own instance](#deploy-a-lazer-instance-for-your-protocol)). Its hard-coded decoder is for brevity only (see the decoder rule above).

Two patterns:

- **Update per call:** Functions that use the price take the update as an argument and verify it in the same transaction (Zest's and Granite's markets do this).
- **Verified mark:** Anyone may call a `mark` function with an update; it stores `{price, time}` only from a verified update strictly newer than the stored one (replays and older updates are refused). Readers reject a mark older than a maximum mark age. Callers choose when, never the price. Staleness halts what depends on the mark; take updates per call if deposits must stay open.

Never value assets from a DEX pool's spot or active-bin price: it can be moved within the same transaction. Recommend a verified on-chain oracle. A price a keeper or admin supplies is a trust assumption the design may accept (no oracle for the asset, a fixed peg, a manual fallback): bound each change, reject stale values, record who set it and when, and tell the developer which party it trusts ([vault valuation](../ecosystem/SKILL.md#value)).

## Liquid staking ratios

Pairs: `stSTX/STX`, `stSTXbtc/STX` (fixed 1:1) and `stBTC/sBTC`.

Price stSTX as STX/USD (Lazer feed 45) times `(contract-call? 'SP4SZE494VC2YC5JYG7AYFQ44F5Q4PYV7DVMDPBG.data-stx-v2 get-stx-per-ststx)`: a bare `uint` (do not unwrap it), STX per stSTX at 6 decimals, rounded down (`get-stx-per-ststx-up` rounds up, for minting). stSTXbtc redeems 1:1 for STX, so it takes the STX price; stBTC uses `data-stbtc-v1` `get-sbtc-per-stbtc` (8 decimals).

- Anyone can raise the ratio at once by sending STX to `stx-reserve-v2` or burning stSTX (+1% costs about 1% of the STX backing stSTX), and StackingDAO governance can move it either way.
- Migrations replace the data contract, and the old getters (`data-core-v1` to `-v3`, `data-stx-v1`, `stacking-dao-core-v1`) now return wrong ratios or revert; the August 2026 cutover cut the ratio 1.24% in one block. Bound the ratio, cap its change per block, and keep a governed way to repoint and pause.
- It is the redemption value, not the market price: slow withdrawals take at least 2,100 Bitcoin blocks, instant ones pay a governed fee and need idle STX, and a large DEX sale can clear well below the ratio. Size liquidation bonuses for selling seized stSTX.

## DIA USDh/USD

DIA's oracle is the only on-chain source of a USDh/USD price. Read it with `(contract-call? 'SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle get-value "USDh/USD")`, which returns `(ok {value, timestamp})`: the value at 8 decimals and the timestamp in Unix milliseconds ([addresses](../protocols/references/addresses/dia.md)).

- One updater key pushes both the value and the timestamp (checked against `tx-sender`), so the price is that key's word.
- The same contract stores other keys, such as `BTC/USD` and `STX/USD`, each updated on its own schedule, and some go stale for weeks: check each key's timestamp.
- A missing key returns zeros, not an error: require a nonzero value and `(/ timestamp u1000)` within your maximum age of `stacks-block-time`.

## Timestamp units

| Field / clock | Unit |
|---|---|
| DIA `get-value` `timestamp` (USDh/USD) | Unix milliseconds |
| Lazer envelope `timestamp` (`timestampUs` off-chain), per-feed `feed-update-timestamp` | Unix microseconds |
| Stacks verifier `max-age`, stale threshold; signer `expires-at`; `stacks-block-time` | Seconds |
| JavaScript `Date.now()`, channel names such as `fixed_rate@200ms` | Milliseconds, not the payload timestamp unit |

- Convert raw Lazer values with `(/ timestamp-us u1000000)` for second-based comparisons (integer division rounds down), and DIA or JavaScript milliseconds with `(/ timestamp-ms u1000)`; do not reuse one feed's conversion for another.
- The verifier converts envelope time for its age check but returns raw decoded timestamps; do not assume the returned tuple was normalized.
- If the consumer caches prices, recheck freshness when reading them; a once-valid update eventually expires.

Sources: [Pyth payload units](https://docs.pyth.network/price-feeds/pro/payload-reference), [DIA oracle](https://explorer.hiro.so/txid/SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle?chain=mainnet&tab=overview), [Stacks verifier](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/contracts/pyth-lazer-oracle.clar).

## Protocol consumers

Each protocol's checks are its own design choice, not a minimum: apply the [price checks](#lazer-price-checks) above to your consumer.

- **Zest v2** `v0-8-market`, on its own instance: price-dependent calls take `price-feeds`, a list that must hold exactly one update despite its ABI maximum of three. That update must carry every Lazer feed the account holds, because the market values the whole position. It accepts feeds 1, 7 and 45 from channels 3 or 4 (200 ms or 1 s fixed rate) and requires confidence within a governed ratio, at least three publishers, and a per-feed timestamp no later than the envelope, within the asset's governed maximum age, at most 60 s ahead and no older than the last one used for that feed. USDh comes from DIA. Collateral adds, repays and liquidations require `contract-caller` to equal `tx-sender` (`u400025`), so a contract calls them from `as-contract?` and owns the position itself. Its local-testing helpers differ ([Zest test fixtures](../protocols/references/zest.md#zest-test-fixtures)).
- **Granite** `borrower-v1`/`liquidator-v1`, on its own instance: borrowing, removing collateral and liquidating take a required update. Its `pyth-adapter-v1` verifies it with `max-age none` (the instance's governed threshold), then requires a positive price, an exponent within [-18, 11], an envelope time within its governed `time-delta` and, when the update carries one, confidence within the token's governed ratio. The live logic does not call its legacy Core adapters ([Granite](../protocols/references/granite.md#granite-oracle-path)).
- **Hermetica** has no Lazer path in production: USDh minting decodes Pyth Core payloads per call, which are no longer published on Stacks, and prices USDCx at a fixed $1; hBTC's share price uses no oracle ([Hermetica prices](../protocols/references/hermetica.md#hermetica-prices)).

## Deploy a Lazer instance for your protocol

Pyth runs no Stacks contract, so each protocol deploys and governs its own verifier; the upstream README says Pyth's terms forbid sharing one deployment. The [subscription terms](https://www.dourolabs.xyz/Subscription-Terms.pdf) do not mention instances but forbid sharing API keys, so each protocol needs its own Pyth Pro key regardless. Steps:

1. **Access:** Get a Pyth Pro API key (a Pyth Terminal account at app.pyth.com; production plans through Pyth). Keys are limited to asset types and a minimum channel, so first look up each feed's id, exponent and `min_channel` at `https://pyth.dourolabs.app/v1/symbols` (no key needed). Keep the key server-side; browsers use short-lived tokens from `https://pyth.dourolabs.app/auth/token`.
2. **Revision:** Deploy [stx-labs/stacks-pyth-lazer](https://github.com/stx-labs/stacks-pyth-lazer/tree/a6034d2e3922892f98558d05330f92b12c857681) at `a6034d2e`, the [audited](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/audits/2026-07-27%20-%20Clarity%20Alliance.pdf) contracts.
3. **Deploy:** Publish `pyth-lazer-traits`, `pyth-lazer-oracle`, then `pyth-lazer-decoder-v1`, unmodified, from one account (they call each other by relative name), with `clarity_version = 5` set explicitly: Clarity 3 fails on `stacks-block-time`, and epoch 4.0 otherwise defaults new contracts to the untested Clarity 6. Upstream ships only testnet plans: write your own mainnet plan and rehearse on testnet, where the default staleness is about five years until you call `set-stale-price-threshold`. The deployer starts with both roles and as fee recipient; deploying from your governance multisig removes that single-key window.
4. **Check:** Compare the published source with the pinned files, and read the initial state with read-only calls: no trusted signers, fee `u0`, threshold `u7200`, not paused, decoder `.pyth-lazer-decoder-v1`.
5. **Trust Pyth's signer:** Every verification fails with `u2105` until you call `(set-trusted-signers (list {pubkey: 0x03a4380f01136eb2640f90c17e1e319e02bbafbeef2e6e67dc48af53f9827e155b, expires-at: u<unix seconds>}))`. The oracle stores this 33-byte compressed key (EVM address `0x26FB61A864c758AE9fBA027a96010480658385B9`); confirm it by recovering the signer of a fresh update with the decoder's read-only `recover-signer`. Each call replaces the whole list.
6. **Hand off governance:** The roles are `0x00` (governance: signers, decoder, threshold, fee, roles) and `0x01` (pause), checked against `contract-caller`. A DAO that executes through proposals needs an adapter that holds the roles and forwards each admin call when `tx-sender` is the DAO, as Zest v1's `SP2VCQJGH7PHP2DJK7Z0V48AGBHQAW3R3ZW1QF4N.pyth-lazer-governance-v1` does. From the deployer, grant both roles to governance and `0x01` to any emergency pauser. Governance then revokes the deployer (no one can remove their own governance role, `u4005`) and points `set-fee-recipient` at the treasury.
7. **Timelock in your governance:** The oracle applies every change at once, and `set-trusted-signers` works even while paused, so whoever can call it can sign any price. Put signer, decoder, threshold and fee changes behind your governance timelock ([immediate actions](../governance/SKILL.md#immediate-actions)) and keep pausing instant. Give governance the pause role too: while paused every other setter fails (`u4004`), so recovering from a rogue pauser takes one contract call that unpauses and revokes it, which a native multisig cannot do.
8. **Verify the end state:** `has-role` false for the deployer on both roles and true for governance, a future signer expiry, fee `u0`, not paused. Every setter prints an event; the contract's event log is the audit trail.

Operate it:

- Renew or rotate the signer well before `expires-at`, allowing for your governance delay. Pyth can rotate its key through its DAO, so follow its announcements. Rotate without downtime by listing the old and new keys together, then dropping the old one.
- Fetch updates server-side: REST `POST https://pyth-lazer.dourolabs.app/v1/latest_price` with `Authorization: Bearer <key>`, or the stream at `wss://pyth-lazer-{0,1,2}.dourolabs.app/v1/stream` (`@pythnetwork/pyth-lazer-sdk` 7.0.1 or later). Request `formats: ["evm"]` (the only envelope the decoder verifies), `jsonBinaryEncoding: "hex"`, a fixed-rate channel (`fixed_rate@200ms` or `fixed_rate@1000ms`) and `price`, `exponent`, `confidence`, `publisherCount` and `feedUpdateTimestamp`. Pass the `evm.data` bytes as the `(buff 8192)` update. The v1 decoder rejects property types above 12 (`u2205`).
- The verifier stores nothing, so a relayer that only pushes updates helps no one: put a fresh update into each consumer transaction.
- Before sending a transaction, check a fetched update with the decoder's read-only `recover-signer` and `decode-lazer-payload`.

## Integrate and test

- Record consumer, oracle, decoder, signer expiry, roles, fees, feed IDs, channels and source revisions.
- Verify payload bounds, signature recovery, field counts, endianness and trailing bytes. Test missing/duplicate feeds and properties explicitly.
- Check envelope and feed age, future timestamps and exact threshold boundaries: stale feeds in fresh envelopes, milliseconds mistaken for microseconds, double conversion.
- Convert prices into the accounting asset's units. USD feeds do not establish a bridged or wrapped token's parity with its reference asset.
- Test the actual verifier/parser (Clarigen by default, or the project's harness), plus authentic signed vectors and isolated test signers ([signed fixtures](#signed-fixtures)). Mutate signature, payload, signer, feed, time, price, exponent and confidence independently. Assert the consumer's behavior, not merely `(ok decoded)` from the verifier.
- Refresh deployed governance/configuration even when repository HEAD is unchanged.
- Migrating from Core changes payload acquisition, feed IDs, decoder, caller checks and storage assumptions. Replace cached-price reads with verified transaction inputs where required, and test missing updates, halted delivery, expired signers, pause/recovery and stale feeds before enabling new collateral or liquidation paths.

## Signed fixtures

- Pin the reviewed upstream revision (a Git submodule, a vendored copy at that commit, or `[[project.requirements]]` for a deployed instance) and reference its contracts from the test manifest. Keep local signer/bootstrap helpers separate; deployment bindings must identify the intended on-chain instance and governance.
- Start with [golden fixture tests](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/tests/pyth-lazer-golden-fixture.test.ts), [synthetic encoders](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/tests/helpers.ts), decoder and governance tests.
- Golden vectors establish external encoding compatibility; self-generated vectors alone can reproduce the encoder's own mistake.
- Historic vectors need controlled fixture time or a test-only freshness override. Never copy those permissive thresholds into production.
- Register deterministic signers only in isolated fixtures. Test untrusted/expired keys, high-S signatures, malformed lengths, trailing data, sparse fields, duplicates and boundary timestamps.
- Refresh signed quotes after time-advancing setup or block skips. Simnet public setup calls advance the clock too; test the timestamp read by the consumer.
- Use `clarity:testing` for Clarigen setup.
- Authentic updates for a mainnet fork: a successful mainnet transaction that verified one carries it in its arguments (for example the `update` argument of a Granite `borrower-v1` call or the `price-feeds` argument of a Zest `v0-8-market` call; list calls with `/extended/v3/principals/<contract>/transactions`, then read arguments with `/extended/v3/transactions/<txid>?include=function_args`). Fork one block before that transaction so the signer registered then is trusted, and send freshness-sensitive calls in one `simnet.mineBlock` before any empty block ([fork block time](../testing/SKILL.md#mainnet-forks)).

## Related skills

- `clarity:testing`: Clarigen, dependency fixtures and public-call assertions.
- `clarity:epochs`: clocks, signatures and buffer semantics.
- `clarity:deployment`: ordered contract publication and governance bootstrap.
- `clarity:protocols`: protocol-specific oracle consumers and deployment records, including [DIA](../protocols/references/addresses/dia.md) (USDh/USD) and [Granite's Lazer adapter](../protocols/references/granite.md#granite-oracle-path).
- `clarity:ecosystem`: vault valuation with these prices.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `pyth-lazer`: [a6034d2e39](https://github.com/stx-labs/stacks-pyth-lazer/tree/a6034d2e3922892f98558d05330f92b12c857681).
- Audit: [Clarity Alliance, 2026-07-27](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/audits/2026-07-27%20-%20Clarity%20Alliance.pdf), final revision `bf945c12c698b008d97624b4c424d720454acb10`; excludes off-chain infrastructure.
