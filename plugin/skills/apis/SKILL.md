---
name: apis
description: "Read Stacks chain data off-chain: Hiro and node APIs, transactions, contract events, balances, read-only calls, sBTC deposit and withdrawal history. Use for scripts, indexers, bots or exports that query Stacks data."
license: MIT
compatibility: "Python 3.10+ and network access to a Stacks API (api.hiro.so by default) for scripts/inspect_contract.py."
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity APIs

Choose the endpoint and evidence appropriate to the question; keep network and state tip explicit.

## Key distinctions

- Node RPC (`/v2/...`), indexed data (`/extended/...`) and simulation answer different questions.
- Every `/extended/v1` REST data route is deprecated. Its responses carry `Warning: 299`, and once Hiro turns deprecated routes off they return 410 Gone ([switch](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/deprecation-plugin.ts#L18-L47)). Write new code against `/extended/v3`, the v2 contract logs or the node's `/v2` RPC; [endpoints](references/endpoints.md#verify-the-chain-and-deployment) lists the replacements.
- A pending/failed deployment payload is not deployed source.
- `index_block_id` hashes block-hash bytes followed by consensus-hash bytes with SHA-512/256, not truncated SHA-512.
- One transaction may emit multiple withdrawals. Transaction ID alone is not a unique event key.
- A principal's activity feed is not a general internal-call index. Select event emitters from the actual call graph.
- Simulated success is not a canonical on-chain receipt.
- Never silently substitute current state when historical evidence is unavailable.

## Read state and transactions

- Read-only call: `POST /v2/contracts/call-read/{address}/{name}/{function}` with body `{"sender": principal, "arguments": ["0x..."]}`, each argument a serialized Clarity value (`Cl.serialize(Cl.uint(1))`). The response is `{"okay": true, "result": "0x..."}` (decode with `Cl.deserialize`) or `{"okay": false, "cause": "..."}`. It never broadcasts. Choose the sender context the function checks.
- Data variable: `GET /v2/data_var/{address}/{name}/{var}?proof=0`. Map entry: `POST /v2/map_entry/{address}/{name}/{map}?proof=0` with the serialized key as a JSON string (`Cl.serialize(Cl.tuple({ stacker: Cl.principal(p) }))`); the returned `data` is `(some entry)`, or `"0x09"` (`none`) when absent. Account nonce/balance: `GET /v2/accounts/{principal}?proof=0`; mempool-aware nonces: `GET /extended/v3/principals/{address}/nonces` (`next_nonce`, which v1 called `possible_next_nonce`; standard addresses only). `fetchNonce` in `@stacks/transactions` 7.6.0 still reads v1 and, on any error, silently falls back to `/v2/accounts`, which ignores pending transactions ([fetch.ts](https://github.com/stx-labs/stacks.js/blob/6101c99efe5a9616ce7e16cef68e28fd10676e7e/packages/transactions/src/fetch.ts#L81-L124)).
- Transaction detail: `GET /extended/v3/transactions/{tx_id}?include=function_args,result` (arguments are positional `{hex, repr}` values); events are a separate, paginated `GET /extended/v3/transactions/{tx_id}/events`. The deprecated `/extended/v1/tx/{id}` answers in the legacy shape (`tx_status`, `canonical`, bounded inline events); do not build on it.
- Broadcast acceptance (a returned txid) is mempool acceptance, not inclusion or success. Require `status: "success"` and mined `block.height`/`block.index_hash`. Current v3 mined lookup selects canonical records and omits a `canonical` boolean, so do not require `canonical === true` there; handle pending/404 and revalidate block identity for reorgs.
- **Pin state with `?tip=<index block id>`:** 64 hex characters without `0x`. `/v2/info.stacks_tip` is the header hash, not that ID; get `index_block_hash` from the canonical indexed block or compute it as above. Indexed endpoints do not universally accept `tip`.
- A malformed `tip`, such as one with `0x`, silently reads the latest tip ([parser](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/net/httpcore.rs#L107-L117)), so validate it locally. Check that a provider honors `tip` with a well-formed but nonexistent one: `curl -s -w ' %{http_code}\n' "$API/v2/contracts/source/$ADDR/$NAME?tip=$(printf '0%.0s' {1..64})"` must answer HTTP 404 `Chain tip not found`. Retain the matching canonical block record; a successful response alone does not establish historical pinning.

### Common calls

```sh
API=https://api.hiro.so   # or https://api.testnet.hiro.so
ADDR=SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4; NAME=sbtc-token
# Read-only call (no broadcast)
curl -s -X POST "$API/v2/contracts/call-read/$ADDR/$NAME/get-decimals" \
  -H 'content-type: application/json' \
  -d '{"sender":"SP000000000000000000002Q6VF78","arguments":[]}'
# {"okay":true,"result":"0x070100000000000000000000000000000008"}   (ok u8)
# Data variable (JSON object with the serialized value under "data")
curl -s "$API/v2/data_var/$ADDR/$NAME/token-name?proof=0"
# Map entry: the body is the serialized key as a JSON string
curl -s -X POST "$API/v2/map_entry/SP000000000000000000002Q6VF78/pox-4/stacking-state?proof=0" \
  -H 'content-type: application/json' -d '"0x0c0000000107737461636b657205160000000000000000000000000000000000000000"'
# Account nonce and balance
curl -s "$API/v2/accounts/SP000000000000000000002Q6VF78?proof=0"
```

Read [references/endpoints.md](references/endpoints.md) when choosing an endpoint for the chain tip, epochs and limits, contract source/ABI/metadata, print history, transaction detail/events, balances, fees, broadcast, mempool, token metadata or Nakamoto blocks: it maps each purpose to its route and evidence limits.

### Rate limits and retries

- Hiro limits keyless requests per client IP; an API key gets its own, higher quota. Send the key as `x-api-key: <key>` from server-side code only ([API keys](https://docs.hiro.so/en/resources/guides/api-keys)). Hiro's [rate limits](https://docs.hiro.so/en/resources/guides/rate-limits) guide gives the current numbers; do not hardcode them. Quota headers can be missing, so never require them: on 429, wait for `retry-after` when present, otherwise back off exponentially, and bound retries.
- Clarinet, the Clarinet SDK's remote data and this package's scripts read the key from `HIRO_API_KEY`; the scripts send it to `*.hiro.so` hosts only. Several agents or test suites on one machine share one IP quota.
- A 429 or 5xx is never the end of a paginated history: retry with backoff or report the history as incomplete. Cache immutable pinned evidence; indexer lag and historical-state availability vary by provider.

### Deployed source and ABI

- `python3 scripts/inspect_contract.py ADDRESS.name --out evidence/contract` fetches node source/ABI/PoX evidence at one captured index tip and hashes the exact source bytes. `--api` selects the network, `--tip` pins an index block hash (a `0x` prefix is normalized), `--expected-sha256` fails on mismatched source text.
- That text SHA-256 is **not** the VM's `contract-hash?` commitment, and the helper does not validate consensus proofs, deployment success or governance registries.
- Require a successful canonical deployment receipt and fetch the actual deployed source: a deployment transaction containing the expected source may have failed, and different source can later occupy the same principal ([LABUBU analysis](https://clarityalliance.org/articles/labubu)). Compare source semantically when tooling rewrites principals and keep the rewrite map in evidence.
- Consensus boot contracts are installed by system initialization: verify boot identity and epoch activation instead of a deployment transaction.

## Historical event readers and exports

- Establish network, contract/version bindings, an inclusive height range and a canonical upper block ID before reading. Indexed endpoints do not accept the node RPC's `tip` parameter universally; pin the upper block ID separately.
- Follow actual emitters through nested calls: a registry may print completion while users call another contract. Principal activity indexes origins/sponsors, top-level targets and asset-event participants, not internal calls ([principal indexing](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/pg-write-store.ts)); a silent inner callee can be absent. Document missing history instead of claiming "all".
- Indexer events are input to verification, not a replacement for signer/bridge protocol rules.

| Purpose | Route | Continue with |
|---|---|---|
| Contract print history | `/extended/v2/smart-contracts/{id}/logs` | `prev_cursor` toward **older** logs |
| Principal activity | `/extended/v3/principals/{id}/transactions` | `cursor.next` toward **older** transactions |
| Transaction events | `/extended/v3/transactions/{txid}/events` | `cursor.next` toward **later** event indices |

- Cursor direction is route-specific. Preserve opaque cursors on the v3 routes and honor returned limits.
- **Seek a height window instead of paging from the tip:** Contract logs accept a position cursor `block_height:microblock_sequence:tx_index:event_index`: `?cursor={toHeight+1}:0:0:0` returns rows at or below that position, newest first (the response `cursor` is the first row's position), or HTTP 404 `Cursor not found` when there is none. An unknown contract gets the same 404, so confirm the deployment first. Follow `prev_cursor` until its height is below `fromHeight`. Paging from the newest log to an old window costs thousands of requests.
- Log rows carry no block height or position: read each row's height from its validated receipt before selecting rows by Stacks height.
- Stop only on a null `prev_cursor` (a latest page can have `next_cursor: null` and still have older pages), never on a short page: page length below the requested limit is not a general end condition. Detect a repeated cursor and fail.
- Deduplicate by `tx_id:event_index`, persist a checkpoint after each page, and resume from it after a retry; handle overlapping pages idempotently. A thrown error means incomplete history, not the end of data.
- V2 log rows contain `tx_id`, `event_index` and `contract_log`, without receipt status or block metadata. V3 principal rows wrap a transaction **summary**, without full arguments or events. Do not invent a v3 logs route; the deprecated v1 contract-events route's successor is v2 logs.

```js
// fragment: seek a height window in v2 contract logs, newest to oldest
let cursor = `${toHeight + 1}:0:0:0`; // block_height:microblock_sequence:tx_index:event_index
const seenCursors = new Set();
while (cursor && Number(cursor.split(':')[0]) >= fromHeight) {
  const res = await fetch(`${API}/extended/v2/smart-contracts/${contractId}/logs?limit=50&cursor=${cursor}`);
  if (res.status === 429 || res.status >= 500) throw new Error(`retry with backoff: HTTP ${res.status}`);
  if (res.status === 404 && seenCursors.size === 0 && (await res.text()).includes('Cursor not found')) break; // no log at or below toHeight
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const body = await res.json();
  for (const log of body.results) keepOnce(`${log.tx_id}:${log.event_index}`, log);
  cursor = body.prev_cursor; // older logs; next_cursor points toward newer ones
  if (seenCursors.has(cursor)) throw new Error('cursor did not advance');
  seenCursors.add(cursor);
  await saveCheckpoint(cursor);
}
```

- Decode serialized `contract_log.value.hex` with the full Clarity decoder (`Cl.deserialize`); `repr` is display text. Validate emitter, outer topic, decoded action/version and field types. Keep uint128 amounts as `bigint` or decimal strings, never `Number`.
- Paginate discovery and event lists independently; compare complete event coverage with the receipt's `event_count`. Cache receipts by txid: one receipt can hold many operations. Match outpoints/request IDs and source-specific event indices, not txid alone.
- Fail clearly on required missing/malformed evidence or persistent errors; a partial prefix is not complete history.
- Write outputs atomically (replace completed snapshots, or stream with durable checkpoints and deduplication); repeated scans must not duplicate records. Keep output format and coverage explicit. Reconcile the upper block identity and canonical receipts before declaring completion; follow [recoverable processing](#recoverable-processing) for ancestry, rollback and continuous recovery.

Sources: [v2 logs](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/v2/smart-contracts.ts), [v3 transactions](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/v3/transactions.ts), [v3 query semantics](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/v3/pg-store-v3.ts).

## sBTC deposit history

- Resolve the network's deposit, registry and token identities from the [sBTC registry](../protocols/references/addresses/sbtc.md), deployed source/ABI and version-specific role bindings; today's active role does not prove historical selection. Under the selected registry version's authorization, its deposit role identifies the permitted completing contract: verify that binding across the requested range, and never attribute every historical registry event to today's deposit implementation.
- Discover the **registry's** `print` events whose decoded tuple has ASCII `topic: "completed-deposit"`; the deposit contract does not emit it. Count committed completions, not inputs or transactions: a successful batch returns `(ok count)` and emits one completion per item, and a failed batch rolls back every item.
- "All deposits through this contract" includes its supported batch and nested calls (`complete-deposit-wrapper`, `complete-deposits-wrapper`); direct-call-only exports need an explicit narrower scope. The deposit wrapper checks the signer `tx-sender`, so an authorized signer can call through a router, and a principal transaction list can omit nested deposit calls.
- Fields: `amount` (net minted satoshis after sweep fees; keep the integer, and do not substitute the original Bitcoin output value or subtract the fee again), `bitcoin-txid` (already in explorer display order; do not reverse it merely because a Bitcoin library uses internal little-endian hash bytes), `output-index`, `burn-hash`, `burn-height`, `sweep-txid`, `topic`.
- **Recipient is absent:** Enrich it from the exact-asset mint emitted immediately before the print, decoded call arguments or a historical registry view. The transaction origin is the signer, not the recipient. Recipients can be contracts.
- In this source version each successful completion emits its sBTC mint immediately before the registry print: fetch all event pages, order by event index and verify the exact native asset/amount when pairing. Do not match repeated equal-amount mints by amount alone. Recheck ordering after upgrades.
- Calldata enrichment: decode positional single-call arguments or a batch list of tuples. Stacks.js 7 Clarity tuples/lists use `.value`; do not reuse older `.data`/`.list` shapes blindly. Nested calls may leave no deposit arguments in the outer receipt; use verified event/state evidence instead.
- Registry logs also hold withdrawals and governance events. A withdrawal can mint sBTC too: a rejection returns the locked amount and an acceptance refunds any unused fee. A mint alone is not a deposit. [Seek the registry logs by height](#historical-event-readers-and-exports) (tens of thousands of deposits).
- Bitcoin funding, sweep and reclaim meaning: [sBTC settlement](../bitcoin-proofs/SKILL.md#sbtc-settlement).

Read [references/sbtc-deposits.md](references/sbtc-deposits.md) before decoding a `completed-deposit` payload: its `decodeCompletedDeposit` helper rejects noncanonical bytes and malformed fields.

## Continuous ingestion

| Need | Approach |
|---|---|
| UI updates, alerts, moderate indexing | Hiro REST plus WebSocket or Socket.IO block notifications, with a checkpoint, polling watchdog and backfill |
| Managed contract-filtered webhooks | [Chainhooks](https://docs.hiro.so/en/tools/chainhooks) `contract_log` filter on the emitter's `contract_identifier`; persist `event.apply` and `event.rollback` |
| Independent, uptime-critical indexing | Your own validating Stacks node, filtered event observer and durable consumer |
| Rich self-hosted historical queries | Your own node plus the [Stacks Blockchain API and PostgreSQL](https://github.com/hirosystems/stacks-blockchain-api#readme); API read replicas still need a writer |

- Hosted notifications are wakeups, not a recoverable journal. Hiro documents [stream reorgs and reconnect requirements](https://docs.hiro.so/en/apis/stacks-blockchain-api/websockets), and its status history records [API errors and stale data](https://status.hiro.so/incidents/6d7qvygg7cw9).
- Recommend running your own node when independent availability, latency or replay control is a requirement. It does not eliminate node bugs, chain stalls, reorgs or application recovery work. [ALEX's node deployment](https://github.com/alexgo-io/stacks-node-mainnet/tree/14e7f986a41705511f64a7587045e3c8cb6e6cd3) combines a node, API and database; it is not an event-only node. Review third-party image provenance and current releases before reuse.
- Use a fork-aware event key such as `(network, index_block_hash, txid, event_index)` within one normalized source. Apply each event once and advance its checkpoint atomically with the projection; redelivery must be harmless.
- Keep block ancestry and reversible effects: on a fork, undo orphaned effects to the common ancestor before applying the new branch (a node observer has no rollback envelope; detect parent changes). Advance a contiguous block checkpoint, including blocks with no matching events, and backfill overlaps after reconnects. A new filter or a node restored from a snapshot does not backfill old events.

Read [references/ingestion.md](references/ingestion.md) when building a live consumer: Hiro WebSocket and Chainhooks limits, the filtered node observer configuration (`events_keys`, acknowledge with exactly HTTP 200 after persisting), and the wire schema and decoder for each event source.

### Recoverable processing

- Journal network, source/schema, index block hash, parent index hash, height, transaction ID/index, source event index and raw bytes. An acknowledgment can be lost after persistence; conflicting data for the same key needs investigation.
- Bootstrap from deployment or a verified checkpoint. Choose and validate an available historical receipt/log source; do not invent a generic node `/v2/events` endpoint. Repair missing ancestors before projecting later blocks. Current canonicality is not permanent finality.
- Monitor independently: node validation tip, API indexing tip, journal cursor, applied cursor, queue age/disk and disconnected subscriptions. Avoid treating "no matching prints" as evidence that ingestion is healthy.
- For irreversible external effects, use an explicit confirmation policy and idempotent outbox/compensation strategy. Your own node does not make a newly observed block irrevocable.
- Test duplicated and reordered delivery, lost acknowledgments, restart between journal/projection, absent blocks, reorged transactions, nested/wrong emitters, aborted transactions, unknown schemas and uint128 boundaries. Test recovery on empty-match blocks too.

## Positions, proofs and simulation

- Record block context, overrides, postcondition mode and missing evidence for every simulation or preview.
- [Addresses](../system-integration/references/addresses.md): boot/trait seeds and deployment verification. [Versions](../epochs/SKILL.md): interpreting epoch and clock fields. [Model corrections](../epochs/SKILL.md#recall-corrections): source-attestation and index-ID errors.
- Read [references/positions-and-proofs.md](references/positions-and-proofs.md) when discovering or valuing protocol positions (maps cannot be enumerated; the transaction origin is not the owner), tracing or simulating with STXER, or proving Stacks transaction inclusion with clarity-stacks.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill inherit its metadata and pins; links into sibling skills use their owner's `SKILL.md`. Review dates do not renew live evidence.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `stacks-core-release`: [10474cdec9](https://github.com/stacks-network/stacks-core/tree/10474cdec9f9c0bdf05841b58cffc89cdad87a9b).
- `stacks-blockchain-api`: [ee0c0ac5be](https://github.com/hirosystems/stacks-blockchain-api/tree/ee0c0ac5bee51b206c67e83e581fab457c34a622).
- `stacks-blockchain-api-release`: [01661c242a](https://github.com/hirosystems/stacks-blockchain-api/tree/01661c242a8aea92ba44b6302cacef4369681d94).
- `stacks-js-release`: [6101c99efe](https://github.com/stx-labs/stacks.js/tree/6101c99efe5a9616ce7e16cef68e28fd10676e7e).
- `alex-node-deployment`: [14e7f986a4](https://github.com/alexgo-io/stacks-node-mainnet/tree/14e7f986a41705511f64a7587045e3c8cb6e6cd3).
- `sbtc`: [ee30d4401f](https://github.com/stacks-sbtc/sbtc/tree/ee30d4401f8ba86fc17add1ed58bb6f30a04c343).
- `stxer-sdk`: [3e45590949](https://github.com/stxer/stxer-sdk/tree/3e455909494b00a52a9d6c1b1ed0768c5fc42463).
- `clarity-stacks`: [119dab9167](https://github.com/MarvinJanssen/clarity-stacks/tree/119dab916740ee0779f3f3243cb8d502a1385712).
