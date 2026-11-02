# Testing an integration

Fork setup and scenarios for integrations built with this skill; [clarity-testing](../../clarity-testing/SKILL.md) holds the general test rules.

## Test on a mainnet fork

- Declare every protocol contract your code calls as a `[[project.requirements]]` entry (sBTC is built into simnet; do not add it), pin `initial_height` and record why you chose it.
- Set `use_mainnet_wallets = true`. Otherwise local contracts are `ST...` principals and mainnet `is-standard` checks reject them (Bitflow `err u3003`).
- Fund test principals by sending a transfer as a real holder, and handle fork block time, height deadlines and rate limits as the [mainnet-fork rules](../../clarity-testing/references/mainnet-forks.md) say.
- Authentic Lazer updates come from a successful mainnet transaction's arguments, for example the `price-feeds` argument of a Zest `v0-8-market` call; fork one block before that transaction so its signer is still registered ([signed fixtures](../../clarity-oracles/SKILL.md#signed-fixtures)).

```toml
# fragment: Clarinet.toml for a pinned mainnet fork
[[project.requirements]]
contract_id = "SP1A27KFY4XERQCCRCARCYD1CC5N7M6688BSYADJ7.v0-vault-usdc"   # one entry per contract you call

[repl.remote_data]
enabled = true
api_url = "https://api.hiro.so"
initial_height = 9260700      # pin a recent height; record why you chose it
use_mainnet_wallets = true    # deployer and wallets get SP... addresses
```

## Test the entire operation

Use actual pinned contracts where authorized, with mocks restricted to controlled test roles and external services. A mock-only run is not a full integration proof. Select scenarios for the operation's actual legs:

- Every permission missing, each protocol paused, wrong callback caller, replayed callback, and altered data.
- Each token's actual transfer guard, privileged exceptions and callback repayment context; native STX through the target's registered wrapper ([Zest wSTX](../../clarity-assets/SKILL.md#stx-through-a-token-interface-zest-wstx) for Zest); available-versus-locked sBTC.
- Wrong signer/feed, stale/future price, negative/zero price, exponent mismatch, wide confidence interval, and oracle fees.
- Healthy borrower, same-block borrow/liquidation restriction, changed debt between quote and execution, liquidation bounds, minimum collateral, swap slippage, and missing liquidity.
- Each lender's fee ceiling, mixed decimals, one-unit rounding, insufficient repayment by one unit, and arithmetic maximums.
- Vault cap/minimum/pause/blacklist and share slippage; exits against the real share token (burn allowance).
- Failure of a late leg reverts the complete operation.
- Every leg's complete exit back to the vault in the vault's asset: unwind, wait out any queue, collect what the protocol paid to the position (Hermetica pays the claim's user, the position), swap non-USDCx assets back with a signer-chosen minimum, and return the proceeds. A mock that pays out at once, or to the caller, hides a stranded asset.
- Measure the exact function call graph, maximum callback buffer/list sizes, stack depth, the five execution costs (runtime, read count, read length, write count, write length), and events/asset post-conditions.
