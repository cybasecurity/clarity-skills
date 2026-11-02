---
name: system-integration
description: "Stacks system facts: boot contract and SIP trait addresses (pox-5, sip-010-trait) on mainnet and testnet, address versions, transactions, blocks and tenures. Use for standard Stacks addresses or chain mechanics."
license: MIT
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
  registry_verified_at: "2026-10-20"
---

# Clarity System Integration

Resolve system identity and boot-contract integration here; use [clarity:protocols](../protocols/SKILL.md) for application protocol addresses.

## Key distinctions

- A file in `stacks-core/.../boot` is not proof that its contract is active on a network.
- Boot contracts can rely on privileged VM behavior and network-specific source assembly. Redeploying the source under another principal is not equivalent.
- SIP token traits are ordinary deployed contracts, not boot contracts.
- Replacing a mainnet prefix with a testnet prefix does not establish a corresponding deployment.
- `costs_5.rs` is an active native schedule, not evidence of a deployed `.costs-5` contract.

## Principals and address versions

- A standard principal is a c32 address: a version byte plus a 20-byte hash. `SP` mainnet single-sig (`0x16`), `SM` mainnet multisig (`0x14`), `ST` testnet single-sig (`0x1a`), `SN` testnet multisig (`0x15`).
- `SM`/`SN` are P2SH version bytes, also used by P2SH-wrapped single keys: version `0x14`/`0x15` shows a script-hash address, not proof of a multisig.
- A contract principal is `deployer.name` (name 1–40 bytes, immutable code; a name can be deployed only once per deployer).
- Boot contracts are issued by `SP000000000000000000002Q6VF78` (mainnet) and `ST000000000000000000002AMW42H` (testnet), for example `SP000000000000000000002Q6VF78.pox-5`. Other boot and standard principals: [address records](references/addresses.md).
- `principal-construct?` with another network's version byte returns `(err {error_code: u0, value: (some principal)})`; a byte above `0x1f` or a hash shorter than 20 bytes gives `u1`, an invalid contract name `u2`. `principal-destruct?` returns `{version, hash-bytes, name}` as `ok` on the matching network and as `err` otherwise; `name` is `some` only for contract principals.
- `is-standard` is true when the principal's version matches the execution network, including **contract** principals. It is not an "is a wallet" check and proves neither key control nor trust.
- `is-in-mainnet` is easy to invert in a guard. Plain simnet, devnet and testnet run only the testnet branch; a [mainnet fork](../testing/SKILL.md#mainnet-forks) runs the mainnet branch, so test both.
- Clarity 1 `principal-of?` derives a **testnet** principal on every network and epoch; Clarity 2+ uses the execution network.
- STX is native with 6 decimals (1 STX = 1,000,000 µSTX). Tokens defined with `define-fungible-token` / `define-non-fungible-token` are also native: the node tracks them and postconditions can constrain them. Map-only "balances" are contract state.
- Token identity is the **contract principal plus asset name** (`SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token::sbtc-token`), never the symbol. Wrappers differ in principals, scales and custody; see [assets](../assets/SKILL.md#stx-through-a-token-interface-zest-wstx).
- `stx-get-balance` returns only the **spendable** STX (unlocked, plus expired locks); `stx-account` returns `{locked, unlock-height, unlocked}`. Staked STX is locked in place, not transferred.

## Chain, clocks and tenures

- Stacks settles to Bitcoin. Since Nakamoto (epoch 3.0), a miner election starts a **tenure**: its miner can produce multiple Stacks blocks, approved by eligible signers. A Bitcoin block does not guarantee a new tenure; tenure extensions and empty sortitions separate the clocks.

| Clock | Clarity | Advances | Use for |
|---|---|---|---|
| Stacks block | `stacks-block-height` (C3+) | every Stacks block (seconds) | ordering, same-block guards |
| Tenure | `tenure-height` (C3+) | each new tenure | legacy `block-height` meaning in C1/C2 after Nakamoto |
| Bitcoin | `burn-block-height` | each Bitcoin block (~10 min) | PoX cycles, Bitcoin-anchored delays |
| Wall time | `stacks-block-time` (C4+) | timestamp of the current block | interest, expiry, oracle staleness |

- Heights and wall-clock timestamps answer different questions. Never convert heights to seconds with a constant.
- `(get-stacks-block-info? time h)` works only for past blocks.
- **Epochs** are consensus upgrades. They select the cost schedule, the newest deployable Clarity version and block limits, and can change how old contracts execute (for example `at-block` aborts from epoch 3.4). Mainnet runs epoch 4.0 (Clarity up to 6); `/v2/pox.epochs` is the authoritative schedule and can list a future epoch with an unreachable start height, so do not hardcode "Epoch 4.0" as the latest.
- Since Nakamoto, blocks of a tenure share its execution budget; see [versions](../epochs/SKILL.md) for resource bounds.

## Transactions

- Types you meet: STX transfer, contract deploy (versioned or epoch-default language), contract call (a public function), plus system coinbase/tenure-change transactions.
- Sequential nonce per account. Fees are paid in µSTX by the origin or by a **sponsor** (`tx-sponsor?`). Fees do not buy extra execution budget.
- **Postconditions** are attached by the client and enforced by the node after execution: "this principal sends at most / exactly N of asset X", "this NFT leaves/stays".
  - *Deny* mode aborts the transaction on any asset movement not covered and, from epoch 4.0, on any uncovered stake or PoX action ([staking conditions](../staking/SKILL.md#transaction-post-conditions)). *Allow* mode permits unlisted movements. *Originator* mode (epoch 3.4+, SIP-040) applies *Deny* to the origin account only.
  - Conditions can name contract principals too, NFTs can be marked "may send" (3.4+), and epoch 4.0 adds Staking/PoX conditions.
  - Contracts cannot read or set them.
  - User-facing calls need postconditions for every asset the user (or a user-owned contract) sends, including native STX moved through a wSTX wrapper.
- Outcome: a top-level `(ok ...)` commits state and events. A top-level `(err ...)`, a runtime abort (`unwrap-panic`, overflow, division by zero) or a postcondition failure rolls back contract state/assets/events; the fee is still paid and the nonce consumed.
- Inside one transaction, a callee's `err` rolls back only that callee's changes; the caller may handle it and continue.

## Execution model

- Clarity is interpreted, not compiled: the source you deploy is the code that runs.
- It is decidable: no recursion, no unbounded loops (iterate with `map`/`fold`/`filter` over bounded lists).
- It is statically typed: `uint`/`int` are 128-bit, and lists, buffers and strings carry a maximum length. Overflow, underflow and division by zero abort the transaction.
- Calling into an already-active function is rejected, but callbacks to a different function of an active contract are possible. Review intermediate state and A → B → C chains with inherited `tx-sender`.
- Dynamic dispatch uses traits passed as arguments; a contract cannot call a principal it loaded from storage unless the caller passes it in as a trait, so validate `contract-of`.
- Trait arguments are checked by shape, not by trait identity, and `impl-trait` is not required. A node's mempool checks each contract argument of a contract call against the whole trait, as deployment analysis does for contract literals in source and for `impl-trait`. Unlike deployment analysis, the mempool checks only the first element of any list ([admission type check](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/analysis/type_checker/v2_1/mod.rs)). When the VM dispatches, it checks only the called function (calling a missing one aborts with `BadTraitImplementation`). Simnet calls skip the mempool, so partial mocks pass there. A trait argument never proves the full standard; bind the expected principal. Exception: a trait-typed parameter inside a trait you define is compared by trait identity, so a local copy there breaks calls to the real contract at runtime.
- A contract that `impl-trait`s a mainnet trait principal fails to deploy on a network where that principal does not exist. Keep the mainnet principal and declare it under `[[project.requirements]]`, or self-deploy the trait; details in [standard traits](references/addresses.md#standard-traits).
- Every transaction is metered in five dimensions against the active execution budget.

## Reading state (no transaction)

| Need | Endpoint (node RPC, e.g. `https://api.hiro.so`) |
|---|---|
| Call a read-only function | `POST /v2/contracts/call-read/{addr}/{name}/{fn}` body `{"sender": "...", "arguments": ["0x<clarity-serialized hex>"]}` |
| Map entry / data var | `POST /v2/map_entry/{addr}/{name}/{map}` (body: the serialized key as a JSON string), `GET /v2/data_var/{addr}/{name}/{var}` |
| Contract source / ABI | `GET /v2/contracts/source/{addr}/{name}`, `GET /v2/contracts/interface/{addr}/{name}` |
| Chain tip, epoch, PoX | `GET /v2/info`, `GET /v2/pox` |
| Transactions, events, balances | Stacks Blockchain API `/extended/v3/transactions/{id}` and its `/events`, `/extended/v3/principals/{principal}/balances/stx` (`/ft`, `/nft`), `/extended/v3/blocks/{height_or_hash}`; `/extended/v1` routes are deprecated ([routes](../apis/references/endpoints.md#verify-the-chain-and-deployment)) |

- Serialize arguments with `@stacks/transactions` (`Cl.*` + `serializeCV`) or `cvToHex`.
- Read-only results come back as serialized hex; decode them, and check `okay`.
- Copyable curl calls, evidence capture and pagination: [APIs and deployment evidence](../apis/SKILL.md#common-calls).

## Resolve and integrate

- Establish network, executing epoch and target contract language version.
- Use [address records](references/addresses.md) for full boot principals, active PoX observations and verified mainnet standard traits.
- From this skill's directory, check the registry's age offline with `python3 ../protocols/scripts/check_registry.py --registry references/addresses.md`. At 30 days or older the installed package may be outdated: tell the user to update the plugin, and verify each address you use against the live node (`python3 ../protocols/scripts/verify_registry.py --observations references/address-observations.json --contract <id>`, plus `/v2/pox` for active selection). Never fetch registry files from a repository.
- Resolve the active PoX contract and cycle from the live node (`/v2/pox.contract_id`; PoX-4 still having source does not make it active), then capture its source and ABI with the helper in `../apis/scripts/` (use `--api https://api.testnet.hiro.so` for testnet):

```sh
curl -s https://api.hiro.so/v2/pox | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['contract_id'],d['current_cycle']['id'])"
python3 ../apis/scripts/inspect_contract.py SP000000000000000000002Q6VF78.pox-5 --out <project>/evidence/pox-5
```

- Inspect the [boot directory](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133/stackslib/src/chainstate/stacks/boot) and registration/epoch code; retain the source hash, revision, network and state tip ([API evidence](../apis/SKILL.md#read-state-and-transactions)).
- For boot contracts, corroborate source/activation with consensus initialization rather than demanding a normal user deployment transaction.
- For ordinary traits/protocols, verify successful canonical deployment. Source existence does not prove current registry selection or permissions.
- Test required system state and permissions; empty simnet mocks do not reproduce consensus boot transitions.
- Staking locks STX across reward cycles; PoX-5 uses signer managers and sBTC reward claims; use [staking](../staking/SKILL.md). sBTC transfers on Stacks are synchronous while Bitcoin settlement is asynchronous; use [sBTC balances](../assets/SKILL.md#sbtc) and [Bitcoin settlement](../bitcoin-proofs/SKILL.md).

## Tooling

- Default to Clarigen for typed project clients and tests.
- Clarinet (CLI + `@stacks/clarinet-sdk`) gives simnet (fast, deterministic, in-process VM), devnet (local node + Bitcoin regtest) and deployment plans.
- `[[project.requirements]]` pulls mainnet contracts (traits, protocols) into simnet. sBTC is built in from epoch 3.0, so do not add it as a requirement.

## References

- [Address records](references/addresses.md): open for full boot principals and contract names, standard trait principals per network (mainnet and testnet status), and the Clarinet requirement remap.
- For on-chain Stacks inclusion proofs, read [clarity-stacks](../apis/references/positions-and-proofs.md#stacks-transaction-inclusion-with-clarity-stacks). Use [clarity:bitcoin-proofs](../bitcoin-proofs/SKILL.md) for Bitcoin proofs and sBTC settlement.
- [clarity:epochs](../epochs/SKILL.md): language and epoch compatibility and activation; its [recall corrections](../epochs/SKILL.md#recall-corrections) cover limits, native costs and chain identifiers.
- [clarity:staking](../staking/SKILL.md) for delegation and rewards, [clarity:optimizer](../optimizer/SKILL.md) for cost formulas and measurement, and [clarity:sip-compliance](../sip-compliance/SKILL.md) for normative token and signature behavior.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins; links into sibling skills use their owner's `SKILL.md`. Review dates do not renew live evidence.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `sips`: [642af6804d](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa).
