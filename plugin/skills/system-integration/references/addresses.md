# System and standard address registry

- Entries are dated lookup seeds: check each one's network, source and verification status before use.
- Boot/standard identities belong here; application addresses belong in the [protocol registry](../../protocols/references/addresses.md).
- Never infer a testnet deployment by changing the address prefix, or select an integration by ticker.

## Boot contracts

| Network | Boot principal | Active PoX observed via `/v2/pox` |
|---|---|---|
| Mainnet | `SP000000000000000000002Q6VF78` | `SP000000000000000000002Q6VF78.pox-5` |
| Testnet | `ST000000000000000000002AMW42H` | `ST000000000000000000002AMW42H.pox-5` |

- `/v2/pox.epochs` is the authoritative epoch schedule; it can list a future epoch with an unreachable start height, so do not hardcode "Epoch 4.0" as the latest.
- Boot contract names include `.pox-4`, `.pox-5`, `.costs-4`, `.signers` and `.signers-voting`; resolve activation on the selected network.
- PoX-4 still having source does not make it the active PoX contract. Select `/v2/pox.contract_id` and verify operation-specific behavior.
- `.costs-4` still evaluates historical formulas; epoch 4.0 selects native Rust Costs5. No `.costs-5` contract exists, so its source request returns 404.
- Genesis/history also includes `.pox`, `.lockup`, `.costs`, `.cost-voting`, `.bns` and `.genesis`; later costs/PoX generations and signer DB contracts are added by upgrade initialization. Inspect the target release and actual chain before using them.
- Historical BNS boot source is not proof of the currently recommended naming service.
- Signer DB files with placeholders such as `signers-0-xxx.clar` are templates; resolve actual instances, not a literal placeholder principal.
- Source can be assembled with network-specific constants. Special boot behavior can depend on VM recognition of the boot identity; redeployed copies are not equivalent.
- Boot contracts need consensus initialization/activation evidence, not an ordinary user deployment transaction.

Sources: [boot source/registration](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/stacks/boot), [mainnet PoX](https://api.mainnet.hiro.so/v2/pox), [testnet PoX](https://api.testnet.hiro.so/v2/pox), [cost dispatch](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/costs/mod.rs).

## Standard traits

| Standard | Mainnet trait reference | Testnet reference listed in the SIP |
|---|---|---|
| SIP-009 | `'SP2PABAF9FTAJYNFZH93XENAJ8FVY99RRM50D2JG9.nft-trait.nft-trait` | `'ST1NXBK3K5YYMD6FD41MVNP3JS1GABZ8TRVX023PT.nft-trait.nft-trait` |
| SIP-010 | `'SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.sip-010-trait-ft-standard.sip-010-trait` | `'ST1NXBK3K5YYMD6FD41MVNP3JS1GABZ8TRVX023PT.sip-010-trait-ft-standard.sip-010-trait` |
| SIP-013 | `'SPDBEG5X8XD50SPM1JJH0E5CTXGDV5NJTKAKKR5V.sip013-semi-fungible-token-trait.sip013-semi-fungible-token-trait` | `'STDBEG5X8XD50SPM1JJH0E5CTXGDV5NJTJTTH7YB.sip013-semi-fungible-token-trait.sip013-semi-fungible-token-trait` |

- The final component is the trait name, not part of the contract name.
- Compare the actual trait definition with the applicable [SIP](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips).
- These are ordinary contracts, not boot contracts. Verify canonical successful deployment and exact trait identity; structural compatibility alone is insufficient evidence of normative conformance.
- The testnet column is what each SIP's deployment section lists ([SIP-009](https://github.com/stacksgov/sips/blob/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-009/sip-009-nft-standard.md#deployed-contracts), [SIP-010](https://github.com/stacksgov/sips/blob/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-010/sip-010-fungible-token-standard.md#deployed-contracts), [SIP-013](https://github.com/stacksgov/sips/blob/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-013/sip-013-semi-fungible-token-standard.md#testnet)). Those were deployed on an earlier testnet, before the canonical testnet reset to a new PoX-5 genesis ([testnet resets](../../environments/SKILL.md#remote-data-epochs-and-networks)). Check `GET https://api.testnet.hiro.so/v2/contracts/interface/{address}/{name}` before relying on any of them.
- Current testnet (a reset chain):
  - The SIP-listed principals do not exist (404).
  - There is no official or shared SIP-010 trait: projects deploy their own copy (what a Clarinet requirement remap does).
  - The most referenced SIP-009 copy, `'ST1S8A3H1GFPRM46E5VVC7P5NJQ13SNGJW4FMAZRE.nft-trait.nft-trait`, has the mainnet SIP-009 definition but belongs to an application, not a standards publisher.
  - The official testnet sBTC token, [`SN3VMHXEN64ZZF71JQ5VESXDWTR301XTTXGF4J8F1.sbtc-token`](https://explorer.hiro.so/txid/SN3VMHXEN64ZZF71JQ5VESXDWTR301XTTXGF4J8F1.sbtc-token?chain=testnet&tab=overview) (source identical to mainnet), implements SIP-010 without `impl-trait`, like mainnet.
- Trait arguments are checked by shape, not by trait identity ([execution model](../SKILL.md#execution-model)), and the official sBTC token has no `impl-trait`. So the copy you `impl-trait` matters for your own deploy succeeding on that network, not for interoperability; bind the expected principal ([trait checks](../../security/SKILL.md#calls-traits-recursion)).
- A contract that `impl-trait`s a mainnet trait principal fails to deploy on testnet if that principal does not exist there. Two ways out:
  - **Clarinet requirement remap:** Declare the mainnet trait as a requirement and keep the mainnet principal in your source:

    ```toml
    [[project.requirements]]
    contract_id = "SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.sip-010-trait-ft-standard"
    ```

    Simnet deploys it at the mainnet principal. For devnet and testnet, `clarinet deployments apply` publishes the requirement under your deployer (skipped if already published) and rewrites its mainnet contract ID in the contracts published after it. The plan file (`clarinet deployments generate --testnet`) lists the requirement-publish step; check the deployed source afterwards.
  - **Self-deploy:** Publish the trait contract from the [SIP source](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips) as `<your-address>.sip-010-trait-ft-standard`. Testnet builds then `impl-trait` that principal: generate them from one source with a build step, never by hand-editing the principal per network ([token rules](../../sip-compliance/SKILL.md#writing-a-token-shared-rules)).
- Neither proves a public testnet deployment of the standard; wallets and indexers may not recognize a self-deployed trait.

- Apply [registry freshness rules](../../protocols/SKILL.md#addresses-and-freshness): at age 30 days suggest a package update and verify the addresses you use against the live node; always check active system selection before production use.
