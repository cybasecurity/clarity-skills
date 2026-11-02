#!/usr/bin/env python3
"""Extract source cost formulas and delegation. Does not execute the target repo."""
import argparse
import json
import re
import subprocess
from pathlib import Path

def function(source, name):
    match = re.search(r"\bfn\s+" + re.escape(name) + r"\s*\(", source)
    if not match:
        raise ValueError(f"Function not found: {name}")
    start = source.index("{", match.end())
    depth = 1
    pos = start + 1
    while depth and pos < len(source):
        depth += (source[pos] == "{") - (source[pos] == "}")
        pos += 1
    if depth:
        raise ValueError(f"Unbalanced source while extracting {name}")
    return {"line": source.count("\n", 0, match.start()) + 1,
            "source": source[match.start():pos]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--schedule", type=int, help="Explicit source schedule; default newest (not necessarily active)")
    parser.add_argument("--function", action="append", dest="functions")
    args = parser.parse_args()
    root = args.repository.resolve()
    costs = root / "clarity/src/vm/costs"
    files = {int(p.stem.split("_")[-1]): p for p in costs.glob("costs_*.rs") if re.fullmatch(r"costs_\d+", p.stem)}
    if not files:
        parser.error("No numbered cost schedules found")
    selected = args.schedule if args.schedule is not None else max(files)
    if selected not in files:
        parser.error(f"Schedule {selected} not found")
    names = args.functions or ["cost_fetch_entry", "cost_load_contract", "cost_contract_call", "cost_print"]
    def resolve(number, name, visited=None):
        visited = set() if visited is None else visited
        key = (number, name)
        if key in visited:
            raise ValueError(f"Delegation cycle at {key}")
        visited.add(key)
        if number not in files:
            raise ValueError(f"Delegated schedule {number} not found")
        item = function(files[number].read_text(encoding='utf-8'), name)
        item.update({"schedule": number, "path": str(files[number].relative_to(root))})
        item["delegates"] = [resolve(int(n), f, visited.copy()) for n, f in
                             re.findall(r"Costs(\d+)::(cost_\w+)\(", item["source"])]
        return item
    try:
        commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        result = {"commit": commit, "available_schedules": sorted(files), "selected_schedule": selected,
                  "warning": "Source extraction, not activation evidence or measured transaction costs",
                  "dispatch": function((costs / "mod.rs").read_text(encoding='utf-8'), "default_cost_contract_for_epoch"),
                  "formulas": [resolve(selected, f) for f in names]}
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
