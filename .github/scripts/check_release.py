#!/usr/bin/env python3
"""Check that a pull request into main is a release. Standard library only; reads files, runs nothing.

  python3 .github/scripts/check_release.py BASE

BASE is a checkout of main. The version in plugin/plugin.json must be newer than the latest dated release in
BASE's docs/CHANGELOG.md, and this tree's changelog must open with that release, dated: `## <version> (YYYY-MM-DD)`.
release_version.py in the maintenance tools makes both changes.
"""
from datetime import date
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RELEASE = re.compile(r'^## (\d+)\.(\d+)\.(\d+) \((\d{4}-\d{2}-\d{2})\)$', re.M)


def latest_release(changelog):
    match = RELEASE.search(changelog)
    return tuple(int(part) for part in match.groups()[:3]) if match else None


if len(sys.argv) != 2:
    sys.exit(__doc__)
base = Path(sys.argv[1])
version = json.loads((REPO / 'plugin/plugin.json').read_text())['version']
new = tuple(int(part) for part in version.split('.'))
errors = []

released = latest_release((base / 'docs/CHANGELOG.md').read_text())
if released and new <= released:
    errors.append(f'plugin/plugin.json: version {version} must be newer than the released {".".join(map(str, released))}')
top = next((line for line in (REPO / 'docs/CHANGELOG.md').read_text().splitlines() if line.startswith('## ')), '')
match = RELEASE.fullmatch(top)
if not match or match.group(0) != f'## {version} ({match.group(4)})':
    errors.append(f'docs/CHANGELOG.md: the first section must be "## {version} (YYYY-MM-DD)", found "{top}"')
else:
    try:
        date.fromisoformat(match.group(4))
    except ValueError:
        errors.append(f'docs/CHANGELOG.md: {match.group(4)} is not a date')

for error in errors:
    print(error, file=sys.stderr)
print(f'release {version}; {len(errors)} problems')
sys.exit(1 if errors else 0)
