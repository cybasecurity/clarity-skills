# Sender preservation and signed authorizations

## Sender preservation

- A downstream token/vault may need the user's `tx-sender`. Switching the entry contract to its own context with `as-contract?` would change whose funds or position it can authorize. Authenticate the entry point, then retain the sender through trusted downstream calls.

### Direct-entry policy

The entry function requires `contract-caller` = `tx-sender` before forwarding the user's sender:

```clarity
;; fragment: .vault must authenticate this entry contract and validate the payment
;; id: user-entrypoint
(define-public (deposit (amount uint))
	(begin
		(asserts! (is-eq contract-caller tx-sender) (err u1100))
		(contract-call? .vault deposit amount tx-sender)))
```

- User U → entry E: both identities are U at E. At vault V, `tx-sender` stays U and `contract-caller` becomes E. V must authenticate E and bind payer, amount and beneficiary correctly.
- U → untrusted R → E: sender is U, caller is R, so the guard rejects inherited user authority.
- This proves identity equality, not that the caller is an account, the UI is honest, or every downstream call is safe. A router can enter under its own sender scope; it then acts as itself, with its own funds/position.
- Native principal multisig transactions can enter directly. Unscoped contract multisigs/routers cannot preserve U through this guard; do not add it indiscriminately to composable APIs.
- Never replace the check with `is-standard`, accept any trait-compatible router, or remove it merely to pass integration tests.
- Deployed example: [Zest market `collateral-add`](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/market/v0-8-market.clar#L1042-L1049) binds `account = contract-caller` and requires equality with `tx-sender`. Check the exact target function: this is not a claim that every market method has the same guard.

### Routed policy

- If preserving U through an intermediary is required, design explicit delegation: authenticate the immediate router, constrain its role, and bind the user's intended operation, assets, limits, beneficiary, deadline and replay protection.
- A router allowlist alone does not establish user consent for every operation. Audit the router's own entry points and callbacks.
- Authenticate before transfers/writes/untrusted calls. Keep downstream targets trusted or validate their exact role/identity; an initial equality check does not prevent a later malicious callback from using inherited authority elsewhere.
- [Asset allowances and postconditions](../../assets/SKILL.md#transfer-authorization) are separate controls; asset bounds do not constrain arbitrary NFT listings or governance state.
- Test both policies: direct user entry, unscoped malicious forwarding, scoped contract-owned entry, forged payer/beneficiary, unauthorized direct vault access and downstream failure rollback. Assert actual balances and identities at each hop. Attack model: [A01](patterns.md#a01-sender-authority-forwarded-through-an-attacker).

## Signed authorizations

- Digest: bind network/chain ID, contract, operation, arguments, signer scope and nonce/deadline. Use SIP-018 serialization/domain rules where that scheme is promised. The primitive consumes a 32-byte digest directly: match the signing scheme's hashing/prefix/serialization exactly; do not hash twice or accept an arbitrary caller-selected digest as authorization for unrelated operation arguments.
- Recovery is not authorization: `secp256k1-recover?` returns a 33-byte **compressed public key**, not an Ethereum address or Stacks principal. Compare it, or its correctly derived identity, with the authorized signer. A changed digest can recover a different valid key rather than return an error.
- For a known public key, prefer `secp256k1-verify`: it already rejects high-S signatures. Pass it the trusted key, not an unchecked caller-supplied one, and require `true`.
- High-S: `secp256k1-recover?` accepts high-S signatures, like EVM `ecrecover`; replacing `s` with `n - s` and flipping the recovery parity recovers the same key. For recovered signers, handle the response, check signer authority and require low-S when canonical signatures are part of the protocol ([canonical recovery helper](#canonical-recovery-helper-clarity-2)). High-S acceptance alone does not prove an exploitable vulnerability.
- Encoding: recovery input is exactly `r[32] || s[32] || recovery-id[1]`; Clarity accepts IDs `0–3`. Ethereum `27/28` needs explicit conversion to `0/1`. Restrict to `0/1` for Ethereum-compatible recovery; do not blindly subtract 27 or accept EIP-155 transaction `v` as a message recovery ID. Raw 64-byte `r || s`, DER and ERC-2098 compact signatures are not recovery inputs; decode the specified format explicitly.
- `secp256k1-verify` accepts 64/65 bytes; a supplied final byte must be `0–3` but is ignored during verification.
- Errors: recovery returns `(err u2)` for a short signature or out-of-range recovery ID; cryptographic recovery failure returns `(err u1)`. It does not return a zero address. Never substitute a default signer on error. A short digest can cause a runtime error; validate exact lengths before calling the primitive when graceful rejection is required.
- Replay: low-S does **not** make ECDSA signatures unique or prevent replay. Consume a signer-scoped nonce or domain-bound authorization digest; check and update replay state before external effects; preserve atomic rollback. Never key usage by raw signature or its hash (high-S twins and the ignored final byte defeat that).
- Test: low/high-S twins, wrong signer/digest, valid alternative encodings, bad lengths/IDs/scalars, replay, wrong domain and expiry. Verify native behavior on the selected tool/epoch.

### Canonical recovery helper, Clarity 2+

- OpenZeppelin's low-S guard rejects the high-S variant; this helper applies the same rule in Clarity.
- Compare the fixed-width, big-endian S bytes lexicographically. Clarity has no uint256; `buff-to-uint-be` cannot consume the 32-byte scalar.
- This helper validates encoding/canonicality only. Its caller must compare the recovered key and enforce the signed operation's replay rules.

```clarity
;; clarity 2
;; id: recover-canonical
(define-constant HALF_ORDER 0x7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a0)

(define-read-only (recover-canonical (digest (buff 32)) (signature (buff 65)))
	(begin
		(asserts! (and (is-eq (len digest) u32) (is-eq (len signature) u65)) (err u1000))
		(asserts! (<= (unwrap! (slice? signature u32 u64) (err u1000)) HALF_ORDER) (err u1001))
		(secp256k1-recover? digest signature)))
```

- The primitive still rejects zero/out-of-range scalars and invalid recovery IDs. The helper permits Clarity's full ID range; add the `0/1` policy when matching Ethereum recovery.
- `u1000/u1001` are local example codes; native `u1/u2` propagate. Allocate or map them deliberately.

Sources: [VM argument/error checks](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity/src/vm/functions/crypto.rs), [native recovery/verification](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/stacks-common/src/util/secp256k1/native.rs), [Stacks regression tests](https://github.com/stacks-network/stacks-core/blob/10474cdec9f9c0bdf05841b58cffc89cdad87a9b/clarity/src/vm/tests/crypto.rs), [OpenZeppelin ECDSA](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/b7f748eae2341b9e8e8f85cf966e94476813d168/contracts/utils/cryptography/ECDSA.sol), [SIP-018](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-018).
