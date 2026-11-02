# Pyth Lazer addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../SKILL.md#addresses-and-freshness).
- [All protocols](../addresses.md).

- Each instance belongs to the protocol that deployed it: Zest v2 (`SP1A27...`) and Granite (`SPMV5HDZ...`, the dedicated deployer in Granite's deployment plan). Upstream requires each consumer to deploy and govern its own instance; calling another protocol's instance makes its governance key your price authority ([deploy your own](../../../oracles/SKILL.md#deploy-a-lazer-instance-for-your-protocol)).
- Both currently trust the same Pyth signer key, charge no fee and are unpaused. Each is governed by one single-signature key, and its signer changes take effect at once. Recheck signer identity and expiry, decoder, fee and pause state before use.
- Use [Lazer units and payload rules](../../../oracles/SKILL.md#lazer-consumer-rules); legacy Pyth Core is not supported for new Stacks integrations.

- Discovery: [upstream deployment model](https://github.com/stx-labs/stacks-pyth-lazer/blob/a6034d2e3922892f98558d05330f92b12c857681/README.md); [Zest consumer deployment table](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/README.md); [Granite deployment plan](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/deployments/pyth-lazer-plan-v1.yaml).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | Pyth Lazer: Zest v2-owned instance; not a universal shared oracle | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-oracle](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-oracle?chain=mainnet&tab=overview) |
| Mainnet | Pyth Lazer: Zest v2-owned instance; not a universal shared oracle | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-decoder-v1](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-decoder-v1?chain=mainnet&tab=overview) |
| Mainnet | Pyth Lazer: Zest v2-owned instance; not a universal shared oracle | [SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-traits](https://explorer.hiro.so/txid/SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.pyth-lazer-traits?chain=mainnet&tab=overview) |
| Mainnet | Pyth Lazer: Granite-owned instance; not a universal shared oracle | [SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-traits](https://explorer.hiro.so/txid/SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-traits?chain=mainnet&tab=overview) |
| Mainnet | Pyth Lazer: Granite-owned instance; not a universal shared oracle | [SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-oracle](https://explorer.hiro.so/txid/SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-oracle?chain=mainnet&tab=overview) |
| Mainnet | Pyth Lazer: Granite-owned instance; not a universal shared oracle | [SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-decoder-v1](https://explorer.hiro.so/txid/SPMV5HDZ4EMB8XY7HAYT3XW0DF7DZ4E8XEG2J1T8.pyth-lazer-decoder-v1?chain=mainnet&tab=overview) |
