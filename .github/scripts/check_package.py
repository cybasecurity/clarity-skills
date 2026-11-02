#!/usr/bin/env python3
"""Check the skills and host manifests in this repository. Standard library only; reads files, runs nothing.

  python3 .github/scripts/check_package.py             # main and pull requests into it
  python3 .github/scripts/check_package.py --develop   # develop: skips the generated skills/ copy

Checks: Agent Skills frontmatter in plugin/skills/ and the generated skills/ copy (the fields hosts accept,
name equal to the folder, lengths, string metadata), that both trees hold the same skills and files,
SKILL.md body size, the description budget, allowed-tools rules, per-skill icons, relative links,
GitHub blob and tree links pinned to a 40-hex commit, README images,
root-relative links in docs/ (GitHub's Contributing and Security tabs resolve links from the root),
the bug report form's skill list,
and that every host manifest names the same plugin and version. The generated skills/ copy is regenerated at each
release, so --develop skips it.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLUGIN = REPO / 'plugin'
COPY = REPO / 'skills'
SKILL_FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
AGENT_PLUGIN_FIELDS = {'$schema', 'name', 'version', 'description', 'author', 'homepage', 'repository', 'license',
                       'keywords', 'extensions'}  # Agent Plugins v1; Cline and Kiro reject other root fields
MAX_BODY = 24000  # bytes after the frontmatter; Google Antigravity reads no further
MAX_DESCRIPTIONS = 4650  # characters across plugin/skills; keeps the always-on context under 2,000 tokens
errors = []
DEVELOP = '--develop' in sys.argv[1:]


def frontmatter(path):
    """Parse the flat frontmatter these skills use: key: "value" lines and one indented metadata map."""
    text = path.read_text()
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not match:
        raise ValueError('missing frontmatter')
    data, current = {}, None
    for line in match.group(1).splitlines():
        nested = re.fullmatch(r'  ([\w-]+): "([^"\\]*)"', line)
        top = re.fullmatch(r'([\w-]+):(?: "([^"\\]*)"| ([^"\s][^"]*))?', line)
        if nested and current is not None:
            data[current][nested.group(1)] = nested.group(2)
        elif top and top.group(2) is None and top.group(3) is None:
            current = top.group(1)
            data[current] = {}
        elif top:
            current = None
            data[top.group(1)] = top.group(2) if top.group(2) is not None else top.group(3)
        else:
            raise ValueError(f'unexpected frontmatter line: {line!r}')
    return data, text[match.end():]


def check_skill(folder, expected_name, root):
    where = folder.relative_to(REPO)
    try:
        meta, body = frontmatter(folder / 'SKILL.md')
    except (OSError, ValueError) as exc:
        errors.append(f'{where}: {exc}')
        return None
    if set(meta) - SKILL_FIELDS:
        errors.append(f'{where}: fields outside the Agent Skills spec: {sorted(set(meta) - SKILL_FIELDS)}')
    if meta.get('name') != expected_name or not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', expected_name):
        errors.append(f'{where}: name must be {expected_name}')
    if not 0 < len(meta.get('description', '')) <= 1024:
        errors.append(f'{where}: description must be 1-1024 characters')
    if 'compatibility' in meta and not 0 < len(meta['compatibility']) <= 500:
        errors.append(f'{where}: compatibility must be 1-500 characters')
    if not isinstance(meta.get('metadata', {}), dict):
        errors.append(f'{where}: metadata must be a map of strings')
    for rule in re.findall(r'Bash\(python3 (\S+) \*\)', meta.get('allowed-tools', '')):
        target = Path(rule.replace('${CLAUDE_SKILL_DIR}', str(folder)).replace('${CLAUDE_PLUGIN_ROOT}', str(PLUGIN)))
        if root == PLUGIN and not target.is_file():
            errors.append(f'{where}: allowed-tools names a missing script: {rule}')
    if meta.get('allowed-tools', '').count('Bash(') != len(re.findall(r'Bash\(python3 \S+ \*\)', meta.get('allowed-tools', ''))):
        errors.append(f'{where}: allowed-tools may only pre-approve bundled scripts as Bash(python3 <path> *)')
    # Per-skill icons: Codex reads them from agents/openai.yaml; the README table shows the small one
    ui = folder / 'agents/openai.yaml'
    ui_text = ui.read_text() if ui.is_file() else ''
    for field, rel in (('icon_small', 'assets/icon-small.svg'), ('icon_large', 'assets/icon-large.png')):
        if f'{field}: "./{rel}"' not in ui_text or not (folder / rel).is_file():
            errors.append(f'{where}: agents/openai.yaml {field} must be ./{rel} and the file must exist')
    if len(body.encode()) > MAX_BODY:
        errors.append(f'{where}: SKILL.md body is {len(body.encode())} bytes (limit {MAX_BODY})')
    return meta


def check_links(root):
    for page in sorted(root.rglob('*.md')):
        # Evidence links name a commit: a GitHub blob or tree link on a branch or tag changes under the reader.
        for link, ref in re.findall(r'(https://github\.com/[^/\s)\]>"\'`]+/[^/\s)\]>"\'`]+/(?:blob|tree)/([^/\s)\]>"\'`#?]+))', page.read_text()):
            if not re.fullmatch(r'[0-9a-f]{40}', ref.rstrip('.,;:')):
                errors.append(f'{page.relative_to(REPO)}: GitHub link not pinned to a 40-hex commit: {link}')
        for target in re.findall(r'\]\(([^\s)]+)\)', page.read_text()):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            path = (page.parent / target.split('#')[0]).resolve()
            if root.resolve() not in path.parents and path != root.resolve():
                errors.append(f'{page.relative_to(REPO)}: link leaves {root.name}/: {target}')
            elif not path.exists():
                errors.append(f'{page.relative_to(REPO)}: missing link target: {target}')


def load(rel):
    try:
        return json.loads((REPO / rel).read_text())
    except (OSError, ValueError) as exc:
        errors.append(f'{rel}: {exc}')
        return {}


topics = sorted(p.name for p in (PLUGIN / 'skills').iterdir() if (p / 'SKILL.md').is_file())
manifest = load('plugin/plugin.json')
name, version = manifest.get('name'), manifest.get('version')
descriptions = 0
for topic in topics:
    meta = check_skill(PLUGIN / 'skills' / topic, topic, PLUGIN)
    if meta:
        descriptions += len(meta.get('description', ''))
        if meta.get('metadata', {}).get('version') != version:
            errors.append(f'plugin/skills/{topic}: metadata.version must be {version}')
    if DEVELOP:
        continue
    copy = COPY / f'clarity-{topic}'
    check_skill(copy, f'clarity-{topic}', COPY)
    source_files = sorted(str(p.relative_to(PLUGIN / 'skills' / topic)) for p in (PLUGIN / 'skills' / topic).rglob('*') if p.is_file())
    copy_files = sorted(str(p.relative_to(copy)) for p in copy.rglob('*') if p.is_file()) if copy.is_dir() else []
    if source_files != copy_files:
        errors.append(f'skills/clarity-{topic}: files differ from plugin/skills/{topic}; regenerate the copy')
extra = sorted(p.name for p in COPY.iterdir() if p.is_dir() and p.name.removeprefix('clarity-') not in topics)
if extra and not DEVELOP:
    errors.append(f'skills/: folders with no source in plugin/skills: {extra}')
if descriptions > MAX_DESCRIPTIONS:
    errors.append(f'skill descriptions total {descriptions} characters (budget {MAX_DESCRIPTIONS})')
check_links(PLUGIN)
if not DEVELOP:
    check_links(COPY)
for src in re.findall(r'<img src="([^"]+)"', (REPO / 'README.md').read_text()):
    if not src.startswith('https://') and not (REPO / src).is_file():
        errors.append(f'README.md: missing image {src}')

for page in sorted((REPO / 'docs').glob('*.md')):  # GitHub's tabs render these as if they were in the root
    for target in re.findall(r'\]\(([^\s)]+)\)', page.read_text()):
        if re.match(r'[a-z]+:', target) or target.startswith('#'):
            continue
        if not target.startswith('/'):
            errors.append(f'{page.relative_to(REPO)}: link must start with / to work in GitHub tabs: {target}')
        elif not (REPO / target.split('#')[0].lstrip('/')).exists():
            errors.append(f'{page.relative_to(REPO)}: missing link target: {target}')

bug_form = (REPO / '.github/ISSUE_TEMPLATE/bug_report.yml').read_text()
listed = sorted(re.findall(r'^ +- clarity:([a-z0-9-]+)$', bug_form, re.M))
if listed != sorted(topics):
    errors.append('.github/ISSUE_TEMPLATE/bug_report.yml: the Skill dropdown must list every skill in plugin/skills')

for rel in ('plugin.json', 'plugin/.claude-plugin/plugin.json', '.cursor-plugin/plugin.json', 'gemini-extension.json'):
    data = load(rel)
    if data and (data.get('name') != name or data.get('version') != version):
        errors.append(f'{rel}: name and version must match plugin/plugin.json ({name} {version})')
root_manifest = load('plugin.json')
if set(root_manifest) - AGENT_PLUGIN_FIELDS:
    errors.append(f'plugin.json: fields outside Agent Plugins v1: {sorted(set(root_manifest) - AGENT_PLUGIN_FIELDS)}')
for rel, source in (('.claude-plugin/marketplace.json', './plugin'), ('.github/plugin/marketplace.json', './'),
                    ('.factory-plugin/marketplace.json', './'), ('.cursor-plugin/marketplace.json', './')):
    listed = {p.get('name'): p.get('source') for p in load(rel).get('plugins', [])}
    if listed.get(name) != source:
        errors.append(f'{rel}: must list {name} with source {source}')
codex = {p.get('name'): p.get('source', {}).get('path') for p in load('.agents/plugins/marketplace.json').get('plugins', [])}
if codex.get(name) != './plugin':
    errors.append('.agents/plugins/marketplace.json: must point the plugin at ./plugin')

for error in errors:
    print(error, file=sys.stderr)
print(f'{len(topics)} skills, {descriptions} description characters; {len(errors)} problems'
      + (' (develop: generated copy skipped)' if DEVELOP else ''))
sys.exit(1 if errors else 0)
