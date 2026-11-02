#!/usr/bin/env python3
"""Print one exact VM reference entry without loading the complete catalog.

Example: python3 scripts/lookup_function.py 'as-contract?'
"""
import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('name', help='Exact Clarity name; quote punctuation, e.g. "as-contract?"')
args = parser.parse_args()
catalog = Path(__file__).resolve().parents[1] / 'references/functions.md'
text = catalog.read_text(encoding='utf-8')
entries = dict(re.findall(r'(?ms)^### ([^\n]+)\n(.*?)(?=^### |\Z)', text))
if args.name not in entries:
    parser.exit(2, 'Unknown name. Search the catalog or the current VM reference; do not guess.\n')
print('VM documentation excerpt: confirm target version/epoch and implementation corrections in epochs/SKILL.md (Version-specific behavior).\n')
# The reviewed version/epoch table lives in the epochs skill entrypoint, under "## Version-specific behavior".
# Hosts install that skill as epochs/ or clarity-epochs/ beside this one, or not at all.
epochs = next((p for p in (catalog.parents[2] / d / 'SKILL.md' for d in ('epochs', 'clarity-epochs')) if p.is_file()), None)
if epochs is None:
    print('The epochs skill is not installed here: read its Version-specific behavior table before relying on this text.\n')
section = epochs and re.search(r'(?ms)^## Version-specific behavior\n(.*?)(?=^## |\Z)', epochs.read_text(encoding='utf-8'))
aliases = {'secp256k1-recover?': 'secp256k1', 'secp256k1-verify': 'secp256k1',
           'secp256k1-decompress?': 'secp256k1'}
names = {args.name, aliases.get(args.name, args.name)}
corrections = [line for line in (section.group(1) if section else '').splitlines()
               if line.startswith('| ') and any(f'`{name}`' in line for name in names)]
if corrections:
    print('Apply these reviewed version/epoch rules before the quoted VM text; historical notes in that text can be incomplete.\n')
    print('| Topic | Behavior | Action |\n|---|---|---|')
    print('\n'.join(corrections) + '\n')
print('# ' + args.name + '\n' + entries[args.name].rstrip())
