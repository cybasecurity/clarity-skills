#!/usr/bin/env python3
"""Check registry age offline; when verification is due, use verify_registry.py against the live chain.

Run from the skill directory: python3 scripts/check_registry.py [--registry references/addresses/<protocol>.md] [--as-of YYYY-MM-DD].
Exit code 0 means within the window, 1 verification due, 2 malformed or unsupported metadata.
"""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re

REFRESH_AFTER_DAYS = 30  # the window the skills state; owners record only registry_verified_at


def frontmatter(text):
    match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not match:
        raise ValueError('Missing metadata')
    return match[1]


def scalar_fields(header, indent=''):
    result = {}
    for key, value in re.findall(r'^' + indent + r'([a-z_]+): ([^\n]+)$', header, re.M):
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        result[key] = value
    return result


def registry_metadata(path):
    path = path.resolve()
    text = path.read_text(encoding='utf-8')
    # Older downloaded registries own their metadata locally; keep their dates.
    if text.startswith('---\n'):
        legacy = scalar_fields(frontmatter(text))
        if 'registry_schema' in legacy:
            if legacy['registry_schema'] != '1':
                raise ValueError('Unsupported registry schema')
            return legacy, path
    owner = next((parent / 'SKILL.md' for parent in path.parents
                  if (parent / 'SKILL.md').is_file()), None)
    if owner is None:
        raise ValueError('Missing owning SKILL.md registry metadata')
    relative = path.relative_to(owner.parent).as_posix()
    if relative != 'references/addresses.md' and not re.fullmatch(r'references/addresses/[a-z0-9-]+\.md', relative):
        raise ValueError('Not a registry address table')
    fields = scalar_fields(frontmatter(owner.read_text(encoding='utf-8')), '  ')
    return {'verified_at': fields['registry_verified_at'], 'refresh_after_days': REFRESH_AFTER_DAYS}, owner


def check(path, today):
    metadata, owner = registry_metadata(path)
    verified = date.fromisoformat(metadata['verified_at'])
    window = int(metadata['refresh_after_days'])
    if window <= 0:
        raise ValueError('Invalid refresh window')
    age = (today - verified).days
    due = age < 0 or age >= window
    return {'registry': str(path), 'verified_at': verified.isoformat(),
            'age_days': age, 'refresh_after_days': window, 'refresh_required': due,
            'metadata_file': str(owner),
            'when_due': 'suggest a package update; verify addresses with scripts/verify_registry.py',
            'live_check_required_before_deployment_or_signing': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=Path(__file__).resolve().parents[1] / 'references/addresses.md')
    parser.add_argument('--as-of', type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args()
    try:
        result = check(args.registry, args.as_of)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'Cannot determine freshness: {exc}\n')
    print(json.dumps(result, indent=2))
    return int(result['refresh_required'])


if __name__ == '__main__':
    raise SystemExit(main())
