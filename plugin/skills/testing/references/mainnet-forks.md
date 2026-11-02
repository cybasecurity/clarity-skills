# Mainnet forks

The full rules behind the summary in [mainnet forks](../SKILL.md#mainnet-forks).

Remote-data sessions fetch contracts and state from a node at a pinned **Stacks** block height. Configure them in `Clarinet.toml` (read by the Vitest environment):

```toml
# fragment: Clarinet.toml for a pinned mainnet fork
[[project.requirements]]          # one entry per mainnet contract your contracts call
contract_id = "SP120SBRBQJ00MCWS7TM5R8WJNTTKD5K0HFRC2CNE.usdcx"

[repl.remote_data]
enabled = true
api_url = "https://api.hiro.so"
initial_height = 9260700      # pin a height; record why, and the block hash it resolves to
use_mainnet_wallets = true    # deployer and wallets get SP... addresses
```

Or in code with `getSDK()`, instead of the `Clarinet.toml` table:

```ts
import { getSDK } from '@stacks/clarinet-sdk';

const simnet = await getSDK();
await simnet.initEmptySession({ enabled: true, api_url: 'https://api.hiro.so', initial_height: 9258000 });
const r = simnet.callReadOnlyFn('SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token', 'get-total-supply', [], 'SP000000000000000000002Q6VF78');
```

- List every external contract your code calls under `[[project.requirements]]` and keep only those; sBTC is built in. `clarinet check` must pass on its own, from requirements, not only remote data. Requirements deploy the mainnet contracts into simnet under their mainnet principals, so contracts call them by those principals; never make an asset or protocol principal admin-settable so that mocks can stand in.
- **Set `use_mainnet_wallets = true`:** Without it the deployer and wallets derive testnet (`ST...`) addresses even on a mainnet fork, so your deployed contracts are testnet principals, and mainnet `is-standard` checks reject them (for example the Bitflow DLMM pool's recipient check, `err u3003`). That is a setup artifact, not proof a route cannot work; confirm any such failure with an `SP...` principal.
- **Pin `initial_height`:** Without it the session forks at the node's latest tip. Label results as remote-state simulation. Heights before a contract's deployment report "does not exist".
- **Fund principals as a real holder:** Simnet does not check signatures, so `simnet.callPublicFn(token, 'transfer', [amount, holder, to, none], holder)` works for any standard address that holds the token at the pinned height. `GET /extended/v3/tokens/ft/{contract}::{asset}/holders` lists current holders with a nonzero balance (`principal`, `balance`), largest first; the largest are often protocol contracts, which cannot send transactions. Pick a standard address, record it as the simulated donor and assert its balance at the pinned height in the test.
- Remote-data sessions have no boot sBTC contract, so a configured `sbtc_balance` cannot be minted (Clarinet prints a warning): set `sbtc_balance = 0` there and fund sBTC from a holder.
- **Block time on a fork:** In SDK 3.26.0, `stacks-block-time` starts at the fork height's time; each simnet transaction mines a block, and transaction blocks (`callPublicFn`, `mineBlock`, `mineEmptyStacksBlock`) add about 10 seconds each. `mineEmptyBlock` and `mineEmptyBurnBlock` start a new burn block and jump up to 600 seconds. Send calls that need a fresh signed price or a short deadline before any empty block (batching them in one `simnet.mineBlock` keeps them at one time); advance time deliberately with empty burn blocks for expiry tests. Router deadlines are Stacks heights: read `simnet.blockHeight`.
- **Rate limits:** Remote reads share `api_url`'s per-IP limit. Clarinet 3.26.0 and the SDK send `HIRO_API_KEY` from the environment as `x-api-key` on every remote-data request (no `Clarinet.toml` setting), giving the suite its own quota; keep the key out of committed files. The SDK retries a 429 only when the response carries `ratelimit-remaining: 0` ([retry policy](https://github.com/stx-labs/clarinet/blob/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarity-repl/src/repl/remote_data/http_request/retry.rs#L97-L106)). It caches state under `cache_dir` (default `./.cache`), keyed by the pinned block hash. Keep the cache between runs (untracked), do not run several fork suites in parallel, expect the first run at a new height to be slow, and point `api_url` at your own node for heavy suites. A 429 is a per-minute limit: wait for the window and retry. It is no reason to drop the fork and test only against mocks.

```ts
// fragment: fork helpers (vitest-environment-clarinet provides `simnet`)
export function fundFromHolder(token: string, holder: string, to: string, amount: bigint) {
  const { result } = simnet.callPublicFn(token, 'transfer',
    [Cl.uint(amount), Cl.principal(holder), Cl.principal(to), Cl.none()], holder);
  if (result.type !== 'ok') throw new Error(`funding from ${holder} failed: ${JSON.stringify(result)}`);
}
export const tokenBalance = (token: string, who: string): bigint =>
  (simnet.callReadOnlyFn(token, 'get-balance', [Cl.principal(who)], who).result as any).value.value;
export const deadlineIn = (blocks: number) => Cl.uint(BigInt(simnet.blockHeight + blocks));
```

- A remote read or simulation is not a live transaction. Use devnet when actual post-conditions, boot-contract transitions, signer/block timing or consensus admission matter.
