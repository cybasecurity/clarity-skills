# sBTC deposit completion decoder

### Decode one completion payload

Use only after emitter, outer topic, successful canonical execution and protocol-version checks. This helper extracts fields from hex; it does not establish provenance or discover recipients. Use the full decoder so unrelated registry topics with other Clarity types remain parseable.

```js
import { Cl, ClarityType } from '@stacks/transactions';

export function decodeCompletedDeposit(hex) {
	const value = Cl.deserialize(hex);
	if (Cl.serialize(value).toLowerCase() !== hex.replace(/^0x/i, '').toLowerCase()) {
		throw new Error('Noncanonical or trailing Clarity bytes');
	}
	if (value.type !== ClarityType.Tuple) return null;
	const fields = value.value;
	if (fields.topic?.type !== ClarityType.StringASCII || fields.topic.value !== 'completed-deposit') return null;
	const amount = fields.amount;
	const txid = fields['bitcoin-txid'];
	const index = fields['output-index'];
	const hashes = ['bitcoin-txid', 'burn-hash', 'sweep-txid'];
	if (amount?.type !== ClarityType.UInt || index?.type !== ClarityType.UInt ||
		fields['burn-height']?.type !== ClarityType.UInt || index.value > 0xffffffffn ||
		!hashes.every(key => fields[key]?.type === ClarityType.Buffer && /^[0-9a-f]{64}$/i.test(fields[key].value))) {
		throw new Error('Invalid completed-deposit fields');
	}
	return { amount: amount.value.toString(), bitcoin_txid: `0x${txid.value.toLowerCase()}`, output_index: Number(index.value) };
}
```

Sources: [deposit entrypoints](https://github.com/stacks-sbtc/sbtc/blob/ee30d4401f8ba86fc17add1ed58bb6f30a04c343/contracts/contracts/sbtc-deposit.clar), [registry completion](https://github.com/stacks-sbtc/sbtc/blob/ee30d4401f8ba86fc17add1ed58bb6f30a04c343/contracts/contracts/sbtc-registry.clar), [token operations](https://github.com/stacks-sbtc/sbtc/blob/ee30d4401f8ba86fc17add1ed58bb6f30a04c343/contracts/contracts/sbtc-token.clar), [signer serialization](https://github.com/stacks-sbtc/sbtc/blob/ee30d4401f8ba86fc17add1ed58bb6f30a04c343/signer/src/stacks/contracts.rs).
