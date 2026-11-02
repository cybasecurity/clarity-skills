# Clarity syntax reference

Tables and examples for [clarity-scholar syntax](../../clarity-scholar/SKILL.md#syntax).

### Values and types

| Value expression | Type / meaning |
|---|---|
| `-1`, `0`, `42` | `int` |
| `u0`, `u42` | `uint`; use `to-uint` / `to-int` for conversion, not `(uint ...)` |
| `true`, `false` | `bool` |
| `0x00ff` | `(buff 2)` maximum length in bytes |
| `"abc"`, `u"abc"` | `(string-ascii 3)`, `(string-utf8 3)` maximum character lengths |
| `'ST000000000000000000002AMW42H` | `principal`: a full standard principal literal |
| `'ST000000000000000000002AMW42H.token`, `.token` | `principal`: full or relative contract literal |
| `(list u1 u2)` | `(list 2 uint)`; value constructor and type expression differ |
| `{amount: u1, active: true}` | `{amount: uint, active: bool}` |
| `(tuple (amount u1) (active true))` | Legacy tuple value; prefer braces. Legacy type: `(tuple (amount uint) (active bool))` |
| `none`, `(some u1)` | `(optional uint)` when inferred/constrained to uint |
| `(ok u1)`, `(err u1000)` | `(response uint uint)` when both sides are inferred/constrained |

- String escapes include `\\`, `\"`, `\n` and `\t`; Unicode escapes use `u"\u{1F600}"`. Use `\n` rather than a literal newline inside a string.
- `(get amount record)` reads a tuple field; `(get amount maybe-record)` preserves the optional wrapper.
- `tx-sender`, `contract-caller`, `current-contract`, `stacks-block-time` and heights are keywords, without `()`; their meaning/version differs.

### Definitions and state

| Top-level form | Use |
|---|---|
| `(define-constant NAME expression)` | Evaluated once on deployment |
| `(define-data-var name type initial-value)` | Mutable slot; `(var-get name)`, `(var-set name value)` |
| `(define-map name key-type value-type)` | `(map-get? name key)` returns optional; `map-set`, `map-insert`, `map-delete` return bool |
| `(define-fungible-token token-name)` | Native FT; optional supply cap expression follows the name |
| `(define-non-fungible-token token-name id-type)` | Native NFT identifier type |
| `(define-private (helper (arg type)) body)` | Internal function; any inferred return type |
| `(define-read-only (read-value (arg type)) body)` | Externally callable; cannot write; any inferred return type |
| `(define-public (action (arg type)) body)` | Public function; body must return a response |

- Definitions stay top-level. For no parameters, use `(name)` without parameter pairs. A function has one body expression; use `begin` or `let` for several operations. Parameters and local bindings cannot shadow contract-level variables/constants.
- Top-level ordinary expressions also run once on deployment, with `tx-sender` = deployer; keep them to initialization. Constants can call functions, including later definitions, and dependency sorting can move stateful initializers: see [deployment-time execution](../../clarity-deployment/SKILL.md#deployment-time-execution).

### Branches, bindings and failures

| Form | Result / control flow |
|---|---|
| `(if condition then-expr else-expr)` | Evaluates one branch |
| `(let ((a expr-a) (b expr-using-a)) expr ... last-expr)` | Sequential bindings; returns last expression |
| `(begin expr ... last-expr)` | Returns last expression; intermediate responses must be handled |
| `(match optional value-name some-expr none-expr)` | Four arguments; binds the unwrapped some value |
| `(match response ok-name ok-expr err-name err-expr)` | Five arguments; both binders are required |
| `(default-to fallback optional)` | Unwraps some or returns fallback |
| `(try! response-or-optional)` | Unwraps success; returns err/none from the enclosing function |
| `(unwrap! response-or-optional fallback)` | Unwraps success; returns fallback from the enclosing function |
| `(asserts! condition failure)` | Returns true or exits the enclosing function with failure |
| `(unwrap-panic response-or-optional)` | Unwraps success or aborts execution |

- `try!` cannot unwrap a plain tuple/value. `unwrap-err!` / `unwrap-err-panic` instead extract the err payload; check their signatures before use.
- An always-`ok` external getter can leave `try!`'s error type indeterminate. Use `unwrap! result ERR` to assign your failure type; keep fixtures consistent with the real ABI.
- `(map helper sequence ...)`, `(filter predicate sequence)`, `(fold reducer sequence initial)` are bounded; reducer arguments are **element, accumulator**. No anonymous callback syntax.

### Traits and calls

The four trait roles, in order: trait definition (in a trait-only contract), import in a consumer, implementation declaration, and a dynamic call through a trait-typed argument.

```text
(define-trait token-trait
  ((transfer (uint principal principal (optional (buff 34))) (response bool uint))))
(use-trait token .trait-contract.token-trait)
(impl-trait .trait-contract.token-trait)
(define-public (send (asset <token>) (amount uint) (recipient principal))
  (contract-call? asset transfer amount tx-sender recipient none))
```

- These illustrate separate roles, not a standalone implementation. `impl-trait` requires matching method definitions. Deploy the referenced trait contract first.
- Arbitrary principals cannot substitute for the trait value in a dynamic call.
- Static call: `(contract-call? .token transfer amount sender recipient none)`.
- Arguments are positional; the callee function name is unquoted. Calls can return plain values from read-only functions; inspect the ABI before using `try!`.
- Asset/context operations are security-sensitive, not mere syntax: see [authority and execution context](authority.md#authority-and-execution-context) and [traits and dynamic calls](authority.md#traits-and-dynamic-calls).

### Complete compilable example

A whole contract using the forms above (constants, state, `fold`, `let`, `asserts!`, events, optional and response `match`):

```clarity
(define-constant ERR_ZERO (err u1000))
(define-data-var total uint u0)
(define-map amounts principal uint)

(define-private (add-item (item uint) (acc uint))
	(+ item acc))

(define-public (record (values (list 8 uint)))
	(let ((amount (fold add-item values u0)) (prior (default-to u0 (map-get? amounts tx-sender))))
		(asserts! (> amount u0) ERR_ZERO)
		(map-set amounts tx-sender (+ prior amount))
		(var-set total (+ (var-get total) amount))
		(print {event: "record", actor: tx-sender, amount: amount})
		(ok amount)))

(define-read-only (get-amount (who principal))
	(match (map-get? amounts who) value (some {amount: value}) none))

(define-read-only (classify (answer (response uint uint)))
	(match answer value {success: true, code: value} failure {success: false, code: failure}))
```

- This records numbers, not deposits. It illustrates syntax; it has no asset transfer or custody policy.
