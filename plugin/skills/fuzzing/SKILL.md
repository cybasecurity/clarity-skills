---
name: fuzzing
description: "Fuzz Clarity contracts with Rendezvous: invariants, property tests and counterexample replay. Use to fuzz a Clarinet project or add invariants or property tests."
license: MIT
compatibility: "A Clarinet project with Node 22.18+, @stacks/rendezvous 1.0.3, fast-check 4.10.2 and @stacks/clarinet-sdk 3.26.0."
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Fuzzing

Use [Rendezvous](https://github.com/stx-labs/rendezvous) for Clarity-native fuzzing. Keep Clarigen as the default for ordinary typed tests and deterministic regressions.

## Key distinctions

- In 1.0.3, properties are private `test-*` and invariants read-only `invariant-*`, inside the target contract. Rendezvous 0.x merged a sibling `<contract>.tests.clar` into the target and ran public `test-*` properties. 1.0 ignores that file, so when upgrading, move each definition into the contract with its own `;; #[env(simnet)]` line and redefine each `test-*` with `define-private`. 1.0 skips a public `test-*` in test mode and calls it as an action in invariant mode.
- Property `(ok true)` passes; `(ok false)` discards. A run with every case discarded can still exit zero and print success.
- Invariant mode ignores failed public actions, including runtime errors, if its selected invariant still holds. A passing invariant is not evidence that operations succeeded.
- Default integer generation does not cover uint128 extremes. Include explicit bigint boundaries and check generated optional values.
- CLI runs retain state and randomly select checks. They do not test every invariant after every call or establish production cost/transaction behavior.

## Build and run

- Define properties from protocol obligations: accounting conservation, backing, bounded debt, caller authority, rounding and settlement. Make denominators, units, reserves and permitted losses explicit.
- Initialize realistic actors, balances, roles and hostile trait implementations. Require successes for each critical action: rejected calls and aggregate counts can hide untested cancellations or settlements. Use reachable setup prefixes or state-aware generators.
- Use the [library](#library-campaigns) for full-width generators, reproducible sequences, cost tracking and multiple-contract orchestration.
- Bound campaigns, inspect per-function checked/success/discard counts and preserve source, lockfile, seed, run count, config, logs and regression records.
- Reproduce failures from clean initial state. Turn reachable failures into [Clarigen regressions](../testing/SKILL.md); assess security impact through [auditor guidance](../auditor/SKILL.md).
- Use [environment fidelity](../environments/SKILL.md) for simulator limits and [optimizer guidance](../optimizer/SKILL.md) for cost claims.

## Install and select a target

- Install in the development project, preserving compatible pins and committing the lockfile. If npm fails on the scaffold's peer dependencies, follow the [setup diagnostics](../testing/references/project-setup.md#setup-diagnostics).

```sh
npm install --save-dev --save-exact @stacks/rendezvous@1.0.3 fast-check@4.10.2
npm ls @stacks/rendezvous @stacks/clarinet-sdk @stacks/transactions fast-check   # one deduped @stacks/transactions
npx --no-install rv --help
```

- Add the [shared npm script](../testing/references/project-setup.md#scripts-and-reports), substituting the manifest contract name: `{ "scripts": { "fuzz": "rv . capped test --runs=1000 && rv . capped invariant --runs=1000" } }`. `npm run fuzz` finds the local `rv`. The `&&` skips the invariant run after a property failure, so use separate CI steps when both reports are needed.
- Keep the exact `fast-check` pin for the CLI too. Rendezvous uses that copy, and what a seed generates can change between fast-check versions. A [library script](#library-campaigns) also imports it.
- CLI arguments are project **directory**, manifest contract **name**, then `test` or `invariant`.
- If present, `Clarinet-<contract-name>.toml` overrides `Clarinet.toml`. Check the printed manifest path.
- Rendezvous fuzzes only a contract deployed by the simnet deployer. Each test, `can-`, action and invariant call comes from a random Devnet account other than `faucet`, or a config `accounts` entry. A property that reaches an owner-only path must discard or expect rejection for other callers. Requirements alone do not establish live roles, funds or oracle state.

## Properties and invariants in the contract

- Properties: private `test-*`, marked `;; #[env(simnet)]`, with no context required. `(ok true)` passes, `(ok false)` discards; `err`, runtime exceptions and incompatible results fail.
- Optional read-only `can-<test-name>` (for example `can-test-write-read`) must declare the test's parameters with the same names, types and order, and return bool: **false skips**, true executes. Do not discard the edge case the test should catch.
- Invariants: read-only boolean `invariant-*`, marked `;; #[env(simnet)]`, checking state after arbitrary public calls, including rejected calls.
- Invariant mode always requires the `context` map and private `update-context`: copy both definitions below verbatim, renaming any conflicting map first. Counts are successful public calls, not attempts or transferred amounts.
- `#[env(simnet)]` is a Clarinet preprocessing annotation, not a VM access-control feature. Clarinet removes the annotated code only when it builds an on-chain deployment; uploading the raw file with another tool keeps it. Inspect the source you deploy.
- A private test calling internal functions does not prove a production public caller can reach the same state. Add real public router/callback regressions where relevant.
- Keep the project's existing `[contracts.<name>]` entry; Rendezvous does not need a particular Clarity version. The example uses `[contracts.capped]` with `path = "contracts/capped.clar"`, `clarity_version = 6`, `epoch = "4.0"`.
- Example: `capped` stores a value; `set-value` rejects above `u100` with `(err u1000)`, and `get-value` reads it. Replace this value-bound example with the project's economic and authority checks.

```clarity
;; fragment
;; #[env(simnet)]
(define-private (test-write-read (raw uint))
	(let ((value (mod raw u101)))
		(try! (set-value value))
		(asserts! (is-eq (get-value) value) (err u1001))
		(ok true)))
;; Required verbatim in every contract fuzzed in invariant mode:
;; #[env(simnet)]
(define-map context (string-ascii 100) {called: uint})
;; #[env(simnet)]
(define-private (update-context (function-name (string-ascii 100)) (called uint))
	(ok (map-set context function-name {called: called})))
;; #[env(simnet)]
(define-read-only (invariant-cap) (<= (var-get stored) u100))
```

## Run, inspect and replay

Run from the project directory:

```sh
npx --no-install rv . capped test --seed=42 --runs=1000
npx --no-install rv . capped invariant --seed=42 --runs=1000
npx --no-install rv . capped invariant --seed=42 --runs=1000 --bail
npx --no-install rv . capped invariant --regr
```

- A fixed `--seed` does not guarantee the same callers or block heights. Callers and principal arguments come from an account list whose order can change with the contract source, or on a run that prints `Updated deployment plan file`. Heights also depend on `--runs`: between trials Rendezvous mines up to 100,000 / `--runs` blocks at random. Vary seeds, record each with its run count, and reproduce a failure from its logged callers and arguments.
- `--runs` counts generated trials, not guaranteed executions of every property/action. A trial selects one invariant after a generated sequence; state persists between trials.
- `--bail` stops at first failure and disables shrinking. Without it, inspect the shrunk result but reproduce it from clean initial state before reporting.
- Failures persist under **current working directory** `.rendezvous-regressions/<contract-id>.json`. Preserve this directory. `--regr` replays saved failures for the selected mode with the failing run number (at least 100) as `--runs`, so a passing replay does not prove a fix.
- Records contain seed, run count, dialer path and timestamp, not a complete state/transaction snapshot. Keep full logs, original run count, manifests, source, SDK/fast-check lock, actors and initialization. Seed alone is insufficient across changed versions/configuration.
- A run that finds a failure exits 1. A wrong contract name, empty test discovery, an invalid `can-` function, no saved regressions or all-discarded tests exit 0. Require expected tests and nonzero checked counts; inspect skipped trait cases and public-action success rates.

## Configuration and callbacks

- `npx --no-install rv . capped invariant --config=rv.config.json` with a file such as `{ "seed": 42, "runs": 1000, "bail": true, "regr": false }`.
- `--config` exclusively supplies run options. Other option flags are ignored; put replay/seed/run changes in the file or run without it.
- `accounts` takes `{ "name": "actor", "address": "..." }` entries; `accounts_mode` defaults to `overwrite`, with `concatenate` available. Selection does not fund accounts or grant contract permissions.
- In invariant mode, `--dial=./checks.cjs` loads exported `pre*`/`post*` callbacks. Context contains `selectedFunction`, `clarityValueArguments` and `functionCall` (`undefined` before execution).
- Post callbacks run only after successful public calls. They cannot enforce that rejected or runtime-aborting actions fail a campaign. Property mode does not use dialers; use the library for custom outcome policy.

## Library campaigns

- Rendezvous exports `getContractFunction(simnet, contract, fn, deployer?)` and `strategyFor(simnet, fn, addresses?, traitImplementations?)`. The latter returns a fast-check arbitrary of Clarity argument arrays.
- Use a custom loop for setup, multiple contracts, every invariant after each action, strict runtime-error handling or explicit block schedules. Generated arguments can use the SDK directly; keep Clarigen for deterministic tests.
- Needs `npm install --save-dev --save-exact @stacks/rendezvous@1.0.3 fast-check@4.10.2 @stacks/clarinet-sdk@3.26.0 @stacks/transactions@7.6.0` (use the project's actual pins). Run the script with `node fuzz.mjs`, or add `"fuzz:lib": "node fuzz.mjs"` to the scripts.
- In 1.0.3, `uint128` uses `fc.nat()` and `int128` uses `fc.integer()`: 32-bit domains with pinned fast-check. Add `fc.bigInt`, exact edges, valid business values and hostile trait/principal cases.
- The optional converter maps falsy values to absent. Explicitly test present false/zero/empty strings/buffers versus `none`, using `Cl.some(Cl.bool(false))`, `Cl.some(Cl.uint(0n))` and `Cl.none()`.
- Reset each independent case (including shrinking/replay) with `initSimnet('./Clarinet.toml', false, options)`. That call keeps the options of the SDK it reuses, so create the SDK first with `noCache` set to `true`, as below, or `costs` can stay `null`. Assert `currentEpoch`, costs, accepted writes, expected rejections and final state.
- For stateful sequences, reset **per sequence**, initialize roles/liquidity, then check every required invariant after each action. Resetting per action would erase the history under test.

```js
// fragment: fuzz.mjs core; imports assert, fc, Cl, initSimnet, getContractFunction, strategyFor
const options = { trackCosts: true, trackCoverage: false };
const initial = await initSimnet('./Clarinet.toml', true, options);
const generated = strategyFor(initial, getContractFunction(initial, 'capped', 'set-value'));
const max = (1n << 128n) - 1n;
const fullWidth = fc.bigInt({ min: 0n, max }).map(n => [Cl.uint(n)]);
async function check(args) {
  const simnet = await initSimnet('./Clarinet.toml', false, options); // new session per case
  const receipt = simnet.callPublicFn('capped', 'set-value', args, simnet.deployer);
  assert.deepEqual(receipt.result, args[0].value <= 100n ? Cl.ok(Cl.bool(true)) : Cl.error(Cl.uint(1000n)));
}
for (const n of [0n, 1n, 99n, 100n, 101n, 1n << 127n, max]) await check([Cl.uint(n)]);
await fc.assert(fc.asyncProperty(fc.oneof(generated, fullWidth), check), { seed: 42, numRuns: 100 });
```

## Interpret results correctly

| 1.0.3 behavior | Required interpretation |
|---|---|
| CLI initializes SDK without `trackCosts` | Use a tracking-enabled library or Clarigen reproduction for cost-sensitive behavior; CLI success is not a budget proof |
| A public action errors during invariant mode | May be ignored while invariants pass; separately assert required success and unexpected runtime failures |
| Property/invariant itself throws | Fails the run, but its FAILED count can stay zero; inspect failure logs/exit status |
| Trait parameter has no known implementation | Test/action can be skipped; supply real and adversarial implementing contracts |
| Only one selected invariant checked after a random action sequence | Short-lived violations can be missed; choose the library when each transition needs every invariant |

- 1.0.3 has no `--fail-on-unchecked`, coverage or snapshot flags; confirm with `rv --help` before advertising one.
- One CLI target covers one contract. Multi-contract models need explicit actions; adapters must preserve the authority being tested.
- A conserved sum is meaningful only over the relevant actors, reserves, shares and liabilities. "Shares never exceed assets" is not a generic invariant across decimals, exchange rates or losses.

## Sources

- [Repository/issues](https://github.com/stx-labs/rendezvous/issues), [releases](https://github.com/stx-labs/rendezvous/releases), [book](https://stx-labs.github.io/rendezvous/), [Clarinet issues](https://github.com/stx-labs/clarinet/issues), [Clarigen issues](https://github.com/hstove/clarigen/issues).
- Workflow: [usage book](https://stx-labs.github.io/rendezvous/chapter_6.html), [CLI](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/cli.ts), [property runner](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/property.ts), [invariant runner](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/invariant.ts), [persistence](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/persistence.ts). Verify the installed release before adopting newer documentation.
- Library: [library API](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/lib.ts), [generators/conversion](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/shared.ts), [CLI initialization](https://github.com/stx-labs/rendezvous/blob/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d/app.ts), [Clarinet SDK](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87/components/clarinet-sdk), [fast-check generators](https://github.com/dubzzz/fast-check/tree/c77afa8277a67250d798c52e61343b8ed5fd268b/packages/fast-check/src/arbitrary).

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `rendezvous`: [a8951ab0c1](https://github.com/stx-labs/rendezvous/tree/a8951ab0c1543331f7c84f2546ddfd6fc8a53e2d).
- `clarinet`: [52e4f35ea5](https://github.com/stx-labs/clarinet/tree/52e4f35ea50f5e6f8a7dd9505b91bd9469909b87).
- `fast-check`: [c77afa8277](https://github.com/dubzzz/fast-check/tree/c77afa8277a67250d798c52e61343b8ed5fd268b).
