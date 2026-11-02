# Helpers and assertions

Complete helpers for the rules in [events and runtime failures](../SKILL.md#events-and-runtime-failures), and the raw SDK alternative to [typed tests](../SKILL.md#write-typed-tests).

### Event and runtime-failure helpers

#### Assert event provenance and payload

This helper preserves every matching event in receipt order and checks emitter, topic and payload shape:

```ts
// id: deposit-events
import { CoreNodeEventType, cvToValue } from '@clarigen/core';
import { filterEvents, type CoreNodeEvent } from '@clarigen/test';

export function depositEvents(events: CoreNodeEvent[], emitter: string) {
  return filterEvents(events, CoreNodeEventType.ContractEvent)
    .filter(({ data }) => data.contract_identifier === emitter && data.topic === 'print')
    .map(({ data }) => cvToValue<unknown>(data.value))
    .filter((value): value is { action: 'deposit'; amount: bigint } =>
      typeof value === 'object' && value !== null &&
      'action' in value && value.action === 'deposit' &&
      'amount' in value && typeof value.amount === 'bigint');
}
```

- Call it with `ledger.identifier` as the emitter (not a bare contract name) and assert the exact count, order and amounts of the returned array.

#### Separate contract errors from runtime failures

```ts
// id: capture-runtime-error
export function captureRuntimeError(run: () => unknown): string {
  try { run(); } catch (error) { return String(error); }
  throw new Error('Expected a runtime exception');
}
```

```ts
// Assumes a public function writeThenSubtract that writes state and then underflows on `amount - 1`.
const before = rov(ledger.getBalance(), alice);
const message = captureRuntimeError(() => txOk(ledger.writeThenSubtract(0n), alice));
expect(message).toMatch(/ArithmeticUnderflow/);
expect(rov(ledger.getBalance(), alice)).toBe(before);
```

- `String(error)` captures SDK values thrown as strings as well as JS `Error`s. Keep assertions out of the callback: one failing inside it would be returned as the expected VM failure.

### Raw SDK escape hatch

Use direct SDK calls when testing dynamically deployed contracts, raw Clarity values or a wrapper gap. Prefer typed calls for ordinary project calls. Post-condition options on raw calls: [post-conditions in tests](../SKILL.md#post-conditions-in-tests).

```ts
import { describe, expect, it } from 'vitest';
import { Cl } from '@stacks/transactions';

const accounts = simnet.getAccounts();          // `simnet` is a global in the clarinet vitest env
const deployer = accounts.get('deployer')!;
const alice = accounts.get('wallet_1')!;

describe('vault', () => {
  it('rejects a withdrawal larger than the deposit', () => {
    simnet.callPublicFn('vault', 'deposit', [Cl.uint(100)], alice);
    const r = simnet.callPublicFn('vault', 'withdraw', [Cl.uint(101)], alice);
    expect(r.result).toBeErr(Cl.uint(1002));
    expect(r.events).toHaveLength(0);           // err => no events, no state
  });
});
```

- Operations within one block share its timestamp; test same-block and long-gap cases ([blocks and clocks](../SKILL.md#blocks-clocks-and-same-block-batches)).

Sources: [Clarigen test helpers](https://github.com/hstove/clarigen/tree/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/clarigen-test/src), [decoding](https://github.com/hstove/clarigen/blob/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/core/src/clarity-types.ts), [error extraction](https://github.com/hstove/clarigen/blob/23dd026fe47ba46513b255aeb3557d0b0f5368bc/packages/core/src/utils.ts), [Vitest lifecycle](https://github.com/stx-labs/clarinet/blob/0b59577fdd3c073a4132aa59348029604a2560e2/components/clarinet-sdk/node/vitest-helpers/src/vitest.setup.ts).
