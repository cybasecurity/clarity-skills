# Arkadiko addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../SKILL.md#addresses-and-freshness).
- [All protocols](../addresses.md).

- The DAO `vaults-pool-liq` key selected v1.2 while the live app selected v1.3. Both are deployed. Resolve the intended call path and current registry before a liquidation.
- The other vault, swap and governance rows are what `arkadiko-dao` `get-qualified-name-by-name` returned for their keys; re-resolve them there before use.

- Discovery: [official contracts](https://docs.arkadiko.finance/additional-resources/contracts); [production app](https://app.arkadiko.finance/); [source revision](https://github.com/arkadiko-dao/arkadiko/tree/854fda1d6d9f4edb39a52d4fb24ec818d09c5317).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | Arkadiko: Active collateral pool passed by app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-active-v1-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-active-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Collateral token registry passed by app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-tokens-v1-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-tokens-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: DIKO token | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-token](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-token?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Governance returned by current DAO governance key | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-governance-v4-3](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-governance-v4-3?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Governed contract registry | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-dao](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-dao?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Liquidation pool used by production app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-liq-v1-3](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-liq-v1-3?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Liquidation/redemption manager used by production app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-manager-v1-2](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-manager-v1-2?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Oracle used by production app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-oracle-v2-3](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-oracle-v2-3?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Pool returned by current DAO vaults-pool-liq key; the live app uses v1.3 | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-liq-v1-2](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-pool-liq-v1-2?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Sorted vault contract passed by app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-sorted-v1-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-sorted-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Swap entry point used by production app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-swap-v2-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-swap-v2-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: USDA token | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.usda-token](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.usda-token?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: User vault create/adjust operations used by production app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-operations-v1-3](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-operations-v1-3?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Vault data contract passed by app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-data-v1-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-data-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: Vault helper contract passed by app | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-helpers-v1-1](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.arkadiko-vaults-helpers-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Arkadiko: wrapped-stx-token | [SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.wrapped-stx-token](https://explorer.hiro.so/txid/SP2C2YFP12AJZB4MABJBAJ55XECVS7E4PMMZ89YZR.wrapped-stx-token?chain=mainnet&tab=overview) |
