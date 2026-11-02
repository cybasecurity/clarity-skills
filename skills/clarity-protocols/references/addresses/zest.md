# Zest v2 addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../../clarity-protocols/SKILL.md#addresses-and-freshness).
- [All protocols](../../../clarity-protocols/references/addresses.md).

- The vault named `v0-vault-usdc` holds USDCx, not aeUSDC. Resolve each vault's underlying and permissions independently.
- Oracle instance: [Zest-owned Pyth Lazer](pyth-lazer.md). Recipe with vault-to-asset map: [calls, flash loans and liquidation](../../../clarity-protocols/references/zest.md#zest-v2).
- The zvstBTC strategy and its zv-* contracts are a separate leveraged product, not an eighth ordinary lending vault.

- Discovery: [mainnet table](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/README.md); [leveraged vault contracts](https://docs.zestprotocol.com/stacks/vaults/contracts); [ZEST token](https://docs.zestprotocol.com/zest-token).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | Zest v2: dao-executor | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.dao-executor](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.dao-executor?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: dao-multisig | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.dao-multisig](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.dao-multisig?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-5-data | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-5-data](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-5-data?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-8-market | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-8-market](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-8-market?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-assets | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-assets](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-assets?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-egroup | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-egroup](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-egroup?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-market-vault | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-market-vault](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-market-vault?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-sbtc | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-sbtc](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-sbtc?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-stbtc | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-stbtc](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-stbtc?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-ststx | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-ststx](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-ststx?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-ststxbtc | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-ststxbtc](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-ststxbtc?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-stx | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-stx](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-stx?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-usdc | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: v0-vault-usdh | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdh](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdh?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: wstx | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.wstx](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.wstx?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zest-token | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zest-token](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zest-token?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zv-engine-stbtc-0 | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-engine-stbtc-0](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-engine-stbtc-0?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zv-ops-stbtc-0 | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-ops-stbtc-0](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-ops-stbtc-0?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zv-state-stbtc-0 | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-state-stbtc-0](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-state-stbtc-0?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zv-traits | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-traits](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zv-traits?chain=mainnet&tab=overview) |
| Mainnet | Zest v2: zvstBTC | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zvstBTC](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.zvstBTC?chain=mainnet&tab=overview) |
