#!/usr/bin/env python3
"""Verify bundled registry evidence against the live chain; read-only, standard library only.

  python3 scripts/verify_registry.py --protocol zest [--protocol granite ...]
  python3 scripts/verify_registry.py --contract SP....name [--state]
  python3 scripts/verify_registry.py --observations ../system-integration/references/address-observations.json

For each selected record: the live contract source must hash to the recorded `source_sha256`, and a recorded
deployment transaction must still be canonical and successful. Deployed Clarity code is immutable, so a match
confirms the address and its code; it does not establish that the protocol still selects that contract or that
its roles and parameters are unchanged. `--state` reruns the recorded read-only state checks and lists results
that changed since the evidence was captured (prices and balances change constantly; review, do not trust).

Exit 0: every selected record verified (or still absent where the evidence is a recorded 404); 1: a source mismatch,
missing contract, failed deployment or a recorded-absent contract that now exists;
2: some records could not be checked (network or rate limit). Use `--api` / `--testnet-api` for other nodes.
A Hiro API key in HIRO_API_KEY (the variable Clarinet reads) is sent as `x-api-key` to *.hiro.so hosts only.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OBSERVATIONS = HERE.parent / 'references/protocols/address-observations.json'


def hiro_key(url):
    """The Hiro API key header, only for Hiro hosts: other nodes never receive the key."""
    key = os.environ.get('HIRO_API_KEY')
    host = urllib.parse.urlparse(url).hostname or ''
    return {'x-api-key': key} if key and (host == 'hiro.so' or host.endswith('.hiro.so')) else {}


class Client:
    def __init__(self, apis, pause):
        self.apis, self.pause, self.requests = apis, pause, 0

    def call(self, network, path, body=None):
        url = self.apis[network] + path
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(6):
            time.sleep(self.pause)
            self.requests += 1
            request = urllib.request.Request(url, data=data, headers={'Accept': 'application/json',
                                             **({'Content-Type': 'application/json'} if data else {})})
            for name, value in hiro_key(url).items():
                request.add_unredirected_header(name, value)  # a redirect never carries the key
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    return response.status, json.loads(response.read())
            except urllib.error.HTTPError as error:
                if error.code == 429 or error.code >= 500:
                    wait = error.headers.get('Retry-After')
                    time.sleep(float(wait) if wait and wait.replace('.', '', 1).isdigit() else 5 * (attempt + 1))
                    continue
                return error.code, None
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                time.sleep(2 * (attempt + 1))
        return None, None


def verify_contract(client, record):
    address, name = record['contract_id'].split('.', 1)
    network = record.get('network', 'mainnet')
    status, body = client.call(network, f'/v2/contracts/source/{address}/{name}?proof=0')
    recorded_absent = record.get('status') == 'unavailable'  # the evidence is a recorded 404
    if status is None:
        return 'unknown', 'source request failed'
    if status == 404:
        return ('absent', 'still not found, as recorded') if recorded_absent else ('missing', 'contract not found')
    if status != 200 or not isinstance(body, dict) or 'source' not in body:
        return 'unknown', f'source HTTP {status}'
    if recorded_absent:
        return 'appeared', 'now deployed but recorded as unavailable: record new evidence'
    digest = hashlib.sha256(body['source'].encode()).hexdigest()
    if record.get('source_sha256') and digest != record['source_sha256']:
        return 'mismatch', f'source sha256 {digest[:16]} != recorded {record["source_sha256"][:16]}'
    tx = record.get('deployment_tx')
    if tx:
        # v3 returns only the canonical mined record or a pending mempool one; it has no canonical flag.
        status, receipt = client.call(network, f'/extended/v3/transactions/{tx}')
        if status is None or receipt is None:
            return 'unknown', f'deployment receipt HTTP {status}' if status else 'deployment receipt request failed'
        if receipt.get('status') != 'success':
            return 'failed-deployment', f'deployment {receipt.get("status")}'
    return 'verified', 'source matches' + (', deployment successful' if tx else '')


def state_target(check):
    """(contract id, function) of a recorded read-only check; older records keep them only in the URL."""
    if check.get('contract_id') and check.get('function'):
        return check['contract_id'], check['function']
    parts = urllib.parse.urlparse(check.get('url', '')).path.strip('/').split('/')
    if parts[:3] == ['v2', 'contracts', 'call-read'] and len(parts) == 6:
        return f'{parts[3]}.{parts[4]}', urllib.parse.unquote(parts[5])
    return None, None


def rerun_state(client, check, network):
    contract_id, function = state_target(check)
    address, name = contract_id.split('.', 1)
    body = {'sender': address, 'arguments': check.get('arguments') or []}
    status, response = client.call(network, f'/v2/contracts/call-read/{address}/{name}/{function}', body)
    if status != 200 or not isinstance(response, dict) or not response.get('okay'):
        return 'unknown'
    before = (check.get('response') or {}).get('result', check.get('result'))
    return 'unchanged' if response.get('result') == before else 'changed'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--observations', type=Path, default=DEFAULT_OBSERVATIONS)
    parser.add_argument('--protocol', action='append', default=[], help='Protocol key in the observations file')
    parser.add_argument('--contract', action='append', default=[], help='Exact contract id')
    parser.add_argument('--state', action='store_true', help='Rerun recorded read-only state checks for the selection')
    parser.add_argument('--api', default='https://api.hiro.so')
    parser.add_argument('--testnet-api', default='https://api.testnet.hiro.so')
    parser.add_argument('--pause', type=float, help='Seconds between requests (default 1.3, or 0.1 with HIRO_API_KEY)')
    parser.add_argument('--json', type=Path, help='Also write the report as JSON')
    args = parser.parse_args()
    data = json.loads(args.observations.read_text())
    records = data.get('contracts', [])
    selected = [r for r in records if (not args.protocol and not args.contract)
                or r.get('protocol') in args.protocol or r['contract_id'] in args.contract]
    if not selected:
        parser.exit(2, 'No matching records; protocols: ' + ', '.join(sorted({r.get('protocol', '-') for r in records})) + '\n')
    pause = args.pause if args.pause is not None else (0.1 if os.environ.get('HIRO_API_KEY') else 1.3)
    client = Client({'mainnet': args.api, 'testnet': args.testnet_api}, pause)
    now = lambda: datetime.now(timezone.utc).isoformat(timespec='seconds')
    report = {'observations': str(args.observations), 'recorded': data.get('retrieved'), 'api': args.api,
              'started': now(), 'contracts': [], 'state': []}
    for record in selected:
        status, detail = verify_contract(client, record)
        report['contracts'].append({'contract_id': record['contract_id'], 'network': record.get('network', 'mainnet'),
                                    'protocol': record.get('protocol'), 'role': record.get('role'),
                                    'status': status, 'detail': detail, 'checked_at': now()})
        print(f"{status:17} {record['contract_id']} ({record.get('role') or record.get('status', '-')}): {detail}")
    if args.state:
        ids = {r['contract_id']: r.get('network', 'mainnet') for r in selected}
        for check in data.get('state_checks', []):
            contract_id, function = state_target(check)
            if contract_id in ids:
                result = rerun_state(client, check, ids[contract_id])
                report['state'].append({'contract_id': contract_id, 'function': function, 'result': result})
                print(f"state {result:9} {contract_id}.{function}")
    counts = {s: sum(c['status'] == s for c in report['contracts']) for s in sorted({c['status'] for c in report['contracts']})}
    print(f'{len(selected)} records: {counts}; {client.requests} requests. Verified code does not prove current '
          'selection or roles: read those from the protocol before calling it.')
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + '\n')
    if any(c['status'] in ('mismatch', 'missing', 'failed-deployment', 'appeared') for c in report['contracts']):
        return 1
    return 2 if any(c['status'] == 'unknown' for c in report['contracts']) else 0


if __name__ == '__main__':
    sys.exit(main())
