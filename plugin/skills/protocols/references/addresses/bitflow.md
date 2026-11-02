# Bitflow addresses

- Recheck mutable configuration before integration; follow [freshness rules](../../SKILL.md#addresses-and-freshness).
- [All protocols](../addresses.md).

- Pool rows are examples, not an exhaustive pool list. Discover the exact pair/fee tier with the [pool API](https://bff.bitflowapis.finance/api/quotes/v2/pools).
- An increasing version suffix or `pool-created = true` does not prove a usable quote. Recheck tokens, core, active/quotable flags and current liquidity.
- The old deployed-address docs lag current API deployments. For ABI/version differences, see [swap guidance](../bitflow.md#bitflow).
- The deployed-contract docs retain legacy SPQC38... routers/pools. Resolve current app/API selection and exact aggregator dependencies; their bound core/router versions can differ from standalone current routes.
- `dlmm-swap-router-v-1-1` (SP1PFR4V...) and `dlmm-swap-router-v-1-2` (SM1FKXGN...) both bind `dlmm-core-v-1-1`; the sBTC/USDCx example pool reports that core. Calls: [Bitflow recipe](../bitflow.md#bitflow).

- Discovery: [HODLMM API](https://docs.bitflow.finance/bitflow-documentation/developers/hodlmm-api-documentation); [v2 API](https://docs.bitflow.finance/bitflow-documentation/developers/hodlmm-api-documentation-v2).

| Network | Protocol | Contract ID |
|---|---|---|
| Mainnet | Bitflow: DLMM core | [SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1](https://explorer.hiro.so/txid/SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: DLMM example pair | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-sbtc-usdcx-v-1-bps-10?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: DLMM example pair | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-stx-usdcx-v-1-bps-10](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-stx-usdcx-v-1-bps-10?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: DLMM example pair | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-stbtc-sbtc-v-1-bps-1](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-stbtc-sbtc-v-1-bps-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: DLMM liquidity router | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: DLMM swap router with deadline | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: STX/stSTX stable pool | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-stx-ststx-v-1-4](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-stx-ststx-v-1-4?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: sBTC/pBTC stable pool | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-sbtc-pbtc-v-1-1](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-sbtc-pbtc-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: stable core | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-core-v-1-4](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-core-v-1-4?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: sip-010-trait-ft-standard-v-1-1 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.sip-010-trait-ft-standard-v-1-1](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.sip-010-trait-ft-standard-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: stableswap-core-v-1-2 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-core-v-1-2](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-core-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: stableswap-pool-trait-v-1-2 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-trait-v-1-2](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.stableswap-pool-trait-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: token-stx-v-1-1 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.token-stx-v-1-1](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.token-stx-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: token-stx-v-1-2 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.token-stx-v-1-2](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.token-stx-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: xyk-core-v-1-1 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-core-v-1-1](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-core-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: xyk-core-v-1-2 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-core-v-1-2](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-core-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: xyk-pool-trait-v-1-1 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-pool-trait-v-1-1](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-pool-trait-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: xyk-pool-trait-v-1-2 | [SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-pool-trait-v-1-2](https://explorer.hiro.so/txid/SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR.xyk-pool-trait-v-1-2?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: dlmm-pool-ststx-stx-v-1-bps-1 | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-ststx-stx-v-1-bps-1](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-ststx-stx-v-1-bps-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: dlmm-pool-trait-v-1-1 | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-trait-v-1-1](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-trait-v-1-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: dlmm-pool-usdh-usdcx-v-1-bps-1 | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-usdh-usdcx-v-1-bps-1](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-usdh-usdcx-v-1-bps-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: aeUSDC/USDCx HODLMM pool (aeUSDC migration route) | [SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-aeusdc-usdcx-v-1-bps-1](https://explorer.hiro.so/txid/SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-aeusdc-usdcx-v-1-bps-1?chain=mainnet&tab=overview) |
| Mainnet | Bitflow: dlmm-swap-router-v-1-1 | [SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-swap-router-v-1-1](https://explorer.hiro.so/txid/SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-swap-router-v-1-1?chain=mainnet&tab=overview) |
