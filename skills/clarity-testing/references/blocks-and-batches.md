# Blocks, clocks and same-block batches

The full rules and examples; the SKILL.md keeps the main rules.

Examples assume the Clarinet test environment, generated `project`/`accounts`, and a public `ledger.deposit(uint)` / `withdraw(uint)` fixture. Use the same `simnet` object with SDK and Clarigen calls.

- Later `stacks-block-height` or same-tenure ordering: `simnet.mineEmptyStacksBlocks(n)` (epoch 3.0+). PoX cycle, `burn-block-height` or Bitcoin delay: `simnet.mineEmptyBurnBlocks(n)`; it also advances the simulated Stacks tip, so measure both heights when their relationship matters. `mineEmptyStacksBlock()`/`mineEmptyBurnBlock()` mine one.
- `mineEmptyBlock()` / `mineEmptyBlocks()` **are aliases for burn-block mining** in SDK 3.26.0 ([SDK WASM core](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk-wasm/src/core.rs)). Do not use them when the clock matters.
- Read starting heights after setup; never assume height 1. On a fork the burn and Stacks clocks start at the forked block's times, so a burn block's time jump can differ from plain simnet: check the resulting window explicitly. A fixed block count is not elapsed seconds: read the contract's clock before and after and hit the actual boundary (one before, at, one after; PoX boundaries from the target's cycle parameters).
- Stacks blocks exercise same-block/order constraints; burn blocks exercise PoX cycles and Bitcoin-height delays. Never turn a protocol's average-cadence comment into an exact duration.

```ts
const stacksBefore = simnet.stacksBlockHeight;
const burnBefore = simnet.burnBlockHeight;

simnet.mineEmptyStacksBlocks(10);
expect(simnet.stacksBlockHeight).toBe(stacksBefore + 10);
expect(simnet.burnBlockHeight).toBe(burnBefore);

simnet.mineEmptyBurnBlocks(2);
expect(simnet.burnBlockHeight).toBe(burnBefore + 2);
```

- Advance to a target burn height, rejecting past targets; use the corresponding Stacks-height helper for guards based on `stacks-block-height`:

```ts
function advanceBurnTo(target: number) {
  const delta = target - simnet.burnBlockHeight;
  if (!Number.isSafeInteger(delta) || delta < 0) throw new Error('Invalid target');
  if (delta > 0) simnet.mineEmptyBurnBlocks(delta);
}
```

## Several transactions in one block

- `simnet.mineBlock([tx.callPublicFn(contract, fn, args, sender), ...])` with `import { tx } from '@stacks/clarinet-sdk'`. Ordinary `callPublicFn`/`txOk` calls each mine their own block, even in a loop.
- In a batch, receipts follow input order and later transactions see earlier committed effects. Each transaction has its own rollback: a returned `err` in one does not revert the others. The batch is one block, **not one atomic transaction**; atomic composition needs one public entry point that calls the legs.

```ts
import { tx } from '@stacks/clarinet-sdk';
import { Cl } from '@stacks/transactions';

const alice = simnet.getAccounts().get('wallet_1')!;
const before = simnet.stacksBlockHeight;
const receipts = simnet.mineBlock([
  tx.callPublicFn('ledger', 'deposit', [Cl.uint(100n)], alice),
  tx.callPublicFn('ledger', 'withdraw', [Cl.uint(101n)], alice),
  tx.callPublicFn('ledger', 'withdraw', [Cl.uint(20n)], alice),
]);
expect(simnet.stacksBlockHeight).toBe(before + 1);
expect(receipts[0].result).toBeOk(Cl.uint(100n));
expect(receipts[1].result).toBeErr(Cl.uint(1002n));
expect(receipts[2].result).toBeOk(Cl.uint(80n));
```

- The `err` in the second entry neither reverts the first deposit nor prevents the valid third withdrawal.
- A runtime exception (including a violated post-condition) throws out of `mineBlock` in SDK 3.26.0: earlier entries stay committed, later ones are skipped and the block is still mined. Detect what committed from state, not receipts. Do not infer real-node mining from this loop ([environment fidelity](../../clarity-environments/SKILL.md)).

```ts
// captureRuntimeError from helpers-and-assertions.md fails the test if nothing throws
const h = simnet.stacksBlockHeight;
const message = captureRuntimeError(() => simnet.mineBlock([ /* tx1, tx2 (throws), tx3 */ ]));
expect(message).toMatch(/ArithmeticUnderflow/); // the intended category only
expect(simnet.stacksBlockHeight).toBe(h + 1);   // block was mined
// tx1's effects are present, tx3's are not: assert balances/storage
```

- Clarigen call objects carry `contractAddress`, `contractName`, `function { name, access }` and `functionArgs`; pass them to `tx.callPublicFn`. This bridge is a local helper, not a Clarigen batching API, and its receipts are raw SDK receipts:

```ts
// fragment: Clarigen calls in one block (tx from @stacks/clarinet-sdk)
type PublicCall = { contractAddress: string; contractName: string;
  function: { name: string; access: string }; functionArgs: ClarityValue[] };
function inBlock(call: PublicCall, sender: string) {
  if (call.function.access !== 'public') throw new Error('Public call required');
  return tx.callPublicFn(`${call.contractAddress}.${call.contractName}`,
    call.function.name, call.functionArgs, sender);
}
const receipts = simnet.mineBlock([inBlock(ledger.deposit(100n), alice), inBlock(ledger.withdraw(20n), alice)]);
expect(receipts[1].result).toBeOk(Cl.uint(80n)); // raw receipt, not txOk-decoded
```

- Use batches for borrow then liquidation in the same versus the next block, sequential proposals, oracle-update ordering and first-depositor races. For a timing guard, first establish valid positions, permissions and oracle state, and assert the intended error so an unrelated earlier guard cannot make the test pass.
