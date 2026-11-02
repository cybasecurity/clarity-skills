# Initialization examples

- Proposal/executor architecture source: [Marvin Janssen's ExecutorDAO](https://github.com/MarvinJanssen/executor-dao). Its core `construct(proposal)` runs a bootstrap proposal under the initial executive's authority; [EDP000](https://github.com/MarvinJanssen/executor-dao/blob/4676718828455a694a6593d251cb2e968f346c8c/contracts/proposals/edp000-bootstrap.clar) configures extensions, members and initial tokens. Its sample principals and legacy tooling are not production defaults.
- Zest adapts this pattern with its own initialization APIs and governance policy; do not interchange the two deployment sequences or proposal traits. Its setup sequence is:
  - Deploy traits and immutable dependencies before contracts that reference them.
  - Deploy DAO multisig/executor, registries, vaults, market and proposal contracts according to actual dependencies.
  - Initialize the multisig with the intended members/threshold and bind the executor to it.
  - Register assets, oracle routing and risk configuration through governance.
  - Fund minimum liquidity with real authorized asset transfers.
  - Initialize vaults and market-vault permissions; verify the chosen market is authorized.
  - Verify state through executed read-only calls and observable balances/events.
- Zest's TypeScript setup helpers prepare local environments, not production signing and broadcast. They use threshold one, dummy feed identifiers and mock `mint` calls. Compare those fixture values with the target's approved signer policy, feeds and actual assets; do not infer production settings from tests.
- Granite's [deployment plans](https://github.com/GraniteProtocol/core-v1/tree/2d44a2df94a5bebe80029efa5ed03f720b255f4b/deployments) show multiple markets/deployers and upgrade generations; a plan named mainnet is not enough to select the active deployment.

Sources: [Zest setup helpers](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/local-testing/tests/setup/helpers.ts), [Zest protocol setup tests](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/local-testing/tests/setup/protocol-init.test.ts), [mainnet v0-init](https://github.com/Zest-Protocol/zest-v2-contracts/blob/f2fce52672bf5bca2c082a132b7ea6edd769b324/mainnet/contracts/proposals/mainnet/v0-init.clar).
