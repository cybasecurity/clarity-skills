# Optimizer cost formulas

Where the effective formulas come from, how to extract them, and what deployed cost contracts can and cannot tell a contract. Per-function formulas: the generated [cost table](cost-table.md).

## Cost formulas and cost contracts

- Inspect the target release, not only `main`; compare the pins in the [reference baseline](../../clarity-optimizer/SKILL.md#reference-baseline) with the target release and inspect relevant upstream changes.
- Schedule by epoch (`default_cost_contract_for_epoch` in `clarity/src/vm/costs/mod.rs`): costs_3 through epoch 3.2, costs_4 for 3.3/3.4, costs_5 for 4.0/4.1. Mainnet and testnet are at epoch 4.0. For epochs ≤ 3.4 the boot `costs-N` contracts mirror these schedules (boot sources stop at `costs-4.clar`); from 4.0 the tracker uses native costs and SIP-044 disables cost voting, so [`costs_5.rs`](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/costs/costs_5.rs), the newest numbered schedule in the source baseline, is authoritative. It forwards many state/analysis functions to Costs4, which forwards to Costs3, so reading one file does not reveal all effective formulas; the generated [cost table](cost-table.md) resolves every delegated formula. An old contract executing in a new epoch can incur the new schedule.
- Function arguments named `n` may mean serialized bytes, argument count, or sequence length: follow the charge site before estimating.
- Extract formulas from a git checkout (output is JSON: commit, newest source schedule, epoch dispatch, recursive delegated formulas; not activation evidence or a transaction's cost):
  - `git clone https://github.com/stacks-network/stacks-core && git -C stacks-core checkout ccf31dc69cddb9a7125e286e733b24484b073133` (or your target node's release tag)
  - `python3 <optimizer>/scripts/inspect_costs.py ./stacks-core --schedule 5 --function cost_fetch_entry --function cost_load_contract --function cost_print` (`<optimizer>` is the skill's directory)
- A contract can call a deployed `costs-*.clar` read-only function to evaluate that schedule's formula for a supplied input (mainnet `SP000000000000000000002Q6VF78.costs-4`, testnet `ST000000000000000000002AMW42H.costs-4`). It does not expose accumulated cost, remaining budget or a `gasleft()` primitive, and does not execute the operation it names; the call, contract loading and arithmetic themselves consume budget, and the formula omits the rest of the transaction. Clarinet SDK 3.26.0 simnet rewrites mainnet boot contract principals in deployed contracts to the testnet address; on a live network, call that network's boot address.

```clarity
;; clarity 4
;; Historical Costs4 formula query, not measurement of this function.
(define-read-only (costs4-add-formula (argument-count uint))
	(contract-call? 'SP000000000000000000002Q6VF78.costs-4 cost_add argument-count))
```

- Costs4 `cost_add(n)` is `11*n + 125`; Costs5's is `(n >> 4) + 31` (147 versus 31 at `n=2`). Mainnet `.costs-4` `cost_add(u2)` returns runtime `u147`, other dimensions zero. The epoch 4.0 tracker loads no boot cost contract, and no `costs-5` contract exists: a still-callable historical contract does not track the active native schedule.
- For current in-contract estimates, maintain a deliberately versioned application formula only if needed, derived from the selected schedule and verified charge sites. Label it an estimate and account for upgrade drift; it cannot enforce the VM's remaining budget. For actual costs, use receipts or STXER traces.
- [STXER](https://stxer.xyz) and its [SDK](https://github.com/stxer/stxer-sdk) attribute costs to expressions/calls. Inclusive trace costs overlap; use exclusive/self costs when summing nodes.
- Sources: [costs-4.clar](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/stackslib/src/chainstate/stacks/boot/costs-4.clar), [Costs5](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/costs/costs_5.rs), [dispatch/boot loading](https://github.com/stacks-network/stacks-core/blob/01a60adcb6cdf38c74e1c9eb8a66e0520563c0f7/clarity/src/vm/costs/mod.rs), [SIP-044](https://github.com/stacksgov/sips/tree/642af6804dacc80455c3d49ef66b62bc4fb209aa/sips/sip-044).
