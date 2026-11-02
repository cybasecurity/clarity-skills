# DIA: USDh/USD oracle addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../../clarity-protocols/SKILL.md#addresses-and-freshness).
- [All protocols](../../../clarity-protocols/references/addresses.md).

- This DIA oracle is the only on-chain source of a USDh/USD price: any contract that values USDh reads it here. Zest prices USDh from it; Hermetica, the USDh issuer, does not use it. One updater key pushes the values. Its timestamps are milliseconds (Pyth Lazer uses microseconds), and a missing key reads as a zero value and timestamp rather than an error: check provenance and freshness yourself.

- Discovery: [Zest oracle implementation](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/market/v0-8-market.clar).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | DIA: USDh/USD oracle: dia-oracle | [SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle](https://explorer.hiro.so/txid/SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.dia-oracle?chain=mainnet&tab=overview) |
| Mainnet | DIA: USDh/USD oracle: trait-dia-oracle | [SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.trait-dia-oracle](https://explorer.hiro.so/txid/SP1G48FZ4Y7JY8G2Z0N51QTCYGBQ6F4J43J77BQC0.trait-dia-oracle?chain=mainnet&tab=overview) |
