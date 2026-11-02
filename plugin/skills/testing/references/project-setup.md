# Project setup files

The initializer's Vitest configuration, the package scripts to add and the inner-loop commands for a project set up as in [new project](../SKILL.md#new-project).

### Vitest configuration

The initializer's `vitest.config.ts` already wires the Clarinet environment. Keep these settings and add runner options (`testTimeout`, `silent`) alongside them.

```ts
import { defineConfig } from "vitest/config";
import { vitestSetupFilePath, getClarinetVitestsArgv } from "@stacks/clarinet-sdk/vitest";

export default defineConfig({
  test: {
    environment: "clarinet",
    pool: "forks",
    isolate: false,       // Clarinet resets simnet between tests itself
    maxWorkers: 1,
    setupFiles: [vitestSetupFilePath],
    environmentOptions: { clarinet: { ...getClarinetVitestsArgv() } },
  },
});
```

- `tsc` over the initializer's `tsconfig.json` fails with `TS2554: Expected 3 arguments` inside the SDK's `vitest.setup.ts`. In `include`, replace `node_modules/@stacks/clarinet-sdk/vitest-helpers/src` with the two files `.../src/global.d.ts` and `.../src/vitest.d.ts` (this keeps the `simnet` global and `toBeOk` matchers typed) and keep `tests`.

### Setup diagnostics

- The `$@stacks/transactions` override follows the direct dependency's version. A literal override fails with `EOVERRIDE` while the scaffold still declares `^7.2.0`; use the command in [new project](../SKILL.md#new-project).
- npm 10.9.8 (bundled with Node 22.23) fails on the scaffold's Vitest 4 peers with `Cannot read properties of null (reading 'edgesOut')`. Use `npx -y npm@11 install`, or install npm 11 globally, for every install in the project. Node 24 and later bundle npm 11.

### Scripts and reports

The initializer provides `test`, `test:report` and `test:watch`. Add the scripts the project needs from this set and keep its existing ones.

```json
{
	"format": "clarinet format --in-place",
	"format:check": "clarinet format --check",
	"clarigen": "clarigen && clarigen docs",
	"pretest": "npm run clarigen",
	"test": "vitest run",
	"test:report": "vitest run -- --coverage --costs",
	"test:costs": "vitest run -- --costs",
	"test:coverage": "vitest run -- --coverage",
	"test:coverage:html": "npm run test:coverage && genhtml lcov.info --branch-coverage --output-directory coverage",
	"fuzz": "rv . capped test --runs=1000 && rv . capped invariant --runs=1000"
}
```

- `fuzz` is the same script as in [clarity:fuzzing](../../fuzzing/SKILL.md#install-and-select-a-target): replace `capped` with the manifest contract name and install `@stacks/rendezvous` as described there. `rv` resolves from `node_modules/.bin` inside an npm script.
- The format scripts assume Clarinet defaults and a manifest containing only owned contracts; use `--file PATH` when upstream contracts are listed too.
- Report flags and interpretation: [coverage](../SKILL.md#coverage-costs-and-properties). Merge per-test records as described below.

### Coverage aggregation

- Merged line coverage (a line counts if any test hit it); `lcov --summary lcov.info` prints the same figure:

```sh
awk -F'[:,]' '/^SF:/{f=substr($0,4)} /^DA:/{k=f","$2; if(!(k in m)||$3+0>m[k])m[k]=$3+0} END{for(k in m){t++; if(m[k]>0)c++} printf "%.1f%% (%d/%d lines)\n",100*c/t,c,t}' lcov.info
```

- The figure covers every manifest contract, including mocks and requirements; state the scope. `genhtml` comes from the separate [LCOV](https://github.com/linux-test-project/lcov) tool, not npm. If tests reset or switch SDK sessions, collect reports before each reset and check that aggregation keeps every suite.

### Inner loop

| Command | Purpose |
|---|---|
| `clarinet check` | Parse, type-check and lint every contract in the manifest |
| `clarinet format --dry-run` | Preview default formatter output (`fmt` alias); follow an existing project's configured style |
| `clarinet format --in-place` | Apply default formatting to manifest contracts; use `--file PATH` to target owned files |
| `clarinet format --check` | Check formatting without rewriting files; use the same configuration/scope as the formatting command |
| `clarinet console` | REPL with the project deployed. `::get_costs <expr>`, `::toggle_costs`, `::set_tx_sender <principal>`, `::mint_stx`, `::describe <fn>` |
| `npx vitest run` | Clarigen tests on SDK simnet. `npx vitest run -- --costs` writes `costs-reports.json`; `-- --coverage` writes `lcov.info` |
| `clarinet devnet start` | Local Stacks + Bitcoin regtest node when you need real blocks, signers, post-conditions or sBTC flows |
| `clarinet deployments generate --testnet` | Produce a reviewable deployment plan (`--simnet`, `--devnet`, `--mainnet` also exist); release steps are in [clarity:deployment](../../deployment/SKILL.md) |

- Generate types before a focused run (`clarigen docs` output is optional documentation), then run one case with `npx vitest run tests/ledger.test.ts -t "rejected withdrawal"`.

### Generation and tool limits

- Prefer the stock Clarigen CLI. Clock-based initialized values can make generated snapshots differ between runs; query runtime state in assertions. If you filter snapshots, preserve constants, error metadata and ABI descriptors and exercise `projectErrors` and the builders afterward.
- Tool limits: the pinned CLI/SDK default to epoch 4.0 / Clarity 6 and cannot select epoch 4.1 (Clarity 7 is untestable); a node's `/v2/pox` can list `Epoch41` before simnet can run it. Simnet reports the epoch-2.1 read budget (15,000 reads / 100 MB), not the live epoch-4.0 limits.

Sources: [Clarinet](https://github.com/stx-labs/clarinet), [SDK docs](https://docs.stacks.co/reference/clarinet-js-sdk/sdk-reference), [Stacks Clarity docs](https://docs.stacks.co/learn/clarity); Clarigen [testing quick start](https://www.clarigen.dev/docs/unit-tests/quick-start), [current implementation](https://github.com/hstove/clarigen/tree/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/clarigen-test), [init configuration](https://github.com/hstove/clarigen/blob/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/cli/scripts/init-config.toml).
