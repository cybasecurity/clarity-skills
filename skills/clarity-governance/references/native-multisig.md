# Native multisig signing

Signing workflow for native Stacks multisig principals in [clarity-governance](../../clarity-governance/SKILL.md#contract-multisig-versus-native-multisig).

## Native multisig transactions

- Build with the installed `@stacks/transactions`: `makeUnsignedContractCall` / `makeUnsignedContractDeploy` with `publicKeys` and `numSignatures`; select the intended sequential/non-sequential mode and network. Use `TransactionSigner` or the wallet's multisig tooling for the chosen mode.
- Signing sequence: add one auth field per public key, in key order, with `signOrigin(privateKey)` for a key that signs and `appendOrigin(publicKey)` for one that does not. Signer 1 signs and passes `tx.serialize()` on; the next signer rebuilds it with `deserializeTransaction` and continues with its own `TransactionSigner`. `getTxInComplete()` returns the transaction for `broadcastTransaction({ transaction })`:

```ts
// fragment: 2-of-3 signed by key1 and key2, the private keys for publicKeys[0] and publicKeys[1]
import { makeUnsignedContractCall, TransactionSigner, deserializeTransaction, Cl } from '@stacks/transactions';

const tx = await makeUnsignedContractCall({
  contractAddress: 'ST000000000000000000002AMW42H', contractName: 'dao-multisig',
  functionName: 'approve', functionArgs: [Cl.uint(0)],
  publicKeys, numSignatures: 2, network: 'testnet', fee: 2000, nonce: 0,
});
const signer1 = new TransactionSigner(tx);
signer1.signOrigin(key1);                      // signer 1, then send tx.serialize() on
const tx2 = deserializeTransaction(tx.serialize());
const signer2 = new TransactionSigner(tx2);
signer2.signOrigin(key2);                      // signer 2 signs
signer2.appendOrigin(publicKeys[2]);           // non-signing key is appended, not signed
const signed = signer2.getTxInComplete();      // then broadcastTransaction({ transaction: signed })
```

- Pass the multisig account's next `nonce`. Without it, the 7.6.0 unsigned builders fetch the nonce of the single-signature `ST`/`SP` address that shares the multisig's hash, not the `SN`/`SM` account ([builders](https://github.com/stx-labs/stacks.js/blob/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions/src/builders.ts#L554-L559)).
- Keep the same public-key order for every signer; preserve address derivation. Do not arbitrarily sort keys or mix signing modes after approval.
- Non-sequential multisig is described by SIP-027; verify the target epoch and SDK's `useNonSequentialMultiSig` support.
- Every signer reviews the same payload, nonce, fee, network, postconditions and signer configuration. Changes after signing can invalidate signatures or authorize a different transaction.
- Signers contribute authorization; they are not separate on-chain proposal votes unless a contract explicitly implements that additional layer.
- Keep transaction bytes, signature collection and broadcast state separate. Simnet accepting a sender string does not test real cryptographic multisig admission.

Sources: [Stacks transaction builders/signers](https://github.com/stx-labs/stacks.js/tree/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions/src), [SIP-027](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-027), [SIP-005 transaction serialization](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-005).
