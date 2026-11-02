---
name: clarity-bitcoin-proofs
description: "Verify Bitcoin transactions from Clarity: transaction parsing, Merkle proofs (clarity-bitcoin, Clarity 6 natives), BTC payment checks, replay protection, sBTC settlement. Use when a contract must react to a Bitcoin payment."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Bitcoin Proofs

Separate parsing, inclusion, spendability, claimant authorization and settlement. Each needs its own evidence.

Writing or changing contract code: also load `clarity-scholar` and `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

- For off-chain sBTC deposit/withdrawal history, event readers or exports, start with [APIs](../clarity-apis/SKILL.md); use this skill for Bitcoin and settlement semantics.

## Key distinctions

- `clarity-bitcoin-lib-v4/v5/v7` are library revisions, not Clarity language versions.
- Clarity 6 adds native `get-bitcoin-tx-output?` and `verify-merkle-proof`; older contracts need compatible helpers. Check target epoch, activation and simulator support first.
- `txid` excludes SegWit witnesses; `wtxid` includes them. A txid proof does not authenticate witness bytes.
- Inclusion proves existence at a historical point. It does not prove an output is unspent, sufficiently confirmed, owned by the caller or eligible for your protocol, or that an included input belongs to the requesting Stacks principal.
- Bitcoin proof verification cannot authorize arbitrary sBTC minting or complete an asynchronous withdrawal.
- Stacks and Bitcoin use different transaction Merkle constructions; `clarity-stacks` is not a Bitcoin verifier.

## Native functions (Clarity 6, epoch 4.0+)

- `get-bitcoin-tx-output? raw-tx vout` returns `(ok {amount: uint, script: (buff 1024), txid: (buff 32)})`: amount in satoshis, `script` the raw `scriptPubKey`, `txid` the non-witness double-SHA-256 digest in **internal byte order**. It accepts legacy or SegWit serialization, rejects trailing data, and errs `u1` invalid serialization, `u2` absent output, `u3` script over 1024 bytes. The input type permits up to 1 MiB; transaction size, execution budget and your entrypoint may bound it tighter.
- `verify-merkle-proof leaf root index count siblings` returns a **bool**: wrap it in `asserts!` (`try!` applies to responses and optionals). Supply internal-order 32-byte hashes, the actual transaction count, the zero-based index and up to 24 siblings. It validates the tree shape implied by count, including odd-row padding; do not pad a proof arbitrarily.
- These natives parse and hash. Neither fetches a transaction, queries a UTXO set or broadcasts.

Sources: [VM implementation](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/functions/bitcoin.rs), [VM function reference](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/docs/mod.rs), [Stacks reference](https://docs.stacks.co/reference/clarity/functions).

## Anchor the proof before trusting an output

- Require exactly 80 header bytes and compare their reversed double SHA-256 with `(get-burn-block-info? header-hash height)`.
- Take the Merkle root from header bytes `[36,68)` in raw internal order; do not reverse it again for the native verifier. Never accept a separate root argument: a proof against a caller-supplied root proves nothing.
- Parse the output with `get-bitcoin-tx-output?` and verify its `txid` against that root. Errors in the verifier below: `u9001` header length, `u9002` unavailable burn height, `u9003` header mismatch, `u9004` invalid proof; the native parser keeps its `u1`-`u3` range.
- The result is an authenticated **historical** output. Before granting credit, the caller still checks the exact script and amount, maturity/confirmations, claimant and intent binding, replay and the relevant spend conditions.
- A read-only result does not consume a claim. Store consumed outpoints (canonical txid plus vout, with the application domain) inside the authorized state-changing operation and propagate failures so credit and replay state roll back together.
- Do not expose a production switch that replaces the native burn-header lookup with caller-controlled hashes.

Verifier signature: `(verify-mined-output (height uint) (header (buff 80)) (raw-tx (buff 4096)) (vout uint) (tx-index uint) (tx-count uint) (siblings (list 24 (buff 32))))` returns the output tuple; 4096 bytes is its input bound, not the parser's maximum. Deploy with Clarity 6 on a supporting epoch.

```clarity
;; fragment: body of verify-mined-output (Clarity 6, epoch 4.0+); authenticates a historical output only
(asserts! (is-eq (len header) u80) (err u9001))
(let ((known-header (unwrap! (get-burn-block-info? header-hash height) (err u9002))))
  (asserts! (is-eq known-header (reverse-hash (sha256 (sha256 header)))) (err u9003))
  (let ((root (unwrap-panic (as-max-len? (unwrap-panic (slice? header u36 u68)) u32)))
        (output (try! (get-bitcoin-tx-output? raw-tx vout))))
    (asserts! (verify-merkle-proof (get txid output) root tx-index tx-count siblings) (err u9004))
    (ok output)))
;; reverse-hash folds the 32 bytes with a prepend: (fold prepend-byte hash 0x), where
;; prepend-byte returns (unwrap-panic (as-max-len? (concat byte result) u32))
```

## Bind the output to your protocol

- Bind raw bytes to canonical txid, exact output index, script, amount, network and application intent before crediting anything. Define whether several outputs of one transaction are separately claimable.
- Match the complete expected output script and value, not an address-looking substring or the first input's pubkey. P2WPKH is `00 14` plus 20 bytes; P2WSH `00 20` plus 32; P2TR `51 20` plus 32. Validate exact lengths and the protocol's intended script/key commitments.
- Enforce the protocol's Bitcoin confirmation/reorg policy; Stacks blocks and Bitcoin blocks are different clocks.
- To prove an output, canonical txid inclusion is sufficient. To authenticate witness contents, use the separate witness tree and the coinbase transaction's witness commitment; stripping witnesses and proving the txid does not prove what the witnesses contained.

Sources: [Bitcoin transaction format](https://developer.bitcoin.org/reference/transactions.html), [BIP-141 witness commitments](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki), [BIP-341](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0341.mediawiki).

## Prepare inputs off-chain

- Fetch the full raw transaction, canonical block header, transaction order/count and Merkle branch from a Bitcoin node or compatible provider. Provider data stays untrusted until the on-chain anchor and proof pass.
- Preserve binary serialization: decode explorer hex as binary (never hash it as UTF-8). Explorer display-order txids and siblings are reversed once to internal order (the native parser's returned txid is already internal). Bind the proof `index` to the transaction's actual position; the block's transaction count is not in the 80-byte header.
- Retain height/hash and handle reorgs rather than treating an earlier API response as permanent finality.
- Call the verifier through the project's client (Clarigen-generated calls by default); pass numeric arguments as bigint so they stay exact.

## Helper libraries for older targets

Existing integrations and pre-Clarity 6 targets use a helper library. Repository activity, library revision, deployed source and Clarity version are separate facts: verify deployed source, ABI, successful deployment and disabled mocks.

- [friedger/clarity-bitcoin](https://github.com/friedger/clarity-bitcoin) continues [Jude Nelson's original library](https://github.com/jcnelson/clarity-bitcoin). It contains `clarity-bitcoin-v4.clar`, `clarity-bitcoin-v5.clar` and `clarity-bitcoin.clar`; its manifest at the pinned revision targets Clarity **2**, epoch 2.1.

| Library revision | Upstream status / distinction |
|---|---|
| v2 | Explicitly marked buggy; do not select it |
| v3 | Uses burn-block information for blocks without a Stacks block |
| v4 | Adds witness verification |
| v5 | Adds canonical txid construction and rejects leftover parsed bytes |
| v6 | Debug variant of v7 |
| v7 | README-listed deployed revision with larger transaction/coinbase and input/output limits |

- Mainnet deployments: `SP2PABAF9FTAJYNFZH93XENAJ8FVY99RRM50D2JG9.clarity-bitcoin-lib-v4`, `-v5` and `-v7`.
- Resolve testnet deployments independently; do not infer source equivalence from a name suffix or changed address prefix.
- The repository's `clarity-bitcoin.clar` and `clarity-bitcoin-v4.clar` set `DEBUG-MODE` to true, so anyone can store mock header hashes and forge proofs; the deployed v4 and v7 omit that path. Call a deployed contract whose bytes you verified, or deploy a copy that reads header hashes only through `get-burn-block-info?`.
- The v7 parser caps raw transactions/coinbase at 4096 bytes, inputs/outputs at 50, and Merkle siblings at 14. Read exact deployed bounds; larger valid Bitcoin transactions can exceed helper limits.

### Calling an existing helper

```clarity
;; fragment
;; Existing v7 ABI: height, raw non-witness tx, 80-byte header, proof tuple.
(contract-call? 'SP2PABAF9FTAJYNFZH93XENAJ8FVY99RRM50D2JG9.clarity-bitcoin-lib-v7 was-tx-mined-compact height raw-tx header
	{tx-index: tx-index, hashes: siblings, tree-depth: depth})
```

- Verify ABI first: v7 returns a response containing a **display-order txid**, not `(ok true)`; several source comments describe older behavior.
- Its `get-reversed-txid` hashes supplied bytes. Supplying raw SegWit bytes there produces a witness hash, not canonical txid. For an output proof, pass the transaction's non-witness serialization.
- `was-segwit-tx-mined-compact` has a different ABI: witness transaction, witness branch/root/reserved value, and a coinbase transaction with its own branch. Verify the full BIP-141 commitment when authenticating witnesses.
- Native Clarity 6 verification uses transaction count and a bool result; this library uses `tree-depth` and response-returning helpers. They are not interchangeable signatures.
- Read [open issues](https://github.com/friedger/clarity-bitcoin/issues), including witness-size limits, and check which fixes the deployed version includes before reuse. Repository examples and unmerged tests are not deployment certification.

## Bridge boundaries

Use these checks for Bitcoin-backed Clarity assets: separate deposit replay from withdrawal reservations and validate the full funding-to-settlement path. An authenticated transaction alone ([proof and replay rules](#anchor-the-proof-before-trusting-an-output)) does not establish the protocol's right to reserve or credit its outputs.

### UTXO reservation and request identity

- Separate deposit-credit replay state, withdrawal request IDs and spendable-UTXO reservations. A caller-controlled withdrawal must not mark somebody else's pending deposit as already credited.
- If the contract tracks spendable UTXOs (some bridges reserve one per withdrawal; others leave UTXO selection to off-chain signers), allocate them from authenticated inventory, bind each reservation to its authorized request, and reject concurrent reuse across every withdrawal route the bridge has.
- Domain-separated replay keys do not authorize arbitrary UTXOs or prevent double allocation by themselves. Preserve one consistent reservation state for each actual spendable outpoint.
- A marker outpoint being spent does not prove the intended withdrawal completed. Match the actual Bitcoin payment, amount, recipient and request before burning/unlocking or marking success.
- Reconcile cancellations, replacement transactions, reorgs and listener restarts. Migrate reservations and replay state together.
- Test front-running with another user's pending deposit outpoint and, where the design has them, two withdrawals sharing one reserved UTXO, cross-asset reuse and an off-chain listener resuming after partial completion.

### Scripts and recipient encoding

- Bitcoin validity, relay policy and your bridge's accepted deposit format are separate boundaries. Validate the exact encoder/parser combination before funding; provide an authenticated reclaim/refund path for unsupported deposits.
- Parse data pushes by opcode and declared length: direct pushes, `OP_PUSHDATA1`, `OP_PUSHDATA2` and `OP_PUSHDATA4`. The latter length fields are 1, 2 and 4 bytes, little-endian for the multi-byte forms. **There is no `OP_PUSHDATA3`.**
- Support the protocol's accepted encodings with bounds checks, or reject unsupported forms before funding. Do not assume that equal pushed data implies identical bytes or the same relay-policy treatment.
- Test truncated length fields/data, oversized pushes, multiple candidate data outputs and equivalent non-minimal encodings. Define exactly which output and payload schema identify the recipient.
- **80 data bytes / 83 script bytes was a historical Bitcoin Core relay-policy default, not a Bitcoin consensus cap:** Core 30.0 raised the default `datacarriersize` to 100,000 and allowed multiple data-carrier outputs. Check the actual node/miner policy and transaction limits; this does not enlarge a Clarity parser's buffers.
- Budget the complete serialized principal, bridge prefix, length fields and push opcode. Contract names in deployments and call targets are at most 40 bytes, but a principal value can carry a name of up to 128 bytes. Epoch 4.1 adds checks on overlong names ([version boundaries](../clarity-epochs/SKILL.md)). Bridge/parser bounds can be tighter.
- Prefer the current encoder's byte length to hand-counted offsets. Check the [native parser's script/input limits](#native-functions-clarity-6-epoch-40) and each downstream `(buff N)`/slice separately.
- A 546-satoshi value can be a protocol constant; it is not a universal Bitcoin dust threshold for every script and fee policy.

Sources: [Bitcoin script decoding](https://github.com/bitcoin/bitcoin/blob/6574cb40869b96b9ffc79c19dc8f4e467d60f321/src/script/script.cpp), [Core 30.0 policy changes](https://bitcoincore.org/en/releases/30.0/), [current policy constants](https://github.com/bitcoin/bitcoin/blob/6574cb40869b96b9ffc79c19dc8f4e467d60f321/src/policy/policy.h), [principal-name representation](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity-types/src/representations.rs).

### Wrapped Bitcoin NFTs

A wrapper that mints a Clarity NFT for a Bitcoin asset, usually an Ordinals inscription, chooses its own identity scheme, collection model and custody flow. Read the wrapper's contracts before integrating it; one wrapper's scheme says nothing about another's.

- Keep the Bitcoin identity complete. An inscription ID is the reveal transaction's display-order txid, `i` and the inscription's index in that reveal (`<txid>i0`, `<txid>i12`). The index is not an output index or the inscription's current location (satpoint), and a 32-byte hash alone drops it.
- Each wrapper maps that identity to a `uint` token ID its own way: a counter with a lookup map, a hash, or one contract per collection. Read the mapping the wrapper uses. The same token ID in two wrappers is unrelated, and IDs need not be sequential or dense.
- When you write a wrapper, store the mapping both ways and keep it one-to-one. Test several inscriptions from one reveal, multi-digit indexes, sparse IDs, and burning then reminting the same inscription.
- Collection membership is the wrapper's policy. A contract can hold one collection or many, so holding any of its tokens does not prove membership of a particular collection. Check the wrapper's own collection data, or a verified membership registry, before granting collection-level rights.
- A proof of the reveal transaction shows that the inscription was created, not who holds it now: transfers move it with its sat. Its content lives in witness data, so a txid-only proof does not authenticate the content either. State what the design trusts for deposit ownership and content: a [witness commitment](#bind-the-output-to-your-protocol) proof, an indexer or an attestation.
- SIP-009 conformance does not authenticate Bitcoin provenance or collection membership. Test metadata lookup and identity round trips, not just minting.

Source: [Ordinal Theory Handbook](https://docs.ordinals.com/inscriptions.html#inscription-ids).

### Who pays for failure?

- Trace costs on both chains: request creation, signer validation, Bitcoin fulfillment, Stacks acceptance/rejection and repeated retries. User-paid initiation does not automatically fund operator-paid cleanup.
- Test zero/underfunded fee ceilings, fee spikes, many tiny requests and repeated rejection. A zero fee ceiling can be an intentional subsidy, so classify the actual cost asymmetry rather than treating zero as inherently invalid.
- Bound queues/retries and choose admission fees, reserves, batching or cancellation rules that preserve withdrawal liveness. Frontend validation alone does not protect a public Clarity entry point.
- Distinguish Bitcoin fees in satoshis from Stacks execution fees in micro-STX. For sBTC, see [withdrawal amount and fee-reserve accounting](#sbtc-withdrawals).

Public historical examples: [Pontis bridge review](https://clarity-alliance.github.io/audits/Clarity%20Alliance%20-%20Pontis%20Bridge.pdf), [BTCz review](https://clarity-alliance.github.io/audits/Clarity%20Alliance%20-%20Zest%20Protocol%20BTCz.pdf), [sBTC review](https://clarity-alliance.github.io/audits/Clarity%20Alliance%20-%20sBTC.pdf). Check current implementations and specifications rather than inheriting report limits or severity unchanged.

## sBTC settlement

- [sBTC token behavior](../clarity-assets/SKILL.md#sbtc) covers spendable versus withdrawal-locked balances and synchronous SIP-010 transfers. Deposits and withdrawals also depend on Bitcoin transactions, the current signer set, registry-selected contracts and external processing: trace the registry roles, request IDs and the BTC settlement.
- Use [the official sBTC repository](https://github.com/stacks-sbtc/sbtc), including its contracts and current deposit tooling. Inspect deployed versions and operational limits before constructing deposits or withdrawals.
- Neither direction can be completed atomically inside a Clarity flash loan.

### sBTC deposits

- Build the current deposit and reclaim scripts with the actual signer key, recipient, network, fees and locktime rules. Validate the produced Bitcoin script/address before funding it.
- Identify a deposit by canonical Bitcoin `txid` plus `vout`; the credited Stacks principal must come from the authenticated deposit intent. sBTC contracts and their events carry display-order txids, so reverse the native parser's `txid` before a registry lookup.
- Track broadcast, canonical inclusion/confirmations, deposit processing/sweep and the committed sBTC mint separately. A submitted API request or included funding transaction is not mint completion.
- In the pinned `sbtc-deposit`, `complete-deposit-wrapper` checks the current signer principal and deposit replay state before protocol minting. An ordinary user cannot bypass this by supplying a Bitcoin Merkle proof.
- Verify mint event emitter, exact asset, recipient and amount, then read available balance. Account for rejection/reclaim paths without counting the same backing twice.

### sBTC withdrawals

- Pinned entrypoint: `initiate-withdrawal-request(amount, {version, hashbytes}, max-fee)`.
- It locks **amount + max-fee** from `tx-sender`; available balance must cover both. Caller context matters when an adapter submits the request.
- Both values use sBTC base units, equivalent to satoshis; `max-fee` is not a micro-STX execution-fee budget. Review [underfunded-request and rejection-cost abuse](#who-pays-for-failure) separately from settlement correctness.
- Record the returned request ID and committed registry state; do not infer completion from the request event.
- Acceptance burns the locked amount plus fee reserve and remints the unused reserve (`max-fee - actual-fee`). Rejection unlocks the funds. Verify actual deployed behavior after upgrades.
- Match completion to request ID, Bitcoin transaction/output, recipient script, amount and actual fee. Reconcile canonical Bitcoin inclusion and the Stacks acceptance state.
- Recipient `version` is the protocol's discriminator, not a Bitcoin Base58 version byte or a Stacks principal version:

| Version | Script family | `hashbytes` length |
|---|---|---|
| `0x00` | P2PKH | 20 |
| `0x01` | P2SH | 20 |
| `0x02` | P2SH-P2WPKH | 20 |
| `0x03` | P2SH-P2WSH | 20 |
| `0x04` | P2WPKH | 20 |
| `0x05` | P2WSH | 32 |
| `0x06` | P2TR | 32 |

- Decode the intended Bitcoin address with a network-aware library and verify the resulting script. Require exactly one version byte and the family-specific payload length.
- Contract tuple validation cannot establish the user's intended Bitcoin network from hash bytes alone.
- Test insufficient available balance, fee reserve/refund, invalid recipient encoding, duplicate completion, unauthorized signer calls, rejects and reorg reconciliation.

Sources: [deposit contract](https://github.com/stacks-sbtc/sbtc/blob/eb507946c65bdf4dde72469ea8cb2481fa276a17/contracts/contracts/sbtc-deposit.clar), [withdrawal contract](https://github.com/stacks-sbtc/sbtc/blob/eb507946c65bdf4dde72469ea8cb2481fa276a17/contracts/contracts/sbtc-withdrawal.clar), [registry](https://github.com/stacks-sbtc/sbtc/blob/eb507946c65bdf4dde72469ea8cb2481fa276a17/contracts/contracts/sbtc-registry.clar).

## Test proofs and outputs

- Compare txid against an independent serializer/hash calculation; use SegWit variants with equal base data and different witnesses.
- Reject malformed/trailing bytes, absent outputs, oversized scripts, wrong scripts/amounts and insufficient confirmations.
- Exercise one-transaction blocks, odd/even trees, wrong index/count, missing/extra siblings, malformed hash lengths and endian swaps.
- Reject the right transaction under the wrong header/height; enforce unavailable-height and confirmation boundaries.
- Replay the same outpoint with different proof encodings, witnesses, claimants or application IDs; test late rollback of credit and replay state together.
- Measure execution cost at the largest inputs you accept.
- Test real anchored inclusion in devnet or a pinned supported chain fixture. Synthetic parser/Merkle tests alone do not establish canonical inclusion or live integration.

## Related

- [clarity-epochs](../clarity-epochs/SKILL.md): language and epoch gates.
- [clarity-apis](../clarity-apis/SKILL.md): Stacks receipts and transaction proofs.
- [clarity-assets](../clarity-assets/SKILL.md#sbtc): ordinary sBTC transfers.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarity-bitcoin`: [2d5ab1b991](https://github.com/friedger/clarity-bitcoin/tree/2d5ab1b99174c4008bd57775d6d1866e303021fb).
- `sbtc`: [eb507946c6](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17).
- `stacks-core-targeted`: [01a60adcb6](https://github.com/stacks-network/stacks-core/tree/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7).
- `bips`: [5aadddb511](https://github.com/bitcoin/bips/tree/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793).
- `bitcoin-core`: [6574cb4086](https://github.com/bitcoin/bitcoin/tree/6574cb40869b96b9ffc79c19dc8f4e467d60f321).
