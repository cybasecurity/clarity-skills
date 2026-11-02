# Language lookup and study material

Detail for [exact language lookup](../SKILL.md#exact-language-lookup) in clarity:scholar.

## Exact language lookup

- Known VM-doc discrepancies (`functions.md` quotes the VM docs verbatim):
  - Docs say only the final `as-contract?`/`restrict-assets?` body expression must be non-response; the type checker rejects any response-typed body expression.
  - `restrict-assets?` docs say `(response A int)`; it returns `(response A uint)`.
  - `principal-of?` docs say fixed in 2.1; Clarity 1 contracts keep the testnet behavior.
- Check [syntax basics](https://book.clarity-lang.org/ch01-02-clarity-basics.html), [type syntax](https://docs.stacks.co/reference/clarity/types) and [Stacks functions](https://docs.stacks.co/reference/clarity/functions) when uncertain. For version-sensitive behavior, cross-check the [VM docs](https://github.com/stacks-network/stacks-core/blob/ccf31dc69cddb9a7125e286e733b24484b073133/clarity/src/vm/docs/mod.rs), implementation and tests.
- Record source revision; distinguish upcoming code from network activation.

## Deployed contracts as study material

- [boomcrypto/clarity-deployed-contracts](https://github.com/boomcrypto/clarity-deployed-contracts/tree/45a7af60288ae72eb36592a9c428e41034c04367) is a searchable archive of deployed Clarity source. Use it to discover contract layouts, idioms, native token wrappers, deployed trait implementations and integration examples.
- Search the `main` branch (mainnet); `testnet` is unmaintained. The archive can lag the chain, so a contract missing from it may still be deployed.
- Search by principal/function/trait, then retrieve the exact deployed source and language version from the target network. Compare against current VM semantics and epoch rules.
- Deployment does not imply audited, safe, maintained or idiomatic code; the archive contains arbitrary contracts and historical patterns.
- Read relevant files only; record archive revision, original principal and license/attribution before reusing source. Do not run repository scripts merely to inspect examples.
