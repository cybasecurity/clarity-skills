# Protocol address registry

- Load only the requested protocol. Every contract ID links to its network in Hiro Explorer.
- Deployment alone does not establish current selection, permissions, liquidity or safety.
- Follow [freshness rules](../SKILL.md#addresses-and-freshness), including live checks before deployment/signing. The 30-day window is a cache policy.
- System/boot/standard principals: [system registry](../../system-integration/references/addresses.md).

| Network | Protocol | Contracts |
|---|---|---:|
| Mainnet, Testnet | [sBTC](addresses/sbtc.md) | 10 |
| Mainnet, Testnet | [USDCx](addresses/usdcx.md) | 5 |
| Mainnet | [Zest v2](addresses/zest.md) | 21 |
| Mainnet | [Granite](addresses/granite.md) | 24 |
| Mainnet | [Bitflow](addresses/bitflow.md) | 23 |
| Mainnet | [Hermetica](addresses/hermetica.md) | 31 |
| Mainnet | [Stacking DAO](addresses/stackingdao.md) | 16 |
| Mainnet | [Arkadiko](addresses/arkadiko.md) | 16 |
| Mainnet | [ALEX](addresses/alex.md) | 14 |
| Mainnet | [Pyth Lazer](addresses/pyth-lazer.md) | 6 |
| Mainnet | [Zest Protocol Stacks Swap](addresses/stacks-swap.md) | 18 |
| Mainnet | [Velar](addresses/velar.md) | 9 |
| Mainnet | [DIA: USDh/USD oracle](addresses/dia.md) | 2 |

- Testnet deployments are independent records. Never derive them by changing a mainnet prefix or by copying a Clarinet remap.
