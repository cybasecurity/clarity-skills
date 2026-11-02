#!/usr/bin/env python3
"""Compare two measured SDK cost records with identical context and limits."""
import argparse
import json
import math
from pathlib import Path

FIELDS = {"runtime": "runtime", "readCount": "read_count", "readLength": "read_length",
          "writeCount": "write_count", "writeLength": "write_length"}

def vector(value):
    result = {}
    for camel, snake in FIELDS.items():
        number = value.get(camel, value.get(snake))
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number) or number < 0:
            raise ValueError(f"Invalid or missing {camel}")
        result[camel] = number
    return result

def record(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    context = data["context"]
    if not isinstance(context, dict) or any(not context.get(k) for k in ("epoch", "clarity", "sdk", "fixture")):
        raise ValueError("context requires epoch, clarity, sdk, and fixture")
    costs = data["costs"]
    total, limit = vector(costs["total"]), vector(costs["limit"])
    if any(n == 0 for n in limit.values()):
        raise ValueError("Budget limits must be positive")
    return context, total, limit

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        ca, a, la = record(args.baseline)
        cb, b, lb = record(args.candidate)
        if ca != cb or la != lb:
            raise ValueError("Contexts or budget limits differ; cannot make an equivalent-fixture comparison")
        rows = {k: {"before": a[k], "after": b[k], "delta": b[k] - a[k],
                    "change_percent": 100 * (b[k] - a[k]) / a[k] if a[k] else None,
                    "before_budget_percent": 100 * a[k] / la[k],
                    "after_budget_percent": 100 * b[k] / la[k]} for k in FIELDS}
        print(json.dumps({"context": ca, "dimensions": rows,
                          "limiting_before": max(FIELDS, key=lambda k: a[k] / la[k]),
                          "limiting_after": max(FIELDS, key=lambda k: b[k] / la[k]),
                          "exceeded_after": [k for k in FIELDS if b[k] > la[k]]}, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
