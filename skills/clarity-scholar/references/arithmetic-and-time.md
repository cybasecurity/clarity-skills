# Arithmetic and time patterns

Detail for [arithmetic](../../clarity-scholar/SKILL.md#arithmetic) and [time](../../clarity-scholar/SKILL.md#time) in clarity-scholar.

## Additive range checks

- Prefer `amount + used <= cap` to `amount <= cap - used` when the sum provably fits uint128. It expresses the capacity invariant without risking subtraction underflow.
- Mathematical equivalence does not preserve runtime failures automatically: addition can overflow, and `cap - used` underflows when `used > cap`. Bound operands before addition, using earlier guards or short-circuit `and`. Each operand being below `cap` suffices only when `2 * cap` fits.

```clarity
;; fragment
;; CAP is 1e18, so two capped uint operands fit uint128.
(asserts! (and (<= amount CAP) (<= used CAP)
	(<= (+ amount used) CAP)) ERR_LIMIT)
```

- For full-range operands, keep a safely guarded subtraction if needed. Preserve intended errors, units and evaluation order; test exact capacity, one over and uint128 extremes.
- Actual differences, such as net payouts and measured balance deltas, can still require subtraction. This is a guard preference, not a ban on `-`.

## Time

- `block-height` (Clarity 1–2) means tenure height after Nakamoto and does not exist in Clarity 3+.
- Use `burn-block-height` for Bitcoin-anchored schedules (PoX).
- Match an external protocol's deadline unit. [Stacks Swap](../../clarity-protocols/references/stacks-swap.md#stacks-swap) requires Stacks block height: explicitly tell the developer, keep it separate from timestamp-based product schedules, and never promise a fixed elapsed duration from block counts.

### Epochs whose length can change

- Store the active segment `{start, length, first}` and derive the epoch from it; never recompute every elapsed epoch with the latest length. Epoch index at `now` = `first + (now - start) / length`; that epoch starts at `start + (index - first) * length`.
- A new length takes effect at the next boundary as a new segment whose `first` comes from the old one, so long gaps without calls stay correct and reads need no writes: readers fold in a pending change once `now` reaches its boundary.
- Authorize the setter like any privileged setter and validate the new length (for example, not shorter than an in-epoch window the protocol uses). It first stores the segment in force now, then sets pending `{at: current epoch start + current length, length: new}`; decide whether a newer request replaces a pending one.
- Timestamps before the first segment are out of range (the subtraction aborts).

```clarity
;; fragment
(define-private (index-in (seg {start: uint, length: uint, first: uint}) (now uint))
	(+ (get first seg) (/ (- now (get start seg)) (get length seg))))

;; Segment in force at `now`, folding in a pending change once its boundary has passed.
(define-read-only (segment-at (now uint))
	(let ((seg (var-get segment)))
		(match (var-get pending) change
			(if (>= now (get at change))
				{start: (get at change), length: (get length change), first: (index-in seg (get at change))}
				seg)
			seg)))
```
