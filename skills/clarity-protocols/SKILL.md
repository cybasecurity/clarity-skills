---
name: clarity-protocols
description: "Verified Stacks DeFi addresses and exact function signatures: Zest, Granite, Bitflow, Stacks Swap, Hermetica, Stacking DAO, ALEX, Velar, USDCx, sBTC, Pyth. Use to call a protocol: loans, swaps, liquidations, deposits."
license: MIT
compatibility: "Python 3.10+ for the bundled scripts; verify_registry.py needs network access to a Stacks API (api.hiro.so by default)."
allowed-tools: "Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_registry.py *)"
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
  registry_verified_at: "2026-10-20"
---

# Clarity Protocols

Never write a protocol call or interface from memory: take each principal from the registry or the protocol's call reference, and each call shape from that reference or the deployed ABI. Position contracts, vault valuation, flash-loan order and fork tests: [clarity-ecosystem](../clarity-ecosystem/SKILL.md).

Writing or changing contract code: also load `clarity-scholar` and `clarity-security`, and finish with the [build checklist](../clarity-start/SKILL.md#before-calling-a-contract-done).

## Addresses and freshness

- Read the selected protocol's [address table](references/addresses.md) before choosing a principal; reuse verified results within the task. Registry age uses `registry_verified_at`, never the review, release or installation date.
- Deployed code is immutable; what ages is whether the protocol still selects that contract and its mutable state (roles, pauses, fees, oracle configuration). A newer deployment with a different interface needs an adapter review, not a string replacement.
- Inspect each accepted asset's [transfer authorization](../clarity-assets/SKILL.md#transfer-authorization), including sender-only tokens and privileged branches; a shared trait does not prove repayment or withdrawal compatibility.
- Unknown, unavailable or conflicting evidence stays unverified. Never guess an address, change its network prefix, or substitute a mock. Testnet deployments are independent records.
- To find or refresh a deployment, check the official docs and deployment tables, what the app or API selects, and the contracts a router binds. Official lists can still name retired contracts; note candidates the registry lacks.
- Code in a protocol's repository does not prove a current, accessible deployment. A registry entry is a discovery seed, not authorization or a safety claim.

### When the registry is due

Evidence is due for re-verification when it is **30 days or more** old, the timestamp is missing or in the future, the network changes, or a newer deployment is suspected.

- Tell the user the installed package may be outdated and suggest updating the plugin; releases carry refreshed registries. Never fetch registry files from a repository or overwrite the installed skill.
- Before relying on an address, run `python3 scripts/verify_registry.py --protocol <name>` (or `--contract <id>`) from this skill's directory. It checks each record's live source against the recorded `source_sha256` and the deployment receipt, read-only. Add `--state` to rerun the recorded read-only state checks and list what changed.
- Confirm current selection from on-chain registries/pointers and the official deployment list; read mutable state.
- Without the script, make the same checks by hand: `GET /v2/contracts/source/{address}/{name}` (hash the `source` text with SHA-256 and compare), the deployment transaction's `status` from `GET /extended/v3/transactions/{txid}` (`success`), and `GET /v2/contracts/interface/{address}/{name}`.
- Record what you verified and when, in the project's dependency record if it keeps one, and tell the user. Verification does not reset the registry's date.
- If live evidence cannot be obtained, explain the unresolved dependency and keep proposed addresses marked unverified. Do not use them for a production transaction.

### Before constructing production calls

Before deployment or signing, always verify, even with a fresh registry:

- Network, active epoch and Clarity version; full principal and exact trait/asset identifiers.
- Deployed source/hash and ABI matching the intended recipe/revision.
- For ordinary contracts, successful canonical deployment. For boot contracts, consensus initialization and activation.
- Current registry selection, authorized roles, pause state, fee scales, oracle configuration (signers/feeds), asset availability and liquidity, read at a recorded tip.
- Recheck mutable parameters close to execution; freshness is not a guarantee against subsequent changes. Use on-chain limits/deadlines/minimum outputs where available.

### Offline age check

```sh
python3 scripts/check_registry.py
python3 scripts/check_registry.py --registry references/addresses/zest.md
python3 scripts/check_registry.py --registry ../clarity-system-integration/references/addresses.md
```

- Run from this skill's directory. Exit `0`: within the window; `1`: verification due; `2`: malformed/unsupported metadata.
- This checks age only, offline; `verify_registry.py` checks the chain.

## Rules for every protocol call

- **Who pays:** Zest, Granite and Hermetica take the payer from `contract-caller` and move the asset under that caller's `tx-sender` context; Stacks Swap and Bitflow pull from `tx-sender`. A contract spending its own funds therefore makes the call inside its own `as-contract?` scope with an exact `with-ft` allowance (`with-stx` for native STX) for the gross outflow, fees included.
- **Burns and escrows are outflows:** Exiting needs an allowance for the share token the protocol burns or escrows: Zest `v0-vault-*` `"zft"`, Granite `state-v1` `"lp-token"`, Hermetica `token-hbtc` `"hBTC"`. Without it the scope returns `(err u128)` and the position cannot exit. A mock that books shares in a map hides this.
- **Beneficiary:** Read the intended recipient before entering the scope; inside it `tx-sender` is your contract.
- **Minimums and deadlines:** Take them from outside the trade and keep them non-zero. Use a function argument chosen by the transaction signer or, for operator-triggered swaps, a floor computed from a verified oracle price. A value derived inside the call from the pool being traded or from the current block, such as `(+ stacks-block-height u10)`, protects nothing. Where a protocol has no minimum argument (Granite deposit/redeem, Hermetica deposit), measure what you received in the same transaction and compare it with the caller's minimum.
- **Static calls:** Call fixed protocol contracts by literal principal (read-only code cannot call through a constant, even through a private helper). A trait-typed parameter in a trait you define, or in a callback you pass to the protocol, must use the protocol's own trait: a local copy there fails `BadTraitImplementation` against the real contract while passing against your mocks ([trait-typed parameters](../clarity-security/SKILL.md#calls-traits-recursion)).
- **Real contracts:** Test against them at a pinned height at least once ([mainnet-fork rules](../clarity-ecosystem/references/testing.md#test-on-a-mainnet-fork)). Mocks that share your own trait copies hide interface and trait-identity errors.

## Protocol call references

Before writing, reviewing or testing a call to one of these protocols, read its reference: it holds the exact signatures, fragments, deployed-body checks and test fixtures. Each line lists rules agents often get wrong; it does not replace the reference.

- **Zest v2** ([references/zest.md](references/zest.md)): market `v0-8-market` and seven `v0-vault-*` vaults; `v0-vault-usdc` holds USDCx. Vault `deposit` and `redeem` take `(amount min-out recipient)` and the payer from `contract-caller`; `redeem` burns `"zft"` shares. `flashloan` pulls `amount + fee` from its `contract-caller` (a `funds-receiver` changes only the destination) and needs a DAO `can-flashloan` grant. `liquidate` requires `contract-caller == tx-sender`, takes the collateral's z-token vault and the underlying debt token, and a `price-feeds` list must hold exactly one Lazer update.
- **Granite** ([references/granite.md](references/granite.md)): lends USDCx; use the exact logic, `state-v1` and callback-trait principals in the reference. LP `deposit (assets recipient)` has no minimum and returns no share count: measure `state-v1` `get-balance` before and after. Exits burn `"lp-token"` (without the allowance: `(err u128)`). `flash-loan` checks that the callback contract is allowed and pulls `amount + fee` from the caller. Borrowing, removing collateral and liquidating need a fresh Pyth Lazer `update`; never route them through the legacy Pyth Core adapters. LP exits, borrows and collateral removals draw on market-wide withdrawal caps and fail with `(err u120002)` to `(err u120004)` above the current bucket: exit large positions in parts.
- **Hermetica** ([references/hermetica.md](references/hermetica.md)): vault `vault-hbtc-v1-2`, sBTC only. Deposits are currently disabled (`(err u102005)`): read `check-is-deposit-enabled` and decide how a refused hBTC leg is handled. `deposit` has no minimum argument; check the returned shares. Redemption is queued (`request-redeem` moves `"hBTC"` into the vault); anyone may redeem a funded claim, which is then deleted, so never `try!` across a list of claims.
- **Stacks Swap** ([references/stacks-swap.md](references/stacks-swap.md)): Zest's aggregator across Bitflow, Velar, ALEX and other venues; choose it or a direct Bitflow call as [choosing a swap venue](#choosing-a-swap-venue) says. `zr-d-0` `r-d` takes 13 arguments in a fixed order and pulls `amount-in` from `tx-sender`. `deadline` is an inclusive Stacks block height taken as an argument (Bitflow's DLMM router takes seconds); `skim-amount` and `max-skim` are absolute output units, zero unless a fee is intended. Also covers multi-hop and split routes, Stacking DAO conversion adapters and test obligations.
- **Bitflow** ([references/bitflow.md](references/bitflow.md)): DLMM router `dlmm-swap-router-v-1-2` and stable swap core `stableswap-core-v-1-4`. Orientation and a stable pool's core come from the pool's `get-pool` (`x-token`, `y-token`, `core-address`), not its name. Payer and recipient are `tx-sender`; `deadline-time` is seconds against `stacks-block-time`. A router trait you define must use Bitflow's own traits (a local copy fails `BadTraitImplementation`); STX pools use `token-stx-v-1-2`, not Zest's wSTX. On a mainnet fork set `use_mainnet_wallets = true`, or pool transfers fail with `err u3003`.
- **USDCx** ([references/usdcx.md](references/usdcx.md)): token `SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx`, asset `usdcx-token` (a contract sending it allows `(with-ft 'SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx "usdcx-token" amount)`), six decimals; not native USDC or aeUSDC. `transfer` accepts `sender == tx-sender` or `sender == contract-caller`. The three balance getters return the same balance: do not add them. The `.usdcx-v1` bridge `burn` burns from the current `tx-sender`, v1 accepts only Ethereum domain `u0`, and the USDC release happens later, so a flash loan cannot rely on it.

### Choosing a swap venue

Neither Stacks Swap nor a direct Bitflow call is the default. Follow a venue or route the task names. Otherwise choose by route, and tell the developer which you chose and why:

- Call Bitflow directly when one Bitflow pool (DLMM or stable swap) covers the pair with enough liquidity for the trade size. It puts fewer contracts in the trust path and usually costs less to execute. The sBTC/USDCx pair has a Bitflow DLMM pool, `dlmm-pool-sbtc-usdcx-v-1-bps-10`, which Stacks Swap's DLMM route also goes through.
- Use Stacks Swap when the best route needs several hops, a split across pools or venues, or a Stacking DAO conversion. A single Velar, ALEX or Arkadiko pool can also be called directly once its deployed router ABI is resolved ([protocol discovery](#protocol-discovery)).
- When both fit, compare them at the actual size: net output after fees and skim, liquidity, transaction cost, hop count and the contracts each adds. More routing options do not guarantee a better fill or a lower cost.

## Oracles and other protocols

- **Pyth:** Core no longer supports Stacks; use Lazer for new integrations (Core/Wormhole is legacy audit/migration material). The documented Lazer model is one governed instance per consumer, not a public shared oracle: Zest v2 (`SP1A27...`) and Granite (`SPMV5HDZ...`) each run their own ([addresses](references/addresses/pyth-lazer.md)). Consumer rules, price checks and deploying your own instance: [clarity-oracles](../clarity-oracles/SKILL.md).
- **DIA:** its oracle is the only on-chain source of a USDh/USD price, so any contract that values USDh reads it there: a push oracle with one updater key, eight decimals, millisecond timestamps ([addresses](references/addresses/dia.md)).
- **Velar** ([addresses](references/addresses/velar.md)), **ALEX** (AMM v2; flash loans are currently disabled on the deployed vault; [addresses](references/addresses/alex.md)), **Arkadiko** and **Stacking DAO** ([staking](../clarity-staking/SKILL.md)): start from [protocol discovery](#protocol-discovery).
- Boot/standard principals: [system integration](../clarity-system-integration/SKILL.md); sBTC balances: [assets](../clarity-assets/SKILL.md).

## Protocol discovery

Read [the repository discovery table](references/discovery.md) when selecting an unfamiliar protocol, finding its source or refreshing a deployment record. It maps use cases to repositories, contract paths and checks. Repository HEAD can include mocks, retired or unreleased code: resolve the deployed implementation, roles, asset, fees, pauses and limits before generating an adapter.

- Current source pins are in the [reference baseline](#reference-baseline).
- Zest wSTX, Bitflow/Velar/ALEX wrappers and native STX are not interchangeable: a call into another protocol passes the wrapper that protocol requires, and your own contracts use Zest's wSTX where nothing requires another ([wSTX](../clarity-assets/SKILL.md#stx-through-a-token-interface-zest-wstx)).
- A Stacks Lazer source repository or cross-chain SDK does not establish a production deployment. Verify the consumer's signer, decoder and service access ([oracles](../clarity-oracles/SKILL.md)).

## References

- [Address index](references/addresses.md) and its per-protocol tables: open for every principal you use.
- Call references, one per protocol: [Zest v2](references/zest.md), [Granite](references/granite.md), [Hermetica](references/hermetica.md), [Stacks Swap](references/stacks-swap.md), [Bitflow](references/bitflow.md), [USDCx](references/usdcx.md). Open the one you call before writing it ([index](#protocol-call-references)).

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill and its references use these pins.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `granite`: [2d44a2df94](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b).
- `hermetica`: [5e13e431f6](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0).
- `sbtc`: [eb507946c6](https://github.com/stacks-sbtc/sbtc/tree/eb507946c65bdf4dde72469ea8cb2481fa276a17).
- `stackingdao`: [125c73dc10](https://github.com/StackingDAO/stackingdao-smart-contracts/tree/125c73dc109988730156f4d0434ff01654480fc7).
- `bitflow`: [31c4e0be27](https://github.com/BitflowFinance/bitflow/tree/31c4e0be27ee5a1627e60f1af027e68327e91d49).
- `bitflow-dlmm`: [b4d3694c86](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0).
- `arkadiko`: [854fda1d6d](https://github.com/arkadiko-dao/arkadiko/tree/854fda1d6d9f4edb39a52d4fb24ec818d09c5317).
- `pyth-lazer`: [a6034d2e39](https://github.com/stx-labs/stacks-pyth-lazer/tree/a6034d2e3922892f98558d05330f92b12c857681).
- `alex-sdk`: [4c7e1bd016](https://github.com/alexgo-io/alex-sdk/tree/4c7e1bd016285d6f917ef4f3d8c96b08e2329058).
- `alexlab-doc`: [7f4b05b461](https://github.com/alexgo-io/alexlab-doc/tree/7f4b05b461fdad508a3c25d79f19aa75ec82954b).
