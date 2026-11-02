# Troubleshooting

Known failures of the pinned toolchain; first follow [troubleshoot against both projects](../SKILL.md#troubleshoot-against-both-projects).

### Stop Clarity prints flooding test output

In `Clarinet.toml`, add or update the existing `[repl]` table (values `none`, `project-only` default, `all`), then restart/reinitialize the session:

```toml
[repl]
log_print_events = "none"
```

- On SDK/WASM 3.26.0 this suppresses the Clarity print logger without changing returned values or receipt events.
- The default `"project-only"` excludes certain boot/sBTC issuers, not every external dependency.
- The logger uses JS `console.log` in WASM, so read-only and later-reverted prints can appear on stdout even though no corresponding receipt event survives. Console output is not proof of a committed event.
- Runtime failures still emit diagnostics/traces on stderr; traces may include executed prints. Vitest `test: { silent: 'passed-only' }` in the existing config hides passing tests' console output; `silent: true` hides failing-test output as well. These are runner settings, not `initSimnet` options ([Vitest silent](https://vitest.dev/config/silent)).
- No console monkey-patching is needed. Keep event assertions on receipts ([events](../SKILL.md#events-and-runtime-failures)).

Sources: [REPL settings](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarity-repl/src/repl/settings.rs), [logger](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarity-repl/src/repl/hooks/logger.rs), [stdout/stderr bridge](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarity-repl/src/uprint.rs).

### Errors from a bad trait argument

- SDK 3.26.0 names the contract you called, not the bad argument, in two cases: a trait argument naming a contract that does not exist gives `Contract '<called contract>' does not exist`, and one whose matching function is `define-private` gives `Method '<called function>' does not exist on contract '<called contract>'`. Check the argument's deployment and visibility before debugging the called contract.
- Other failures name the trait: a missing function or wrong argument types give `RuntimeCheck(BadTraitImplementation("<trait>", "<function>"))`, a returned value that does not fit the trait gives `ReturnTypesMustMatch`, and a standard principal gives `TypeValueError(CallableType(Trait(...)))`.
- A mock passed as a trait argument needs only the functions the test calls, because simnet calls skip mempool admission. A node's mempool rejects the same call unless the mock implements the whole trait (`BadFunctionArgument`), and passing does not show that the real contract implements the trait ([trait arguments](../../ecosystem/SKILL.md#key-distinctions)). The mempool checks only the first element of any list, so a partial mock later in a list passes admission and fails only when a missing function is called.

### Windows manifest paths

- On Windows, SDK/WASM **3.26.0** still joins a drive-letter absolute manifest path to `cwd`, producing paths such as `D:/project/D:/project/Clarinet.toml`, in both `initSession` and `generateDeploymentPlan`. [Clarinet #1634 and the Clarigen diagnosis](https://github.com/stx-labs/clarinet/issues/1634#issuecomment-4114124173) and [#2199](https://github.com/stx-labs/clarinet/issues/2199) remain open.
- Symptoms include duplicated drive paths and `ENOENT`; the older report also contains `unable to mutate url`. Diagnose the actual path before changing contract code.
- For direct SDK calls, run from the project directory and pass `./Clarinet.toml`. For an arbitrary manifest, convert it to a relative path **before** the Node-to-WASM call:

```ts
// id: manifest-path
import path from 'node:path';

export function sdkManifestPath(manifest: string, cwd = process.cwd(), paths = path): string {
  const relative = paths.relative(cwd, paths.resolve(cwd, manifest));
  if (paths.isAbsolute(relative)) {
    throw new Error('Run from the manifest drive/share');
  }
  return relative.split(paths.sep).join('/');
}
```

- Pass `sdkManifestPath(manifest)` to `initSimnet`. An SDK adapter/patch must normalize both initialization and deployment-plan paths against the same `cwd`.
- Replacing backslashes alone does not fix an absolute drive path. Different Windows drives can leave `path.relative` absolute; change the shell's working directory first. Keep `cwd` stable during parallel tests.
- **Clarigen CLI 4.1.7 resolves its configured manifest to an absolute path:** A relative `Clarigen.toml` setting alone therefore does not avoid this bug.
- For that CLI, use WSL2 with Linux Node/dependencies, or a version-pinned package-manager patch at the SDK boundary. Commit the patch and lockfile; test generation and execution, then remove it after verifying an upstream fix. Do not rely on an untracked `node_modules` edit.
- Recheck [Clarinet issues](https://github.com/stx-labs/clarinet/issues) and [Clarigen issues](https://github.com/hstove/clarigen/issues) for the installed versions. These reports establish specific path failures, not that every Windows workflow fails.

### Minimal diagnostic record

- Record OS/shell, native Windows versus WSL, `node --version`, `clarinet --version`, and resolved SDK/WASM/Clarigen versions from the lockfile.
- Record `cwd`, the configured manifest and the actual path passed to the SDK. Distinguish generation, session startup and contract execution failures.
- Reproduce in a small project with the same package versions and language/epoch. A native CLI success does not prove the WASM SDK handles paths identically.
- For execution failures, distinguish a Clarity `err` from an SDK/runtime exception; see [runtime failures](helpers-and-assertions.md#separate-contract-errors-from-runtime-failures) and [simulator traps](../../environments/SKILL.md#simulator-traps).

### Numeric tuple keys

- At this skill's Clarigen baseline, ABI tuple key `min-mid-1` generates the TypeScript key `minMid1`, but the runtime encoder cannot find that generated key. Type generation alone does not prove encoding works.
- Pack with `Cl.tuple({'min-mid-1': Cl.uint(1n)})`; for a fixed external ABI, preserve its exact key and pack explicitly. Prefer word suffixes in new ABIs.
- Exercise the generated builder against the VM and recheck the installed version before applying a workaround. See the [tuple encoder](https://github.com/hstove/clarigen/blob/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/core/src/clarity-types.ts).

Sources: [SDK entry points](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk/node/src/index.ts), [WASM session/plan handling](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk-wasm/src/core.rs), [path resolution](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-files/src/paths.rs), [Clarigen configuration](https://github.com/hstove/clarigen/blob/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/cli/src/config.ts).
