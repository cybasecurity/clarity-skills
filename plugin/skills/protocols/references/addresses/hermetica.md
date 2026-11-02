# Hermetica addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../SKILL.md#addresses-and-freshness).
- [All protocols](../addresses.md).

- HQ `get-protocol` returns true for vault v1.2 and false for v1/v1.1 (recheck live). This checks membership, not full readiness.
- Docs still link the old vault. Select v1.2 for new dependency verification, then check state, limits, pauses and liquidity; see [hBTC recipe](../hermetica.md#hermetica).
- USDh/sUSDh modules are separate from this hBTC deployment.

- Discovery: [official hBTC contracts](https://docs.hermetica.fi/hbtc/how-it-works/smart-contracts); [current vault source](https://github.com/hermetica-fi/hermetica-contracts/blob/5e13e431f69dd840fe297791fa2a73d9993a27e0/mainnet/contracts/hbtc/protocol/vault-v1-2.clar); [USDh technical primitives](https://docs.hermetica.fi/usdh/how-it-works/technical-primitives).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | Hermetica: blacklist-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.blacklist-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.blacklist-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: controller-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.controller-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.controller-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: hermetica-interface-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.hermetica-interface-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.hermetica-interface-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: hq-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.hq-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.hq-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: reserve-fund-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.reserve-fund-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.reserve-fund-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: reserve-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.reserve-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.reserve-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: state-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.state-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.state-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: token-hbtc | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.token-hbtc](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.token-hbtc?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: trading-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.trading-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.trading-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: vault-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: vault-hbtc-v1-2 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1-2](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.vault-hbtc-v1-2?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: zest-interface-hbtc-v1 | [SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.zest-interface-hbtc-v1](https://explorer.hiro.so/txid/SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D.zest-interface-hbtc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh controller-v1-1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.controller-v1-1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.controller-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh emergency-recover-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.emergency-recover-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.emergency-recover-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh hq-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.hq-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.hq-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-auto-state-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-state-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-state-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-auto-trait-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-trait-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-trait-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-auto-v1-2 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-v1-2](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-auto-v1-2?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-otc-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-otc-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-otc-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-state-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-state-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-state-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh minting-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.minting-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh redeeming-reserve-v1-2 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.redeeming-reserve-v1-2](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.redeeming-reserve-v1-2?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-reserve-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-reserve-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-reserve-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-silo-trait-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-silo-trait-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-silo-trait-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-silo-v1-1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-silo-v1-1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-silo-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-state-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-state-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-state-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-trait-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-trait-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-trait-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh staking-v1-1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-v1-1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.staking-v1-1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh susdh-token-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.susdh-token-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.susdh-token-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh usdh-airdrop-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-airdrop-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-airdrop-v1?chain=mainnet&tab=overview) |
| Mainnet | Hermetica: USDh/sUSDh usdh-token-v1 | [SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1](https://explorer.hiro.so/txid/SPN5AKG35QZSK2M8GAMR4AFX45659RJHDW353HSG.usdh-token-v1?chain=mainnet&tab=overview) |
