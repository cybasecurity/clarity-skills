# Ledger and hardware signing limits

Device limits behind [Ledger and hardware signing](../../clarity-wallets/SKILL.md#ledger-and-hardware-signing) in clarity-wallets. They come from app source and issues: confirm each on the installed app.

## Size and language support

| Boundary | Source | Consequence |
| --- | --- | --- |
| Historical deployment size failures | [Issue 166](https://github.com/Zondax/ledger-stacks/issues/166), [fix 172](https://github.com/Zondax/ledger-stacks/pull/172), 2024 | Old non-Nano-S flash buffer was 16 KiB; fix increased it to 85 KiB. Compare transaction bytes, not source length or hex-character counts. |
| Configured transaction storage | [v0.27.0 `tx.c`](https://github.com/Zondax/ledger-stacks/blob/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d/app/src/common/tx.c) | Non-Nano-S: 8 KiB RAM and 85 KiB flash; original Nano S: 8 KiB flash. These are buffer configurations, not additive guaranteed source-size limits. |
| Versioned deployments | [LedgerHQ master snapshot](https://github.com/LedgerHQ/app-stacks/blob/3be06bebdef4b7b9bf858759cc096fe5474ab8b3/app/rust/src/parser/transaction_payload/versioned_contract.rs) accepts Clarity tags 1 to 4; [Zondax v0.27.0](https://github.com/Zondax/ledger-stacks/blob/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d/app/rust/src/parser/transaction_payload/versioned_contract.rs) accepts nonzero tags | Confirm the installed app. Chain support for Clarity 5/6 does not prove the signer accepts their versioned deployment payloads. |
| Large multisig deployments | [Fix 206](https://github.com/Zondax/ledger-stacks/pull/206), merged 2025-12-16 | Historical signature-validation failure and unsigned multisig parsing were fixed. A generic size diagnosis can miss a signing bug. |
| Deployment review | [v0.27.0 payload review](https://github.com/Zondax/ledger-stacks/blob/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d/app/rust/src/parser/transaction_payload.rs) | Device review does not display full Clarity source. Review the exact prepared source/payload separately; do not treat its screen as a contract audit. |

## Versioned deployment and multisig failures

- **Do not apply a blanket rule that Ledger rejects `VersionedSmartContract`:** Both apps dispatch payload `0x06`; supported language tags depend on the revision, as shown above. The node still decides whether that language version is valid and activated.
- `SmartContract` (`0x01`) omits the language tag. **Unversioned means the executing epoch's default language**, not an equivalent encoding of your requested version. Retest semantics and verify the deployed version, especially across an epoch boundary.
- Stacks.js 7.6.0 `makeUnsignedContractDeploy` defaults to Clarity 4 when `clarityVersion` is omitted. Omitting the builder option therefore does not necessarily produce an unversioned payload.
- If intentionally choosing node-default deployment, construct the unversioned payload with `createSmartContractPayload(name, code)` before signing. Inspect the serialized round trip. Replacing a payload changes the signing digest and txid: discard old signatures and have every required signer approve the final bytes. Re-estimate fees after rebuilding.
- Before epoch 4.1, prefer an explicit version with a compatible app/wallet. Epoch 4.1 (unscheduled) rejects every versioned deploy ([versions](../../clarity-epochs/SKILL.md#current-network-and-versions)). Check the actual installed app, transport and transaction, not only the newest GitHub tag.
- A `SignatureValidation` error is not proof of an unsupported payload. [PR 206](https://github.com/Zondax/ledger-stacks/pull/206) separately fixed large-contract multisig signing and unsigned multisig parsing. Check signer keys/order, threshold and assembled bytes as well.
- v0.27.0 flags both deployment types as blind signing because the full source is not displayed. Its version parser accepting a payload does not prove that signing policy, device capacity and UI review will also accept it.

Sources: [payload dispatch](https://github.com/Zondax/ledger-stacks/blob/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d/app/rust/src/parser/transaction_payload.rs), [version parser](https://github.com/Zondax/ledger-stacks/blob/3f9bc89ce74bfa74fd4046ee12db8e33c54b984d/app/rust/src/parser/transaction_payload/versioned_contract.rs), [SDK builder defaults](https://github.com/stx-labs/stacks.js/blob/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions/src/builders.ts), [payload construction](https://github.com/stx-labs/stacks.js/blob/e6084a52140b2ad010a9d1a0f1b87d527c3a8870/packages/transactions/src/wire/create.ts), [node language selection](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/stacks/db/transactions/processing/mod.rs).

## Other confirmed corner cases

- Transactions with many post-conditions (for example one NFT condition per DLMM bin) hit device parsing and display caps that have changed between app releases ([PR 227](https://github.com/Zondax/ledger-stacks/pull/227) raised one from 16 to 128; [issue 238](https://github.com/Zondax/ledger-stacks/issues/238) reports failures for wider positions). Test the widest realistic transaction on the installed app, and do not treat a closed issue or unmerged fix as shipped.
- New post-condition modes/types require wallet and device support. Test `MaySend`, `Originator`, staking and PoX conditions when used; support in a node or SDK is insufficient.
- Wallets gate Ledger features on a minimum device-app version (Leather's [version gate](https://github.com/leather-io/mono/blob/c7f03715845889e62bcd52d88caa792400915ed1/apps/extension/src/app/features/ledger/utils/stacks-ledger-utils.ts) requires 0.26.19 at the pinned snapshot). Check the installed app against the wallet release and device model before prescribing an upgrade; a source gate does not prove catalog availability.
- `@zondax/ledger-stacks` 2.0.0 prefers `DMKTransport`. Its guidance disables the DMK session refresher during chunked APDU signing to avoid competing requests. Use the current client instructions; do not copy old transport constructors blindly. [Client](https://github.com/Zondax/ledger-stacks-js).
- Native multisig requires the complete signer configuration and correct signature assembly. Use the [governance skill](../../clarity-governance/SKILL.md) and inspect [Stacks Labs multisig CLI](https://github.com/stx-labs/multisig-cli) as an implementation reference, not evidence every browser wallet supports the same flow.
- Retest after any wallet, device-app or transport upgrade affecting payload parsing/signing. A GitHub release, merge or source fix does not establish availability on every hardware model.
