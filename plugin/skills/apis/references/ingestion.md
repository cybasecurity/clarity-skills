# Live ingestion: hosted streams, node observer and wire schemas

### Hosted streams and Chainhooks

- Hiro's WebSocket subscriptions cover blocks, transaction/address updates and NFTs, not arbitrary contract-print filters, and a top-level contract-call filter misses nested prints. The JSON-RPC stream is `/extended/v1/ws` and Socket.IO is served at the API root. Neither is marked deprecated: the deprecation switch covers REST routes only ([upgrade handler](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/ws/channels/ws-rpc-channel.ts#L149-L170)). Pushed blocks and transactions use the v1 shapes (`tx_status`, `canonical`) ([payloads](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/ws/web-socket-transmitter.ts#L114-L173)), so confirm each one with a v3 receipt before acting ([WebSocket docs](https://docs.hiro.so/en/apis/stacks-blockchain-api/websockets)).
- Raw WebSocket clients must reconnect and resubscribe; Socket.IO reconnection does not establish historical replay. Backfill with the [historical readers](../SKILL.md#historical-event-readers-and-exports); their route-specific cursors and complete-receipt checks also apply after reconnecting. Use [sBTC deposit history](../SKILL.md#sbtc-deposit-history) for completion emitters and recipient enrichment.
- Check the current Chainhooks release stage and limits in Hiro's documentation before depending on it. Filter on the emitter, not only the transaction origin, and undo your own projections on `event.rollback`. [Filters](https://docs.hiro.so/en/tools/chainhooks/reference/filters), [payloads](https://docs.hiro.so/en/tools/chainhooks/reference/payload-anatomy).
- Verify its current enabling/expiration options, delivery retries, retention and service limits. Authenticate the configured bearer secret, journal before acknowledging and use supported historical block evaluation for repairs. The evaluate request's `204` is not confirmation that your consumer applied the resulting webhook. [Options](https://docs.hiro.so/en/tools/chainhooks/reference/options), [secrets](https://docs.hiro.so/en/tools/chainhooks/secrets), [replay](https://docs.hiro.so/en/tools/chainhooks/evaluate).
- The archived `hirosystems/chainhook` Rust repository is not the current hosted 2.0 service; verify maintenance and compatibility before choosing a self-hosted Chainhook implementation.

### Filtered node observer

Start from a supported standard node, not a consensus fork just to decode selected events. Add this to its existing network configuration, replacing the example contract; the dispatcher queue, timeout and retry values are starting points to size for your consumer:

```toml
[node]
event_dispatcher_blocking = false
event_dispatcher_queue_size = 1000

[[events_observer]]
endpoint = "127.0.0.1:3700"
events_keys = ["SP000000000000000000002Q6VF78.example::print"]
timeout_ms = 5000
disable_retries = false
disable_contract_interface = true
```

- Event keys: `ADDRESS.name::topic` for contract events (`ADDRESS.name::print` for `print`), `ADDRESS.name.asset` for FT/NFT events, and `*`, `stx`, `memtx`, `burn_blocks`, `microblocks`, `stackerdb`, `block_proposal`. API asset identifiers usually use `ADDRESS.contract::asset`, unlike observer keys. The config loader unwraps the key parse, so an invalid key prevents node startup. Check the actual [key parser](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stackslib/src/config/mod.rs), not just an API identifier example.
- A key is not a tuple-field filter (not `::deposit`): a field such as `event: "deposit"` is decoded and filtered by your consumer.
- Receive `POST /new_block`, durably append the raw request, then return exactly **HTTP 200** (`202`/`204` are failures) promptly and parse/project asynchronously; never acknowledge before persisting. [Delivery worker](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stacks-node/src/event_dispatcher/worker.rs).
- This node configuration uses HTTP, not an authenticated public webhook: keep the receiver on a private network.
- Do not design new Nakamoto ingestion around legacy `/new_microblocks`. Support documented auxiliary observer routes such as `/attachments/new` if delivered. [Observer interface](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/docs/event-dispatcher.md).
- Filtering reduces the events array, not consensus validation or necessarily transaction metadata. Preserve empty-match block ancestry. The dispatcher sends a block envelope even when no selected event matches. [Dispatcher](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stacks-node/src/event_dispatcher.rs).
- Retain the node's dispatcher database across restarts, but maintain an application journal too. A retry queue is not complete historical replay. Nonblocking delivery eventually blocks when its bounded queue fills; a slow observer can delay node processing.

### Decode the correct wire schema

| Source | Contract log discriminator | Serialized Clarity value |
|---|---|---|
| Node observer | `type: "contract_event"`, `contract_event.contract_identifier` | `contract_event.raw_value` |
| Indexed v2 logs | `event_type: "smart_contract_log"`, `contract_log.contract_id` | `contract_log.value.hex` |
| Indexed v3 receipt events | `type: "contract_log"`, `contract_log.contract_id` | `contract_log.value.hex` |
| Chainhooks | `event.apply` / `event.rollback` blocks and operations | Use that service generation's operation schema |

This example handles **one node-observer event**, after envelope validation: it decodes `contract_event.raw_value` only when `type: "contract_event"`, `committed: true`, the emitter and topic `print` match, and rejects noncanonical bytes. `committed: true` is not finality: the successful receipt, canonical block, domain schema and durable processing remain separate checks.

```js
import { Cl } from '@stacks/transactions';

export function decodeNodePrint(event, contractId) {
	if (event.type !== 'contract_event' || event.committed !== true ||
		event.contract_event?.contract_identifier !== contractId ||
		event.contract_event.topic !== 'print') return null;
	const hex = event.contract_event.raw_value;
	if (typeof hex !== 'string' || !/^0x(?:[0-9a-f]{2})+$/i.test(hex)) {
		throw new Error('Invalid Clarity hex');
	}
	const value = Cl.deserialize(hex);
	if (Cl.serialize(value).toLowerCase() !== hex.slice(2).toLowerCase()) {
		throw new Error('Noncanonical or trailing Clarity bytes');
	}
	return value;
}
```

- Check expected tuple fields, Clarity types, event/schema version, principals and units before projecting; retain unknown versions for review rather than silently treating them as a known action.
- Match the actual emitter, including nested calls. Another contract can print an identical tuple.
- Node event indices in this baseline are block-wide and filtered arrays can be unordered. Indexed schemas may remap indices; preserve source identity and an explicit mapping rather than joining different feeds by a guessed index. [Node serialization](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity/src/vm/events.rs).
