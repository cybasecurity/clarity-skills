# Release scripts and transaction builders

Code and extensions for the [release script rules](../SKILL.md#release-script-rules) and [transaction builders](../SKILL.md#transaction-builders); apply the rules there first.

### Sign, checkpoint, then broadcast

```ts
// fragment: sign, checkpoint, then broadcast one call step (@stacks/transactions 7.6.0)
const tx = await makeContractCall({
  senderKey, network, client, nonce, fee: BigInt(step.fee), contractAddress, contractName,
  functionName: step.function, functionArgs: step.args.map((a) => Cl.parse(fill(a))),
  postConditionMode: PostConditionMode.Deny, postConditions, // exact conditions for any asset movement
});
state[step.id] = { status: 'signed', txid: tx.txid(), tx: tx.serialize() };
save(); // atomic write of release.<network>.json before the broadcast
const res = await broadcastTransaction({ transaction: tx, network, client });
if ('error' in res) { delete state[step.id]; save(); throw new Error(`${step.id}: ${res.error} ${res.reason ?? ''}`); }
nonce += 1n;
await confirm(res.txid); // poll /extended/v3/transactions/0x{txid}; lasting 404: nonce check, then the saved bytes again; timeout = unknown status, never re-sign
```

Sources: [v3 nonces](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/api/routes/v3/principals.ts#L674-L702) and [how they are derived](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/pg-store.ts#L618-L707), [v3 lookup](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/v3/pg-store-v3.ts#L1245-L1321), [drops and replacements leave the index](https://github.com/hirosystems/stacks-blockchain-api/blob/ee0c0ac5bee51b206c67e83e581fab457c34a622/src/datastore/pg-write-store.ts#L3737-L3958), [`fetchNonce` in 7.6.0](https://github.com/stx-labs/stacks.js/blob/6101c99efe5a9616ce7e16cef68e28fd10676e7e/packages/transactions/src/fetch.ts#L81-L124), [`/v2/accounts` reads chain state only](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/net/api/getaccount.rs#L132-L177), [a known txid returns 200 and is not relayed](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/net/api/posttransaction.rs#L181-L270), [a used nonce is `BadNonce`](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/stacks/db/blocks.rs#L6632-L6673), [replace-by-fee](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/core/mempool.rs#L2115-L2174), [`problematic_skipped` uses the nonce](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/stacks/db/transactions/processing/mod.rs#L397-L444).

### Extended (multisig or governed) releases

When extending a script for multisig, sponsorship or governance waits, keep:

- An ordered release manifest: step ID, dependencies, network, sender, contract ID, source/config hash, Clarity version, expected pre-state, transaction payload and verification predicate.
- Atomic checkpoints: prepared bytes/hash, signer state, txid, inclusion block, canonical status and verified post-state.
- Independent nonce tracking per originating principal; independent deployers each need their own.
- Proposal IDs for governed steps; continue only when the actual signer or timelock conditions hold.

### Unsigned deployment for review

```ts
// fragment: unsigned deployment for review
const codeBody = await readFile('contracts/adapter.clar', 'utf8');
const unsigned = await makeUnsignedContractDeploy({
  contractName: 'adapter-v1', codeBody, network: 'testnet',
  clarityVersion: ClarityVersion.Clarity6, // omitting it makes this builder pin Clarity4
  publicKey,          // actual deployer's public key, verified against the intended principal
  nonce: 0n,          // replace with the assigned, checked nonce
  fee: 10000n,        // replace with a reviewed estimate and fee bound; not a recommendation
  postConditionMode: PostConditionMode.Deny,
  postConditions: [], // valid only if this deployment's top-level code has no outflows
});
await writeFile('adapter-v1.unsigned.hex', unsigned.serialize(), { flag: 'wx' });
await writeFile('adapter-v1.source.sha256', createHash('sha256').update(codeBody).digest('hex'), { flag: 'wx' });
```
