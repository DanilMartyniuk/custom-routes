#!/usr/bin/env python3
"""Merge upstream Throne "Bypass_Russia" route profile with custom_rules.json.

Output: My_Bypass_Russia (same throne://route/<base64> format as upstream),
to be used as the Fetch URL in Throne.
"""
import base64
import json
import sys
import urllib.request

UPSTREAM = "https://raw.githubusercontent.com/throneproj/routeprofiles/profile/Bypass_Russia"
PREFIX = "throne://route/"
OUT_NAME = "My Bypass Russia"


def decode(raw: str) -> dict:
    b64 = raw.strip().split(PREFIX)[-1]
    b64 += "=" * (-len(b64) % 4)
    try:
        data = base64.b64decode(b64, validate=True)
    except Exception:
        data = base64.urlsafe_b64decode(b64)
    return json.loads(data)


def encode(profile: dict) -> str:
    js = json.dumps(profile, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return PREFIX + base64.b64encode(js.encode()).decode().rstrip("=")


def main() -> int:
    raw = urllib.request.urlopen(UPSTREAM, timeout=30).read().decode()
    prof = decode(raw)
    if prof.get("kind") != "throne-route-profile" or not isinstance(prof.get("rules"), list):
        print("Unexpected upstream format, aborting", file=sys.stderr)
        return 1

    custom = json.load(open("custom_rules.json", encoding="utf-8"))
    if not isinstance(custom, list) or not all(isinstance(r, dict) for r in custom):
        print("custom_rules.json must be a JSON list of rule objects", file=sys.stderr)
        return 1
    for i, r in enumerate(custom, 1):
        r.setdefault("type", "custom")
        r.setdefault("action", "route")
        r.setdefault("name", f"custom rule #{i}")

    rules = prof["rules"]
    # Custom rules go before the first rule-set (geo) rule so they win over it.
    idx = next((i for i, r in enumerate(rules) if "rule_set" in r), len(rules))
    rules[idx:idx] = custom
    prof["name"] = OUT_NAME

    open("My_Bypass_Russia", "w", encoding="utf-8").write(encode(prof) + "\n")
    print(f"OK: {len(custom)} custom rules inserted at position {idx + 1}, total {len(rules)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
