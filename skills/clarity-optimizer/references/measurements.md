# Optimizer measurements and source compaction

Cost data for choices in [clarity-optimizer](../../clarity-optimizer/SKILL.md), and the opt-in compaction procedure.

## Filtering fixture

Data for [filtering with per-call context](../../clarity-optimizer/SKILL.md#filtering-with-per-call-context).

- Fixture: 350 `(buff 32)` items, list bound 1,000, all retained:

| Epoch / implementation | Runtime | Reads | Read bytes | Writes | Write bytes |
|---|---:|---:|---:|---:|---:|
| 2.4 / context-output fold | 105,362,039 | 3 | 1,646 | 0 | 0 |
| 2.4 / helper filter, including setup | 640,557 | 354 | 14,946 | 1 | 38 |
| 4.0 / context-output fold | 18,188,519 | 3 | 1,646 | 0 | 0 |
| 4.0 / helper filter, including setup | 172,649 | 354 | 14,946 | 1 | 38 |

- Distribution matters: when all 350 items are removed, the epoch 4.0 fold runtime falls to **500,633**; the filter still visits and reads all 350 items.
- Source examples: [Bitflow's context/result fold](https://github.com/BitflowFinance/bitflow-dlmm/blob/b4d3694c863fb737574b2830acaa33a02f399bc0/clarity/contracts/dlmm-swap-router-v-1-1.clar#L41-L51), [helper setup/filter](https://github.com/BitflowFinance/bitflow-dlmm/blob/b4d3694c863fb737574b2830acaa33a02f399bc0/clarity/contracts/dlmm-core-v-1-1.clar#L574-L576) and [predicate](https://github.com/BitflowFinance/bitflow-dlmm/blob/b4d3694c863fb737574b2830acaa33a02f399bc0/clarity/contracts/dlmm-core-v-1-1.clar#L2088-L2091).

## Measured examples

Epoch 4.0, Clarity 4 and 6; identical return values:

| Change | Source-byte delta | Runtime delta per later call | Read-byte delta |
|---|---:|---:|---:|
| Four indentation spaces → one tab | -3 | -3 | -3 |
| Append a comment | +1,003 | +1,003 | +1,003 |
| Retain 100 top-level initialization writes | +1,900 | +1,900 | +1,900 |

- Calling the padded callee twice doubles its size penalty. Initialization writes run only at deployment; later calls do not repeat them.
- These are synthetic call measurements, not deployment costs or capacity estimates.

## Extreme source compaction

- **Explicit opt-in only:** the user must ask for it, e.g. "extreme optimizations at the cost of readability". Do not recommend or apply it during ordinary optimization.
- Keep readable, documented authoring source and a reproducible release transform. Pack forms onto fewer lines and remove redundant indentation/newlines while preserving required token separators. Replacing one LF with one space saves no bytes.
- Use a Clarity-aware tokenizer: preserve literals, token boundaries and required notices. `;;` consumes the rest of its line; naively joining a comment line to code comments out that code. Retain its terminating newline or remove the comment deliberately, subject to notice requirements.
- Compile and test the exact compacted artifact for the target epoch/version; compare behavior, ABI, all five costs and final bytes. Hash/sign only after the final transform. Savings depend on bytes actually removed; compaction does not reduce the function's logical work.
