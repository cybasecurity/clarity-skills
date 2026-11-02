# SFT post-conditions

Contract pattern, client conditions and tests behind [SIP-013 semi-fungible tokens](../../clarity-sip-compliance/SKILL.md#sip-013-semi-fungible-tokens) in clarity-sip-compliance.

Post-conditions see only native asset movements: `ft-transfer?`, `ft-burn?`, `nft-transfer?` and `nft-burn?`. A burn counts as a send by the owner ([burn logging](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/functions/assets.rs#L1252)); mints are not recorded. An SFT that keeps balances only in a map is invisible to them. [SIP-013](https://github.com/stacksgov/sips/blob/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-013/sip-013-semi-fungible-token-standard.md#use-of-post-conditions) asks for conditions on both the amount and the token ID and recommends using both `define-fungible-token` and `define-non-fungible-token`. Its [reference implementation](https://github.com/MarvinJanssen/stx-semi-fungible-token/blob/2b6206b1068af694bd5b2a75ec481d7a9447dae6/README.md#sfts-and-post-conditions) shows how.

## Contract pattern

- One FT carries the amounts of every ID, so `get-overall-balance` and `get-overall-supply` read `ft-get-balance` and `ft-get-supply`. The map keeps the per-ID balances.
- A tag NFT keyed `{token-id: uint, owner: principal}` marks a holder of an ID. The `owner` field makes each key unique, so many principals can hold the same ID.
- A transfer moves the amount with `ft-transfer?`, then burns and re-mints the sender's tag. The burn records a send of that ID by the sender, who still holds the tag afterwards.
- Mint the recipient's tag only when it is missing. The [reference implementation](https://github.com/MarvinJanssen/stx-semi-fungible-token/blob/2b6206b1068af694bd5b2a75ec481d7a9447dae6/contracts/semi-fungible-token.clar) burns and re-mints it too, which records a send by any recipient that already holds the ID ([recipient tags](#recipient-tags-in-deny-mode)).
- Mints use `ft-mint?` and `tag-if-missing`. Burns use `ft-burn?` and `retag` on the owner, so a burn takes the same two conditions as a transfer.
- Only the defining contract can move or burn its native assets, so tags stay in step with balances as long as no public function moves a tag on its own.

```clarity
;; fragment: SIP-013 transfer with native mirrors; ERR_INSUFFICIENT_BALANCE is (err u1), ERR_NOT_TOKEN_OWNER is (err u4)
(define-fungible-token sft)
(define-non-fungible-token sft-id {token-id: uint, owner: principal})
(define-map balances {token-id: uint, owner: principal} uint)

(define-private (get-balance-uint (token-id uint) (who principal))
	(default-to u0 (map-get? balances {token-id: token-id, owner: who})))

;; burn and re-mint: the burn records a send of this ID by its owner
(define-private (retag (tag {token-id: uint, owner: principal}))
	(begin
		(and (is-some (nft-get-owner? sft-id tag)) (try! (nft-burn? sft-id tag (get owner tag))))
		(nft-mint? sft-id tag (get owner tag))))

;; mint only when missing: mints are not recorded, so the recipient sends nothing
(define-private (tag-if-missing (tag {token-id: uint, owner: principal}))
	(if (is-none (nft-get-owner? sft-id tag)) (nft-mint? sft-id tag (get owner tag)) (ok true)))

(define-public (transfer (token-id uint) (amount uint) (sender principal) (recipient principal))
	(let ((sender-balance (get-balance-uint token-id sender)))
		(asserts! (or (is-eq tx-sender sender) (is-eq contract-caller sender)) ERR_NOT_TOKEN_OWNER)
		(asserts! (<= amount sender-balance) ERR_INSUFFICIENT_BALANCE)
		(try! (ft-transfer? sft amount sender recipient))
		(try! (retag {token-id: token-id, owner: sender}))
		(try! (tag-if-missing {token-id: token-id, owner: recipient}))
		(map-set balances {token-id: token-id, owner: sender} (- sender-balance amount))
		(map-set balances {token-id: token-id, owner: recipient} (+ (get-balance-uint token-id recipient) amount))
		(print {type: "sft_transfer", token-id: token-id, amount: amount, sender: sender, recipient: recipient})
		(ok true)))
```

- `ft-transfer?` returns SIP-013's `u2` (sender is the recipient) and `u3` (zero amount). The events come in the order the SIP asks for: native events, then `sft_transfer`.

## Client conditions

```js
import { Cl, Pc } from '@stacks/transactions';

const tagOf = (id, owner) => Cl.tuple({ 'token-id': Cl.uint(id), owner: Cl.principal(owner) });

// token = { contractId, ftName, tagName }, names as declared in the contract
export function sftSendConditions(token, id, amount, sender) {
  return [
    Pc.principal(sender).willSendEq(amount).ft(token.contractId, token.ftName),
    Pc.principal(sender).willSendAsset().nft(`${token.contractId}::${token.tagName}`, tagOf(id, sender)),
  ];
}

// for contracts that also burn and re-mint the recipient's tag (Stacks 3.4+)
export function sftRecipientTagCondition(token, id, recipient) {
  return Pc.principal(recipient).willMaybeSendAsset().nft(`${token.contractId}::${token.tagName}`, tagOf(id, recipient));
}
```

- In `Deny` mode both sender conditions are needed. The FT condition alone aborts with `No checks for non-fungible asset <asset> moved by <sender>`, because the tag burn is a send.
- A wrong ID or a wrong amount aborts, so the pair bounds "exactly N of ID I from this sender".
- Take the FT and tag names from the contract's `define-fungible-token` and `define-non-fungible-token`, and validate the contract ID as in [Build an FT condition](../../clarity-wallets/SKILL.md#build-an-ft-condition).
- The FT condition counts the total over all IDs. For several IDs in one transaction (`transfer-many`), use one FT condition for the sum and one tag condition per ID. Nothing then ties an amount to an ID: 5 of ID 1 and 7 of ID 2 pass the same conditions as 7 and 5. Send one ID per transaction when the split matters.

### Recipient tags in Deny mode

- `Deny` mode checks the sends of every principal, not only the signer's ([coverage](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/crates/stacks-transactions/src/lib.rs#L325-L330)). With a contract that burns and re-mints the recipient's tag, a transfer or mint to a principal that already holds the ID aborts with `No checks for non-fungible asset <asset> moved by <recipient>` unless the client covers that tag.
- Cover it with `sftRecipientTagCondition`: SIP-040 `MAY SEND` passes whether or not the tag moves. Alternatively, use `Originator` mode when the origin is the sender. Read the deployed contract to see which tags it burns.

### Contract holders

- A contract that sends its SFTs inside `as-contract?` needs `with-ft` for the FT and `with-nft` for its own tag. With `with-ft` alone the call returns `(err u128)` ([`as-contract?` rules](../../clarity-security/SKILL.md#execution-context)). Bitflow's DLMM pools use the same FT plus tag-NFT shape: [position allowances](../../clarity-ecosystem/references/positions.md#bitflow-dlmm-liquidity-sbtcusdcx-pool-dlmm-pool-sbtc-usdcx-v-1-bps-10).

## Tests

- The Clarinet SDK enforces conditions passed to raw `simnet.callPublicFn` calls, and a violated condition throws `Post-condition check failure` ([post-conditions in tests](../../clarity-testing/SKILL.md#post-conditions-in-tests)).
- In `Deny` mode, assert that the two sender conditions pass for a transfer to a new holder, a transfer to an existing holder and a burn. Then assert that a wrong ID, a wrong amount and the FT condition alone each throw and leave balances unchanged. For a contract that burns recipient tags, also assert that a transfer to an existing holder throws without the recipient condition.
- Assert that the mirrors match the map: each holder's `ft-get-balance` equals the sum of its per-ID balances, `ft-get-supply` equals the sum of `get-total-supply`, and every holder with a nonzero ID balance owns that tag.
- Simnet checks conditions the way a node does. A wallet's display and signing of tuple-valued NFT conditions still need a devnet test ([wallets](../../clarity-wallets/SKILL.md#post-conditions)).
