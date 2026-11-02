# USDCx calls

Exact USDCx token and bridge call shapes, integration constraints and tests. Apply the [rules for every protocol call](../../clarity-protocols/SKILL.md#rules-for-every-protocol-call) and the [freshness rules](../../clarity-protocols/SKILL.md#addresses-and-freshness) first.

## USDCx

- SIP-010 token backed by USDC held in Circle xReserve; distinct from Circle-issued native USDC and from other bridged tokens such as aeUSDC. Mainnet token `SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx`, native FT `usdcx-token` (`with-ft` asset name and `<token>::usdcx-token` identifier), six decimals (`u1000000` is one USDCx).
- aeUSDC (Allbridge Classic) is deprecated: Allbridge stops Classic in November 2026 (Zest and Granite cite November 3), and Granite closes its aeUSDC market by then. Swap it to USDCx in Bitflow's HODLMM pool `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-pool-aeusdc-usdcx-v-1-bps-1` ([migration](https://www.stacks.co/blog/usdcx-comes-to-allbridge-core-circle-standard-usdc-now-bridges-directly-to-stacks)). A bridge-out to Ethereum burns the aeUSDC at once, so one sent after Allbridge stops signing releases nothing.
- Resolve the network's `.usdcx` token and `.usdcx-v1` bridge in the [address registry](addresses/usdcx.md); the documented mainnet and testnet sources differ. The facts below describe the mainnet contracts: refresh source/ABI, active roles, attestors, minimum withdrawal and pause state before use.
- **Testnet mismatch:** the documented `.usdcx-v1` calls `.usdcx-token`; the documented `.usdcx` initially grants the mint role to `.usdcx-xreserve-v1`. The latter bridge exists and calls `.usdcx`; it is recorded as a source-discovered candidate in the registry. Confirm current roles and service selection before using it. Do not combine the docs table's mismatched pair.
- `transfer (amount uint) (sender principal) (recipient principal) (memo (optional (buff 34)))` returns `(response bool uint)` and accepts `sender == tx-sender` **or** `sender == contract-caller`. An adapter can transfer its own tokens as immediate caller; inherited user-sender authority still requires careful routing and client postconditions.
- Use FT postconditions and `with-ft` when an allowance scope spends USDCx. Do not confuse the `.usdcx-v1` bridge principal with the token contract or asset name.
- `get-balance`, `get-balance-available` and `get-balance-locked` return the same balance; do not add them or apply sBTC's formula. Ordinary `transfer` does not check the pause flag; `protocol-transfer`, `protocol-mint` and `protocol-burn` do.
- The mint role permits mint, burn and privileged transfer. Governance can change roles; verify current authority instead of assuming the deployment's initial `.usdcx-v1` assignment remains sufficient.

### USDCx bridge

| Operation | Mainnet v1 interface | Integration constraint |
|---|---|---|
| Mint from a deposit | `mint(deposit-intent (buff 320), signature (buff 65), fee-amount uint)` | Requires an accepted Circle attestation, valid token/domain/recipient encoding and unused nonce; a local mint mock does not establish bridge authorization |
| Request withdrawal | `burn(amount uint, native-domain uint, native-recipient (buff 32))` | Burns from **current `tx-sender`**; no separate owner argument. v1 accepts only Ethereum domain `u0` |
| Read minimum | `get-min-withdrawal-amount()` | Mutable amount; check at execution and handle a changed minimum |

- Deposit to xReserve on the source chain, then follow attestation and Stacks mint completion. Source-chain inclusion alone does not establish a Stacks balance.
- Stacks deposit domain is `10003`. Obtain `remote-token` from `get-valid-remote-token`; use the documented recipient encoder. Contract recipients require valid serialized `{ contract-name: (string-ascii 40) }` hook data; malformed hook data can fall back to the standard principal.
- `parse-deposit-intent` is only a parser. `mint` also validates the intent and attestor signature and consumes its nonce.
- Enforce `fee-amount <= max-fee <= amount`; account for the fee paid to `tx-sender` and credit only the recipient's actual minted amount. The implementation subtracts the fee before its fee assertion, so excessive input can cause uint underflow rather than a returned error.
- Withdrawal recipients must be valid 20-byte Ethereum addresses left-padded to exactly 32 bytes. Clarity `(buff 32)` is a maximum; this `burn` body does not enforce exact length or validate the Ethereum destination.
- Contract-owned withdrawals need the contract's sender context and appropriate FT allowance. Ordinary token-transfer caller authorization does not change the bridge's `tx-sender` burn owner.
- Successful burn emits an intent; offchain attestation and source-chain USDC release happen later. A flash loan cannot rely on that later release for atomic repayment.
- Process all matching canonical burn events with verified contract provenance, event position, deduplication and reorg handling. One transaction can contain several intents.
- Follow current service batch limits. The bridging guide lists at most 50 intents per request, 10 per batch and five batches; these are processing limits, not a Clarity guarantee.

### USDCx tests

- Test the paths you use: wrong token/network, both transfer authorization paths and zero/dust amounts for any transfer; pause scope and role changes if you call protocol functions; malformed/duplicate attestations, fee boundaries, recipient encoding and pending withdrawals if you call the bridge.
- For lending or swaps, verify that the selected market/pool registers this exact asset and price feed. A protocol's `usdc` label does not establish USDCx identity.

Sources: [official deployments](https://docs.stacks.co/learn/bridging/usdcx/contracts), [token source/docs](https://docs.stacks.co/learn/bridging/usdcx/contracts/usdcx-token), [bridge source/docs](https://docs.stacks.co/learn/bridging/usdcx/contracts/usdcx-v1), [bridging guide](https://docs.stacks.co/more-guides/bridging-usdcx), [Circle xReserve](https://developers.circle.com/xreserve).
