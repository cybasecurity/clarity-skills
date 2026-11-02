#!/usr/bin/env python3
"""Download read-only node evidence; never signs, broadcasts, or executes a repository."""
import argparse
import datetime
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

def fetch(base, endpoint):
    url = base.rstrip("/") + endpoint
    headers = {"User-Agent": "clarity-skills/1.0.0", "Accept": "application/json"}
    host = urllib.parse.urlparse(url).hostname or ""
    request = urllib.request.Request(url, headers=headers)
    if os.environ.get("HIRO_API_KEY") and (host == "hiro.so" or host.endswith(".hiro.so")):
        # Hiro hosts only, and never forwarded on a redirect; the variable Clarinet reads
        request.add_unredirected_header("x-api-key", os.environ["HIRO_API_KEY"])
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", help="ADDRESS.contract-name")
    parser.add_argument("--api", default="https://api.hiro.so", help="Node-compatible API base URL")
    parser.add_argument("--tip", help="Explicit index block hash; otherwise snapshots the node tip")
    parser.add_argument("--expected-sha256", help="Expected SHA256 of the exact UTF-8 source; not contract-hash?")
    parser.add_argument("--out", type=Path, help="New evidence directory (will not overwrite)")
    args = parser.parse_args()
    if not re.fullmatch(r"S[PMTN][0-9A-Z]{20,40}\.[A-Za-z][A-Za-z0-9_-]{0,39}", args.contract):
        parser.error("Expected a Stacks contract principal ADDRESS.name")
    parsed = urllib.parse.urlparse(args.api)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment or parsed.username:
        parser.error("API must be an HTTP(S) base URL without credentials, query, or fragment")
    if args.tip and not re.fullmatch(r"(?:0x)?[a-fA-F0-9]{64}", args.tip):
        parser.error("tip must be a 32-byte hexadecimal index block hash")
    if args.expected_sha256 and not re.fullmatch(r"[a-fA-F0-9]{64}", args.expected_sha256):
        parser.error("expected-sha256 must be 64 hexadecimal characters")
    address, name = args.contract.split(".", 1)
    try:
        info = fetch(args.api, "/v2/info")
        # Node RPC tip parsing expects bare hexadecimal, unlike indexed API hashes.
        tip = args.tip.removeprefix('0x') if args.tip else None
        if not tip:
            # Node /v2/info exposes the block hash, not the index block ID.
            # StacksBlockId::new = SHA512/256(block_hash || consensus_hash).
            block_hash = bytes.fromhex(info["stacks_tip"].removeprefix("0x"))
            consensus_hash = bytes.fromhex(info["stacks_tip_consensus_hash"].removeprefix("0x"))
            if len(block_hash) != 32 or len(consensus_hash) != 20:
                raise ValueError("Invalid node tip hashes; specify a verified --tip")
            tip = hashlib.new("sha512_256", block_hash + consensus_hash).hexdigest()
        query = "?" + urllib.parse.urlencode({"tip": tip, "proof": 0})
        source = fetch(args.api, f"/v2/contracts/source/{address}/{name}" + query)
        interface = fetch(args.api, f"/v2/contracts/interface/{address}/{name}" + query)
        pox = fetch(args.api, "/v2/pox?" + urllib.parse.urlencode({"tip": tip}))
        code = source["source"]
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        result = {"retrieved": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "api": args.api, "contract": args.contract, "tip": tip, "source_sha256": digest,
                  "expected_matches": digest == args.expected_sha256.lower() if args.expected_sha256 else None,
                  "source": source, "interface": interface, "node_info_at_fetch": info, "pox": pox,
                  "limitations": ["Node responses are trusted evidence, not independently verified consensus proofs",
                                  "Check successful canonical deployment receipt separately; retain ABI epoch/clarity_version metadata",
                                  "SHA256 of source text is not the VM contract-hash? commitment"]}
        if args.out:
            args.out.mkdir(parents=True, exist_ok=False)
            (args.out / "source.clar").write_bytes(code.encode("utf-8"))
            (args.out / "evidence.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({k: result[k] for k in ("contract", "tip", "source_sha256", "expected_matches")}))
        else:
            print(json.dumps(result, indent=2))
        if result["expected_matches"] is False:
            raise SystemExit(2)
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
