---
name: clarity-testing
description: "Test Clarity contracts with Clarigen and the Clarinet SDK (vitest, simnet): setup, typed calls, mining blocks, coverage, mainnet forks, attacker contracts. Use whenever adding or fixing tests in a Clarinet project."
license: MIT
compatibility: "A Clarinet 3.26.0 project with Node 22.18+ and npm 11, @stacks/clarinet-sdk 3.26.0, @stacks/transactions 7.6.0, Vitest 5.0.5 and Clarigen 4.1.7."
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Testing

Use **Clarigen by default for typed clients and tests** (`@clarigen/core`, `@clarigen/test`, `@clarigen/cli`). Clarinet supplies the VM, manifest, simnet, devnet and deployment tooling. Preserve existing manifests, package managers, tests and explicit tooling choices; add only the needed Clarigen changes.

## Key distinctions

- Clarigen does not replace the Clarinet execution engine or add unsupported epochs.
- Generated types prove neither authorization nor correct economic behavior.
- Direct wallet calls miss router/callback sender context. Private calls and patched storage do not prove public reachability.
- A source requirement does not import every live permission, balance or oracle setting.
- Separate simnet calls mine separate blocks; test same-block restrictions with an explicit batch. One block is not one atomic transaction.
- Raw simulated senders do not prove signature or mempool admission; use [environment fidelity](../clarity-environments/SKILL.md) to choose simnet, devnet or a network check.

## New project

`clarinet new` writes `Clarinet.toml`, `settings/`, `package.json`, `vitest.config.ts`, `tsconfig.json` and `tests/`; it does not run `npm install`. `clarinet contract new` (alias `contracts new`) adds `contracts/vault.clar`, `tests/vault.test.ts` and the manifest entry.

```sh
clarinet new my-protocol && cd my-protocol
clarinet contract new vault
# One copy of @stacks/transactions: Clarigen packages otherwise install 7.1/7.2 next to the SDK's 7.6.0
npm pkg set 'overrides.@stacks/transactions=$@stacks/transactions'
# npm 11 (Node 24+ ships it): the npm 10.9 bundled with Node 22 crashes on this scaffold (see below)
npx -y npm@11 install --save-dev --save-exact \
  @clarigen/cli@4.1.7 @clarigen/core@4.1.7 @clarigen/test@4.1.7 \
  @stacks/clarinet-sdk@3.26.0 @stacks/clarinet-sdk-wasm@3.26.0 @stacks/transactions@7.6.0 \
  vitest@5.0.5 vitest-environment-clarinet@3.1.0
npm pkg set scripts.clarigen="clarigen && clarigen docs" scripts.pretest="npm run clarigen"
npx clarigen init     # writes Clarigen.toml; refuses if it exists (--overwrite)
npx clarigen          # generates src/clarigen-types.ts and the simnet deployment plan
npx vitest run
```

- `npm ls @stacks/transactions` must show one `7.6.0` copy or `deduped`: mixed copies compare Clarity values badly. The override follows the direct dependency; a literal override can cause `EOVERRIDE`.
- With npm, use npm 11 for every install; npm 10.9.8 fails on the initializer's Vitest 4 peers. For either install error, read [setup diagnostics](references/project-setup.md#setup-diagnostics).
- `@clarigen/test` declares Clarinet SDK/WASM peers `^3.9.2`; keep both at the same version and commit the lockfile.
- Stay on Clarinet and the SDK 3.26.0: SDK 4 (Clarinet 4.0) removed `simnet.runSnippet`, so Clarigen 4.1.7 fails with `simnet.runSnippet is not a function`. A project created by Clarinet 4 works once the install above pins the 3.26.0 packages.
- Keep generated `Clarigen.toml` and comments (`output = "src/clarigen-types.ts"`, `[docs] output = "docs"`). From `tests/`, import `../src/clarigen-types`; these examples instead set output to `tests/clarigen-types.ts` and import `./clarigen-types`.
- Regenerate after ABI, deployment or requirement changes (`npx clarigen`, or `--watch`). Never fix a stale ABI by editing generated types. `TestProvider`, Deno-only, `clarigen.config.json` and `[esm]` guides are obsolete.
- Keep the initializer's Clarinet settings in [`vitest.config.ts`](references/project-setup.md#vitest-configuration) and add runner options such as `testTimeout` or `silent` alongside them; flags after `--` (for example `-- --coverage --costs`) are read by `getClarinetVitestsArgv()`. The `transformMode` warning (environment 3.1.0 on Vitest 5) is harmless.
- Keep initializer defaults; apply [formatting and function comments](../clarity-scholar/references/style.md#formatting-and-function-comments) to authored production contracts (mock comments optional).
- On Windows, read [Windows manifest paths](references/troubleshooting.md#windows-manifest-paths) before generation.
- Read [project setup](references/project-setup.md) for scripts, Vitest config, focused tests, snapshot filtering and tool limits (no epoch 4.1 / Clarity 7 in simnet).

### Manifest settings

```toml
# Clarinet.toml (fragment)
[contracts.vault]
path = "contracts/vault.clar"
clarity_version = 6         # `clarinet contract new` writes the toolchain default; omit to inherit it
epoch = "latest"            # or an explicit epoch such as "4.0"

# Ordinary mainnet requirements keep this principal in simnet; boot contracts are separate.
[[project.requirements]]
contract_id = "SP3FBR2AGK5H9QBDH3EEN6DF8EK8JY7RX8QJ5SVTE.sip-010-trait-ft-standard"
```

- Set `clarity_version` and `epoch` per contract in `Clarinet.toml` deliberately: manifest contracts deploy at session start with them, and `simnet.setEpoch()` only affects later dynamic deployments and execution. Assert `simnet.currentEpoch`; invalid epoch strings fall back to defaults.
- Never raise `clarity_version` just to silence an analysis error in a contract that is already deployed: it changes semantics ([versions](../clarity-epochs/SKILL.md)).
- Same-deployer dependencies use `.token`; external requirements use their full principal, and traits use `principal.contract.trait-name`. **Ordinary mainnet requirements retain their original mainnet principal and name in simnet.** Do not substitute an `ST...` principal. Boot-principal handling and deployment-plan network remapping are separate ([environments](../clarity-environments/SKILL.md#simulator-traps)).
- sBTC is a boot contract in simnet/devnet from epoch 3.0 (`SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4.sbtc-token`); do not add it as a requirement. Each wallet in `settings/Devnet.toml` is credited `sbtc_balance` sats (default `1_000_000_000`); override per account:

```toml
# settings/Devnet.toml: per-account override
[accounts.wallet_1]
mnemonic = "..."          # keep the generated value
balance = 100_000_000_000_000
sbtc_balance = 1_000_000
```

- A `clarinet` binary on PATH may be years old (0.x releases predate Clarity 2). Check that `clarinet --version` matches the project's SDK (`npm ls @stacks/clarinet-sdk`, 3.26.0).

## Write typed tests

```ts
// fragment: Clarigen 4.1.7 typed calls; generated project has ledger with ERR_TOO_LARGE
import { projectFactory, projectErrors } from '@clarigen/core';
import { txOk, txErr, rov } from '@clarigen/test';
import { project, accounts } from './clarigen-types';

const { ledger } = projectFactory(project, 'simnet');
const errors = projectErrors(project);
const alice = accounts.wallet_1.address;

txOk(ledger.deposit(100n), alice);
const rejected = txErr(ledger.withdraw(101n), alice);
expect(rejected.value).toBe(errors.ledger.ERR_TOO_LARGE);
expect(rejected.events).toHaveLength(0);
```

| Helper | Result |
|---|---|
| `txOk` / `txErr` | Receipt with raw `.result` and validated, unwrapped `.value` |
| `tx` | Receipt; `.value` retains `{ isOk, value }` |
| `ro` / `rov` | Read-only receipt / decoded value, preserving a response wrapper if present |
| `roOk` / `rovOk` | Read-only receipt / unwrapped value; requires an `ok` response |

- Share factories, errors and actors through one helper module (for example `tests/helpers.ts`) instead of redefining them in each test.
- Prefer `.value` after `txOk`/`txErr`; it validates the branch. Do not re-decode `receipt.result` by hand.
- `rov` for a plain uint/tuple/bool; `rovOk` for response-returning functions. Pass an explicit sender for caller-sensitive views; the default is the contract's deployer.
- `projectErrors` extracts constants whose names begin with `err` (case-insensitive) per contract. Name errors and keep their originating contract; numeric codes are not globally unique.
- Raw SDK assertions use `Cl.ok(value)` and `Cl.error(value)`, not `Cl.err`. For a raw optional tuple compare the whole value: `expect(result).toBeSome(Cl.tuple({ status: Cl.uint(0n) }))`. Decoded Clarigen values have a different shape than raw Clarity values.
- Integer results are bigint. Use `100n` and `Cl.uint(2n ** 127n)`; JavaScript numbers lose precision above 2^53.
- Keep Vitest's simnet reset before every test (`initBeforeEach`). Put role/token/pool setup in `beforeEach` helpers with explicit parameters, units and assertions; the reset before each test discards whatever a `beforeAll` set up.
- Run semantic and cost regression tests with cost tracking and assert receipts contain costs (`receipt.costs`): the free tracker can hide cost-triggered runtime failures. Under Vitest, `-- --costs` or `costs: true` in `environmentOptions.clarinet` turns on `trackCosts`; plain `npm test` runs without it.
- Exercise public caller graphs; assert response, balances (`simnet.getAssetsMap()`), storage (`simnet.getMapEntry`, `simnet.getDataVar`) and ordered events. On failure, check unchanged balances/storage, not only empty events.
- ABI tuple keys with a numeric suffix need explicit packing: [numeric tuple keys](references/troubleshooting.md#numeric-tuple-keys).

### Events and runtime failures

- `filterEvents` selects an event type only. Also check emitter (`ledger.identifier`, a full principal), topic `print` and payload shape; another contract can print the same tuple. Assert exact count, order and amounts ([`depositEvents`](references/helpers-and-assertions.md#assert-event-provenance-and-payload)).
- Read-only prints appear on stdout but are discarded from receipts, even when a public function calls the read-only function ([VM transaction contexts](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/contexts.rs)). Emit the intended event in the public execution context and assert its receipt.
- `txErr` is for a returned `(err ...)`. An underflow, overflow or panic **throws** instead; it is not another error code. Match the intended category (`/ArithmeticUnderflow/`, not Rust file paths or line numbers), then assert unchanged balances/storage ([`captureRuntimeError`](references/helpers-and-assertions.md#separate-contract-errors-from-runtime-failures)).
- Full helpers and raw SDK use for dynamic contracts, raw values or wrapper gaps: [helpers and assertions](references/helpers-and-assertions.md).

### Post-conditions in tests

Typed `txOk`/`txErr` take no options, so they cannot carry post-conditions. Pass them on the raw call:

```ts
// fragment: raw SDK call with post-conditions
import { Cl, Pc } from '@stacks/transactions';
const r = simnet.callPublicFn('ledger', 'withdraw', [Cl.uint(20)], alice, {
  postConditions: [Pc.principal(`${deployer}.ledger`).willSendEq(20n).ustx()],
  postConditionMode: 'deny',          // 'allow' | 'deny' | 'originator'
});
expect(r.result).toBeOk(Cl.uint(80));
```

- Supplying either option turns enforcement on (mode defaults to `deny`); supplying neither disables the check.
- A violated condition **throws** (`Post-condition check failure on STX owned by ...: 20 SentEq 19` when 19 is sent) and rolls back; it does not return an `err`. In `deny` mode an unchecked STX or FT movement throws `... was moved by ... but not checked`, but an NFT whose sender has no NFT condition throws `No checks for non-fungible asset ...`. Match the shared prefix `Post-condition check failure` and the asset.
- The same options exist on `simnet.deployContract` (fifth argument) and `tx.callPublicFn(..., sender, options)` inside `mineBlock`. `simnet.transferSTX` throws when given any condition, as a node rejects an STX transfer transaction that carries post-conditions.
- Amount semantics (gross outflow per principal and asset): [postcondition rules](../clarity-wallets/SKILL.md#post-conditions).

## Blocks, clocks and same-block batches

- Later `stacks-block-height` or same-tenure ordering: `simnet.mineEmptyStacksBlocks(n)` (epoch 3.0+). PoX cycle, `burn-block-height` or Bitcoin delay: `simnet.mineEmptyBurnBlocks(n)`; it also advances the simulated Stacks tip, so measure both heights when their relationship matters. `mineEmptyStacksBlock()`/`mineEmptyBurnBlock()` mine one.
- `mineEmptyBlock()` / `mineEmptyBlocks()` **are aliases for burn-block mining** in SDK 3.26.0 ([SDK WASM core](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk-wasm/src/core.rs)). Do not use them when the clock matters.
- Read starting heights after setup; never assume height 1. On a fork the burn and Stacks clocks start at the forked block's times, so a burn block's time jump can differ from plain simnet: check the resulting window explicitly. A fixed block count is not elapsed seconds: read the contract's clock before and after and hit the actual boundary (one before, at, one after; PoX boundaries from the target's cycle parameters).

### Several transactions in one block

- `simnet.mineBlock([tx.callPublicFn(contract, fn, args, sender), ...])` with `import { tx } from '@stacks/clarinet-sdk'`. Ordinary `callPublicFn`/`txOk` calls each mine their own block, even in a loop.
- In a batch, receipts follow input order and later transactions see earlier committed effects. Each transaction has its own rollback: a returned `err` in one does not revert the others. The batch is one block, **not one atomic transaction**; atomic composition needs one public entry point that calls the legs.
- Read [references/blocks-and-batches.md](references/blocks-and-batches.md) for the full rules and examples: clock boundaries, an `advanceBurnTo` helper, batch receipts, a throwing entry and an `inBlock` bridge for Clarigen calls.

## Drive public functions through attacker contracts

- Test through **contracts**, not only wallets: deploy a small caller/attacker contract to create the `contract-caller`/`tx-sender` context a router, callback or malicious contract would. `callPrivateFn` and storage patches skip the public boundary.
- Assert the asset delta, not only the response, and contrast with the control (direct call refused, fixed code or trusted path fails with the expected error).
- Read [references/test-design.md](references/test-design.md#drive-public-functions-through-attacker-contracts) before writing one: deploy order, sender contexts, lying trait implementations and an admin-to-bait fragment.

Case selection per surface: [test matrix](#test-matrix); write-up: [PoC construction](../clarity-auditor/SKILL.md#proof-of-concept).

## Test matrix

Choose rows relevant to the reviewed behavior, rather than adding generic tests for every helper.

- Read [references/test-design.md](references/test-design.md#test-matrix) for the required contrasting cases and what to observe per surface (authority, trait, allowance, token, math, oracle, time, upgrade and more).
- Use a version-matched simnet for contract semantics and devnet/replay for node/epoch/bridge behavior that simnet does not model.

## Mainnet forks

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

Read [references/mainnet-forks.md](references/mainnet-forks.md) before configuring or debugging a fork (full rules, `getSDK()`, funding helpers). In short:

- Set `use_mainnet_wallets = true`, or mainnet `is-standard` checks reject your `ST...` contracts.
- Fund principals by transferring as a real standard holder; set `sbtc_balance = 0` and fund sBTC from a holder.
- Transaction blocks add about 10 seconds, empty burn blocks up to 600: send calls that need a fresh signed price before any empty block.
- Set `HIRO_API_KEY` and keep the cache; a 429 is no reason to drop the fork for mocks.

- A remote read or simulation is not a live transaction. Use devnet when actual post-conditions, boot-contract transitions, signer/block timing or consensus admission matter.

## Dependencies and fixtures

- Pin upstream source revisions and network principals (a submodule or other pinned checkout, declared requirements, ignored caches). Call deployed dependencies through requirements instead of copying their code into owned contracts; when you embed upstream code, record its repository and revision.
- Keep one authored logic set. Prefer requirements, which keep mainnet principals in simnet, over per-network copies. If the project generates local/deployment variants, derive them from explicit principal bindings that preserve comments, strings, ABI and behavior; distinguish contract identities, authority principals and signed domains, and reject unconfigured principals before writing outputs. Never replace mainnet principals with an indiscriminate string replacement that also rewrites role checks or signed domains.
- Keep mock contracts (for example under `contracts/mock/`) out of integration manifests. Integration tests execute unmodified requirements at pinned state and assert custody/roles; mocks alone do not establish readiness.
- Before pinning dependencies or building fixtures, read [dependency rules and examples](references/dependencies.md).

## Coverage, costs and properties

- `npx vitest run -- --coverage --costs` (the `test:report` script) writes `lcov.info` (Clarity line/branch coverage, one record per test) and `costs-reports.json` in the project root. These are Clarity VM flags, not Vitest's V8 coverage. Ignore the reports in Git. Script set: [scripts and reports](references/project-setup.md#scripts-and-reports).
- Read [coverage aggregation](references/project-setup.md#coverage-aggregation) before reporting a percentage or generating HTML: merge per-test records, state which contracts count and collect reports before SDK resets.
- Coverage does not prove invariants, authorization or economic safety; inspect reachable critical branches. Check current tooling issues before treating a percentage as a security gate.
- Read [references/test-design.md](references/test-design.md#properties-and-generated-inputs) before writing property or generated-input tests: bigint boundaries and rounding, seeded generators, invariants and saved failures.
- Report coverage and simulator/live-state differences. Execute downloaded reference repositories only when that execution is authorized.
- Before deployment, follow the release runbook in [clarity-deployment](../clarity-deployment/SKILL.md); after the tests pass, run `npm run test:report` and state the coverage figure.
- Deployment easter egg: if measured authored-Clarity line coverage is below 90%, name the figure/scope and add a friendly jab: "Leaving the untested bits to vibes? Are you sure you want to deploy?" Ask once and respect the answer. Coverage is not a security guarantee; local testing or deployment preparation does not trigger this.

## Troubleshoot against both projects

- [Clarigen repository](https://github.com/hstove/clarigen) and [issues](https://github.com/hstove/clarigen/issues); [Clarinet repository](https://github.com/stx-labs/clarinet) and [issues](https://github.com/stx-labs/clarinet/issues).
- Search the exact installed version and error before changing APIs or downgrading semantics. Some older examples use obsolete Deno/configuration APIs.
- [Versions](../clarity-epochs/SKILL.md) and [model corrections](../clarity-epochs/SKILL.md#recall-corrections) help separate code errors from tooling gaps.
- Read [references/troubleshooting.md](references/troubleshooting.md) for print floods, [bad trait argument errors](references/troubleshooting.md#errors-from-a-bad-trait-argument), Windows manifest paths, a diagnostic record and numeric tuple keys.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
- `clarigen`: [23dd026fe4](https://github.com/hstove/clarigen/tree/23dd026fe47ba46513b255aeb3557d0b0f5368bc).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
- `stackingdao`: [125c73dc10](https://github.com/StackingDAO/stackingdao-smart-contracts/tree/125c73dc109988730156f4d0434ff01654480fc7).
- `bitflow-dlmm`: [b4d3694c86](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0).
- `clarinet-targeted`: [0b59577fdd](https://github.com/stx-labs/clarinet/tree/0b59577fdd3c073a4132aa59348029604a2560e2).
- `granite`: [2d44a2df94](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b).
- `hermetica`: [5e13e431f6](https://github.com/hermetica-fi/hermetica-contracts/tree/5e13e431f69dd840fe297791fa2a73d9993a27e0).
