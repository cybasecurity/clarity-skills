# Wallet examples

Complete code for [new dapp: install, button, status](../SKILL.md#new-dapp-install-button-status) (the transaction status poller) and [messages, deployments and sessions](../SKILL.md#messages-deployments-and-sessions) (deployment, message-signing and WalletConnect requests) in clarity:wallets.

## Transaction status poller

`waitForTx` applies the status rules in [new dapp: install, button, status](../SKILL.md#new-dapp-install-button-status). It returns the first mined record it sees, or `{ status: 'unknown' }` after `tries`. It throws on an HTTP error other than 404, a network failure or an unexpected body. Treat `unknown` and a throw as "not known yet": keep the txid yourself and resume, because neither proves failure. A 400 is the exception: the txid itself is malformed (for example the legacy `result.txId`, which is `undefined` in Connect 8), so fix the input instead of resuming.

```ts
// observe canonical inclusion, not permanent finality
type TxObservation = { status: string; block?: { height: number; index_hash: string } };
export async function waitForTx(txid: string, api: string, tries = 60): Promise<TxObservation> {
  for (let i = 0; i < tries; i++) {
    const res = await fetch(`${api}/extended/v3/transactions/${txid}`, { cache: 'no-store' });
    if (res.ok) {
      const tx = (await res.json()) as TxObservation;
      if (!tx || typeof tx.status !== 'string') throw new Error('Unexpected v3 transaction response');
      const block = tx.block;
      const mined = block && Number.isSafeInteger(block.height) && block.height > 0 &&
        /^0x[0-9a-f]{64}$/i.test(block.index_hash);
      if (mined && ['success', 'abort_by_response', 'abort_by_post_condition', 'problematic_skipped'].includes(tx.status)) {
        return tx; // retain the block identity for later confirmation/reorg checks
      }
    } else if (res.status !== 404) {
      throw new Error(`Transaction lookup failed (${res.status}); retain txid ${txid}`);
    }
    if (i + 1 < tries) await new Promise((r) => setTimeout(r, 10_000));
  }
  return { status: 'unknown' };
}
```

- It observes inclusion once. Only `status === 'success'` is success; show the other three mined statuses as failed, not pending.
- To recheck, call the same route again. After a reorg it returns the restored mempool record, a 404 or a record with a different `block.index_hash`. In each case the earlier observation no longer holds, so apply the app's confirmation policy before irreversible effects.

Sources: [route](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/v3/transactions.ts#L115-L158), [txid pattern](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/schemas/v3/entities/common.ts#L31-L36), [canonical or mempool query](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/v3/pg-store-v3.ts#L1245-L1321), [mined statuses](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/schemas/v3/entities/transaction-summaries.ts#L36-L44), [block fields](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/schemas/v3/entities/common.ts#L143-L161), [mempool restore after a reorg](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/pg-write-store.ts#L4330-L4355).

## Deployment request

```ts
import { request } from '@stacks/connect';

export async function requestDeployment(
  name: string,
  clarityCode: string,
  clarityVersion: number,
  network: 'mainnet' | 'testnet',
) {
  return request('stx_deployContract', {
    name, clarityCode, clarityVersion, network,
    postConditionMode: 'deny',
    postConditions: [], // Appropriate only when deployment performs no asset outflows.
  });
}
```

## Mobile, sessions and messages

```ts
import { request } from '@stacks/connect';
import { Cl } from '@stacks/transactions';

// Plain text signature (wallet-specific prefix, not for contracts): bind it to your own challenge.
const nonce = await (await fetch('https://example.com/auth/nonce')).text(); // server-issued, single-use, expiring
const text = await request('stx_signMessage', { message: `Sign in to example.com\nnonce: ${nonce}` });
// SIP-018 structured data (contract-verifiable). chain-id: mainnet u1, testnet u2147483648.
const structured = await request('stx_signStructuredMessage', {
  message: Cl.tuple({ action: Cl.stringAscii('withdraw'), amount: Cl.uint(100), nonce: Cl.uint(1) }),
  domain: Cl.tuple({ name: Cl.stringAscii('example'), version: Cl.stringAscii('1.0.0'), 'chain-id': Cl.uint(1) }),
});
console.log(text.signature, text.publicKey, structured.signature, structured.publicKey);
```

```ts
import { connect, WalletConnect } from '@stacks/connect';

await connect({
  walletConnect: {
    projectId: 'YOUR_REOWN_PROJECT_ID',
    networks: [WalletConnect.Networks.Stacks],
  },
});
```
