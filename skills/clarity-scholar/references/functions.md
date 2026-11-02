# Clarity functions and keywords by version

<!-- generated-reference -->

Version ranges are the VM's own lookup tables (`clarity/src/vm/functions/mod.rs`, `variables.rs`); text is from `clarity/src/vm/docs/mod.rs`. A name outside its range does not exist for that contract's Clarity version: analysis fails on deploy.

`1–3` means available in Clarity 1 through 3 only. A contract keeps its declared Clarity version forever, but epoch-wide consensus changes (notices marked ⚠) can still change how old contracts execute. Re-check the live docs at https://docs.stacks.co/reference/clarity/functions when they disagree, and prefer this VM source.

## Removed or replaced names

| Name | Clarity | Use instead |
|---|---|---|
| `as-contract` | 1–3 | `as-contract?` with explicit allowances (Clarity 4+); `current-contract` for the contract's own principal |
| `at-block` | 1–4 | Nothing equivalent; existing callers throw from epoch 3.4 (see notice) |
| `block-height` | 1–2 | `stacks-block-height` (every Stacks block) or `tenure-height` (Clarity 3+); `burn-block-height` for Bitcoin |
| `get-block-info?` | 1–2 | `get-stacks-block-info?`, `get-tenure-info?` (Clarity 3+); `stacks-block-time` for the current block (Clarity 4+) |
| `with-stacking` | 4–5 | `with-staking` (Clarity 6+); `with-pox` is a separate no-amount allowance for position-changing PoX calls |

## Additions by version

- **Clarity 2**: `bit-and`, `bit-not`, `bit-or`, `bit-shift-left`, `bit-shift-right`, `bit-xor`, `buff-to-int-be`, `buff-to-int-le`, `buff-to-uint-be`, `buff-to-uint-le`, `chain-id`, `element-at?`, `from-consensus-buff?`, `get-burn-block-info?`, `index-of?`, `int-to-ascii`, `int-to-utf8`, `is-in-mainnet`, `is-standard`, `principal-construct?`, `principal-destruct?`, `replace-at?`, `slice?`, `string-to-int?`, `string-to-uint?`, `stx-account`, `stx-transfer-memo?`, `to-consensus-buff?`, `tx-sponsor?`
- **Clarity 3**: `get-stacks-block-info?`, `get-tenure-info?`, `stacks-block-height`, `tenure-height`
- **Clarity 4**: `as-contract?`, `contract-hash?`, `current-contract`, `restrict-assets?`, `secp256r1-verify`, `stacks-block-time`, `to-ascii?`, `with-all-assets-unsafe`, `with-ft`, `with-nft`, `with-stacking`, `with-stx`
- **Clarity 6**: `ed25519-verify`, `get-bitcoin-tx-output?`, `secp256k1-decompress?`, `verify-merkle-proof`, `with-pox`, `with-staking`

Clarity 2 added `element-at?` and `index-of?` as aliases; the Clarity 1 spellings still work.

## Notices from the VM documentation

- ℹ `as-contract?` (info): The previous version of `as-contract`, introduced in Clarity 1, has changed to `as-contract?` in Clarity 4, with several new security enhancements.
- ⚠ `at-block` (danger): As of Epoch 3.4, existing contracts using `at-block` will throw an error if called.
- ℹ `fold` (info): As of Epoch 4.1, the result type of `fold` covers both `initial_B` and the return type of `func`. Earlier epochs used the return type of `func` alone.
- ℹ `stacks-block-time` (info): This same timestamp can also be retrieved for previous blocks using `(get-stacks-block-info? time height)`, which exists since Clarity 3, but cannot be used for the current block.
- ℹ `tuple` (info): As of Epoch 4.1, tuples that must share one type, such as the two branches of `if`, the arguments of `is-eq` or the elements of a `list`, must have the same fields. Earlier epochs could drop fields that only one of the tuples had.
- ⚠ `tx-sender` (warning): Use caution when leveraging tx-sender, as based on the design, you can unintentionally introduce attack surface area. [Read more](https://www.setzeus.com/community-blog-posts/clarity-carefully-tx-sender).
- Additional security reading: [100proof's NFT callback analysis](https://100proof.org/a-questionable-design-choice.html). See [A01](../../clarity-security/references/patterns.md#a01-sender-authority-forwarded-through-an-attacker) for listing changes that asset postconditions do not prevent.

## Index

| Name | Kind | Clarity | Signature |
|---|---|---|---|
| `*` | function | 1+ | `(* i1 i2...)` |
| `+` | function | 1+ | `(+ i1 i2...)` |
| `-` | function | 1+ | `(- i1 i2...)` |
| `/` | function | 1+ | `(/ i1 i2...)` |
| `<` | function | 1+ | `(< i1 i2)` |
| `<=` | function | 1+ | `(<= i1 i2)` |
| `>` | function | 1+ | `(> i1 i2)` |
| `>=` | function | 1+ | `(>= i1 i2)` |
| `and` | function | 1+ | `(and b1 b2 ...)` |
| `append` | function | 1+ | `(append (list 1 2 3 4) 5)` |
| `as-contract` | function | 1–3 | `(as-contract expr)` |
| `as-contract?` | function | 4+ | `(as-contract? ((with-stx\|with-ft\|with-nft\|with-stacking\|with-staking\|with-pox)*) expr-body1 expr-body2 ... expr-body-last)` |
| `as-max-len?` | function | 1+ | `(as-max-len? sequence max_length)` |
| `asserts!` | function | 1+ | `(asserts! bool-expr thrown-value)` |
| `at-block` | function | 1–4 | `(at-block id-block-hash expr)` |
| `begin` | function | 1+ | `(begin expr1 expr2 expr3 ... expr-last)` |
| `bit-and` | function | 2+ | `(bit-and i1 i2...)` |
| `bit-not` | function | 2+ | `(bit-not i1)` |
| `bit-or` | function | 2+ | `(bit-or i1 i2...)` |
| `bit-shift-left` | function | 2+ | `(bit-shift-left i1 shamt)` |
| `bit-shift-right` | function | 2+ | `(bit-shift-right i1 shamt)` |
| `bit-xor` | function | 2+ | `(bit-xor i1 i2...)` |
| `block-height` | keyword | 1–2 | `block-height` |
| `buff-to-int-be` | function | 2+ | `(buff-to-int-be (buff 16))` |
| `buff-to-int-le` | function | 2+ | `(buff-to-int-le (buff 16))` |
| `buff-to-uint-be` | function | 2+ | `(buff-to-uint-be (buff 16))` |
| `buff-to-uint-le` | function | 2+ | `(buff-to-uint-le (buff 16))` |
| `burn-block-height` | keyword | 1+ | `burn-block-height` |
| `chain-id` | keyword | 2+ | `chain-id` |
| `concat` | function | 1+ | `(concat sequence1 sequence2 ...)` |
| `contract-call?` | function | 1+ | `(contract-call? .contract-name function-name arg0 arg1 ...)` |
| `contract-caller` | keyword | 1+ | `contract-caller` |
| `contract-hash?` | function | 4+ | `(contract-hash? contract)` |
| `contract-of` | function | 1+ | `(contract-of .contract-name)` |
| `current-contract` | keyword | 4+ | `current-contract` |
| `default-to` | function | 1+ | `(default-to default-value option-value)` |
| `define-constant` | definition | 1+ | `(define-constant name expression)` |
| `define-data-var` | definition | 1+ | `(define-data-var var-name type value)` |
| `define-fungible-token` | definition | 1+ | `(define-fungible-token token-name <total-supply>)` |
| `define-map` | definition | 1+ | `(define-map map-name key-type value-type)` |
| `define-non-fungible-token` | definition | 1+ | `(define-non-fungible-token asset-name asset-identifier-type)` |
| `define-private` | definition | 1+ | `(define-private (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` |
| `define-public` | definition | 1+ | `(define-public (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` |
| `define-read-only` | definition | 1+ | `(define-read-only (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` |
| `define-trait` | definition | 1+ | `(define-trait trait-name ((func1-name (arg1-type arg2-type ...) (return-type))))` |
| `ed25519-verify` | function | 6+ | `(ed25519-verify message signature public-key)` |
| `element-at` | function | 1+ | `(element-at? sequence index)` |
| `element-at?` | function | 2+ | `(element-at? sequence index)` |
| `err` | function | 1+ | `(err value)` |
| `false` | keyword | 1+ | `false` |
| `filter` | function | 1+ | `(filter func sequence)` |
| `fold` | function | 1+ | `(fold func sequence_A initial_B)` |
| `from-consensus-buff?` | function | 2+ | `(from-consensus-buff? type-signature buffer)` |
| `ft-burn?` | function | 1+ | `(ft-burn? token-name amount sender)` |
| `ft-get-balance` | function | 1+ | `(ft-get-balance token-name principal)` |
| `ft-get-supply` | function | 1+ | `(ft-get-supply token-name)` |
| `ft-mint?` | function | 1+ | `(ft-mint? token-name amount recipient)` |
| `ft-transfer?` | function | 1+ | `(ft-transfer? token-name amount sender recipient)` |
| `get` | function | 1+ | `(get key-name tuple)` |
| `get-bitcoin-tx-output?` | function | 6+ | `(get-bitcoin-tx-output? tx-bytes vout)` |
| `get-block-info?` | function | 1–2 | `(get-block-info? prop-name block-height)` |
| `get-burn-block-info?` | function | 2+ | `(get-burn-block-info? prop-name burn-block-height)` |
| `get-stacks-block-info?` | function | 3+ | `(get-stacks-block-info? prop-name stacks-block-height)` |
| `get-tenure-info?` | function | 3+ | `(get-tenure-info? prop-name stacks-block-height)` |
| `hash160` | function | 1+ | `(hash160 value)` |
| `if` | function | 1+ | `(if bool1 expr1 expr2)` |
| `impl-trait` | definition | 1+ | `(impl-trait trait-identifier)` |
| `index-of` | function | 1+ | `(index-of? sequence item)` |
| `index-of?` | function | 2+ | `(index-of? sequence item)` |
| `int-to-ascii` | function | 2+ | `(int-to-ascii (int\|uint))` |
| `int-to-utf8` | function | 2+ | `(int-to-utf8 (int\|uint))` |
| `is-eq` | function | 1+ | `(is-eq v1 v2...)` |
| `is-err` | function | 1+ | `(is-err value)` |
| `is-in-mainnet` | keyword | 2+ | `is-in-mainnet` |
| `is-in-regtest` | keyword | 1+ | `is-in-regtest` |
| `is-none` | function | 1+ | `(is-none value)` |
| `is-ok` | function | 1+ | `(is-ok value)` |
| `is-some` | function | 1+ | `(is-some value)` |
| `is-standard` | function | 2+ | `(is-standard standard-or-contract-principal)` |
| `keccak256` | function | 1+ | `(keccak256 value)` |
| `len` | function | 1+ | `(len sequence)` |
| `let` | function | 1+ | `(let ((name1 expr1) (name2 expr2) ...) expr-body1 expr-body2 ... expr-body-last)` |
| `list` | function | 1+ | `(list expr1 expr2 expr3 ...)` |
| `log2` | function | 1+ | `(log2 n)` |
| `map` | function | 1+ | `(map func sequence_A sequence_B ... sequence_N)` |
| `map-delete` | function | 1+ | `(map-delete map-name key-tuple)` |
| `map-get?` | function | 1+ | `(map-get? map-name key-tuple)` |
| `map-insert` | function | 1+ | `(map-insert map-name key-tuple value-tuple)` |
| `map-set` | function | 1+ | `(map-set map-name key-tuple value-tuple)` |
| `match` | function | 1+ | `(match opt-input some-binding-name some-branch none-branch) \| (match-resp input ok-binding-name ok-branch err-binding-name err-branch)` |
| `merge` | function | 1+ | `(merge tuple { key1: val1 })` |
| `mod` | function | 1+ | `(mod i1 i2)` |
| `nft-burn?` | function | 1+ | `(nft-burn? asset-class asset-identifier sender)` |
| `nft-get-owner?` | function | 1+ | `(nft-get-owner? asset-class asset-identifier)` |
| `nft-mint?` | function | 1+ | `(nft-mint? asset-class asset-identifier recipient)` |
| `nft-transfer?` | function | 1+ | `(nft-transfer? asset-class asset-identifier sender recipient)` |
| `none` | keyword | 1+ | `none` |
| `not` | function | 1+ | `(not b1)` |
| `ok` | function | 1+ | `(ok value)` |
| `or` | function | 1+ | `(or b1 b2 ...)` |
| `pow` | function | 1+ | `(pow i1 i2)` |
| `principal-construct?` | function | 2+ | `(principal-construct? (buff 1) (buff 20) [(string-ascii 40)])` |
| `principal-destruct?` | function | 2+ | `(principal-destruct? principal-address)` |
| `principal-of?` | function | 1+ | `(principal-of? public-key)` |
| `print` | function | 1+ | `(print expr)` |
| `replace-at?` | function | 2+ | `(replace-at? sequence index element)` |
| `restrict-assets?` | function | 4+ | `(restrict-assets? asset-owner ((with-stx\|with-ft\|with-nft\|with-stacking\|with-staking\|with-pox)*) expr-body1 expr-body2 ... expr-body-last)` |
| `secp256k1-decompress?` | function | 6+ | `(secp256k1-decompress? public-key)` |
| `secp256k1-recover?` | function | 1+ | `(secp256k1-recover? message-hash signature)` |
| `secp256k1-verify` | function | 1+ | `(secp256k1-verify message-hash signature public-key)` |
| `secp256r1-verify` | function | 4+ | `(secp256r1-verify message-hash signature public-key)` |
| `sha256` | function | 1+ | `(sha256 value)` |
| `sha512` | function | 1+ | `(sha512 value)` |
| `sha512/256` | function | 1+ | `(sha512/256 value)` |
| `slice?` | function | 2+ | `(slice? sequence left-position right-position)` |
| `some` | function | 1+ | `(some value)` |
| `sqrti` | function | 1+ | `(sqrti n)` |
| `stacks-block-height` | keyword | 3+ | `stacks-block-height` |
| `stacks-block-time` | keyword | 4+ | `stacks-block-time` |
| `string-to-int?` | function | 2+ | `(string-to-int? (string-ascii\|string-utf8))` |
| `string-to-uint?` | function | 2+ | `(string-to-uint? (string-ascii\|string-utf8))` |
| `stx-account` | function | 2+ | `(stx-account owner)` |
| `stx-burn?` | function | 1+ | `(stx-burn? amount sender)` |
| `stx-get-balance` | function | 1+ | `(stx-get-balance owner)` |
| `stx-liquid-supply` | keyword | 1+ | `stx-liquid-supply` |
| `stx-transfer-memo?` | function | 2+ | `(stx-transfer-memo? amount sender recipient memo)` |
| `stx-transfer?` | function | 1+ | `(stx-transfer? amount sender recipient)` |
| `tenure-height` | keyword | 3+ | `tenure-height` |
| `to-ascii?` | function | 4+ | `(to-ascii? value)` |
| `to-consensus-buff?` | function | 2+ | `(to-consensus-buff? value)` |
| `to-int` | function | 1+ | `(to-int u)` |
| `to-uint` | function | 1+ | `(to-uint i)` |
| `true` | keyword | 1+ | `true` |
| `try!` | function | 1+ | `(try! option-input)` |
| `tuple` | function | 1+ | `(tuple (key0 expr0) (key1 expr1) ...)` |
| `tx-sender` | keyword | 1+ | `tx-sender` |
| `tx-sponsor?` | keyword | 2+ | `tx-sponsor?` |
| `unwrap!` | function | 1+ | `(unwrap! option-input thrown-value)` |
| `unwrap-err!` | function | 1+ | `(unwrap-err! response-input thrown-value)` |
| `unwrap-err-panic` | function | 1+ | `(unwrap-err-panic response-input)` |
| `unwrap-panic` | function | 1+ | `(unwrap-panic option-input)` |
| `use-trait` | definition | 1+ | `(use-trait trait-alias trait-identifier)` |
| `var-get` | function | 1+ | `(var-get var-name)` |
| `var-set` | function | 1+ | `(var-set var-name expr1)` |
| `verify-merkle-proof` | function | 6+ | `(verify-merkle-proof leaf-hash root-hash tx-index tx-count sibling-hashes)` |
| `with-all-assets-unsafe` | function | 4+ | `(with-all-assets-unsafe)` |
| `with-ft` | function | 4+ | `(with-ft contract-id token-name amount)` |
| `with-nft` | function | 4+ | `(with-nft contract-id asset-name identifiers)` |
| `with-pox` | function | 6+ | `(with-pox)` |
| `with-stacking` | function | 4–5 | `(with-stacking amount)` |
| `with-staking` | function | 6+ | `(with-staking amount)` |
| `with-stx` | function | 4+ | `(with-stx amount)` |
| `xor` | function | 1+ | `(xor i1 i2)` |

## Reference

### *

Clarity 1+ · function · `(* i1 i2...)`

Multiplies a variable number of integer inputs and returns the result. In the event of an _overflow_, throws a runtime error.

```clarity
(* 2 3) ;; Returns 6
(* 5 2) ;; Returns 10
(* 2 2 2) ;; Returns 8
```

### +

Clarity 1+ · function · `(+ i1 i2...)`

Adds a variable number of integer inputs and returns the result. In the event of an _overflow_, throws a runtime error.

```clarity
(+ 1 2 3) ;; Returns 6
```

### -

Clarity 1+ · function · `(- i1 i2...)`

Subtracts a variable number of integer inputs and returns the result. In the event of an _underflow_, throws a runtime error.

```clarity
(- 2 1 1) ;; Returns 0
(- 0 3) ;; Returns -3
```

### /

Clarity 1+ · function · `(/ i1 i2...)`

Integer divides a variable number of integer inputs and returns the result. In the event of division by zero, throws a runtime error.

```clarity
(/ 2 3) ;; Returns 0
(/ 5 2) ;; Returns 2
(/ 4 2 2) ;; Returns 1
```

### <

Clarity 1+ · function · `(< i1 i2)`

Compares two integers, returning `true` if `i1` is less than `i2` and `false` otherwise.
i1 and i2 must be of the same type. Starting with Stacks 1.0, the `<`-comparable types are `int` and `uint`. Starting with Stacks 2.1,
the `<`-comparable types are expanded to include `string-ascii`, `string-utf8` and `buff`.

```clarity
(< 1 2) ;; Returns true
(< 5 2) ;; Returns false
(< "aaa" "baa") ;; Returns true
(< "aa" "aaa") ;; Returns true
(< 0x01 0x02) ;; Returns true
(< 5 u2) ;; Throws type error
```

### <=

Clarity 1+ · function · `(<= i1 i2)`

Compares two integers, returning true if `i1` is less than or equal to `i2` and `false` otherwise.
i1 and i2 must be of the same type. Starting with Stacks 1.0, the `<=`-comparable types are `int` and `uint`. Starting with Stacks 2.1,
the `<=`-comparable types are expanded to include `string-ascii`, `string-utf8` and `buff`.

```clarity
(<= 1 1) ;; Returns true
(<= 5 2) ;; Returns false
(<= "aaa" "baa") ;; Returns true
(<= "aa" "aaa") ;; Returns true
(<= 0x01 0x02) ;; Returns true
(<= 5 u2) ;; Throws type error
```

### >

Clarity 1+ · function · `(> i1 i2)`

Compares two integers, returning `true` if `i1` is greater than `i2` and false otherwise.
i1 and i2 must be of the same type. Starting with Stacks 1.0, the `>`-comparable types are `int` and `uint`. Starting with Stacks 2.1,
the `>`-comparable types are expanded to include `string-ascii`, `string-utf8` and `buff`.

```clarity
(> 1 2) ;; Returns false
(> 5 2) ;; Returns true
(> "baa" "aaa") ;; Returns true
(> "aaa" "aa") ;; Returns true
(> 0x02 0x01) ;; Returns true
(> 5 u2) ;; Throws type error
```

### >=

Clarity 1+ · function · `(>= i1 i2)`

Compares two integers, returning `true` if `i1` is greater than or equal to `i2` and `false` otherwise.
i1 and i2 must be of the same type. Starting with Stacks 1.0, the `>=`-comparable types are `int` and `uint`. Starting with Stacks 2.1,
the `>=`-comparable types are expanded to include `string-ascii`, `string-utf8` and `buff`.

```clarity
(>= 1 1) ;; Returns true
(>= 5 2) ;; Returns true
(>= "baa" "aaa") ;; Returns true
(>= "aaa" "aa") ;; Returns true
(>= 0x02 0x01) ;; Returns true
(>= 5 u2) ;; Throws type error
```

### and

Clarity 1+ · function · `(and b1 b2 ...)`

Returns `true` if all boolean inputs are `true`. Importantly, the supplied arguments are
evaluated in-order and lazily. Lazy evaluation means that if one of the arguments returns `false`, the function
short-circuits, and no subsequent arguments are evaluated.

```clarity
(and true false) ;; Returns false
(and (is-eq (+ 1 2) 1) (is-eq 4 4)) ;; Returns false
(and (is-eq (+ 1 2) 3) (is-eq 4 4)) ;; Returns true
```

### append

Clarity 1+ · function · `(append (list 1 2 3 4) 5)` · in: `list A, A` · out: `list`

The `append` function takes a list and another value with the same entry type,
and outputs a list of the same type with max_len += 1.

```clarity
(append (list 1 2 3 4) 5) ;; Returns (1 2 3 4 5)
```

### as-contract

Clarity 1–3 · function · `(as-contract expr)` · in: `A` · out: `A`

The `as-contract` function switches the current context's `tx-sender` value to the _contract's_
principal and executes `expr` with that context. It returns the resulting value of `expr`.

```clarity
(as-contract tx-sender) ;; Returns S1G2081040G2081040G2081040G208105NK8PE5.docs-test
```

### as-contract?

Clarity 4+ · function · `(as-contract? ((with-stx\|with-ft\|with-nft\|with-stacking\|with-staking\|with-pox)*) expr-body1 expr-body2 ... expr-body-last)` · in: `((Allowance){0,128}), AnyType, ... A` · out: `(response A uint)`

> **info:** The previous version of `as-contract`, introduced in Clarity 1, has changed to `as-contract?` in Clarity 4, with several new security enhancements.

Switches the current context's `tx-sender` and
`contract-caller` values to the contract's principal and executes the body
expressions within that context, then checks the asset outflows from the
contract against the granted allowances, in declaration order. If any
allowance is violated, the body expressions are reverted, an error is
returned, and an event is emitted with the full details of the violation to
help with debugging. Note that the allowance setup expressions are evaluated
before executing the body expressions. The final body expression cannot
return a `response` value in order to avoid returning a nested `response`
value from `as-contract?` (nested responses are error-prone). Returns:
* `(ok x)` if the outflows are within the allowances, where `x` is the
    result of the final body expression and has type `A`.
* `(err index)` if an allowance was violated, where `index` is the 0-based
    index of the first violated allowance in the list of granted allowances,
    or `u128` if an asset with no allowance caused the violation.

```clarity
(let ((recipient tx-sender))
  (as-contract? ((with-stx u100))
    (try! (stx-transfer? u50 tx-sender recipient))
  )
) ;; Returns (ok true)
(let ((recipient tx-sender))
  (as-contract? ()
    (try! (stx-transfer? u50 tx-sender recipient))
  )
) ;; Returns (err u128)
```

### as-max-len?

Clarity 1+ · function · `(as-max-len? sequence max_length)` · in: `sequence_A, uint` · out: `(optional sequence_A)`

The `as-max-len?` function takes a sequence argument and a uint-valued, literal length argument.
The function returns an optional type. If the input sequence length is less than
or equal to the supplied max_length, this returns `(some sequence)`, otherwise it returns `none`.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`.

```clarity
(as-max-len? (list 2 2 2) u3) ;; Returns (some (2 2 2))
(as-max-len? (list 1 2 3) u2) ;; Returns none
(as-max-len? "hello" u10) ;; Returns (some "hello")
(as-max-len? 0x010203 u10) ;; Returns (some 0x010203)
```

### asserts!

Clarity 1+ · function · `(asserts! bool-expr thrown-value)` · in: `bool, C` · out: `bool`

The `asserts!` function admits a boolean argument and asserts its evaluation:
if bool-expr is `true`, `asserts!` returns `true` and proceeds in the program execution.
If the supplied argument is returning a false value, `asserts!` _returns_ `thrown-value` and exits the current
control-flow.

```clarity
(asserts! (is-eq 1 1) (err 1)) ;; Returns true
```

### at-block

Clarity 1–4 · function · `(at-block id-block-hash expr)` · in: `(buff 32), A` · out: `A`

> **danger:** As of Epoch 3.4, existing contracts using `at-block` will throw an error if called.

Removed in Epoch 3.4 (see SIP-042).

The `at-block` function evaluates the expression `expr` _as if_ it were evaluated at the end of the
block indicated by the _block-hash_ argument. The `expr` closure must be read-only.

Note: The block identifying hash must be a hash returned by the `id-header-hash` block information
property. This hash uniquely identifies Stacks blocks and is unique across Stacks forks. While the hash returned by
`header-hash` is unique within the context of a single fork, it is not unique across Stacks forks.

The function returns the result of evaluating `expr`.

```clarity
(define-data-var data int 1)
(at-block 0x0000000000000000000000000000000000000000000000000000000000000000 block-height) ;; Returns u0
(at-block (unwrap-panic (get-stacks-block-info? id-header-hash u0)) (var-get data)) ;; Throws NoSuchDataVariable because `data` wasn't initialized at block height 0
```

### begin

Clarity 1+ · function · `(begin expr1 expr2 expr3 ... expr-last)` · in: `AnyType, ... A` · out: `A`

The `begin` function evaluates each of its input expressions, returning the
return value of the last such expression.

Note: intermediary statements returning a response type must be checked.

```clarity
(begin (+ 1 2) 4 5) ;; Returns 5
```

### bit-and

Clarity 2+ · function · `(bit-and i1 i2...)`

Returns the result of bitwise and'ing a variable number of integer inputs.

```clarity
(bit-and 24 16) ;; Returns 16
(bit-and 28 24 -1) ;; Returns 24
(bit-and u24 u16) ;; Returns u16
(bit-and -128 -64) ;; Returns -128
(bit-and 28 24 -1) ;; Returns 24
```

### bit-not

Clarity 2+ · function · `(bit-not i1)`

Returns the one's compliement (sometimes also called the bitwise compliment or not operator) of `i1`, effectively reversing the bits in `i1`.
In other words, every bit that is `1` in `ì1` will be `0` in the result.  Conversely, every bit that is `0` in `i1` will be `1` in the result.

```clarity
(bit-not 3) ;; Returns -4
(bit-not u128) ;; Returns u340282366920938463463374607431768211327
(bit-not 128) ;; Returns -129
(bit-not -128) ;; Returns 127
```

### bit-or

Clarity 2+ · function · `(bit-or i1 i2...)`

Returns the result of bitwise inclusive or'ing a variable number of integer inputs.

```clarity
(bit-or 4 8) ;; Returns 12
(bit-or 1 2 4) ;; Returns 7
(bit-or 64 -32 -16) ;; Returns -16
(bit-or u2 u4 u32) ;; Returns u38
```

### bit-shift-left

Clarity 2+ · function · `(bit-shift-left i1 shamt)`

Shifts all the bits in `i1` to the left by the number of places specified in `shamt` modulo 128 (the bit width of Clarity integers).

Note that there is a deliberate choice made to ignore arithmetic overflow for this operation.  In use cases where overflow should be detected, developers
should use `*`, `/`, and `pow` instead of the shift operators.

```clarity
(bit-shift-left 2 u1) ;; Returns 4
(bit-shift-left 16 u2) ;; Returns 64
(bit-shift-left -64 u1) ;; Returns -128
(bit-shift-left u4 u2) ;; Returns u16
(bit-shift-left 123 u9999999999) ;; Returns -170141183460469231731687303715884105728
(bit-shift-left u123 u9999999999) ;; Returns u170141183460469231731687303715884105728
(bit-shift-left -1 u7) ;; Returns -128
(bit-shift-left -1 u128) ;; Returns -1
```

### bit-shift-right

Clarity 2+ · function · `(bit-shift-right i1 shamt)`

Shifts all the bits in `i1` to the right by the number of places specified in `shamt` modulo 128 (the bit width of Clarity integers).
When `i1` is a `uint` (unsigned), new bits are filled with zeros. When `i1` is an `int` (signed), the sign is preserved, meaning that new bits are filled with the value of the previous sign-bit.

Note that there is a deliberate choice made to ignore arithmetic overflow for this operation. In use cases where overflow should be detected, developers should use `*`, `/`, and `pow` instead of the shift operators.

```clarity
(bit-shift-right 2 u1) ;; Returns 1
(bit-shift-right 128 u2) ;; Returns 32
(bit-shift-right -64 u1) ;; Returns -32
(bit-shift-right u128 u2) ;; Returns u32
(bit-shift-right 123 u9999999999) ;; Returns 0
(bit-shift-right u123 u9999999999) ;; Returns u0
(bit-shift-right -128 u7) ;; Returns -1
(bit-shift-right -256 u1) ;; Returns -128
(bit-shift-right 5 u2) ;; Returns 1
(bit-shift-right -5 u2) ;; Returns -2
```

### bit-xor

Clarity 2+ · function · `(bit-xor i1 i2...)`

Returns the result of bitwise exclusive or'ing a variable number of integer inputs.

```clarity
(bit-xor 1 2) ;; Returns 3
(bit-xor 120 280) ;; Returns 352
(bit-xor -128 64) ;; Returns -64
(bit-xor u24 u4) ;; Returns u28
(bit-xor 1 2 4 -1) ;; Returns -8
```

### block-height

Clarity 1–2 · keyword · out: `uint`

Returns the current block height of the Stacks blockchain in Clarity 1 and 2.
Upon activation of epoch 3.0, `block-height` will return the same value as `tenure-height`.
In Clarity 3, `block-height` is removed and has been replaced with `stacks-block-height`.

```clarity
(> block-height u1000) ;; returns true if the current block-height has passed 1000 blocks.
```

### buff-to-int-be

Clarity 2+ · function · `(buff-to-int-be (buff 16))`

Converts a byte buffer to a signed integer use a big-endian encoding.
The byte buffer can be up to 16 bytes in length. If there are fewer than 16 bytes, as
this function uses a big-endian encoding, the input behaves as if it is
zero-padded on the _left_.

Note: This function is only available starting with Stacks 2.1.

```clarity
(buff-to-int-be 0x01) ;; Returns 1
(buff-to-int-be 0x00000000000000000000000000000001) ;; Returns 1
(buff-to-int-be 0xffffffffffffffffffffffffffffffff) ;; Returns -1
(buff-to-int-be 0x) ;; Returns 0
```

### buff-to-int-le

Clarity 2+ · function · `(buff-to-int-le (buff 16))`

Converts a byte buffer to a signed integer use a little-endian encoding.
The byte buffer can be up to 16 bytes in length. If there are fewer than 16 bytes, as
this function uses a little-endian encoding, the input behaves as if it is
zero-padded on the _right_.

Note: This function is only available starting with Stacks 2.1.

```clarity
(buff-to-int-le 0x01) ;; Returns 1
(buff-to-int-le 0x01000000000000000000000000000000) ;; Returns 1
(buff-to-int-le 0xffffffffffffffffffffffffffffffff) ;; Returns -1
(buff-to-int-le 0x) ;; Returns 0
```

### buff-to-uint-be

Clarity 2+ · function · `(buff-to-uint-be (buff 16))`

Converts a byte buffer to an unsigned integer use a big-endian encoding.
The byte buffer can be up to 16 bytes in length. If there are fewer than 16 bytes, as
this function uses a big-endian encoding, the input behaves as if it is
zero-padded on the _left_.

Note: This function is only available starting with Stacks 2.1.

```clarity
(buff-to-uint-be 0x01) ;; Returns u1
(buff-to-uint-be 0x00000000000000000000000000000001) ;; Returns u1
(buff-to-uint-be 0xffffffffffffffffffffffffffffffff) ;; Returns u340282366920938463463374607431768211455
(buff-to-uint-be 0x) ;; Returns u0
```

### buff-to-uint-le

Clarity 2+ · function · `(buff-to-uint-le (buff 16))`

Converts a byte buffer to an unsigned integer use a little-endian encoding.
The byte buffer can be up to 16 bytes in length. If there are fewer than 16 bytes, as
this function uses a little-endian encoding, the input behaves as if it is
zero-padded on the _right_.

Note: This function is only available starting with Stacks 2.1.

```clarity
(buff-to-uint-le 0x01) ;; Returns u1
(buff-to-uint-le 0x01000000000000000000000000000000) ;; Returns u1
(buff-to-uint-le 0xffffffffffffffffffffffffffffffff) ;; Returns u340282366920938463463374607431768211455
(buff-to-uint-le 0x) ;; Returns u0
```

### burn-block-height

Clarity 1+ · keyword · out: `uint`

Returns the current block height of the underlying burn blockchain.

```clarity
(> burn-block-height u832000) ;; returns true if the current height of the underlying burn blockchain has passed 832,000 blocks.
```

### chain-id

Clarity 2+ · keyword · out: `uint`

Returns the 32-bit chain ID of the blockchain running this transaction

```clarity
(print chain-id) ;; Will print 'u1' if the code is running on mainnet, and 'u2147483648' on testnet, and other values on different chains.
```

### concat

Clarity 1+ · function · `(concat sequence1 sequence2 ...)` · in: `sequence_A, sequence_A, ...` · out: `sequence_A`

The `concat` function takes two or more sequences of the same type,
and returns a concatenated sequence of the same type, with the resulting
sequence_len equal to the sum of the input sequence lengths.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`.

Prior to Clarity 6, `concat` accepts exactly two arguments. Beginning in
Clarity 6, `concat` is variadic and accepts two or more arguments in a single
call. The variadic form charges runtime cost proportional to the combined
length of the inputs (rather than the quadratic-in-N cost of an equivalent
nested-binary chain), so it is strictly cheaper than chaining binary calls.

```clarity
(concat (list 1 2) (list 3 4)) ;; Returns (1 2 3 4)
(concat "hello " "world") ;; Returns "hello world"
(concat 0x0102 0x0304) ;; Returns 0x01020304
(concat 0x01 0x02 0x03 0x04) ;; Returns 0x01020304
```

### contract-call?

Clarity 1+ · function · `(contract-call? .contract-name function-name arg0 arg1 ...)` · in: `ContractName, PublicFunctionName, Arg0, ...` · out: `(response A B)`

The `contract-call?` function executes the given public function of the given contract.
You _may not_ use this function to call a public function defined in the current contract. If the public
function returns _err_, any database changes resulting from calling `contract-call?` are aborted.
If the function returns _ok_, database changes occurred.

```clarity
;; instantiate the sample/contracts/tokens.clar contract first!
(as-contract? () (try! (contract-call? .tokens mint! u19))) ;; Returns (ok u19)
```

### contract-caller

Clarity 1+ · keyword · out: `principal`

Returns the caller of the current contract context. If this contract is the first one called by a signed transaction,
the caller will be equal to the signing principal. If `contract-call?` was used to invoke a function from a new contract, `contract-caller`
changes to the _calling_ contract's principal. If `as-contract` is used to change the `tx-sender` context, `contract-caller` _also_ changes
to the same contract principal.

```clarity
(print contract-caller) ;; Will print out a Stacks address of the transaction sender
```

### contract-hash?

Clarity 4+ · function · `(contract-hash? contract)`

Returns the hash of the specified contract, or an error if the principal
is not a contract or the specified contract does not exist. Returns:
* `(ok 0x<hash>)` on success, where `<hash>` is the SHA-512/256 hash of the code body
* `(err u1)` if the principal is not a contract principal.
* `(err u2)` if the specified contract does not exist.

```clarity
;; instantiate the sample/contracts/tokens.clar contract first!
(contract-hash? .tokens) ;; Returns (ok 0x90b4a559286ba8ec3801fe8ef49d5e646043861f29376771918d1afb8ff68af7)
(contract-hash? 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM) ;; Returns (err u1)
(contract-hash? 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM.does-not-exist) ;; Returns (err u2)
```

### contract-of

Clarity 1+ · function · `(contract-of .contract-name)` · in: `Trait` · out: `principal`

The `contract-of` function returns the principal of the contract implementing the trait.

```clarity
(use-trait token-a-trait 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF.token-a.token-trait)
(define-public (forward-get-balance (user principal) (contract <token-a-trait>))
  (begin
    (ok (contract-of contract)))) ;; returns the principal of the contract implementing <token-a-trait>
```

### current-contract

Clarity 4+ · keyword · out: `principal`

Returns the principal of the current contract.

```clarity
(print current-contract) ;; Will print out the Stacks address of the current contract
```

### default-to

Clarity 1+ · function · `(default-to default-value option-value)` · in: `A, (optional A)` · out: `A`

The `default-to` function attempts to 'unpack' the second argument: if the argument is
a `(some ...)` option, it returns the inner value of the option. If the second argument is a `none` value,
`default-to` it returns the value of `default-value`.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(default-to 0 (get id (map-get? names-map (tuple (name "blockstack"))))) ;; Returns 1337
(default-to 0 (get id (map-get? names-map (tuple (name "non-existant"))))) ;; Returns 0
```

### define-constant

Clarity 1+ · definition · `(define-constant name expression)` · in: `MethodSignature, MethodBody` · out: `Not Applicable`

`define-constant` is used to define a private constant value in a smart contract.
The expression passed into the definition is evaluated at contract launch, in the order that it is
supplied in the contract. This can lead to undefined function or undefined variable errors in the
event that a function or variable used in the expression has not been defined before the constant.

Like other kinds of definition statements, `define-constant` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

```clarity
(define-constant four (+ 2 2))
(+ 4 four) ;; Returns 8
```

### define-data-var

Clarity 1+ · definition · `(define-data-var var-name type value)` · in: `VarName, TypeDefinition, Value` · out: `Not Applicable`

`define-data-var` is used to define a new persisted variable for use in a smart contract. Such
variable are only modifiable by the current smart contract.

Persisted variable are defined with a type and a value.

Like other kinds of definition statements, `define-data-var` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

```clarity
(define-data-var size int 0)
(define-private (set-size (value int))
  (var-set size value))
(set-size 1)
(set-size 2)
```

### define-fungible-token

Clarity 1+ · definition · `(define-fungible-token token-name <total-supply>)` · in: `TokenName, <uint>` · out: `Not Applicable`

`define-fungible-token` is used to define a new fungible token class for use in the current contract.

The second argument, if supplied, defines the total supply of the fungible token. This ensures that all calls to the `ft-mint?`
function will never be able to create more than `total-supply` tokens. If any such call were to increase the total supply
of tokens passed that amount, that invocation of `ft-mint?` will result in a runtime error and abort.

Like other kinds of definition statements, `define-fungible-token` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

Tokens defined using `define-fungible-token` may be used in `ft-transfer?`, `ft-mint?`, and `ft-get-balance` functions

```clarity
(define-fungible-token stacks)
(define-fungible-token limited-supply-stacks u100)
```

### define-map

Clarity 1+ · definition · `(define-map map-name key-type value-type)` · in: `MapName, TypeDefinition, TypeDefinition` · out: `Not Applicable`

`define-map` is used to define a new datamap for use in a smart contract. Such
maps are only modifiable by the current smart contract.

Maps are defined with a key type and value type, often these types are tuple types.

Like other kinds of definition statements, `define-map` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

```clarity
(define-map squares { x: int } { square: int })
(define-private (add-entry (x int))
  (map-insert squares { x: 2 } { square: (* x x) }))
(add-entry 1)
(add-entry 2)
(add-entry 3)
(add-entry 4)
(add-entry 5)
```

### define-non-fungible-token

Clarity 1+ · definition · `(define-non-fungible-token asset-name asset-identifier-type)` · in: `AssetName, TypeSignature` · out: `Not Applicable`

`define-non-fungible-token` is used to define a new non-fungible token class for use in the current contract.
Individual assets are identified by their asset identifier, which must be of the type `asset-identifier-type`. Asset
identifiers are _unique_ identifiers.

Like other kinds of definition statements, `define-non-fungible-token` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

Assets defined using `define-non-fungible-token` may be used in `nft-transfer?`, `nft-mint?`, and `nft-get-owner?` functions

```clarity
(define-non-fungible-token names (buff 50))
```

### define-private

Clarity 1+ · definition · `(define-private (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` · in: `MethodSignature, MethodBody` · out: `Not Applicable`

`define-private` is used to define _private_ functions for a smart contract. Private
functions may not be called from other smart contracts, nor may they be invoked directly by users.
Instead, these functions may only be invoked by other functions defined in the same smart contract.

Like other kinds of definition statements, `define-private` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

Private functions may return any type.

```clarity
(define-private (max-of (i1 int) (i2 int))
  (if (> i1 i2)
      i1
      i2))
(max-of 4 6) ;; Returns 6
```

### define-public

Clarity 1+ · definition · `(define-public (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` · in: `MethodSignature, MethodBody` · out: `Not Applicable`

`define-public` is used to define a _public_ function and transaction for a smart contract. Public
functions are callable from other smart contracts and may be invoked directly by users by submitting a transaction
to the Stacks blockchain.

Like other kinds of definition statements, `define-public` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

Public functions _must_ return a ResponseType (using either `ok` or `err`). Any datamap modifications performed by
a public function is aborted if the function returns an `err` type. Public functions may be invoked by other
contracts via `contract-call?`.

Function names may not collide with a native function or keyword. Beginning in Epoch 4.1, one exception applies:
a public function may take a reserved name (e.g. `slice?`) to implement a method of a trait listed in `impl-trait`,
provided the name was still free in the trait's Clarity version. Inside the contract the native function or keyword
keeps its meaning, so the implementation is reached through `contract-call?` and trait dispatch; a keyword-named one
can also be applied directly or passed to `map`/`fold`/`filter`, since no native function has that name. A function
under a reserved name that matches no such trait method fails with `NameAlreadyUsed`.

```clarity
(define-public (hello-world (input int))
  (begin (print (+ 2 input))
         (ok input)))
```

### define-read-only

Clarity 1+ · definition · `(define-read-only (function-name (arg-name-0 arg-type-0) (arg-name-1 arg-type-1) ...) function-body)` · in: `MethodSignature, MethodBody` · out: `Not Applicable`

`define-read-only` is used to define a _public read-only_ function for a smart contract. Such
functions are callable from other smart contracts.

Like other kinds of definition statements, `define-read-only` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

Read-only functions may return any type. However, read-only functions
may not perform any datamap modifications, or call any functions which
perform such modifications. This is enforced both during type checks and during
the execution of the function. Public read-only functions may
be invoked by other contracts via `contract-call?`.

Beginning in Epoch 4.1, the reserved-name exception described under `define-public` applies to read-only functions as well.

```clarity
(define-read-only (just-return-one-hundred)
  (* 10 10))
```

### define-trait

Clarity 1+ · definition · `(define-trait trait-name ((func1-name (arg1-type arg2-type ...) (return-type))))` · in: `VarName, [MethodSignature]` · out: `Not Applicable`

`define-trait` is used to define a new trait definition for use in a smart contract. Other contracts
can implement a given trait and then have their contract identifier being passed as a function argument in order to be called
dynamically with `contract-call?`.

Traits are defined with a name, and a list of functions, where each function is defined with a name, a list of argument types, and a return type.

In Clarity 1, a trait type can be used to specify the type of a function parameter. A parameter with a trait type can
be used as the target of a dynamic `contract-call?`. A principal literal (e.g. `ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM.foo`)
may be passed as a trait parameter if the specified contract implements all of the functions specified by the trait.
A trait value (originating from a parameter with trait type) may also be passed as a trait parameter if the types are the same.

Beginning in Clarity 2, a trait can be used in all of the same ways that a built-in type can be used,
except that it cannot be stored in a data var or map, since this would inhibit static analysis.
This means that a trait type can be embedded in a compound type (e.g. `(optional <my-trait>)` or `(list 4 <my-trait>)`)
and a trait value can be bound to a variable in a `let` or `match` expression. In addition to the principal literal
and trait value with matching type allowed in Clarity 1, Clarity 2 also supports implicit casting from a
compatible trait, meaning that a value of type `trait-a` may be passed to a parameter with type `trait-b` if `trait-a`
includes all of the requirements of `trait-b` (and optionally additional functions).

Beginning in Epoch 4.1, a trait method may not take a name reserved in the contract's Clarity version;
`define-trait` rejects it with `NameAlreadyUsed`. Traits from versions where the name was still free stay
implementable: see `define-public`.

Like other kinds of definition statements, `define-trait` may only be used at the top level of a smart contract
definition (i.e., you cannot put a define statement in the middle of a function body).

```clarity
(define-trait token-trait
    ((transfer? (principal principal uint) (response uint uint))
     (get-balance (principal) (response uint uint))))
```

### ed25519-verify

Clarity 6+ · function · `(ed25519-verify message signature public-key)` · in: `(buff 1048576), (buff 64), (buff 32)` · out: `bool`

The `ed25519-verify` function verifies that the provided signature of the message
was signed with the private key that generated the public key.
The `message` can be up to 1 MiB in size. The `signature` is the raw 64-byte signature, and the `public-key` is the raw 32-byte public key.
returns `true` if the signature is valid, and `false` otherwise.
Note that validation is in strict mode, so non-canonical signatures will be rejected.

```clarity
(ed25519-verify 0xaf82
    0x6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a
    0xfc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025) ;; Returns true
(ed25519-verify 0x00000000000000000000000000000000000000 0x6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a
    0xfc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025) ;; Returns false
```

### element-at

Clarity 1+ · function · `(element-at? sequence index)` · in: `sequence_A, uint` · out: `(optional A)`

The `element-at?` function returns the element at `index` in the provided sequence.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.

In Clarity1, `element-at` must be used (without the `?`). The `?` is added in Clarity2 for consistency -- built-ins that return responses or optionals end in `?`. The Clarity1 spelling is left as an alias in Clarity2 for backwards compatibility.

```clarity
(element-at? "blockstack" u5) ;; Returns (some "s")
(element-at? (list 1 2 3 4 5) u5) ;; Returns none
(element-at? (list 1 2 3 4 5) (+ u1 u2)) ;; Returns (some 4)
(element-at? "abcd" u1) ;; Returns (some "b")
(element-at? 0xfb01 u1) ;; Returns (some 0x01)
```

### element-at?

Clarity 2+ · function · `(element-at? sequence index)` · in: `sequence_A, uint` · out: `(optional A)`

The `element-at?` function returns the element at `index` in the provided sequence.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.

In Clarity1, `element-at` must be used (without the `?`). The `?` is added in Clarity2 for consistency -- built-ins that return responses or optionals end in `?`. The Clarity1 spelling is left as an alias in Clarity2 for backwards compatibility.

```clarity
(element-at? "blockstack" u5) ;; Returns (some "s")
(element-at? (list 1 2 3 4 5) u5) ;; Returns none
(element-at? (list 1 2 3 4 5) (+ u1 u2)) ;; Returns (some 4)
(element-at? "abcd" u1) ;; Returns (some "b")
(element-at? 0xfb01 u1) ;; Returns (some 0x01)
```

### err

Clarity 1+ · function · `(err value)` · in: `A` · out: `(response A B)`

The `err` function constructs a response type from the input value. Use `err` for
creating return values in public functions. An _err_ value indicates that any database changes during
the processing of the function should be rolled back.

```clarity
(err true) ;; Returns (err true)
```

### false

Clarity 1+ · keyword · out: `bool`

Boolean false constant.

```clarity
(and true false) ;; Evaluates to false
(or false true)  ;; Evaluates to true
```

### filter

Clarity 1+ · function · `(filter func sequence)` · in: `Function(A) -> bool, sequence_A` · out: `sequence_A`

The `filter` function applies the input function `func` to each element of the
input sequence, and returns the same sequence with any elements removed for which `func` returned `false`.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.
The `func` argument must be a literal function name.

```clarity
(filter not (list true false true false)) ;; Returns (false false)
(define-private (is-a (char (string-utf8 1))) (is-eq char u"a"))
(filter is-a u"acabd") ;; Returns u"aa"
(define-private (is-zero (char (buff 1))) (is-eq char 0x00))
(filter is-zero 0x00010002) ;; Returns 0x0000
```

### fold

Clarity 1+ · function · `(fold func sequence_A initial_B)` · in: `Function(A, B) -> B, sequence_A, B` · out: `B`

> **info:** As of Epoch 4.1, the result type of `fold` covers both `initial_B` and the return type of `func`. Earlier epochs used the return type of `func` alone.

The `fold` function condenses `sequence_A` into a value of type
`B` by recursively applies the function `func` to each element of the
input sequence _and_ the output of a previous application of `func`.

`fold` uses `initial_B` in the initial application of `func`, along with the
first element of `sequence_A`. The resulting value of type `B` is used for the
next application of `func`, along with the next element of `sequence_A` and so
on. `fold` returns the last value of type `B` returned by these successive
applications of `func`. If `sequence_A` is empty, `func` is never applied and
`fold` returns `initial_B` unchanged.

Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.
The `func` argument must be a literal function name.

```clarity
(fold * (list 2 2 2) 1) ;; Returns 8
(fold * (list 2 2 2) 0) ;; Returns 0
;; calculates (- 11 (- 7 (- 3 2)))
(fold - (list 3 7 11) 2) ;; Returns 5
(define-private (concat-string (a (string-ascii 20)) (b (string-ascii 20))) (unwrap-panic (as-max-len? (concat a b) u20)))
(fold concat-string "cdef" "ab")   ;; Returns "fedcab"
(fold concat-string (list "cd" "ef") "ab")   ;; Returns "efcdab"
(fold concat-string "" "ab")   ;; Returns "ab"
(define-private (concat-buff (a (buff 20)) (b (buff 20))) (unwrap-panic (as-max-len? (concat a b) u20)))
(fold concat-buff 0x03040506 0x0102)   ;; Returns 0x060504030102
```

### from-consensus-buff?

Clarity 2+ · function · `(from-consensus-buff? type-signature buffer)` · in: `type-signature(t), buff` · out: `(optional t)`

`from-consensus-buff?` is a special function that will deserialize a
buffer into a Clarity value, using the SIP-005 serialization of the
Clarity value. The type that `from-consensus-buff?` tries to deserialize
into is provided by the first parameter to the function. If it fails
to deserialize the type, the method returns `none`.

Starting in Stacks 4.1, a buffer containing a contract principal whose name is
longer than 40 characters fails to deserialize, and the method returns `none`.

```clarity
(from-consensus-buff? int 0x0000000000000000000000000000000001) ;; Returns (some 1)
(from-consensus-buff? uint 0x0000000000000000000000000000000001) ;; Returns none
(from-consensus-buff? uint 0x0100000000000000000000000000000001) ;; Returns (some u1)
(from-consensus-buff? bool 0x0000000000000000000000000000000001) ;; Returns none
(from-consensus-buff? bool 0x03) ;; Returns (some true)
(from-consensus-buff? bool 0x04) ;; Returns (some false)
(from-consensus-buff? principal 0x051fa46ff88886c2ef9762d970b4d2c63678835bd39d) ;; Returns (some SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR)
(from-consensus-buff? { abc: int, def: int } 0x0c00000002036162630000000000000000000000000000000003036465660000000000000000000000000000000004) ;; Returns (some (tuple (abc 3) (def 4)))
```

### ft-burn?

Clarity 1+ · function · `(ft-burn? token-name amount sender)` · in: `TokenName, uint, principal` · out: `(response bool uint)`

`ft-burn?` is used to decrease the token balance for the `sender` principal for a token
type defined using `define-fungible-token`. The decreased token balance is _not_ transferred to another principal, but
rather destroyed, reducing the circulating supply.

On a successful burn, it returns `(ok true)`. The burn may fail with error code:

* `(err u1)` -- `sender` does not have enough balance to burn this amount or the amount specified is not positive

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u100 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
(ft-burn? stackaroo u50 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
```

### ft-get-balance

Clarity 1+ · function · `(ft-get-balance token-name principal)` · in: `TokenName, principal` · out: `uint`

`ft-get-balance` returns `token-name` balance of the principal `principal`.
The token type must have been defined using `define-fungible-token`.

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u100 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR)
(ft-get-balance stackaroo 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns u100
```

### ft-get-supply

Clarity 1+ · function · `(ft-get-supply token-name)` · in: `TokenName` · out: `uint`

`ft-get-balance` returns `token-name` circulating supply.
The token type must have been defined using `define-fungible-token`.

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u100 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR)
(ft-get-supply stackaroo) ;; Returns u100
```

### ft-mint?

Clarity 1+ · function · `(ft-mint? token-name amount recipient)` · in: `TokenName, uint, principal` · out: `(response bool uint)`

`ft-mint?` is used to increase the token balance for the `recipient` principal for a token
type defined using `define-fungible-token`. The increased token balance is _not_ transferred from another principal, but
rather minted.

If a non-positive amount is provided to mint, this function returns `(err 1)`. Otherwise, on successfully mint, it
returns `(ok true)`. If this call would result in more supplied tokens than defined by the total supply in
`define-fungible-token`, then a `SupplyOverflow` runtime error is thrown.

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u100 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
```

### ft-transfer?

Clarity 1+ · function · `(ft-transfer? token-name amount sender recipient)` · in: `TokenName, uint, principal, principal` · out: `(response bool uint)`

`ft-transfer?` is used to increase the token balance for the `recipient` principal for a token
type defined using `define-fungible-token` by debiting the `sender` principal. In contrast to `stx-transfer?`,
any user can transfer the assets. When used, relevant guards need to be added.

This function returns (ok true) if the transfer is successful. In the event of an unsuccessful transfer it returns
one of the following error codes:

* `(err u1)` -- `sender` does not have enough balance to transfer
* `(err u2)` -- `sender` and `recipient` are the same principal
* `(err u3)` -- amount to send is non-positive

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u100 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR)
(ft-transfer? stackaroo u50 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
(ft-transfer? stackaroo u60 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (err u1)
```

### get

Clarity 1+ · function · `(get key-name tuple)` · in: `KeyName, (tuple) \| (optional (tuple))` · out: `A`

The `get` function fetches the value associated with a given key from the supplied typed tuple.
If an `Optional` value is supplied as the inputted tuple, `get` returns an `Optional` type of the specified key in
the tuple. If the supplied option is a `none` option, get returns `none`.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-insert names-map { name: "blockstack" } { id: 1337 }) ;; Returns true
(get id (tuple (name "blockstack") (id 1337))) ;; Returns 1337
(get id (map-get? names-map (tuple (name "blockstack")))) ;; Returns (some 1337)
(get id (map-get? names-map (tuple (name "non-existent")))) ;; Returns none
```

### get-bitcoin-tx-output?

Clarity 6+ · function · `(get-bitcoin-tx-output? tx-bytes vout)` · in: `(buff 1048576), uint` · out: `(response (tuple (script (buff 1024)) (amount uint) (txid (buff 32))) uint)`

The `get-bitcoin-tx-output?` function parses a serialized Bitcoin transaction
(`tx-bytes`, with or without SegWit witness data) and returns the output at the given `vout`
index, plus the canonical (non-witness) `txid` of the transaction.

The returned `txid` is in *internal* byte order (the raw double-SHA-256 result), ready to be
passed directly to `verify-merkle-proof` as the leaf hash. The `script` is the raw
`scriptPubKey` bytes of the output: contracts can pattern-match these bytes to recognize
P2WSH (`0x00 0x20 ...`), P2TR (`0x51 0x20 ...`), P2WPKH (`0x00 0x14 ...`), OP_RETURN
(`0x6a ...`), or any other output script.

Returns one of three error codes on failure:
- `(err u1)`: `tx-bytes` did not deserialize as a Bitcoin transaction.
- `(err u2)`: `vout` is out of range for this transaction.
- `(err u3)`: the output's `scriptPubKey` exceeds the 1024-byte cap.

This builtin is intended to be paired with `verify-merkle-proof` and the burn-block header
data exposed by `get-burn-block-info?` to verify that a Bitcoin output exists on-chain
without trusting the caller to have correctly hashed or stripped witness data from the tx.

```clarity
;; Parse the Bitcoin genesis block coinbase tx and return its sole output.
(get-bitcoin-tx-output? 0x01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4d04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000 u0)
;; Returns (ok (tuple (amount u5000000000) (script 0x4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac) (txid 0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a)))
(get-bitcoin-tx-output? 0x00 u0) ;; Returns (err u1)
```

### get-block-info?

Clarity 1–2 · function · `(get-block-info? prop-name block-height)` · in: `BlockInfoPropertyName, uint` · out: `(optional buff) \| (optional uint)`

In Clarity 3, `get-block-info?` is removed. In its place, `get-stacks-block-info?` can be used to retrieve
information about a Stacks block and `get-tenure-info?` can be used to get information pertaining to the tenure.

The `get-block-info?` function fetches data for a block of the given *Stacks* block height. The
value and type returned are determined by the specified `BlockInfoPropertyName`. If the provided `block-height` does
not correspond to an existing block prior to the current block, the function returns `none`. The currently available property names
are as follows:

- `burnchain-header-hash`: This property returns a `(buff 32)` value containing the header hash of the burnchain (Bitcoin) block that selected the
Stacks block at the given Stacks chain height.

- `id-header-hash`: This property returns a `(buff 32)` value containing the _index block hash_ of a Stacks block.   This hash is globally unique, and is derived
from the block hash and the history of accepted PoX operations.  This is also the block hash value you would pass into `(at-block)`.

- `header-hash`: This property returns a `(buff 32)` value containing the header hash of a Stacks block, given a Stacks chain height.  **WARNING* this hash is
not guaranteed to be globally unique, since the same Stacks block can be mined in different PoX forks.  If you need global uniqueness, you should use `id-header-hash`.

- `miner-address`: This property returns a `principal` value corresponding to the miner of the given block.  **WARNING** In Stacks 2.1, this is not guaranteed to
be the same `principal` that received the block reward, since Stacks 2.1 supports coinbase transactions that pay the reward to a contract address.  This is merely
the address of the `principal` that produced the block.

- `time`: This property returns a `uint` value of the block header time field. This is a Unix epoch timestamp in seconds
which roughly corresponds to when the block was mined. This timestamp comes from the burnchain block. **Note**: this does not increase monotonically with each block
and block times are accurate only to within two hours. See [BIP113](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0113.mediawiki) for more information.
For blocks mined after epoch 3.0, all Stacks blocks in one tenure will share the same timestamp. To get the Stacks block time for a block in epoch 3.0+, use `get-stacks-block-info?`.

- `vrf-seed`: This property returns a `(buff 32)` value of the VRF seed for the corresponding block.

- `block-reward`: This property returns a `uint` value for the total block reward of the indicated Stacks block.  This value is only available once the reward for
the block matures.  That is, the latest `block-reward` value available is at least 101 Stacks blocks in the past (on mainnet).  The reward includes the coinbase,
the anchored block's transaction fees, and the shares of the confirmed and produced microblock transaction fees earned by this block's miner.  Note that this value may
be smaller than the Stacks coinbase at this height, because the miner may have been punished with a valid `PoisonMicroblock` transaction in the event that the miner
published two or more microblock stream forks. Added in Clarity 2.

- `miner-spend-total`: This property returns a `uint` value for the total number of burnchain tokens (i.e. satoshis) spent by all miners trying to win this block. Added in Clarity 2.

- `miner-spend-winner`: This property returns a `uint` value for the number of burnchain tokens (i.e. satoshis) spent by the winning miner for this Stacks block.  Note that
this value is less than or equal to the value for `miner-spend-total` at the same block height. Added in Clarity 2.

```clarity
(get-block-info? time u0) ;; Returns (some u1557860301)
(get-block-info? header-hash u0) ;; Returns (some 0x374708fff7719dd5979ec875d56cd2286f6d3cf7ec317a3b25632aab28ec37bb)
(get-block-info? vrf-seed u0) ;; Returns (some 0xf490de2920c8a35fabeb13208852aa28c76f9be9b03a4dd2b3c075f7a26923b4)
```

### get-burn-block-info?

Clarity 2+ · function · `(get-burn-block-info? prop-name burn-block-height)` · in: `BurnBlockInfoPropertyName, uint` · out: `(optional buff) \| (optional (tuple (addrs (list 2 (tuple (hashbytes (buff 32)) (version (buff 1))))) (payout uint)))`

The `get-burn-block-info?` function fetches data for a block of the given *burnchain* block height. The
value and type returned are determined by the specified `BlockInfoPropertyName`.  Valid values for `burn-block-height` only
include heights between the burnchain height at the time the Stacks chain was launched, and the last-processed burnchain
block.  If the `burn-block-height` argument falls outside of this range, then `none` shall be returned.

The following `BlockInfoPropertyName` values are defined:

* The `header-hash` property returns a 32-byte buffer representing the header hash of the burnchain block at
burnchain height `burn-block-height`.

* The `pox-addrs` property returns a tuple with two items: a list of up to two PoX addresses that received a PoX payout at that block height, and the amount of burnchain
tokens paid to each address (note that per the blockchain consensus rules, each PoX payout will be the same for each address in the block-commit transaction).
The list will include burn addresses -- that is, the unspendable addresses that miners pay to when there are no PoX addresses left to be paid.  During the prepare phase,
there will be exactly one burn address reported. During the reward phase, up to two burn addresses may be reported in the event that some PoX reward slots are not claimed.

The `addrs` list contains the same PoX address values passed into the PoX smart contract:
   * They each have type signature `(tuple (hashbytes (buff 32)) (version (buff 1)))`
   * The `version` field can be any of the following:
      * `0x00` means this is a p2pkh address, and `hashbytes` is the 20-byte hash160 of a single public key
      * `0x01` means this is a p2sh address, and `hashbytes` is the 20-byte hash160 of a redeemScript script
      * `0x02` means this is a p2wpkh-p2sh address, and `hashbytes` is the 20-byte hash160 of a p2wpkh witness script
      * `0x03` means this is a p2wsh-p2sh address, and `hashbytes` is the 20-byte hash160 of a p2wsh witness script
      * `0x04` means this is a p2wpkh address, and `hashbytes` is the 20-byte hash160 of the witness script
      * `0x05` means this is a p2wsh address, and `hashbytes` is the 32-byte sha256 of the witness script
      * `0x06` means this is a p2tr address, and `hashbytes` is the 32-byte sha256 of the witness script

```clarity
(get-burn-block-info? header-hash u677050) ;; Returns (some 0xe67141016c88a7f1203eca0b4312f2ed141531f59303a1c267d7d83ab6b977d8)
(get-burn-block-info? pox-addrs u677050) ;; Returns (some (tuple (addrs ((tuple (hashbytes 0x395f3643cea07ec4eec73b4d9a973dcce56b9bf1) (version 0x00)) (tuple (hashbytes 0x7c6775e20e3e938d2d7e9d79ac310108ba501ddb) (version 0x01)))) (payout u123)))
```

### get-stacks-block-info?

Clarity 3+ · function · `(get-stacks-block-info? prop-name stacks-block-height)` · in: `StacksBlockInfoPropertyName, uint` · out: `(optional buff) \| (optional uint)`

The `get-stacks-block-info?` function fetches data for a block of the given *Stacks* block height. The
value and type returned are determined by the specified `StacksBlockInfoPropertyName`. If the provided `stacks-block-height` does
not correspond to an existing block prior to the current block, the function returns `none`. The currently available property names
are as follows:

- `id-header-hash`: This property returns a `(buff 32)` value containing the _index block hash_ of a Stacks block.   This hash is globally unique, and is derived
from the block hash and the history of accepted PoX operations.  This is also the block hash value you would pass into `(at-block)`.

- `header-hash`: This property returns a `(buff 32)` value containing the header hash of a Stacks block, given a Stacks chain height.  **WARNING* this hash is
not guaranteed to be globally unique, since the same Stacks block can be mined in different PoX forks.  If you need global uniqueness, you should use `id-header-hash`.

- `time`: This property returns a `uint` value of the block header time field. This is a Unix epoch timestamp in seconds
which roughly corresponds to when the block was mined. For a block mined before epoch 3.0, this timestamp comes from the burnchain block. **Note**: this does not increase monotonically with each block
and block times are accurate only to within two hours. See [BIP113](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0113.mediawiki) for more information.
For a block mined after epoch 3.0, this timestamp comes from the Stacks block header. **Note**: this is the time, according to the miner, when
the mining of this block started, but is not guaranteed to be accurate. This time will be validated by the signers to be:
  - Greater than the timestamp of the previous block
  - At most 15 seconds into the future (according to their own local clocks)

```clarity
(get-stacks-block-info? time u0) ;; Returns (some u1557860301)
(get-stacks-block-info? header-hash u0) ;; Returns (some 0x374708fff7719dd5979ec875d56cd2286f6d3cf7ec317a3b25632aab28ec37bb)
```

### get-tenure-info?

Clarity 3+ · function · `(get-tenure-info? prop-name stacks-block-height)` · in: `TenureInfoPropertyName, uint` · out: `(optional buff) \| (optional uint)`

The `get-tenure-info?` function fetches data for the tenure at the given block height. The
value and type returned are determined by the specified `TenureInfoPropertyName`. If the provided `stacks-block-height` does
not correspond to an existing block prior to the current block, the function returns `none`. The currently available property names
are as follows:

- `burnchain-header-hash`: This property returns a `(buff 32)` value containing the header hash of the burnchain (Bitcoin) block that selected the
tenure at the given height.

- `miner-address`: This property returns a `principal` value corresponding to the miner of the given tenure.  **WARNING** This is not guaranteed to
be the same `principal` that received the block reward, since Stacks 2.1+ supports coinbase transactions that pay the reward to a contract address.  This is merely
the address of the `principal` that produced the tenure.

- `time`: This property returns a `uint` Unix epoch timestamp in seconds which roughly corresponds to when the tenure was started. This timestamp comes
from the burnchain block. **Note**: this does not increase monotonically with each tenure and tenure times are accurate only to within two hours. See
[BIP113](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0113.mediawiki) for more information.

- `vrf-seed`: This property returns a `(buff 32)` value of the VRF seed for the corresponding tenure.

- `block-reward`: This property returns a `uint` value for the total block reward of the indicated tenure.  This value is only available once the reward for
the tenure matures.  That is, the latest `block-reward` value available is at least 101 Stacks blocks in the past (on mainnet).  The reward includes the coinbase,
the anchored tenure's transaction fees, and the shares of the confirmed and produced microblock transaction fees earned by this block's miner.  Note that this value may
be smaller than the Stacks coinbase at this height, because the miner may have been punished with a valid `PoisonMicroblock` transaction in the event that the miner
published two or more microblock stream forks.

- `miner-spend-total`: This property returns a `uint` value for the total number of burnchain tokens (i.e. satoshis) spent by all miners trying to win this tenure.

- `miner-spend-winner`: This property returns a `uint` value for the number of burnchain tokens (i.e. satoshis) spent by the winning miner for this tennure.  Note that
this value is less than or equal to the value for `miner-spend-total` at the same tenure height.

```clarity
(get-tenure-info? time u0) ;; Returns (some u1557860301)
(get-tenure-info? vrf-seed u0) ;; Returns (some 0xf490de2920c8a35fabeb13208852aa28c76f9be9b03a4dd2b3c075f7a26923b4)
```

### hash160

Clarity 1+ · function · `(hash160 value)` · in: `buff\|uint\|int` · out: `(buff 20)`

The `hash160` function computes `RIPEMD160(SHA256(x))` of the inputted value.
If an integer (128 bit) is supplied the hash is computed over the little-endian representation of the
integer.

```clarity
(hash160 0) ;; Returns 0xe4352f72356db555721651aa612e00379167b30f
```

### if

Clarity 1+ · function · `(if bool1 expr1 expr2)` · in: `bool, A, A` · out: `A`

The `if` function admits a boolean argument and two expressions
which must return the same type. In the case that the boolean input is `true`, the
`if` function evaluates and returns `expr1`. If the boolean input is `false`, the
`if` function evaluates and returns `expr2`.

```clarity
(if true 1 2) ;; Returns 1
(if (> 1 2) 1 2) ;; Returns 2
```

### impl-trait

Clarity 1+ · definition · `(impl-trait trait-identifier)` · in: `TraitIdentifier` · out: `Not Applicable`

`impl-trait` can be use for asserting that a contract is fully implementing a given trait.
Additional checks are being performed when the contract is being published, rejecting the deployment if the
contract is violating the trait specification.

Trait identifiers can either be using the sugared syntax (.token-a.token-trait), or be fully qualified
('SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF.token-a.token-trait).

Like other kinds of definition statements, `impl-trait` may only be used at the top level of a smart contract
definition (i.e., you cannot put such a statement in the middle of a function body).

```clarity
(impl-trait 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF.token-a.token-trait)
(define-public (get-balance (account principal))
  (ok u0))
(define-public (transfer? (from principal) (to principal) (amount uint))
  (ok u0))
```

### index-of

Clarity 1+ · function · `(index-of? sequence item)` · in: `sequence_A, A` · out: `(optional uint)`

The `index-of?` function returns the first index at which `item` can be
found, using `is-eq` checks, in the provided sequence.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.
If the target item is not found in the sequence (or if an empty string or buffer is
supplied), this function returns `none`.

In Clarity1, `index-of` must be used (without the `?`). The `?` is added in Clarity2 for consistency -- built-ins that return responses or optionals end in `?`. The Clarity1 spelling is left as an alias in Clarity2 for backwards compatibility.

```clarity
(index-of? "blockstack" "b") ;; Returns (some u0)
(index-of? "blockstack" "k") ;; Returns (some u4)
(index-of? "blockstack" "") ;; Returns none
(index-of? (list 1 2 3 4 5) 6) ;; Returns none
(index-of? 0xfb01 0x01) ;; Returns (some u1)
```

### index-of?

Clarity 2+ · function · `(index-of? sequence item)` · in: `sequence_A, A` · out: `(optional uint)`

The `index-of?` function returns the first index at which `item` can be
found, using `is-eq` checks, in the provided sequence.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.
If the target item is not found in the sequence (or if an empty string or buffer is
supplied), this function returns `none`.

In Clarity1, `index-of` must be used (without the `?`). The `?` is added in Clarity2 for consistency -- built-ins that return responses or optionals end in `?`. The Clarity1 spelling is left as an alias in Clarity2 for backwards compatibility.

```clarity
(index-of? "blockstack" "b") ;; Returns (some u0)
(index-of? "blockstack" "k") ;; Returns (some u4)
(index-of? "blockstack" "") ;; Returns none
(index-of? (list 1 2 3 4 5) 6) ;; Returns none
(index-of? 0xfb01 0x01) ;; Returns (some u1)
```

### int-to-ascii

Clarity 2+ · function · `(int-to-ascii (int\|uint))`

Converts an integer, either `int` or `uint`, to a `string-ascii` string-value representation.

Note: This function is only available starting with Stacks 2.1.

```clarity
(int-to-ascii 1) ;; Returns "1"
(int-to-ascii u1) ;; Returns "1"
(int-to-ascii -1) ;; Returns "-1"
```

### int-to-utf8

Clarity 2+ · function · `(int-to-utf8 (int\|uint))`

Converts an integer, either `int` or `uint`, to a `string-utf8` string-value representation.

Note: This function is only available starting with Stacks 2.1.

```clarity
(int-to-utf8 1) ;; Returns u"1"
(int-to-utf8 u1) ;; Returns u"1"
(int-to-utf8 -1) ;; Returns u"-1"
```

### is-eq

Clarity 1+ · function · `(is-eq v1 v2...)` · in: `A, A, ...` · out: `bool`

Compares the inputted values, returning `true` if they are all equal. Note that
_unlike_ the `(and ...)` function, `(is-eq ...)` will _not_ short-circuit. All values supplied to
is-eq _must_ be the same type.

```clarity
(is-eq 1 1) ;; Returns true
(is-eq true false) ;; Returns false
(is-eq "abc" 234 234) ;; Throws type error
(is-eq "abc" "abc") ;; Returns true
(is-eq 0x0102 0x0102) ;; Returns true
```

### is-err

Clarity 1+ · function · `(is-err value)` · in: `(response A B)` · out: `bool`

`is-err` tests a supplied response value, returning `true` if the response was an `err`,
and `false` if it was an `ok`.

```clarity
(is-err (ok 1)) ;; Returns false
(is-err (err 1)) ;; Returns true
```

### is-in-mainnet

Clarity 2+ · keyword · out: `bool`

Returns a boolean indicating whether or not the code is running on the mainnet

```clarity
(print is-in-mainnet) ;; Will print 'true' if the code is running on the mainnet
```

### is-in-regtest

Clarity 1+ · keyword · out: `bool`

Returns whether or not the code is running in a regression test

```clarity
(print is-in-regtest) ;; Will print 'true' if the code is running in a regression test
```

### is-none

Clarity 1+ · function · `(is-none value)` · in: `(optional A)` · out: `bool`

`is-none` tests a supplied option value, returning `true` if the option value is `none`,
and `false` if it is a `(some ...)`.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(is-none (get id (map-get? names-map { name: "blockstack" }))) ;; Returns false
(is-none (get id (map-get? names-map { name: "non-existant" }))) ;; Returns true
```

### is-ok

Clarity 1+ · function · `(is-ok value)` · in: `(response A B)` · out: `bool`

`is-ok` tests a supplied response value, returning `true` if the response was `ok`,
and `false` if it was an `err`.

```clarity
(is-ok (ok 1)) ;; Returns true
(is-ok (err 1)) ;; Returns false
```

### is-some

Clarity 1+ · function · `(is-some value)` · in: `(optional A)` · out: `bool`

`is-some` tests a supplied option value, returning `true` if the option value is `(some ...)`,
and `false` if it is a `none`.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(is-some (get id (map-get? names-map { name: "blockstack" }))) ;; Returns true
(is-some (get id (map-get? names-map { name: "non-existant" }))) ;; Returns false
```

### is-standard

Clarity 2+ · function · `(is-standard standard-or-contract-principal)`

Tests whether `standard-or-contract-principal` _matches_ the current network
type, and therefore represents a principal that can spend tokens on the current
network type. That is, the network is either of type `mainnet`, or `testnet`.
Only `SPxxxx` and `SMxxxx` _c32check form_ addresses can spend tokens on
a mainnet, whereas only `STxxxx` and `SNxxxx` _c32check forms_ addresses can spend
tokens on a testnet. All addresses can _receive_ tokens, but only principal
_c32check form_ addresses that match the network type can _spend_ tokens on the
network.  This method will return `true` if and only if the principal matches
the network type, and false otherwise.

Note: This function is only available starting with Stacks 2.1.

```clarity
(is-standard 'STB44HYPYAT2BB2QE513NSP81HTMYWBJP02HPGK6) ;; returns true on testnet and false on mainnet
(is-standard 'STB44HYPYAT2BB2QE513NSP81HTMYWBJP02HPGK6.foo) ;; returns true on testnet and false on mainnet
(is-standard 'SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY) ;; returns true on mainnet and false on testnet
(is-standard 'SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY.foo) ;; returns true on mainnet and false on testnet
(is-standard 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; returns false on both mainnet and testnet
```

### keccak256

Clarity 1+ · function · `(keccak256 value)` · in: `buff\|uint\|int` · out: `(buff 32)`

The `keccak256` function computes `KECCAK256(value)` of the inputted value.

Note: this differs from the `NIST SHA-3` (that is, FIPS 202) standard. If an integer (128 bit)
is supplied the hash is computed over the little-endian representation of the integer.

```clarity
(keccak256 0) ;; Returns 0xf490de2920c8a35fabeb13208852aa28c76f9be9b03a4dd2b3c075f7a26923b4
```

### len

Clarity 1+ · function · `(len sequence)` · in: `sequence_A` · out: `uint`

The `len` function returns the length of a given sequence.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`.

```clarity
(len "blockstack") ;; Returns u10
(len (list 1 2 3 4 5)) ;; Returns u5
(len 0x010203) ;; Returns u3
```

### let

Clarity 1+ · function · `(let ((name1 expr1) (name2 expr2) ...) expr-body1 expr-body2 ... expr-body-last)` · in: `((name1 AnyType) (name2 AnyType) ...), AnyType, ... A` · out: `A`

The `let` function accepts a list of `variable name` and `expression` pairs,
evaluating each expression and _binding_ it to the corresponding variable name.
`let` bindings are sequential: when a `let` binding is evaluated, it may refer to prior binding.
The _context_ created by this set of bindings is used for evaluating its body expressions.
The let expression returns the value of the last such body expression.

Note: intermediary statements returning a response type must be checked

```clarity
(let ((a 2) (b (+ 5 6 7))) (print a) (print b) (+ a b)) ;; Returns 20
(let ((a 5) (c (+ a 1)) (d (+ c 1)) (b (+ a c d))) (print a) (print b) (+ a b)) ;; Returns 23
```

### list

Clarity 1+ · function · `(list expr1 expr2 expr3 ...)` · in: `A, ...` · out: `(list A)`

The `list` function constructs a list composed of the inputted values. Each
supplied value must be of the same type.

```clarity
(list (+ 1 2) 4 5) ;; Returns (3 4 5)
```

### log2

Clarity 1+ · function · `(log2 n)`

Returns the power to which the number 2 must be raised to obtain the value `n`, rounded
down to the nearest integer. Fails on a negative numbers.

```clarity
(log2 u8) ;; Returns u3
(log2 8) ;; Returns 3
(log2 u1) ;; Returns u0
(log2 1000) ;; Returns 9
```

### map

Clarity 1+ · function · `(map func sequence_A sequence_B ... sequence_N)` · in: `Function(A, B, ..., N) -> X, sequence_A, sequence_B, ..., sequence_N` · out: `(list X)`

The `map` function applies the function `func` to each corresponding element of the input sequences,
and outputs a _list_ of the same type containing the outputs from those function applications.
Applicable sequence types are `(list A)`, `buff`, `string-ascii` and `string-utf8`,
for which the corresponding element types are, respectively, `A`, `(buff 1)`, `(string-ascii 1)` and `(string-utf8 1)`.
The `func` argument must be a literal function name.

Note: no matter what kind of sequences the inputs are, the output is always a list.

```clarity
(map not (list true false true false)) ;; Returns (false true false true)
(map + (list 1 2 3) (list 1 2 3) (list 1 2 3)) ;; Returns (3 6 9)
(define-private (a-or-b (char (string-utf8 1))) (if (is-eq char u"a") u"a" u"b"))
(map a-or-b u"aca") ;; Returns (u"a" u"b" u"a")
(define-private (zero-or-one (char (buff 1))) (if (is-eq char 0x00) 0x00 0x01))
(map zero-or-one 0x000102) ;; Returns (0x00 0x01 0x01)
```

### map-delete

Clarity 1+ · function · `(map-delete map-name key-tuple)` · in: `MapName, tuple` · out: `bool`

The `map-delete` function removes the value associated with the input key for
the given map. If an item exists and is removed, the function returns `true`.
If a value did not exist for this key in the data map, the function returns `false`.

```clarity
(define-map names-map { name: (string-ascii 10) } { id: int })
(map-insert names-map { name: "blockstack" } { id: 1337 }) ;; Returns true
(map-delete names-map { name: "blockstack" }) ;; Returns true
(map-delete names-map { name: "blockstack" }) ;; Returns false
(map-delete names-map (tuple (name "blockstack"))) ;; Same command, using a shorthand for constructing the tuple
```

### map-get?

Clarity 1+ · function · `(map-get? map-name key-tuple)` · in: `MapName, tuple` · out: `(optional (tuple))`

The `map-get?` function looks up and returns an entry from a contract's data map.
The value is looked up using `key-tuple`.
If there is no value associated with that key in the data map, the function returns a `none` option. Otherwise,
it returns `(some value)`.

```clarity
(define-map names-map { name: (string-ascii 10) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(map-get? names-map (tuple (name "blockstack"))) ;; Returns (some (tuple (id 1337)))
(map-get? names-map { name: "blockstack" }) ;; Same command, using a shorthand for constructing the tuple
```

### map-insert

Clarity 1+ · function · `(map-insert map-name key-tuple value-tuple)` · in: `MapName, tuple_A, tuple_B` · out: `bool`

The `map-insert` function sets the value associated with the input key to the
inputted value if and only if there is not already a value associated with the key in the map.
If an insert occurs, the function returns `true`. If a value already existed for
this key in the data map, the function returns `false`.

Note: the `value-tuple` requires 1 additional byte for storage in the materialized blockchain state,
and therefore the maximum size of a value that may be inserted into a map is MAX_CLARITY_VALUE - 1.

```clarity
(define-map names-map { name: (string-ascii 10) } { id: int })
(map-insert names-map { name: "blockstack" } { id: 1337 }) ;; Returns true
(map-insert names-map { name: "blockstack" } { id: 1337 }) ;; Returns false
(map-insert names-map (tuple (name "blockstack")) (tuple (id 1337))) ;; Same command, using a shorthand for constructing the tuple
```

### map-set

Clarity 1+ · function · `(map-set map-name key-tuple value-tuple)` · in: `MapName, tuple_A, tuple_B` · out: `bool`

The `map-set` function sets the value associated with the input key to the
inputted value. This function performs a _blind_ update; whether or not a value is already associated
with the key, the function overwrites that existing association.

Note: the `value-tuple` requires 1 additional byte for storage in the materialized blockchain state,
and therefore the maximum size of a value that may be inserted into a map is MAX_CLARITY_VALUE - 1.

```clarity
(define-map names-map { name: (string-ascii 10) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 }) ;; Returns true
(map-set names-map (tuple (name "blockstack")) (tuple (id 1337))) ;; Same command, using a shorthand for constructing the tuple
```

### match

Clarity 1+ · function · `(match opt-input some-binding-name some-branch none-branch) \| (match-resp input ok-binding-name ok-branch err-binding-name err-branch)` · in: `(optional A) name expression expression \| (response A B) name expression name expression` · out: `C`

The `match` function is used to test and destructure optional and response types.

If the `input` is an optional, it tests whether the provided
`input` is a `some` or `none` option, and evaluates `some-branch` or
`none-branch` in each respective case.

Within the `some-branch`, the _contained value_ of the `input`
argument is bound to the provided `some-binding-name` name.

Only _one_ of the branches will be evaluated (similar to `if` statements).

If the `input` is a response, it tests whether the provided `input` is
an `ok` or `err` response type, and evaluates `ok-branch` or
`err-branch` in each respective case.

Within the `ok-branch`, the _contained ok value_ of the `input`
argument is bound to the provided `ok-binding-name` name.

Within the `err-branch`, the _contained err value_ of the `input`
argument is bound to the provided `err-binding-name` name.

Only _one_ of the branches will be evaluated (similar to `if` statements).

Note: Type checking requires that the type of both the ok and err parts of the
response object be determinable. For situations in which one of the parts of a response
is untyped, you should use `unwrap-panic` or `unwrap-err-panic` instead of `match`.

```clarity
(define-private (add-10 (x (optional int)))
  (match x
  value (+ 10 value)
  10))
(add-10 (some 5)) ;; Returns 15
(add-10 none) ;; Returns 10

(define-private (add-or-pass-err (x (response int (string-ascii 10))) (to-add int))
  (match x
   value (ok (+ to-add value))
   err-value (err err-value)))
(add-or-pass-err (ok 5) 20) ;; Returns (ok 25)
(add-or-pass-err (err "ERROR") 20) ;; Returns (err "ERROR")
```

### merge

Clarity 1+ · function · `(merge tuple { key1: val1 })` · in: `tuple, tuple` · out: `tuple`

The `merge` function returns a new tuple with the combined fields, without mutating the supplied tuples.

```clarity
(define-map users { id: int } { name: (string-ascii 12), address: (optional principal) })
(map-insert users { id: 1337 } { name: "john", address: none }) ;; Returns true
(let ((user (unwrap-panic (map-get? users { id: 1337 }))))
    (merge user { address: (some 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) })) ;; Returns (tuple (address (some SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF)) (name "john"))
```

### mod

Clarity 1+ · function · `(mod i1 i2)`

Returns the integer remainder from integer dividing `i1` by `i2`. In the event of a division by zero, throws a runtime error.

```clarity
(mod 2 3) ;; Returns 2
(mod 5 2) ;; Returns 1
(mod 7 1) ;; Returns 0
```

### nft-burn?

Clarity 1+ · function · `(nft-burn? asset-class asset-identifier sender)` · in: `AssetName, A, principal` · out: `(response bool uint)`

`nft-burn?` is used to burn an asset that the `sender` principal owns.
The asset must have been defined using `define-non-fungible-token`, and the supplied
`asset-identifier` must be of the same type specified in that definition.

On a successful burn, it returns `(ok true)`. In the event of an unsuccessful burn it
returns one of the following error codes:

* `(err u1)` -- `sender` does not own the specified asset
* `(err u3)` -- the asset specified by `asset-identifier` does not exist

```clarity
(define-non-fungible-token stackaroo (string-ascii 40))
(nft-mint? stackaroo "Roo" 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
(nft-burn? stackaroo "Roo" 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
```

### nft-get-owner?

Clarity 1+ · function · `(nft-get-owner? asset-class asset-identifier)` · in: `AssetName, A` · out: `(optional principal)`

`nft-get-owner?` returns the owner of an asset, identified by `asset-identifier`, or `none` if the asset does not exist.
The asset type must have been defined using `define-non-fungible-token`, and the supplied `asset-identifier` must be of the same type specified in
that definition.

```clarity
(define-non-fungible-token stackaroo (string-ascii 40))
(nft-mint? stackaroo "Roo" 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF)
(nft-get-owner? stackaroo "Roo") ;; Returns (some SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF)
(nft-get-owner? stackaroo "Too") ;; Returns none
```

### nft-mint?

Clarity 1+ · function · `(nft-mint? asset-class asset-identifier recipient)` · in: `AssetName, A, principal` · out: `(response bool uint)`

`nft-mint?` is used to instantiate an asset and set that asset's owner to the `recipient` principal.
The asset must have been defined using `define-non-fungible-token`, and the supplied `asset-identifier` must be of the same type specified in
that definition.

The function returns `(ok true)` if the mint is successful. This function may fail with the error code:

* `(err u1)` -- an asset identified by `asset-identifier` _already exists_

```clarity
(define-non-fungible-token stackaroo (string-ascii 40))
(nft-mint? stackaroo "Roo" 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
```

### nft-transfer?

Clarity 1+ · function · `(nft-transfer? asset-class asset-identifier sender recipient)` · in: `AssetName, A, principal, principal` · out: `(response bool uint)`

`nft-transfer?` is used to change the owner of an asset identified by `asset-identifier`
from `sender` to `recipient`. The `asset-class` must have been defined by `define-non-fungible-token` and `asset-identifier`
must be of the type specified in that definition. In contrast to `stx-transfer?`, any user can transfer the asset.
When used, relevant guards need to be added.

This function returns (ok true) if the transfer is successful. In the event of an unsuccessful transfer it returns
one of the following error codes:

* `(err u1)` -- `sender` does not own the asset
* `(err u2)` -- `sender` and `recipient` are the same principal
* `(err u3)` -- asset identified by asset-identifier does not exist

```clarity
(define-non-fungible-token stackaroo (string-ascii 40))
(nft-mint? stackaroo "Roo" 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR)
(nft-transfer? stackaroo "Roo" 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (ok true)
(nft-transfer? stackaroo "Roo" 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (err u1)
(nft-transfer? stackaroo "Stacka" 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF) ;; Returns (err u3)
```

### none

Clarity 1+ · keyword · out: `(optional ?)`

Represents the _none_ option indicating no value for a given optional (analogous to a null value).

```clarity
(define-public (only-if-positive (a int))
  (if (> a 0)
      (some a)
      none))
(only-if-positive 4) ;; Returns (some 4)
(only-if-positive (- 3)) ;; Returns none
```

### not

Clarity 1+ · function · `(not b1)`

Returns the inverse of the boolean input.

```clarity
(not true) ;; Returns false
(not (is-eq 1 2)) ;; Returns true
```

### ok

Clarity 1+ · function · `(ok value)` · in: `A` · out: `(response A B)`

The `ok` function constructs a response type from the input value. Use `ok` for
creating return values in public functions. An _ok_ value indicates that any database changes during
the processing of the function should materialize.

```clarity
(ok 1) ;; Returns (ok 1)
```

### or

Clarity 1+ · function · `(or b1 b2 ...)`

Returns `true` if any boolean inputs are `true`. Importantly, the supplied arguments are
evaluated in-order and lazily. Lazy evaluation means that if one of the arguments returns `true`, the function
short-circuits, and no subsequent arguments are evaluated.

```clarity
(or true false) ;; Returns true
(or (is-eq (+ 1 2) 1) (is-eq 4 4)) ;; Returns true
(or (is-eq (+ 1 2) 1) (is-eq 3 4)) ;; Returns false
(or (is-eq (+ 1 2) 3) (is-eq 4 4)) ;; Returns true
```

### pow

Clarity 1+ · function · `(pow i1 i2)`

Returns the result of raising `i1` to the power of `i2`. In the event of an _overflow_, throws a runtime error.
Note: Corner cases are handled with the following rules:
  * if both `i1` and `i2` are `0`, return `1`
  * if `i1` is `1`, return `1`
  * if `i1` is `0`, return `0`
  * if `i2` is negative or greater than `u32::MAX`, throw a runtime error

```clarity
(pow 2 3) ;; Returns 8
(pow 2 2) ;; Returns 4
(pow 7 1) ;; Returns 7
```

### principal-construct?

Clarity 2+ · function · `(principal-construct? (buff 1) (buff 20) [(string-ascii 40)])` · in: `(buff 1), (buff 20), [(string-ascii 40)]` · out: `(response principal { error_code: uint, value: (optional principal) })`

A principal value represents either a set of keys, or a smart contract.
The former, called a _standard principal_,
is encoded as a `(buff 1)` *version byte*, indicating the type of account
and the type of network that this principal can spend tokens on,
and a `(buff 20)` *public key hash*, characterizing the principal's unique identity.
The latter, a _contract principal_, is encoded as a standard principal concatenated with
a `(string-ascii 40)` *contract name* that identifies the code body.

The `principal-construct?` function allows users to create either standard or contract principals,
depending on which form is used.  To create a standard principal,
`principal-construct?` would be called with two arguments: it
takes as input a `(buff 1)` which encodes the principal address's
`version-byte`, a `(buff 20)` which encodes the principal address's `hash-bytes`.
To create a contract principal, `principal-construct?` would be called with
three arguments: the `(buff 1)` and `(buff 20)` to represent the standard principal
that created the contract, and a `(string-ascii 40)` which encodes the contract's name.
On success, this function returns either a standard principal or contract principal,
depending on whether or not the third `(string-ascii 40)` argument is given.

This function returns a `Response`. On success, the `ok` value is a `Principal`.
The `err` value is a value tuple with the form `{ error_code: uint, value: (optional principal) }`.

If the single-byte `version-byte` is in the valid range `0x00` to `0x1f`, but is not an appropriate
version byte for the current network, then the error will be `u0`, and `value` will contain
`(some principal)`, where the wrapped value is the principal.  If the `version-byte` is not in this range,
however, then the `value` will be `none`.

If the `version-byte` is a `buff` of length 0, if the single-byte `version-byte` is a
value greater than `0x1f`, or the `hash-bytes` is a `buff` of length not equal to 20, then `error_code`
will be `u1` and `value` will be `none`.

If a name is given, and the name is either an empty string or contains ASCII characters
that are not allowed in contract names, then `error_code` will be `u2`.

Note: This function is only available starting with Stacks 2.1.

```clarity
(principal-construct? 0x1a 0xfa6bf38ed557fe417333710d6033e9419391a320) ;; Returns (ok ST3X6QWWETNBZWGBK6DRGTR1KX50S74D3425Q1TPK)
(principal-construct? 0x1a 0xfa6bf38ed557fe417333710d6033e9419391a320 "foo") ;; Returns (ok ST3X6QWWETNBZWGBK6DRGTR1KX50S74D3425Q1TPK.foo)
(principal-construct? 0x16 0xfa6bf38ed557fe417333710d6033e9419391a320) ;; Returns (err (tuple (error_code u0) (value (some SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY))))
(principal-construct? 0x16 0xfa6bf38ed557fe417333710d6033e9419391a320 "foo") ;; Returns (err (tuple (error_code u0) (value (some SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY.foo))))
(principal-construct? 0x   0xfa6bf38ed557fe417333710d6033e9419391a320) ;; Returns (err (tuple (error_code u1) (value none)))
(principal-construct? 0x16 0xfa6bf38ed557fe417333710d6033e9419391a3)   ;; Returns (err (tuple (error_code u1) (value none)))
(principal-construct? 0x20 0xfa6bf38ed557fe417333710d6033e9419391a320) ;; Returns (err (tuple (error_code u1) (value none)))
(principal-construct? 0x1a 0xfa6bf38ed557fe417333710d6033e9419391a320 "") ;; Returns (err (tuple (error_code u2) (value none)))
(principal-construct? 0x1a 0xfa6bf38ed557fe417333710d6033e9419391a320 "foo[") ;; Returns (err (tuple (error_code u2) (value none)))
```

### principal-destruct?

Clarity 2+ · function · `(principal-destruct? principal-address)`

A principal value represents either a set of keys, or a smart contract.
The former, called a _standard principal_,
is encoded as a `(buff 1)` *version byte*, indicating the type of account
and the type of network that this principal can spend tokens on,
and a `(buff 20)` *public key hash*, characterizing the principal's unique identity.
The latter, a _contract principal_, is encoded as a standard principal concatenated with
a `(string-ascii 40)` *contract name* that identifies the code body.

`principal-destruct?` will decompose a principal into its component parts: either`{version-byte, hash-bytes}`
for standard principals, or `{version-byte, hash-bytes, name}` for contract principals.

This method returns a `Response` that wraps this data as a tuple.

If the version byte of `principal-address` matches the network (see `is-standard`), then this method
returns the pair as its `ok` value.

If the version byte of `principal-address` does not match the network, then this method
returns the pair as its `err` value.

In both cases, the value itself is a tuple containing three fields: a `version` value as a `(buff 1)`,
a `hash-bytes` value as a `(buff 20)`, and a `name` value as an `(optional (string-ascii 40))`.  The `name`
field will only be `(some ..)` if the principal is a contract principal.

Starting in Stacks 4.1, if the contract name is longer than 40 characters, this function
aborts the transaction with a runtime error. Such principals can only have been created
before Stacks 4.1.

Note: This function is only available starting with Stacks 2.1.

```clarity
(principal-destruct? 'STB44HYPYAT2BB2QE513NSP81HTMYWBJP02HPGK6) ;; Returns (ok (tuple (hash-bytes 0x164247d6f2b425ac5771423ae6c80c754f7172b0) (name none) (version 0x1a)))
(principal-destruct? 'STB44HYPYAT2BB2QE513NSP81HTMYWBJP02HPGK6.foo) ;; Returns (ok (tuple (hash-bytes 0x164247d6f2b425ac5771423ae6c80c754f7172b0) (name (some "foo")) (version 0x1a)))
(principal-destruct? 'SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY) ;; Returns (err (tuple (hash-bytes 0xfa6bf38ed557fe417333710d6033e9419391a320) (name none) (version 0x16)))
(principal-destruct? 'SP3X6QWWETNBZWGBK6DRGTR1KX50S74D3433WDGJY.foo) ;; Returns (err (tuple (hash-bytes 0xfa6bf38ed557fe417333710d6033e9419391a320) (name (some "foo")) (version 0x16)))
```

### principal-of?

Clarity 1+ · function · `(principal-of? public-key)` · in: `(buff 33)` · out: `(response principal uint)`

The `principal-of?` function returns the principal derived from the provided public key.
This function may fail with the error code:

* `(err u1)` -- `public-key` is invalid

Note: Before Stacks 2.1, this function has a bug, in that the principal returned would always
be a testnet single-signature principal, even if the function were run on the mainnet. Starting
with Stacks 2.1, this bug is fixed, so that this function will return a principal suited to
the network it is called on. In particular, if this is called on the mainnet, it will
return a single-signature mainnet principal.

```clarity
(principal-of? 0x03adb8de4bfb65db2cfd6120d55c6526ae9c52e675db7e47308636534ba7786110) ;; Returns (ok ST1AW6EKPGT61SQ9FNVDS17RKNWT8ZP582VF9HSCP)
```

### print

Clarity 1+ · function · `(print expr)` · in: `A` · out: `A`

The `print` function evaluates and returns its input expression. On Stacks Core
nodes configured for development (as opposed to production mining nodes), this function prints the resulting value to `STDOUT` (standard output).

```clarity
(print (+ 1 2 3)) ;; Returns 6
```

### replace-at?

Clarity 2+ · function · `(replace-at? sequence index element)` · in: `sequence_A, uint, A` · out: `(optional sequence_A)`

The `replace-at?` function takes in a sequence, an index, and an element,
and returns a new sequence with the data at the index position replaced with the given element.
The given element's type must match the type of the sequence, and must correspond to a single
index of the input sequence. The return type on success is the same type as the input sequence.

If the provided index is out of bounds, this function returns `none`.

```clarity
(replace-at? u"ab" u1 u"c") ;; Returns (some u"ac")
(replace-at? 0x00112233 u2 0x44) ;; Returns (some 0x00114433)
(replace-at? "abcd" u3 "e") ;; Returns (some "abce")
(replace-at? (list 1) u0 10) ;; Returns (some (10))
(replace-at? (list (list 1) (list 2)) u0 (list 33)) ;; Returns (some ((33) (2)))
(replace-at? (list 1 2) u3 4) ;; Returns none
```

### restrict-assets?

Clarity 4+ · function · `(restrict-assets? asset-owner ((with-stx\|with-ft\|with-nft\|with-stacking\|with-staking\|with-pox)*) expr-body1 expr-body2 ... expr-body-last)` · in: `principal, ((Allowance){0,128}), AnyType, ... A` · out: `(response A int)`

Executes the body expressions, then checks the asset
outflows against the granted allowances, in declaration order. If any
allowance is violated, the body expressions are reverted, an error is
returned, and an event is emitted with the full details of the violation to
help with debugging. Note that the `asset-owner` and allowance setup
expressions are evaluated before executing the body expressions. The final
body expression cannot return a `response` value in order to avoid returning
a nested `response` value from `restrict-assets?` (nested responses are
error-prone). Returns:
* `(ok x)` if the outflows are within the allowances, where `x` is the
    result of the final body expression and has type `A`.
* `(err index)` if an allowance was violated, where `index` is the 0-based
    index of the first violated allowance in the list of granted allowances,
    or `u128` if an asset with no allowance caused the violation.

```clarity
(restrict-assets? tx-sender ()
  (+ u1 u2)
) ;; Returns (ok u3)
(restrict-assets? tx-sender ()
  (try! (stx-transfer? u50 tx-sender 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM))
) ;; Returns (err u128)
```

### secp256k1-decompress?

Clarity 6+ · function · `(secp256k1-decompress? public-key)` · in: `(buff 33)` · out: `(response (buff 65) uint)`

The `secp256k1-decompress?` function decompresses the provided (compressed) public key.
    Returns the uncompressed public key as a 65-byte buffer on success. This function may fail with the error code:
    - `(err u1)`: invalid compressed public-key.

```clarity
(secp256k1-decompress? 0x0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352)
    ;; Returns (ok 0x0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b23522cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6)
```

### secp256k1-recover?

Clarity 1+ · function · `(secp256k1-recover? message-hash signature)` · in: `(buff 32), (buff 65)` · out: `(response (buff 33) uint)`

The `secp256k1-recover?` function recovers the public key used to sign the hash, `message-hash`, typically
a sha256 hash, with the provided `signature`. The signature includes 64 bytes plus an additional recovery id (00..03) for a total of 65 bytes.
On success, it returns the public key as a 33-byte buffer. This function may fail with one of the following error codes:

* `(err u1)` - the signature does not match the message hash
* `(err u2)` - the signature is invalid

```clarity
(secp256k1-recover? 0xde5b9eb9e7c5592930eb2e30a01369c36586d872082ed8181ee83d2a0ec20f04
 0x8738487ebe69b93d8e51583be8eee50bb4213fc49c767d329632730cc193b873554428fc936ca3569afc15f1c9365f6591d6251a89fee9c9ac661116824d3a1301)
 ;; Returns (ok 0x03adb8de4bfb65db2cfd6120d55c6526ae9c52e675db7e47308636534ba7786110)
```

### secp256k1-verify

Clarity 1+ · function · `(secp256k1-verify message-hash signature public-key)` · in: `(buff 32), (buff 64) \| (buff 65), (buff 33)` · out: `bool`

The `secp256k1-verify` function verifies that the provided signature of the message-hash
was signed with the private key that generated the public key.
The `message-hash` is typically the `sha256` of a message.
The signature includes 64 bytes plus an optional additional recovery id (00..03) for a total of 64 or 65 bytes.
High-S signatures are rejected to enforce the canonical low-S form and prevent malleable signatures.

```clarity
(secp256k1-verify 0xde5b9eb9e7c5592930eb2e30a01369c36586d872082ed8181ee83d2a0ec20f04
 0x8738487ebe69b93d8e51583be8eee50bb4213fc49c767d329632730cc193b873554428fc936ca3569afc15f1c9365f6591d6251a89fee9c9ac661116824d3a1301
 0x03adb8de4bfb65db2cfd6120d55c6526ae9c52e675db7e47308636534ba7786110) ;; Returns true
(secp256k1-verify 0xde5b9eb9e7c5592930eb2e30a01369c36586d872082ed8181ee83d2a0ec20f04
 0x8738487ebe69b93d8e51583be8eee50bb4213fc49c767d329632730cc193b873554428fc936ca3569afc15f1c9365f6591d6251a89fee9c9ac661116824d3a13
 0x03adb8de4bfb65db2cfd6120d55c6526ae9c52e675db7e47308636534ba7786110) ;; Returns true
(secp256k1-verify 0x0000000000000000000000000000000000000000000000000000000000000000
 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
 0x03adb8de4bfb65db2cfd6120d55c6526ae9c52e675db7e47308636534ba7786110) ;; Returns false
```

### secp256r1-verify

Clarity 4+ · function · `(secp256r1-verify message-hash signature public-key)` · in: `(buff 32), (buff 64), (buff 33)` · out: `bool`

The `secp256r1-verify` function verifies that the provided signature of the message-hash
was signed with the private key that generated the public key.
In Clarity 4, the `message-hash` is SHA256 hashed again internally before verification (i.e. double SHA256)
but in Clarity 5 and later, the `message-hash` is used directly without additional hashing.
`message-hash` is typically the `sha256` of a message and `signature` is the raw 64-byte signature.
High-S signatures are allowed.
Note that this is NOT the Bitcoin (or default Stacks) signature scheme, secp256k1, but rather the
NIST P-256 curve (also known as secp256r1).

```clarity
(secp256r1-verify 0x44acf6b7e36c1342c2c5897204fe09504e1e2efb1a900377dbc4e7a6a133ec56
    0xf3ac8061b514795b8843e3d6629527ed2afd6b1f6a555a7acabb5e6f79c8c2ac8bf77819ca05a6b2786c76262bf7371cef97b218e96f175a3ccdda2acc058903
    0x031ccbe91c075fc7f4f033bfa248db8fccd3565de94bbfb12f3c59ff46c271bf83) ;; Returns true
(secp256r1-verify 0x0000000000000000000000000000000000000000000000000000000000000000
    0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    0x031ccbe91c075fc7f4f033bfa248db8fccd3565de94bbfb12f3c59ff46c271bf83) ;; Returns false
```

### sha256

Clarity 1+ · function · `(sha256 value)` · in: `buff\|uint\|int` · out: `(buff 32)`

The `sha256` function computes `SHA256(x)` of the inputted value.
If an integer (128 bit) is supplied the hash is computed over the little-endian representation of the
integer.

```clarity
(sha256 0) ;; Returns 0x374708fff7719dd5979ec875d56cd2286f6d3cf7ec317a3b25632aab28ec37bb
```

### sha512

Clarity 1+ · function · `(sha512 value)` · in: `buff\|uint\|int` · out: `(buff 64)`

The `sha512` function computes `SHA512(x)` of the inputted value.
If an integer (128 bit) is supplied the hash is computed over the little-endian representation of the
integer.

```clarity
(sha512 1) ;; Returns 0x6fcee9a7b7a7b821d241c03c82377928bc6882e7a08c78a4221199bfa220cdc55212273018ee613317c8293bb8d1ce08d1e017508e94e06ab85a734c99c7cc34
```

### sha512/256

Clarity 1+ · function · `(sha512/256 value)` · in: `buff\|uint\|int` · out: `(buff 32)`

The `sha512/256` function computes `SHA512/256(x)` (the SHA512 algorithm with the 512/256 initialization vector, truncated
to 256 bits) of the inputted value.
If an integer (128 bit) is supplied the hash is computed over the little-endian representation of the
integer.

```clarity
(sha512/256 1) ;; Returns 0x515a7e92e7c60522db968d81ff70b80818fc17aeabbec36baf0dda2812e94a86
```

### slice?

Clarity 2+ · function · `(slice? sequence left-position right-position)` · in: `sequence_A, uint, uint` · out: `(optional sequence_A)`

The `slice?` function attempts to return a sub-sequence of that starts at `left-position` (inclusive), and
ends at `right-position` (non-inclusive).
If `left_position`==`right_position`, the function returns an empty sequence.
If either `left_position` or `right_position` are out of bounds OR if `right_position` is less than
`left_position`, the function returns `none`.

```clarity
(slice? "blockstack" u5 u10) ;; Returns (some "stack")
(slice? (list 1 2 3 4 5) u5 u9) ;; Returns none
(slice? (list 1 2 3 4 5) u3 u4) ;; Returns (some (4))
(slice? "abcd" u1 u3) ;; Returns (some "bc")
(slice? "abcd" u2 u2) ;; Returns (some "")
(slice? "abcd" u3 u1) ;; Returns none
```

### some

Clarity 1+ · function · `(some value)` · in: `A` · out: `(optional A)`

The `some` function constructs a `optional` type from the input value.

```clarity
(some 1) ;; Returns (some 1)
(is-none (some 2)) ;; Returns false
```

### sqrti

Clarity 1+ · function · `(sqrti n)`

Returns the largest integer that is less than or equal to the square root of `n`.
Fails on a negative numbers.

```clarity
(sqrti u11) ;; Returns u3
(sqrti 1000000) ;; Returns 1000
(sqrti u1) ;; Returns u1
(sqrti 0) ;; Returns 0
```

### stacks-block-height

Clarity 3+ · keyword · out: `uint`

Returns the current block height of the Stacks blockchain.

```clarity
(<= stacks-block-height u500000) ;; returns true if the current block-height has not passed 500,000 blocks.
```

### stacks-block-time

Clarity 4+ · keyword · out: `uint`

> **info:** This same timestamp can also be retrieved for previous blocks using `(get-stacks-block-info? time height)`, which exists since Clarity 3, but cannot be used for the current block.

Returns the Unix timestamp (in seconds) of the current Stacks block. Introduced
in Clarity 4. Provides access to the timestamp of the current block, which is
not available with `get-stacks-block-info?`.

```clarity
(>= stacks-block-time u1755820800) ;; returns true if current block timestamp is at or after 2025-07-22.
```

### string-to-int?

Clarity 2+ · function · `(string-to-int? (string-ascii\|string-utf8))`

Converts a string, either `string-ascii` or `string-utf8`, to an optional-wrapped signed integer.
If the input string does not represent a valid integer, then the function returns `none`. Otherwise it returns
an integer wrapped in `some`.

Note: This function is only available starting with Stacks 2.1.

```clarity
(string-to-int? "1") ;; Returns (some 1)
(string-to-int? u"-1") ;; Returns (some -1)
(string-to-int? "a") ;; Returns none
```

### string-to-uint?

Clarity 2+ · function · `(string-to-uint? (string-ascii\|string-utf8))`

Converts a string, either `string-ascii` or `string-utf8`, to an optional-wrapped unsigned integer.
If the input string does not represent a valid integer, then the function returns `none`. Otherwise it returns
an unsigned integer wrapped in `some`.

Note: This function is only available starting with Stacks 2.1.

```clarity
(string-to-uint? "1") ;; Returns (some u1)
(string-to-uint? u"1") ;; Returns (some u1)
(string-to-uint? "a") ;; Returns none
```

### stx-account

Clarity 2+ · function · `(stx-account owner)`

`stx-account` is used to query the STX account of the `owner` principal.

This function returns a tuple with the canonical account representation for an STX account.
This includes the current amount of unlocked STX, the current amount of locked STX, and the
unlock height for any locked STX, all denominated in microstacks.

```clarity
(stx-account 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns (tuple (locked u0) (unlock-height u0) (unlocked u0))
(stx-account tx-sender) ;; Returns (tuple (locked u0) (unlock-height u0) (unlocked u1000))
```

### stx-burn?

Clarity 1+ · function · `(stx-burn? amount sender)`

`stx-burn?` decreases the `sender` principal's STX holdings by `amount`,
specified in microstacks, by destroying the STX. The `sender` principal _must_ be equal to the current
context's `tx-sender`.

This function returns (ok true) if the burn is successful. In the event of an unsuccessful burn it returns
one of the following error codes:

* `(err u1)` -- `sender` does not have enough balance to burn
* `(err u3)` -- amount to burn is non-positive
* `(err u4)` -- the `sender` principal is not the current `tx-sender`

```clarity
(stx-burn? u60 tx-sender) ;; Returns (ok true)
(stx-burn? u50 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns (err u4)
```

### stx-get-balance

Clarity 1+ · function · `(stx-get-balance owner)`

`stx-get-balance` is used to query the STX balance of the `owner` principal.

This function returns the (unlocked) STX balance, in microstacks (1 STX = 1,000,000 microstacks), of the
`owner` principal. The result is the same as `(get unlocked (stx-account user))`.
In the event that the `owner` principal isn't materialized, it returns 0.

```clarity
(stx-get-balance 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns u0
(stx-get-balance tx-sender) ;; Returns u1000
```

### stx-liquid-supply

Clarity 1+ · keyword · out: `uint`

Returns the total number of micro-STX (uSTX) that are liquid in the system as of this block.

```clarity
(print stx-liquid-supply) ;; Will print out the total number of liquid uSTX
```

### stx-transfer-memo?

Clarity 2+ · function · `(stx-transfer-memo? amount sender recipient memo)` · in: `uint, principal, principal, buff` · out: `(response bool uint)`

`stx-transfer-memo?` is similar to `stx-transfer?`, except that it adds a `memo` field.

This function returns (ok true) if the transfer is successful, or, on an error, returns the same codes as `stx-transfer?`.

```clarity
(stx-transfer-memo? u60 tx-sender 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR 0x010203) ;; Returns (ok true)
```

### stx-transfer?

Clarity 1+ · function · `(stx-transfer? amount sender recipient)` · in: `uint, principal, principal, buff` · out: `(response bool uint)`

`stx-transfer?` is used to increase the STX balance for the `recipient` principal
by debiting the `sender` principal by `amount`, specified in microstacks. The `sender` principal
 _must_ be equal to the current context's `tx-sender`.

This function returns (ok true) if the transfer is successful. In the event of an unsuccessful transfer it returns
one of the following error codes:

* `(err u1)` -- `sender` does not have enough balance to transfer
* `(err u2)` -- `sender` and `recipient` are the same principal
* `(err u3)` -- amount to send is non-positive
* `(err u4)` -- the `sender` principal is not the current `tx-sender`

```clarity
(stx-transfer? u60 tx-sender 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns (ok true)
(stx-transfer? u60 tx-sender 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns (ok true)
(stx-transfer? u50 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR tx-sender) ;; Returns (err u4)
```

### tenure-height

Clarity 3+ · keyword · out: `uint`

Returns the number of tenures that have passed.
At the start of epoch 3.0, `tenure-height` will return the same value as `block-height`, then it will continue to increase as each tenures passes.

```clarity
(< tenure-height u140000) ;; returns true if the current tenure-height has passed 140,000 blocks.
```

### to-ascii?

Clarity 4+ · function · `(to-ascii? value)` · in: `int\|uint\|bool\|principal\|(buff 524284)\|(string-utf8 1048571)` · out: `(response (string-ascii 1048571) uint)`

The `to-ascii?` function converts the input value to its ASCII representation.
If the input is a `string-utf8`, it will fail with `(err u1)` if the string contains non-ASCII
characters.

```clarity
(to-ascii? 123) ;; Returns (ok "123")
(to-ascii? u456) ;; Returns (ok "u456")
(to-ascii? false) ;; Returns (ok "false")
(to-ascii? 'SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4) ;; Returns (ok "SM3VDXK3WZZSA84XXFKAFAF15NNZX32CTSG82JFQ4")
(to-ascii? 0x00112233) ;; Returns (ok "0x00112233")
(to-ascii? u"An ASCII smiley face: :)") ;; Returns (ok "An ASCII smiley face: :)")
(to-ascii? u"A smiley face emoji: \u{1F600}") ;; Returns (err u1)
```

### to-consensus-buff?

Clarity 2+ · function · `(to-consensus-buff? value)` · in: `any` · out: `(optional buff)`

`to-consensus-buff?` is a special function that will serialize any
Clarity value into a buffer, using the SIP-005 serialization of the
Clarity value. Not all values can be serialized: some value's
consensus serialization is too large to fit in a Clarity buffer (this
is because of the type prefix in the consensus serialization).

If the value cannot fit as serialized into the maximum buffer size,
this returns `none`, otherwise, it will be
`(some consensus-serialized-buffer)`. During type checking, the
analyzed type of the result of this method will be the maximum possible
consensus buffer length based on the inferred type of the supplied value.

```clarity
(to-consensus-buff? 1) ;; Returns (some 0x0000000000000000000000000000000001)
(to-consensus-buff? u1) ;; Returns (some 0x0100000000000000000000000000000001)
(to-consensus-buff? true) ;; Returns (some 0x03)
(to-consensus-buff? false) ;; Returns (some 0x04)
(to-consensus-buff? none) ;; Returns (some 0x09)
(to-consensus-buff? 'SZ2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKQ9H6DPR) ;; Returns (some 0x051fa46ff88886c2ef9762d970b4d2c63678835bd39d)
(to-consensus-buff? { abc: 3, def: 4 }) ;; Returns (some 0x0c00000002036162630000000000000000000000000000000003036465660000000000000000000000000000000004)
```

### to-int

Clarity 1+ · function · `(to-int u)`

Tries to convert the `uint` argument to an `int`. Will cause a runtime error and abort if the supplied argument is >= `pow(2, 127)`

```clarity
(to-int u238) ;; Returns 238
```

### to-uint

Clarity 1+ · function · `(to-uint i)`

Tries to convert the `int` argument to a `uint`. Will cause a runtime error and abort if the supplied argument is negative.

```clarity
(to-uint 238) ;; Returns u238
```

### true

Clarity 1+ · keyword · out: `bool`

Boolean true constant.

```clarity
(and true false) ;; Evaluates to false
(or false true)  ;; Evaluates to true
```

### try!

Clarity 1+ · function · `(try! option-input)` · in: `(optional A) \| (response A B)` · out: `A`

The `try!` function attempts to 'unpack' the first argument: if the argument is
an option type, and the argument is a `(some ...)` option, `try!` returns the inner value of the
option. If the argument is a response type, and the argument is an `(ok ...)` response, `try!` returns
 the inner value of the `ok`. If the supplied argument is either an `(err ...)` or a `none` value,
`try!` _returns_ either `none` or the `(err ...)` value from the current function and exits the current control-flow.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(try! (map-get? names-map { name: "blockstack" })) ;; Returns (tuple (id 1337))
(define-private (checked-even (x int))
  (if (is-eq (mod x 2) 0)
      (ok x)
      (err false)))
(define-private (double-if-even (x int))
  (ok (* 2 (try! (checked-even x)))))
(double-if-even 10) ;; Returns (ok 20)
(double-if-even 3) ;; Returns (err false)
```

### tuple

Clarity 1+ · function · `(tuple (key0 expr0) (key1 expr1) ...)` · in: `(key-name A), (key-name-2 B), ...` · out: `(tuple (key-name A) (key-name-2 B) ...)`

> **info:** As of Epoch 4.1, tuples that must share one type, such as the two branches of `if`, the arguments of `is-eq` or the elements of a `list`, must have the same fields. Earlier epochs could drop fields that only one of the tuples had.

The `tuple` special form constructs a typed tuple from the supplied key and expression pairs.
A `get` function can use typed tuples as input to select specific values from a given tuple.
Key names may not appear multiple times in the same tuple definition. Supplied expressions are evaluated and
associated with the expressions' paired key name.

There is a shorthand using curly brackets of the form {key0: expr0, key1: expr, ...}

```clarity
(tuple (name "blockstack") (id 1337)) ;; using tuple
    {name: "blockstack", id: 1337} ;; using curly brackets
```

### tx-sender

Clarity 1+ · keyword · out: `principal`

> **warning:** Use caution when leveraging tx-sender, as based on the design, you can unintentionally introduce attack surface area. [Read more](https://www.setzeus.com/community-blog-posts/clarity-carefully-tx-sender).

Additional security reading: [100proof's NFT callback analysis](https://100proof.org/a-questionable-design-choice.html). See [A01](../../clarity-security/references/patterns.md#a01-sender-authority-forwarded-through-an-attacker) for listing changes that asset postconditions do not prevent.

Returns the original sender of the current transaction, or if `as-contract` was called to modify the sending context, it returns that
contract principal.

```clarity
(print tx-sender) ;; Will print out a Stacks address of the transaction sender
```

### tx-sponsor?

Clarity 2+ · keyword · out: `optional principal`

Returns the sponsor of the current transaction if there is a sponsor, otherwise returns None.

```clarity
(print tx-sponsor?) ;; Will print out an optional value containing the Stacks address of the transaction sponsor
```

### unwrap!

Clarity 1+ · function · `(unwrap! option-input thrown-value)` · in: `(optional A) \| (response A B), C` · out: `A`

The `unwrap!` function attempts to 'unpack' the first argument: if the argument is
an option type, and the argument is a `(some ...)` option, `unwrap!` returns the inner value of the
option. If the argument is a response type, and the argument is an `(ok ...)` response, `unwrap!` returns
 the inner value of the `ok`. If the supplied argument is either an `(err ...)` or a `none` value,
`unwrap!` _returns_ `thrown-value` from the current function and exits the current control-flow.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(define-private (get-name-or-err (name (string-ascii 12)))
  (let ((raw-name (unwrap! (map-get? names-map { name: name }) (err 1))))
       (ok raw-name)))

(get-name-or-err "blockstack") ;; Returns (ok (tuple (id 1337)))
(get-name-or-err "non-existant") ;; Returns (err 1)
```

### unwrap-err!

Clarity 1+ · function · `(unwrap-err! response-input thrown-value)` · in: `(response A B), C` · out: `B`

The `unwrap-err!` function attempts to 'unpack' the first argument: if the argument
is an `(err ...)` response, `unwrap-err!` returns the inner value of the `err`.
If the supplied argument is an `(ok ...)` value,
`unwrap-err!` _returns_ `thrown-value` from the current function and exits the current control-flow.

```clarity
(unwrap-err! (err 1) false) ;; Returns 1
```

### unwrap-err-panic

Clarity 1+ · function · `(unwrap-err-panic response-input)` · in: `(response A B)` · out: `B`

The `unwrap-err` function attempts to 'unpack' the first argument: if the argument
is an `(err ...)` response, `unwrap` returns the inner value of the `err`.
If the supplied argument is an `(ok ...)` value,
`unwrap-err` throws a runtime error, aborting any further processing of the current transaction.

```clarity
(unwrap-err-panic (err 1)) ;; Returns 1
(unwrap-err-panic (ok 1)) ;; Throws a runtime exception
```

### unwrap-panic

Clarity 1+ · function · `(unwrap-panic option-input)` · in: `(optional A) \| (response A B)` · out: `A`

The `unwrap` function attempts to 'unpack' its argument: if the argument is
an option type, and the argument is a `(some ...)` option, this function returns the inner value of the
option. If the argument is a response type, and the argument is an `(ok ...)` response, it returns
 the inner value of the `ok`. If the supplied argument is either an `(err ...)` or a `none` value,
`unwrap` throws a runtime error, aborting any further processing of the current transaction.

```clarity
(define-map names-map { name: (string-ascii 12) } { id: int })
(map-set names-map { name: "blockstack" } { id: 1337 })
(unwrap-panic (map-get? names-map { name: "blockstack" })) ;; Returns (tuple (id 1337))
(unwrap-panic (map-get? names-map { name: "non-existant" })) ;; Throws a runtime exception
```

### use-trait

Clarity 1+ · definition · `(use-trait trait-alias trait-identifier)` · in: `VarName, TraitIdentifier` · out: `Not Applicable`

`use-trait` is used to bring a trait, defined in another contract, to the current contract. Subsequent
references to an imported trait are signaled with the syntax `<trait-alias>`.

Traits import are defined with a name, used as an alias, and a trait identifier. Trait identifiers can either be
using the sugared syntax (.token-a.token-trait), or be fully qualified ('SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF.token-a.token-trait).

Like other kinds of definition statements, `use-trait` may only be used at the top level of a smart contract
definition (i.e., you cannot put such a statement in the middle of a function body).

```clarity
(use-trait token-a-trait 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF.token-a.token-trait)
(define-public (forward-get-balance (user principal) (contract <token-a-trait>))
  (begin
    (ok 1)))
```

### var-get

Clarity 1+ · function · `(var-get var-name)` · in: `VarName` · out: `A`

The `var-get` function looks up and returns an entry from a contract's data map.
The value is looked up using `var-name`.

```clarity
(define-data-var cursor int 6)
(var-get cursor) ;; Returns 6
```

### var-set

Clarity 1+ · function · `(var-set var-name expr1)` · in: `VarName, AnyType` · out: `bool`

The `var-set` function sets the value associated with the input variable to the
inputted value. The function always returns `true`.

```clarity
(define-data-var cursor int 6)
(var-get cursor) ;; Returns 6
(var-set cursor (+ (var-get cursor) 1)) ;; Returns true
(var-get cursor) ;; Returns 7
```

### verify-merkle-proof

Clarity 6+ · function · `(verify-merkle-proof leaf-hash root-hash tx-index tx-count sibling-hashes)` · in: `(buff 32), (buff 32), uint, uint, (list 24 (buff 32))` · out: `bool`

The `verify-merkle-proof` function verifies a Bitcoin-style merkle inclusion proof
using double-SHA-256 hashing with the "duplicate the last node on odd-sized rows" rule.

Given a `leaf-hash` (typically a Bitcoin txid), the merkle `root-hash` of a block, the
`tx-index` of the leaf within the tree (0-indexed), the `tx-count` of transactions in the
block, and the list of `sibling-hashes` along the path from the leaf to the root, the
function returns `true` iff hashing pairwise up the tree in the order described by
`tx-index` produces `root-hash`.

`tx-count` pins down the canonical Bitcoin tree shape and is required to defend against
CVE-2012-2459-style attacks where an intermediate node in an odd-row-padded tree could
otherwise be passed off as a leaf, or where the last real leaf of an odd-sized tree
could be relocated into the duplicated-padding region by inflating `tx-count`. The
function rejects any proof whose path length doesn't match `ceil(log2(tx-count))`, any
`tx-index` not less than `tx-count`, and any sibling whose value is inconsistent with the
canonical tree shape implied by the supplied `tx-count`.

All 32-byte hashes (leaf, root, siblings) are passed in *internal* (raw) byte order, not
the display (reversed) order conventionally used for Bitcoin txids and block hashes. The
`txid` returned by `get-bitcoin-tx-output?` is already in internal byte order and can be
passed directly as `leaf-hash`.

Returns `false` for any malformed proof and `true` for a valid proof.

```clarity
;; The Bitcoin genesis block contains a single tx, so its coinbase txid
;; (in internal byte order) is also the block's merkle root. A proof
;; with an empty sibling list verifies trivially.
(verify-merkle-proof
    0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
    0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
    u0
    u1
    (list)) ;; Returns true
```

### with-all-assets-unsafe

Clarity 4+ · function · `(with-all-assets-unsafe)` · in: `N/A` · out: `Allowance`

Grants unrestricted access to all assets of the contract to
the enclosing `as-contract?` expression. `with-all-assets-unsafe` is not
allowed outside of `as-contract?` contexts. Note that this is not allowed in
`restrict-assets?` and will trigger an analysis error, since usage there does
not make sense (i.e. just remove the `restrict-assets?` instead).
**_⚠️ Security Warning: This should be used with extreme caution, as it
effectively disables all asset protection for the contract. ⚠️_** This
dangerous allowance should only be used when the code executing within the
`as-contract?` body is verified to be trusted through other means (e.g.
checking traits against an allow list, passed in from a trusted caller), and
even then the more restrictive allowances should be preferred when possible.

```clarity
(let ((recipient tx-sender))
  (as-contract? ((with-all-assets-unsafe))
    (try! (stx-transfer? u100 tx-sender recipient))
  )
) ;; Returns (ok true)
```

### with-ft

Clarity 4+ · function · `(with-ft contract-id token-name amount)` · in: `principal (string-ascii 128) uint` · out: `Allowance`

Adds an outflow allowance for `amount` of the fungible
token defined in `contract-id` with name `token-name` from the `asset-owner`
of the enclosing `restrict-assets?` or `as-contract?` expression.  `with-ft` is
not allowed outside of `restrict-assets?` or `as-contract?` contexts. Note that
`token-name` should match the name used in the `define-fungible-token` call in
the contract. When `"*"` is used for the token name, the allowance applies to
**all** FTs defined in `contract-id`.

```clarity
(define-fungible-token stackaroo)
(ft-mint? stackaroo u200 tx-sender)
(restrict-assets? tx-sender
  ((with-ft current-contract "stackaroo" u100))
  (try! (ft-transfer? stackaroo u100 tx-sender 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF))
) ;; Returns (ok true)
(restrict-assets? tx-sender
  ((with-ft current-contract "stackaroo" u50))
  (try! (ft-transfer? stackaroo u100 tx-sender 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF))
) ;; Returns (err u0)
```

### with-nft

Clarity 4+ · function · `(with-nft contract-id asset-name identifiers)` · in: `principal (string-ascii 128) (list 128 T)` · out: `Allowance`

Adds an outflow allowance for the non-fungible tokens
identified by `identifiers` defined in `contract-id` with name `token-name`
from the `asset-owner` of the enclosing `restrict-assets?` or `as-contract?`
expression. `with-nft` is not allowed outside of `restrict-assets?` or
`as-contract?` contexts. Note that `token-name` should match the name used in
the `define-non-fungible-token` call in the contract. When `"*"` is used for
the token name, the allowance applies to **all** NFTs defined in `contract-id`.
Note that the type of the elements in `asset-identifiers` should match the type
defined in the `define-non-fungible-token` call in the contract, but this is
**not** checked by the type-checker. An identifier with the wrong type will
simply never match any asset.

```clarity
(define-non-fungible-token stackaroo uint)
(nft-mint? stackaroo u123 tx-sender)
(nft-mint? stackaroo u124 tx-sender)
(nft-mint? stackaroo u125 tx-sender)
(restrict-assets? tx-sender
  ((with-nft current-contract "stackaroo" (list u123)))
  (try! (nft-transfer? stackaroo u123 tx-sender 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF))
) ;; Returns (ok true)
(restrict-assets? tx-sender
  ((with-nft current-contract "stackaroo" (list u125)))
  (try! (nft-transfer? stackaroo u124 tx-sender 'SPAXYA5XS51713FDTQ8H94EJ4V579CXMTRNBZKSF))
) ;; Returns (err u0)
```

### with-pox

Clarity 6+ · function · `(with-pox)` · in: `N/A` · out: `Allowance`

Permits the `asset-owner` of the enclosing `restrict-assets?`
or `as-contract?` expression to perform a position-altering PoX action: calling
the active PoX contract to `unstake`, `unstake-sbtc`, `update-bond-registration`,
or `announce-l1-early-exit`. `with-pox` is not allowed outside of
`restrict-assets?` or `as-contract?` contexts. These actions are all-or-nothing
for a position, so this allowance takes no amount: its presence simply permits
them, and its absence forbids them within the protected scope. A call to one
of these functions counts as an attempt even when it returns `(err ...)`, so
without `with-pox` the scope also rejects a failed attempt to touch the
position. The record of an attempt is an effect like any other: if a public
function between the PoX contract and the protected scope returns `(err ...)`,
its effects are rolled back and the attempt is no longer visible to the scope.
In both of these error cases, the position itself remains unchanged. Locking
STX is covered by `with-staking`, not `with-pox`.

```clarity
(restrict-assets? tx-sender
  ()
  (try! (contract-call? 'ST000000000000000000002AMW42H.pox-5 unstake .signer))
) ;; Returns (err u128) -- no allowance permits the PoX action
(restrict-assets? tx-sender
  ((with-pox))
  (try! (contract-call? 'ST000000000000000000002AMW42H.pox-5 unstake .signer))
) ;; Returns (ok true)
```

### with-stacking

Clarity 4–5 · function · `(with-stacking amount)` · in: `uint` · out: `Allowance`

Adds a staking allowance for `amount` uSTX from the
`asset-owner` of the enclosing `restrict-assets?` or `as-contract?`
expression. `with-stacking` is not allowed outside of `restrict-assets?` or
`as-contract?` contexts. This restricts calls to the active PoX contract
that either delegate funds for staking or stake directly, ensuring that the
locked amount is limited by the amount of uSTX specified. Note that the
amount specified here is the total amount allowed to be staked, i.e. a call to
`stack-increase` will need an allowance for the new total, not just the
increase amount. Replaced with `with-staking` in Clarity 6+ for consistency
with the active PoX contract's naming.

```clarity
(restrict-assets? tx-sender
  ((with-stacking u1000000000000))
  (try! (contract-call? 'SP000000000000000000002Q6VF78.pox-4 delegate-stx
    u1100000000000 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM none none
  ))
) ;; Returns (err u0)
(restrict-assets? tx-sender
  ((with-stacking u1000000000000))
  (try! (contract-call? 'SP000000000000000000002Q6VF78.pox-4 delegate-stx
    u900000000000 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM none none
  ))
) ;; Returns (ok true)
```

### with-staking

Clarity 6+ · function · `(with-staking amount)` · in: `uint` · out: `Allowance`

Adds a staking allowance for `amount` uSTX from the
`asset-owner` of the enclosing `restrict-assets?` or `as-contract?`
expression. `with-staking` is the Clarity 6+ spelling of the allowance that was
called `with-stacking` in Clarity 4 and 5; it is not allowed outside of
`restrict-assets?` or `as-contract?` contexts. This restricts calls to the
active PoX contract to stake STX, ensuring that the locked amount is limited by
the amount of uSTX specified. Note that the amount specified here is the total
amount allowed to be staked, i.e. a call that increases an existing stake will
need an allowance for the new total, not just the increase amount.

```clarity
(restrict-assets? tx-sender
  ((with-staking u1000000000000))
  (try! (contract-call? 'ST000000000000000000002AMW42H.pox-5 stake
    .signer u1100000000000 u12 burn-block-height none
  ))
) ;; Returns (err u0)
(restrict-assets? tx-sender
  ((with-staking u1000000000000))
  (try! (contract-call? 'ST000000000000000000002AMW42H.pox-5 stake
    .signer u900000000000 u12 burn-block-height none
  ))
) ;; Returns (ok true)
```

### with-stx

Clarity 4+ · function · `(with-stx amount)` · in: `uint` · out: `Allowance`

Adds an outflow allowance for `amount` uSTX from the
`asset-owner` of the enclosing `restrict-assets?` or `as-contract?`
expression. `with-stx` is not allowed outside of `restrict-assets?` or
`as-contract?` contexts.

```clarity
(restrict-assets? tx-sender
  ((with-stx u100))
  (try! (stx-transfer? u100 tx-sender 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM))
) ;; Returns (ok true)
(restrict-assets? tx-sender
  ((with-stx u50))
  (try! (stx-transfer? u100 tx-sender 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM))
) ;; Returns (err u0)
```

### xor

Clarity 1+ · function · `(xor i1 i2)`

Returns the result of bitwise exclusive or'ing `i1` with `i2`.

```clarity
(xor 1 2) ;; Returns 3
(xor 120 280) ;; Returns 352
```
