---
name: clarity-deployment
description: "Deploy Clarity contracts to testnet or mainnet: Clarinet deployment plans, scripted releases, initialization calls, nonces and post-deploy checks. Use to deploy, publish or initialize contracts."
license: MIT
compatibility: "Clarinet deployment plans, or scripts with @stacks/transactions 7.6.0 on Node 22.18+; network access to the target network."
metadata:
  version: "1.0.0"
  baseline_date: "2026-11-02"
---

# Clarity Deployment

A release is complete only when it covers immutable source, deployment identity, dependency order, initialization, governance and operational verification.
- Use [protocols](../clarity-protocols/SKILL.md) for verified addresses/interfaces and [ecosystem](../clarity-ecosystem/SKILL.md) for composition; return here for deployment and initialization. For an adapter release, resolve external interfaces there and prepare the adapter's own deployment graph here.
- Do not redeploy external production protocols as if they were your dependencies to control. Resolve their deployed principals and required integration permissions.

## Key distinctions

- Publishing contracts is not complete protocol initialization. Unfinished initialization is not a complete release.
- A Clarinet deployment plan can include contract calls and is sufficient for straightforward publication and fixed initialization. Recommend a resumable script for anything more complex: state-dependent setup, external verification, multisig signatures, governance waits, checkpointed retries or transaction postconditions constructed in code. A script can supplement the plan with wiring calls or handle the whole release.
- A submitted transaction or nonce advance does not prove success. Reverted deployments can leave a name available for different code.
- Review test setup before reuse: signer thresholds, emergency paths, mock assets and oracle feeds must match the intended deployment.
- Multiple transactions in one block, or one plan batch, are not an atomic deployment bundle. If the protocol requires atomic initialization, implement one authenticated transaction or proposal and prove its budget fits.

## Release

For "deploy these N contracts":

1. `clarinet check`, then the test suite with coverage; state the line-coverage figure ([coverage report](../clarity-testing/SKILL.md#coverage-costs-and-properties)).
2. `clarinet deployments generate --testnet --medium-cost`; hand-edit the plan to add initialization `contract-call` steps; `clarinet deployments check`.
3. Review the plan: deployer, order, contract names, Clarity versions, fees.
4. Apply straightforward publication and initialization with `clarinet deployments apply --testnet -d --no-dashboard` (`-d` applies the reviewed file as is). For more complex releases or postconditions constructed in code, recommend a resumable script for wiring calls or the whole release; follow the [release script rules](#release-script-rules).
5. Verify: `/v2/contracts/source`, `/v2/contracts/interface`, read-only calls for initialized state, roles and balances ([verify the release](#verify-the-release)).
6. Repeat for mainnet with the same sources and plan content; save principals, txids and hashes.

- **Preparing a mainnet plan without the production key:** The scaffold's `settings/Mainnet.toml` holds a placeholder mnemonic, so `clarinet deployments generate --mainnet --medium-cost` fails ("invalid word count"). For a reviewable plan, generate it with a throwaway mnemonic that is never funded (for example the public devnet one), set every `expected-sender` to the real deployer address, put the placeholder back in `settings/Mainnet.toml`, and commit the plan, plus the release steps file and script if used. Every role principal (admin, keeper, guardian, treasury) is a literal address from the release configuration; never use a devnet or throwaway account for a role, because their keys are public. At release, regenerate with the real (encrypted) mnemonic, check that the diff shows only your added steps and fees, answer `n` to keep the reviewed plan, and apply it with `-d`.
- Establish network, deployer/signer mechanism, Clarity/epoch support, contract names, source revisions and intended final authority first.
- Separate prepare, sign, broadcast, confirm and verify stages. Prepare a concrete release artifact before external writes; act within the user's existing deployment authorization.
- Rehearse the exact graph and initialization through public calls with the project's tests (Clarigen by default, see [testing](../clarity-testing/SKILL.md)) and an appropriate devnet/pinned simulation; reuse the reviewed plan content and source hashes from the testnet rehearsal and regenerate only network-specific fields.
- Maintain one authored logic set; use [explicit environment bindings](../clarity-testing/SKILL.md#dependencies-and-fixtures) for mock tests and reviewed production artifacts. Do not deploy a manually maintained testing copy.

## Clarinet plans

```sh
clarinet check
clarinet deployments generate --testnet --medium-cost   # --low-cost|--medium-cost|--high-cost|--manual-cost is required; the first three query the network for fees
clarinet deployments check
# Review deployments/default.testnet-plan.yaml; hand-edit it to add initialization contract-call steps.
# This broadcasts. -d applies exactly the reviewed file and skips the Y/n prompt:
clarinet deployments apply --testnet --use-on-disk-deployment-plan --no-dashboard
```

- Without `-d`, `apply` recomputes the plan from the manifest. If it differs from the file you reviewed, it prints a diff and asks `Overwrite? [Y/n]` (Enter means yes), then `Continue [Y/n]?` (Enter means yes). `-c` overwrites with the recomputed plan without asking. `generate` also asks before replacing a changed existing plan, so hand-edit only after the last `generate`.
- `--no-dashboard` prints status lines instead of the terminal UI (use it in CI and agent shells). `-p path/to/plan.yaml` applies a custom plan; it cannot be combined with `--testnet`/`--mainnet`.
- The deployer comes from `settings/Testnet.toml` or `settings/Mainnet.toml` (`[accounts.deployer]`, gitignored by `clarinet new`). Run `clarinet deployments encrypt` (prompts for mnemonic and password, `--strength` basic|medium|high|extreme) and paste the printed `encrypted_mnemonic_<strength> = "..."` line instead of a plaintext `mnemonic`.
- Use `--mainnet` only for the intended mainnet release.
- Step types: `contract-publish`, `contract-call`, `requirement-publish` (remapped dependency) and `emulated-*` (simnet only). Plan layout (from Clarinet's `counter` example) with one `contract-call` step: `parameters` are evaluated as Clarity expressions (literals as shown), and `cost` is its fee in micro-STX:

```yaml
# fragment: one contract-call step in a plan batch
plan:
  batches:
    - id: 1
      transactions:
        - transaction-type: contract-call
          contract-id: ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM.vault
          expected-sender: ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM
          method: initialize
          parameters:
            - u1000000
            - "'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM.treasury"
          cost: 5960
```

- Each batch is broadcast, then Clarinet waits for its inclusion before starting the next; neither batching nor order makes the group atomic. Plan transactions carry no postconditions (`Allow` mode), so send any step that moves assets from a script.
- Check deployer identities, exact Clarity versions, dependency remaps, contract names, fees, nonces and initialization calls.

Source: [Clarinet CLI](https://docs.stacks.co/reference/clarinet/cli-reference).

## Release script rules

A script for wiring calls (or a whole release) with a single-signature deployer and `@stacks/transactions` 7.6.0 follows these rules. Node 22.18+ runs a `.ts` script directly.

- **Ordered steps:** Keep the project's existing release format if it has one. Otherwise list steps in dependency order: traits first, then contracts, then wiring calls (owner handoffs, strategy registration, roles, caps), then the hand-over of setup authority. For example, a deploy step `{ "id", "deploy": name, "source": path relative to the steps file, "fee" }` and a call step `{ "id", "call": contract, "function", "args": [...], "fee", "verify": [{ "contract", "function", "args", "expect" }] }`. Arguments and expected values are Clarity literals as in plans, `{deployer}` is replaced by the deployer address, and every fee is a reviewed micro-STX amount.
- **Role principals** (admin, keeper, guardian, treasury) are literals from the release configuration, never devnet or test accounts, whose mnemonics are public.
- **Dry run without a key:** With only the deployer address the script reads the chain and prints what it would send, with source sha256 hashes.
- **Checkpoint every step** in a release record next to the steps file (for example `release.<network>.json`), written atomically (temporary file, then rename). It is the release record: txids and signed transactions, no keys. Commit it after the release; never commit the deployer key or an env file holding it. Never log the key; for mainnet prefer a signer service or wallet flow over environment keys.
- **Save the signed transaction and txid before broadcasting:** A lost response or a pending transaction is resolved by waiting on that txid; never re-sign a step that has a saved txid. A polling timeout is unknown status, never permission to re-sign.
- **Explicit nonces:** After resumed steps are confirmed, read `next_nonce` once from `GET /extended/v3/principals/{deployer}/nonces` (it counts mempool transactions) and increment it per broadcast step. Stop if that read fails or `mempool.last_nonce` is not null: a new nonce after a pending transaction can let both run. Not `fetchNonce`: 7.6.0 reads the deprecated v1 route and on any error silently falls back to `/v2/accounts`, whose nonce ignores pending transactions.
- **Retries only where the request was not processed:** 429 for every request, plus 500/502/503/504 for reads (GETs and `call-read`). Honor `retry-after`, otherwise back off exponentially, and bound the attempts. Never retry a broadcast on a 5xx.
- **Stop on any non-success status:** `broadcastTransaction` returns `{ txid }` on acceptance and `{ error, reason, txid }` on rejection (for example `BadNonce`, fee too low): remove that step's checkpoint entry (this transaction used no nonce), fix the cause and rerun. Poll `GET /extended/v3/transactions/0x{txid}`: `success` with a `block` is done; `abort_by_response`, `abort_by_post_condition` or `problematic_skipped` (nonce used, payload not run) stops the run and the entry keeps the txid, so a rerun stops again without resending. A 404 means not indexed yet, dropped or replaced. If it lasts, read the v3 nonces, then the txid again: if `last_confirmed_nonce` or `mempool.last_nonce` has reached the step's nonce, another transaction used it or is pending at or after it, so stop; otherwise rebroadcast the saved bytes, a few times at most (same txid, so it still runs at most once). Delete the entry only once you have decided to send a new transaction; to replace a pending one, re-sign at its nonce with a higher fee.
- **Read-only checks after every step that describe its whole effect**, for example `get-owner` returning `(some '{deployer}.vault)`. If they already hold before a call step (for example after a lost checkpoint), record the step instead of sending it. A read on a contract that does not exist yet (`NoSuchContract`) counts as not holding.
- **Refuse a deployed name with different source:** Before a deploy step, fetch `/v2/contracts/source/{address}/{name}?proof=0`: same sha256 means record it as already deployed; different source means stop, because contract names cannot be reused. This also lets you publish with the Clarinet plan (same deployer) and run the script for the wiring only; omit deploy steps for sources Clarinet [rewrote](#verify-the-release).
- **Never publish `#[env(simnet)]` code:** Clarinet strips it before publishing, but a script sends the file as is. Refuse such a source, or publish it with the plan.
- **`PostConditionMode.Deny` with exact postconditions** for steps that move assets. An empty list makes any step that moves an asset, the deployer's or a contract's (including top-level code during a deploy), abort on chain; add exact conditions for steps that seed liquidity or fund contracts.
- **Mainnet guard:** Nothing is broadcast on mainnet unless an explicit confirmation (for example `CONFIRM_MAINNET`) equals the deployer address.
- Validate `clarityVersion` (1-6 at this baseline) and pass it to the deploy builder.
- API bases: devnet `http://localhost:3999`, testnet `https://api.testnet.hiro.so`, mainnet `https://api.hiro.so`. Rehearse on devnet (key from the `# secret_key:` comment of the deployer in `settings/Devnet.toml`), then testnet, then mainnet.
- Steps are separate transactions and the sequence is not atomic: anyone can call a public function between your steps. Wiring that must happen right after deployment belongs in the deploying contract's top-level code or behind an owner check, with the deployer as the initial owner.
- Single-signature deployer only. For a multisig or governed deployer, or governed initialization that waits on signers or a timelock (persist the proposal ID), use [governance](../clarity-governance/SKILL.md).
- Read [references/scripts-and-builders.md](references/scripts-and-builders.md#sign-checkpoint-then-broadcast) for a fragment that signs, checkpoints and broadcasts one call step in that order, and when extending the script for multisig, sponsorship or governance waits ([extended releases](references/scripts-and-builders.md#extended-multisig-or-governed-releases)).

## Transaction builders

- `@stacks/transactions` 7.6.0: `ClarityVersion.Clarity5` exists from 7.4.0 and `Clarity6` from 7.5.0 (7.3.1 stops at Clarity4). Keep one deduped copy (`npm ls @stacks/transactions`, `overrides` if needed).
- `makeContractDeploy` and `makeUnsignedContractDeploy` **pin Clarity 4 when `clarityVersion` is omitted**; pass the intended version. Epoch 4.1 (unscheduled) will reject any deploy that pins a Clarity version, so keep the version a release-config input and re-check it before a post-4.1 release.
- Set fee and nonce explicitly instead of relying on mutable automatic defaults during signing.
- Preparing unsigned transactions needs no private key: `publicKey`, source file and contract name come from the release configuration. Signing and broadcasting are later steps of the user's release; never log private keys or commit credentials.
- Read [references/scripts-and-builders.md](references/scripts-and-builders.md#unsigned-deployment-for-review) when preparing an unsigned deployment for review: a fragment that pins the Clarity version and writes the serialized transaction and source hash.
- Native multisig: `publicKeys`, `numSignatures`, the selected signing mode and the verified address instead of `publicKey`. Nonces are per originating principal, including native multisig; account for sponsor authorization separately.
- Build initialization calls with `makeUnsignedContractCall` and exact serialized arguments from the verified ABI or generated clients; supply postconditions for any initialization funding.
- Preserve exact source bytes and principal substitutions. Do not blindly replace addresses inside signed domains or authorization checks.
- For browser or Ledger signing, read [wallet compatibility](../clarity-wallets/SKILL.md): inspect serialized payload/version, transaction size and device/app support. Check [historical payload workarounds](../clarity-wallets/references/ledger.md#versioned-deployment-and-multisig-failures) before reuse: changing the payload requires new signatures and can change the deployed language.

Source: [transaction builders](https://github.com/stx-labs/stacks.js/blob/6101c99efe5a9616ce7e16cef68e28fd10676e7e/packages/transactions/src/builders.ts).

## Deployment-time execution

- Top-level expressions and constant initializers execute once at deployment. `define-constant` can call local or deployed functions, including side effects; `define-data-var` evaluates its initial value at deployment. Constants remain fixed when external state later changes.
- Function definitions register bodies; those bodies execute only when called. A later call loads the deployed contract; it does not repeat the top-level expressions.
- At top level `tx-sender` and `contract-caller` are the deployer; trace subsequent cross-contract calls and context changes from the deployer normally, and include deployment-time outflows in postconditions.

### Definition dependencies determine order

- Clarity dependency-sorts top-level definitions: forward references work, cycles fail analysis, and textual order does not fix the order of stateful initializers. Function placement alone does not schedule execution. Cross-contract dependencies must already exist on the target network.
- Avoid distributing ordered setup across side-effecting constants: keep dependent effects in one explicit `begin`/initializer and assert the resulting state.

### Failures must actually abort

- A top-level `(err ...)` does not abort deployment, and a constant may retain an `err` response while deployment succeeds. Wrap mandatory setup calls in `unwrap-panic` and verify initialized state (a lost dead-share mint reopens share inflation).
- A runtime failure (for example `unwrap-panic` on a mandatory response) aborts deployment and rolls back its nested effects; test both contract absence and dependency state.
- Distinguish failed publication from successful publication with incomplete setup. Verify initialized state, not only the deployment transaction status.

### Keep recurring costs in view

- Deployment-only code stays in the immutable source and is charged on later loads. [Source-size guidance](../clarity-optimizer/SKILL.md#source-size-and-recurring-load-costs) explains runtime/read-byte charges, formatting and measured examples.
- Large setup is valid when it fits [resource limits](../clarity-epochs/SKILL.md#resource-limits). Check serialized transaction size, analysis, runtime, reads/writes and memory separately.
- Prefer small atomic top-level setup when appropriate. For bulky registries or orchestration, prefer bounded authenticated initialization calls from a script or setup/proposal contract; guard initialization authority, allowed progress and finalization, and block normal operations until setup completes.
- Separate transactions lose atomicity, and calls made from a setup contract see it as `contract-caller`, not the deployer.

Sources: [definition sorter](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/ast/definition_sorter/mod.rs), [top-level evaluator](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/mod.rs), [constant initializer](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/functions/define.rs), [initialization transaction](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/contexts.rs).

## Initialization

- Derive the graph from deployment-time calls, trait/static dependencies, initialization functions and the approved release configuration. Publish required traits/dependencies before contracts that reference them. A principal literal passed as a trait argument is also a dependency, even without `contract-call?`; a principal used only as data is not.
- For a dependency cycle, use authenticated one-time post-deployment bindings; test initialization and rebinding refusal.
- Regenerate the simnet deployment plan after dependency-graph changes; a preserved old plan can keep an invalid order.
- Add only the target's required steps (governance, registries, assets/oracles, seed liquidity, integration permissions) and set members, thresholds, timelocks, feeds and funding explicitly; review any value copied from local tests.
- Calling `contract.getImpl()` only constructs a Clarigen call object. Use `rov`/`rovOk` in tests or a real read-only client in scripts to execute verification. A local test helper does not establish a production signing/broadcast workflow.
- Confirm every dependency's successful canonical deployment before dependent steps; resume by checking chain state, not by re-signing. Re-check when a reorg invalidates a dependency or confirmation; do not roll back committed independent transactions by deleting checkpoints.
- Read the [protocol registry](../clarity-protocols/references/addresses.md) and its [freshness rules](../clarity-protocols/SKILL.md#addresses-and-freshness) (live verification once evidence is 30 days old). Verify live addresses/ABIs, mutable roles, traits and remaps before signing; capture source/configuration hashes.
- For upgrades, use [upgrade architecture](../clarity-upgrades/SKILL.md) and its [release plan rules](../clarity-upgrades/SKILL.md#release-plan); prepare timelocked activation, preserve state/custody/pending claims, and verify old-role retirement. Publishing replacement code does not activate or migrate it.
- Read [references/examples.md](references/examples.md#initialization-examples) when adapting ExecutorDAO, Zest or Granite deployments or looking for an initialization pattern; their choices are examples, not default dependencies or authority settings.

## Verify the release

- Require a successful canonical receipt for each step: `GET /extended/v3/transactions/0x{txid}` with `status: "success"` and a `block`, and for a deploy the intended `smart_contract.contract_id` and `smart_contract.clarity_version`. v3 returns the canonical mined record or a pending one and has no `canonical` flag; a reorg can return it to pending or move it to another block, so re-read it before you report. API acceptance is not execution success.
- Capture the deployed source and ABI and compare hashes. Clarinet strips `#[env(simnet)]` code before publishing and, on devnet and testnet, rewrites mainnet boot, sBTC and requirement contract IDs; the two may differ only by those changes.
- Confirm registry-selected implementations, admin/owner/executor, multisig membership/threshold, timelocks and emergency roles.
- Verify native asset identity and spendable funds, pool/token order, share beneficiaries, integration approvals and pause/cap/fee settings. Assert initial reserves/minimum shares; use [null-principal shares](../clarity-assets/SKILL.md#supply-preserving-retirement-null-principal) for a permanent supply floor.
- Remove temporary setup authority only through the intended transition and verify the final controller can act.
- Report network, source revision, deployed principals, transaction IDs, state/config checks and pending governance/timelock actions.
- [System addresses](../clarity-system-integration/references/addresses.md), [API evidence](../clarity-apis/references/endpoints.md#verify-the-chain-and-deployment), [versions](../clarity-epochs/SKILL.md): use only as needed.

## Reference baseline

Examples use Clarity 4+ syntax unless marked, checked on epoch 4.0. Source links in this skill use these pins; links into sibling skills use their owner's `SKILL.md`.

- `stacks-core`: [ccf31dc69c](https://github.com/stacks-network/stacks-core/tree/ccf31dc69cddb9a7125e286e733b24484b073133).
- `executor-dao`: [4676718828](https://github.com/MarvinJanssen/executor-dao/tree/4676718828455a694a6593d251cb2e968f346c8c).
- `stacks-core-targeted`: [01a60adcb6](https://github.com/stacks-network/stacks-core/tree/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7).
- `granite`: [2d44a2df94](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b).
- `stacks-blockchain-api`: [ee0c0ac5be](https://github.com/hirosystems/stacks-blockchain-api/tree/ee0c0ac5bee51b206c67e83e581fab457c34a622).
- `stacks-js-release`: [6101c99efe](https://github.com/stx-labs/stacks.js/tree/6101c99efe5a9616ce7e16cef68e28fd10676e7e).
- `zest-v2`: [f2fce52672](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324).
