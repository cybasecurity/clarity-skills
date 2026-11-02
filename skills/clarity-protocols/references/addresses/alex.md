# ALEX addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../../clarity-protocols/SKILL.md#addresses-and-freshness).
- [All protocols](../../../clarity-protocols/references/addresses.md).

- The official SDK/app selects the AMM v2 deployment below; older docs list a different historical deployer. Do not combine those sets.
- The vault's flash-loan flag is currently false, so ALEX is not a flash-loan source.
- The actual ALEX token defines native `alex` and `alex-locked` assets. Verify exact token/trait identity; other ALEX wrappers are separate.
- The mainnet docs mix legacy SP3K8... contracts with the current SDK AMM v2 family. Old deployment names do not establish current integration targets; the aggregator also binds specific wrapper contracts.

- Discovery: [official SDK config](https://github.com/alexgo-io/alex-sdk/blob/4c7e1bd016285d6f917ef4f3d8c96b08e2329058/src/config.ts); [self-listing helper docs](https://github.com/alexgo-io/alexlab-doc/blob/7f4b05b461fdad508a3c25d79f19aa75ec82954b/developers/alex-contracts/protocol-contracts/self-listing-helper-v3a.clar.md).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | ALEX: ALEX fungible-token contract selected by current official SDK and docs; defines alex and alex-locked assets | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-alex?chain=mainnet&tab=overview) |
| Mainnet | ALEX: AMM v2 DAO referenced by on-chain pool source | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.executor-dao](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.executor-dao?chain=mainnet&tab=overview) |
| Mainnet | ALEX: AMM v2 entry point selected by current official SDK | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-pool-v2-01](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-pool-v2-01?chain=mainnet&tab=overview) |
| Mainnet | ALEX: AMM v2 registry referenced by on-chain pool source | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-registry-v2-01](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-registry-v2-01?chain=mainnet&tab=overview) |
| Mainnet | ALEX: AMM v2 vault referenced by on-chain pool source | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-vault-v2-01](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-vault-v2-01?chain=mainnet&tab=overview) |
| Mainnet | ALEX: Self-listing helper directly linked by current official docs; references SP102V8... AMM v2 set | [SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.self-listing-helper-v3a](https://explorer.hiro.so/txid/SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.self-listing-helper-v3a?chain=mainnet&tab=overview) |
| Mainnet | ALEX: auto-alex-v3 | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.auto-alex-v3](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.auto-alex-v3?chain=mainnet&tab=overview) |
| Mainnet | ALEX: token-wstx-v2 | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-wstx-v2](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-wstx-v2?chain=mainnet&tab=overview) |
| Mainnet | ALEX: token-wstx | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-wstx](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.token-wstx?chain=mainnet&tab=overview) |
| Mainnet | ALEX: trait-sip-010 | [SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.trait-sip-010](https://explorer.hiro.so/txid/SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.trait-sip-010?chain=mainnet&tab=overview) |
| Mainnet | ALEX: farming-campaign-v2-02 | [SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.farming-campaign-v2-02](https://explorer.hiro.so/txid/SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.farming-campaign-v2-02?chain=mainnet&tab=overview) |
| Mainnet | ALEX: token-wsbtc | [SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wsbtc](https://explorer.hiro.so/txid/SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wsbtc?chain=mainnet&tab=overview) |
| Mainnet | ALEX: token-wststx | [SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wststx](https://explorer.hiro.so/txid/SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wststx?chain=mainnet&tab=overview) |
| Mainnet | ALEX: token-wusdh | [SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wusdh](https://explorer.hiro.so/txid/SP1E0XBN9T4B10E9QMR7XMFJPMA19D77WY3KP2QKC.token-wusdh?chain=mainnet&tab=overview) |
