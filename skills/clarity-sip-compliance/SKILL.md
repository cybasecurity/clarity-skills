---
name: clarity-sip-compliance
description: "Token standards in Clarity: SIP-010, SIP-009 and SIP-013 traits and conformance, metadata, SIP-018 signed data. Use when writing a token or NFT contract or checking trait conformance."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity SIP Compliance

Assess clause-to-code-to-test conformance or implement standards while preserving requested behavior.

Writing or changing contract code: also load `clarity-scholar` and `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

## Key distinctions

- **`impl-trait` checks types only:** Verify balances, native assets, transfer effects, memos and errors separately. Bounded return types need compatibility, not identical text ([SIP-010](#sip-010-fungible-tokens)).
- **SIP-009 does not prescribe caller authentication:** It specifies transfer ownership results. Missing authentication is a security issue; cite an actual clause before claiming a normative violation.
- **SIP-010's `tx-sender` check is an example:** The SIP mandates neither one sender check nor global error codes. Its `u1`–`u4` meanings are recommendations local to the token interface, not an application-wide numbering.
- **Not every memo print complies:** Print a present memo unwrapped after a successful native transfer. `some 0x` is present and `none` is absent; a custom tuple changes the event interface.
- **Accepted is not activated:** Separate application compatibility, proposal status and activation. SIP-044 disables the `cost-voting` boot contract (SIP-006's voting mechanism) from epoch 4.0; SIP-006's cost model remains. Historical proposals need not describe current APIs.

See [recall corrections](../clarity-epochs/SKILL.md#recall-corrections) for common mistakes.

## Writing a token: shared rules

- Compile with Clarity 4 or later. Every extension beyond the standard (mint, burn, pause, admin) is a new surface to review.
- Use native assets (`define-fungible-token`, optional second argument caps supply; `define-non-fungible-token`) so postconditions and indexers see every movement. Map-only balances are invisible to native asset constraints, and SIP-shaped methods alone do not make a synthetic balance equivalent to a native FT.
- `ft-transfer?`, `nft-transfer?`, `ft-burn?` and `nft-burn?` do not look at `tx-sender`: the VM lets the defining contract move any holder's balance. Only native STX transfers and burns require `sender == tx-sender`. Every public path that reaches a native token operation therefore needs its own owner check.
- Owners may be contract principals; avoid EOA-only assumptions.
- `impl-trait` the deployed mainnet trait principal and keep it in source on every network. On testnet/devnet the trait needs a deployment on that network: in Clarinet add the mainnet principal under `[[project.requirements]]` (simnet deploys it at the mainnet principal; `clarinet deployments apply` publishes it under your deployer on devnet/testnet and rewrites the ID in later contracts). Never hand-edit the principal per environment, and do not silently choose a testnet trait on mainnet. SIP-listed testnet principals and their current status: [standard traits](../clarity-system-integration/references/addresses.md#standard-traits).

### Authorization choice

- SIP-010's example checks only `tx-sender`; SIP-013 recommends also accepting `contract-caller`. Neither requires rejecting contract-mediated transfers. The default here is either identity, `(or (is-eq tx-sender sender) (is-eq contract-caller sender))`, because a contract can then hold and spend tokens or NFTs it owns without `as-contract?` (sBTC does this).
- Trade-off: the `tx-sender` branch still lets any contract the owner calls (a marketplace, a commission or other callback) move the owner's assets; the `contract-caller` branch adds nothing against that. A `tx-sender`-only check is no safer in that respect; it only stops contracts from spending their own balances without `as-contract?`. Owner-side protection is bounded postconditions and not calling untrusted contracts. See [A01](../clarity-security/references/patterns.md#a01-sender-authority-forwarded-through-an-attacker) and the [per-asset authorization matrix](../clarity-assets/SKILL.md#transfer-authorization).
- To forbid forwarded owner authority, check `(asserts! (is-eq contract-caller sender) ...)` (direct calls and contract-held balances only); that breaks routers that call on the user's behalf unless the user is the direct caller.
- Document whichever model you pick; integrators depend on it. The either-identity default is a design choice, not SIP-mandated.

### Token administration

- If the token has an administrator and the project has no governance model yet, keep it in a data var initialized to `tx-sender` (the deployer) plus `pending-admin (optional principal)`. Keep an existing model (DAO extension checks, role maps, a multisig contract); a token with no privileged functions needs no administrator.
- Privileged functions (mint, set-token-uri, admin changes) check `contract-caller`, not `tx-sender`: an admin calling an untrusted contract must not lend it this power. Under an ExecutorDAO-style owner, setters check `tx-sender` against the DAO instead ([proposal contracts](../clarity-governance/SKILL.md#proposal-contract-dao)).
- Standard-account administrators use nomination then acceptance. The nominee must be a standard principal of the execution network: `principal-destruct?` returns `err` for another network's version byte, and `name` is `none` for a standard principal. Acceptance requires `(is-eq (some contract-caller) (var-get pending-admin))` and clears the nomination.
- Direct handoff to a contract (`set-contract-admin`) accepts only a contract principal (`name` is `some`), clears any nomination, and requires a reviewed onward administration route; see [ownership setters](../clarity-governance/SKILL.md#two-step-ownership).
- Print every change (for example `actor`, `previous` and the new `administrator`). Application errors use a range separate from SIP transfer and native codes (for example `u1000` and up; keep a project's existing range).

```clarity
;; fragment: nomination/acceptance (standard-account nominee); ERR_* are (err u1000+)
(define-public (propose-admin (new-admin principal))
	(begin
		(asserts! (is-eq contract-caller (var-get administrator)) ERR_OWNER_ONLY)
		(asserts! (is-none (get name (unwrap! (principal-destruct? new-admin) ERR_ADMIN_KIND))) ERR_ADMIN_KIND)
		(var-set pending-admin (some new-admin))
		(print {event: "admin-proposed", actor: contract-caller, previous: (var-get administrator), administrator: new-admin})
		(ok true)))
(define-public (accept-admin)
	(let ((previous (var-get administrator)))
		(asserts! (is-eq (some contract-caller) (var-get pending-admin)) ERR_PENDING_ADMIN)
		(var-set administrator contract-caller)
		(var-set pending-admin none)
		(print {event: "admin-accepted", actor: contract-caller, previous: previous, administrator: contract-caller})
		(ok true)))
```

## SIP-010 fungible tokens

Source: [SIP-010](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-010). Mainnet trait: `'SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.sip-010-trait-ft-standard.sip-010-trait`, defined as:

```clarity
;; SIP-010 trait as deployed at SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.sip-010-trait-ft-standard
(define-trait sip-010-trait
	(
		(transfer (uint principal principal (optional (buff 34))) (response bool uint))
		(get-name () (response (string-ascii 32) uint))
		(get-symbol () (response (string-ascii 32) uint))
		(get-decimals () (response uint uint))
		(get-balance (principal) (response uint uint))
		(get-total-supply () (response uint uint))
		(get-token-uri () (response (optional (string-utf8 256)) uint))
	)
)
```

- Return bounds are maxima: a `(string-ascii 10)` return satisfies `(string-ascii 32)`; a declared bound of 40 does not, even if the current value is short. Check [return-type admission](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/analysis/types.rs), not textual type equality, and do not extrapolate the same direction to parameter types.
- Getters are recommended to be read-only. Return balance and supply from the native asset (`(ok (ft-get-balance token who))`, `(ok (ft-get-supply token))`) and check them against real mint/burn/transfer operations, including contract holders. `impl-trait` checks compatible function types, not honest balances or transfer semantics.
- Error codes **should** follow `u1` insufficient balance, `u2` identical sender/recipient, `u3` zero amount, `u4` unauthorized. `ft-transfer?` itself returns `u1`/`u2`/`u3`; the owner check returns `(err u4)`. Classify a deviation at its actual normative strength and explain consumer impact; do not move these into a project's local error range and still claim conventional compatibility.
- Memo: print a present memo **unwrapped** via `print` **after** a successful native transfer: `(match memo to-print (print to-print) 0x)`. `none` emits no memo; `some 0x` is present and is still emitted; wrapping the memo in a custom tuple is a different event. Error paths must not leave transferred funds or success events.
- Client postconditions are explicitly recommended; if a wrapper transfers native STX, state the native asset consumers must constrain.
- For sBTC, the deployed `get-balance` includes locked units and availability needs its separate getter; classify that integration fact separately from a blanket claim of SIP noncompliance.

```clarity
;; fragment: SIP-010 transfer; ERR_NOT_TOKEN_OWNER is (err u4)
(define-public (transfer (amount uint) (sender principal) (recipient principal) (memo (optional (buff 34))))
	(begin
		(asserts! (or (is-eq tx-sender sender) (is-eq contract-caller sender)) ERR_NOT_TOKEN_OWNER)
		(try! (ft-transfer? example-token amount sender recipient))
		(match memo to-print (print to-print) 0x)
		(ok true)))
```

- Regression set: direct authorized transfer; unauthorized third-party transfer and unauthorized indirect transfer (`err u4`); intended authorized contract transfer; insufficient balance (`err u1`); zero amount (`err u3`); self-transfer (`err u2`); `none` memo emits no print; `(some 0x)` emits an empty-buffer print **after** the `ft_transfer_event`; 34-byte memo; oversized memo rejected by type; failed transfer emits nothing; balance/supply before and after mint/burn/transfer.

## SIP-009 non-fungible tokens

Source: [SIP-009](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-009). Mainnet trait: `'SP2PABAF9FTAJYNFZH93XENAJ8FVY99RRM50D2JG9.nft-trait.nft-trait`, defined as:

```clarity
;; SIP-009 trait as deployed at SP2PABAF9FTAJYNFZH93XENAJ8FVY99RRM50D2JG9.nft-trait
(define-trait nft-trait
	(
		(get-last-token-id () (response uint uint))
		(get-token-uri (uint) (response (optional (string-ascii 256)) uint))
		(get-owner (uint) (response (optional principal) uint))
		(transfer (uint principal principal) (response bool uint))
	)
)
```

- The NFT URI is optional **ASCII 256**, unlike SIP-010's UTF-8 URI. SIP-016 clients substitute `{id}` with the decimal token ID.
- Getters must never return `err`. Unknown IDs give `(ok none)` for owner and URI; IDs above the last ID have no owner. `get-last-token-id` is an upper bound, not the number currently minted after burns.
- A successful transfer changes the owner to the recipient, and a transfer of an ID above `get-last-token-id` must fail.
- SIP-009 says nothing about authorization: rejecting transfers by non-owners is a security requirement of your implementation, not SIP text. The owner check in `transfer` is the only theft guard. `nft-transfer?` then checks that `sender` owns the ID (`err u1`) and that the ID exists (`err u3`). NFT application errors use a range of their own (for example `u1000` and up) so they do not collide with native codes.
- Mint: authorize minting the way the design requires (an administrator, a minter role or contract, or a public mint with its own payment and supply checks). The common scheme below mints `last-token-id + 1` and stores it; sparse or derived IDs are valid if `get-last-token-id` stays at least the highest minted ID. Return `(ok id)`.
- The standard requires native NFT assets for postcondition observability. Its clause that a `transfer` without a deny-mode or NFT owner-change postcondition **must** fail with `abort_by_post_condition` is not enforced by the node for allow-mode transactions, and a contract cannot read postconditions: record it as "normative text not implementable at contract level" (not applicable), not a failed check, and use `define-non-fungible-token` so wallets can attach NFT conditions. Verify transaction-level postconditions with an SDK/node that enforces them.
- `get-owner` stability: once `get-owner` returns `A`, it must return the same value until `transfer` is called with `A` as sender. A burn (`nft-burn?`) changes the owner without `transfer`; document it as a deviation or do not offer burns. With burns, `last-token-id` stays an upper bound, not a count.

```clarity
;; fragment: SIP-009 transfer, mint and getters (ERR_* are (err u1000+))
(define-public (transfer (id uint) (sender principal) (recipient principal))
	(begin
		(asserts! (or (is-eq tx-sender sender) (is-eq contract-caller sender)) ERR_NOT_TOKEN_OWNER)
		(nft-transfer? example-nft id sender recipient)))
(define-public (mint (recipient principal))
	(begin
		(asserts! (is-eq contract-caller (var-get administrator)) ERR_OWNER_ONLY)
		(let ((id (+ (var-get last-token-id) u1)))
			(try! (nft-mint? example-nft id recipient))
			(var-set last-token-id id)
			(ok id))))
(define-read-only (get-owner (id uint)) (ok (nft-get-owner? example-nft id)))
(define-read-only (get-token-uri (id uint))
	(ok (if (is-some (nft-get-owner? example-nft id)) (some "ipfs://example/{id}.json") none)))
```

- Tests: unknown ID getters return `(ok none)`, transfer of an ID above `get-last-token-id` fails, owner after transfer equals recipient, a third party's transfer fails, contract principals can own tokens.

## SIP-013 semi-fungible tokens

Source: [SIP-013](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-013). Mainnet trait: `'SPDBEG5X8XD50SPM1JJH0E5CTXGDV5NJTKAKKR5V.sip013-semi-fungible-token-trait.sip013-semi-fungible-token-trait`.

- This is an SFT standard, **not** a generic SIP-010 batch-transfer standard.
- Trait functions, all returning `(response T uint)`: `get-balance (uint principal)`, `get-overall-balance (principal)`, `get-total-supply (uint)`, `get-overall-supply ()` and `get-decimals (uint)` → `uint`; `get-token-uri (uint)` → `(optional (string-ascii 256))`; `transfer (uint uint principal principal)` and `transfer-memo (uint uint principal principal (buff 34))` → `bool`.
- `transfer` argument order is token ID, amount, sender, recipient; `transfer-memo` adds a non-optional `(buff 34)`.
- Balance and supply getters should never return `err`. Unknown IDs and holders give `u0`; the overall balance and supply are sums over all IDs.
- Postconditions cannot see map-only balances. Mirror them in native assets as SIP-013 recommends: one FT for all IDs plus a tag NFT keyed `{token-id: uint, owner: principal}`, which each transfer burns and re-mints for the sender. Wallets can then bound the amount (FT) and the ID (tag). Contract pattern, client conditions and the Deny-mode recipient trap: [SFT post-conditions](references/sft-post-conditions.md).
- Custom `sft_transfer`, `sft_mint`, `sft_burn` events carry the specified token ID, amount, and relevant principals. Order: native event, SFT event, then memo when present.
- The optional send-many extension has its own trait with bounded lists (200 in the current spec). If one entry fails, the batch should fail: test a late failure and prove earlier state is rolled back; an outer `ok` containing a list of `err` values does not establish atomicity.

## Metadata: SIP-016 and SIP-019

Sources: [SIP-016](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-016), [SIP-019](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-019).

- Validate the URI type from the token's interface separately from the JSON schema it serves. Check actual required fields and token-class extensions; do not infer metadata compliance from a reachable image URL. Consumers should prefer authoritative on-chain fields where specified.
- Restrict URI setters to the administrator. After a metadata change, emit the SIP-019 notification for the token's class. For an FT: `(print {notification: "token-metadata-update", payload: {token-class: "ft", contract-id: current-contract}})`. An NFT uses `token-class: "nft"` and may list the changed `token-ids`; an SFT uses `"sft"` and must list them.
- An NFT notification without `token-ids` refreshes every token. Use `update-mode` and `ttl` only as defined.
- Indexers must validate notification provenance/target and treat a notification as a refresh hint, not authority to replace token ownership or financial state.
- A contract test cannot prove the availability or correctness of off-chain metadata; list it as an evidence gap.

## SIP-018: signed structured data

Source: [SIP-018](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-018).

- Use consensus serialization and SHA-256, not JSON text. The digest is SHA-256 of prefix `0x534950303138`, the domain hash and the message hash. The domain includes application name, version and chain ID with the specified types.
- Use the SIP's vectors to establish cross-language compatibility, including field ordering imposed by consensus serialization.
- Bind actions, amount, asset, recipient and the intended contract/application as the protocol needs. Nonce, expiry and replay protection are security requirements of the application's message and state, not fields supplied by SIP-018.
- Reject wrong signer, chain, domain, expired data, altered amount/recipient and replay.
- Clarity 1 retains the testnet-only `principal-of?` behavior even under later epochs; Clarity 2+ selects the execution network.
- Do not confuse secp256k1 recoverable signatures with secp256r1 verification or assume their encodings are interchangeable.

## Consensus and adjacent standards

The specification's wording governs; check [versions](../clarity-epochs/SKILL.md) and the activated node implementation.

- SIP-002/005 define language/serialization foundations.
- SIP-021 (Nakamoto) and later upgrades change timing and execution.
- SIP-024 repairs historical type/serialization validation.
- SIP-033/039/044 introduce Clarity 4/5/6; SIP-035 is informational (documents the Clarity 4 `secp256r1-verify` double hash).
- SIP-040 adds Originator post-condition mode and NFT may-send; epoch 4.0 adds Staking/PoX post-conditions.
- SIP-042 disables `at-block` for **all** versions from epoch 3.4: merely keeping `clarity_version = 4` does not preserve historical execution. SIP-039's earlier proposed historical-state repairs are superseded by that removal.
- SIP-045 describes PoX-5; its boot-contract requirements belong to the actual network epoch and PoX version, not a fabricated 'SIP-010-compatible staking' trait.
- Wallet interface SIP-030 and transaction multisig SIP-027 are relevant only when the project implements those client/transaction flows.
- Drafts such as SIP-038 are not universal requirements for NFTs.
- For consensus upgrades, state the effect on existing deployments as well as new source.

## Conformance review

- Start with the protocol's claims and exposed interfaces. Select applicable standards, pin the [official SIP repository](https://github.com/stacksgov/sips) commit, and inspect proposal status, layer, specification, amendments, superseding proposals and activation; consult [versions](../clarity-epochs/SKILL.md) for activation questions.
- Refresh the dated [catalog](references/catalog.json) before deciding requirements: compare its `commit` with `gh api repos/stacksgov/sips/commits/main --jq .sha` (or `git -C <sips checkout> log -1 --format=%H`) and re-read the status of each SIP you rely on.
- Ratification does not mandate universal implementation; applicability follows interfaces and claims. Contracts can implement token/signing interfaces; arbitrary application functions cannot implement VM/network consensus upgrades. Draft/withdrawn proposals require explicit product intent.
- Read beyond the trait: semantic clauses, events, native assets, error conventions and client obligations can be outside it. Check ABI types, argument order, list/buffer bounds, native assets, response variants, authorization, errors, memo/event order, getters, metadata and invariants.
- Inspect the code and real dependency behavior first. A name scanner can miss compatible but differently named aliases, optional extension traits and malicious implementations. Traits, function-name scans, audit labels and happy-path transfers cannot establish complete compliance.
- Record each clause in a table: SIP/section; normative strength (must/should/may or exact wording); applicable component; code location; positive/negative test; result (pass, fail, not applicable, unverified); explanation.
- A 'should' deviation is not a 'must' violation. Separate mandatory violations, recommendation deviations and security issues; keep ordinary application bugs separate from standards violations even when both need repair. Do not silently strengthen a recommendation because an audit report called it noncompliance.
- Use the official test vectors for serialization/signing; assert balance/supply/owner invariants for assets. Test direct and contract-mediated callers on the selected network, since standard users include other protocols. Default to Clarigen-generated calls backed by the Clarinet SDK. A contract test cannot prove a wallet's transaction postconditions.
- Reuse a verified deployed trait where appropriate, verifying network principals against the [system addresses](../clarity-system-integration/references/addresses.md); SIP-listed testnet examples may no longer exist. Resolve relative names in the deployment context; compile with the selected language/epoch, then test behavior.
- When sources conflict, quote only the short disputed clause, pin both sources, and mark the affected conclusion unverified until the version-matched implementation/test resolves it.
- Deliver the conformance matrix, changes, executed tests and evidence gaps (unresolved remote metadata, missing transaction-level tests, unverified deployments). Limit claims to the inspected scope/version; explain intentional extensions and consumer effects.

## References

- [Catalog](references/catalog.json): dated SIP numbers, titles, status and paths.
- [SFT post-conditions](references/sft-post-conditions.md): FT plus tag-NFT mirror, client conditions, recipient tags and tests.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
- `stx-semi-fungible-token`: [2b6206b106](https://github.com/MarvinJanssen/stx-semi-fungible-token/tree/2b6206b1068af694bd5b2a75ec481d7a9447dae6), the SIP-013 reference implementation.
