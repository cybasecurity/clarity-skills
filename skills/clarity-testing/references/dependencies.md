# Dependencies and fixtures

The full rules; the SKILL.md keeps the main ones.

- Pin each dependency by repository revision and exact network principal: a pinned Git submodule or checkout for upstream source, declared requirements for deployed contracts, fetched caches out of version control. Call deployed dependencies through requirements instead of copying their code into protocol-owned contracts; when you embed upstream code (a math library, a token implementation), record its repository and revision.
- For each integration (Pyth submodule, deployed requirement), record the revision or principal, the manifest entry and the setup calls; verify the production instance separately.
- Keep one authored logic set. Prefer requirements, which keep mainnet principals in simnet, over per-network copies. If the project generates local/deployment variants, derive them from explicit principal bindings that preserve comments, strings, ABI and behavior; distinguish contract identities, authority principals and signed domains, and reject unconfigured principals before writing outputs. Never replace mainnet principals with an indiscriminate string replacement that also rewrites role checks or signed domains.
- Keep mock unit models (for example under `contracts/mock/`) out of integration manifests. Integration coverage executes unmodified requirements against pinned remote state with real custody/role assertions; mock success alone does not establish readiness.
- Clarinet requirements and deployment plans can fetch contracts, but a fetched source cache does not necessarily include the live state the scenario requires.
- Use a local fixture manifest for deterministic tests. Seed accounts, permissions, pools, balances and oracle signers deliberately and record deviations from production. Keep mock minting/admin access local.
- Review the generated plan, boot contracts, deployers, language versions and simulated contract IDs; regenerate after dependency-graph changes.
- For Pyth, use [signed fixtures](../../clarity-oracles/SKILL.md#signed-fixtures); mocks and older Core payloads do not establish Lazer compatibility.
- Repository examples:
  - [Granite's Pyth submodule](https://github.com/GraniteProtocol/core-v1/blob/2d44a2df94a5bebe80029efa5ed03f720b255f4b/.gitmodules): pin the dependency and reference its paths directly. Check out an existing pin with `git submodule update --init --recursive`; `--remote` changes the reviewed revision.
  - [Hermetica's manifest](https://github.com/hermetica-fi/hermetica-contracts/blob/5e13e431f69dd840fe297791fa2a73d9993a27e0/Clarinet.toml): deployed requirements plus pinned `repl.remote_data`. Its historical height is an example, not a current integration snapshot.
  - Neither pattern establishes current deposit availability, liquidity or permission. Assert those capabilities through the real public routes.

Sources: [Clarinet SDK](https://github.com/stx-labs/clarinet/tree/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk), [REPL settings](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarity-repl/src/repl/settings.rs).

### Protocol examples worth reading

| Source | Reusable technique | Adaptation needed |
|---|---|---|
| [Zest setup/helpers.ts](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/local-testing/tests/setup/helpers.ts) | One generated factory, shared actors, project error extraction, filtered events, ordered DAO/asset/vault initialization | Single signer, mock minting and dummy oracle data are local fixtures |
| [Zest oracle helpers](https://github.com/Zest-Protocol/zest-v2-contracts/tree/f2fce52672bf5bca2c082a132b7ea6edd769b324/local-testing/tests/setup/helpers) | Product-specific signed inputs and reusable vault operations | Match deployed parser and mainnet feed policy |
| [Stacking DAO test helpers](https://github.com/StackingDAO/stackingdao-smart-contracts/blob/125c73dc109988730156f4d0434ff01654480fc7/local-testing/tests/test-helpers.ts) | Advance to a target burn height | Reject past targets and use actual cycle parameters |
| [Stacking DAO PoX helpers](https://github.com/StackingDAO/stackingdao-smart-contracts/blob/125c73dc109988730156f4d0434ff01654480fc7/local-testing/tests/pox-5/pox-5-helpers.ts) | Explicit signer authorization, IDs, role setup and rewards | Test signer keys and role overrides are not production authority |
| [Bitflow DLMM tests/fuzzing](https://github.com/BitflowFinance/bitflow-dlmm/tree/b4d3694c863fb737574b2830acaa33a02f399bc0/clarity/fuzz) | Typed calls, actor balances, bin traversal and bounded state-machine actions | Preserve exact token/bin semantics and oracle assumptions |
| [Clarinet SDK tests](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk/node/tests/simnet-usage.test.ts) | Authoritative method/receipt examples | Read the implementation and installed version too; even repository tests may retain old defaults |
