#!/usr/bin/env python3
"""Build a v2rayNG routing-ruleset file from the upstream Throne profile + custom_rules.json.

v2rayNG imports a JSON array of rules (Routing settings -> menu -> "Import rulesets from
clipboard"). It has no URL import, so open the raw file URL, copy everything and paste.

Input : upstream Throne "Bypass_Russia" (rules) + custom_rules.json (Throne format)
        + optional custom_rules_v2rayng.json (native v2rayNG rules, Android-only extras)
Output: My_Bypass_Russia_v2rayNG.json

Only rule fields with a safe equivalent are converted. A rule with any condition that
v2rayNG cannot express is skipped (never widened), and reported on stderr.
"""
import json
import os
import sys

from merge import UPSTREAM, decode  # reuse the Throne decoder
import urllib.request

OUT = "My_Bypass_Russia_v2rayNG.json"
EXTRA = "custom_rules_v2rayng.json"

# Throne rule_set name -> (v2rayNG field, geo tag). Only tags that exist in the default
# v2fly geo files shipped with v2rayNG; an unknown tag makes the core fail to start.
RULESETS = {
    "geoip-ru": ("ip", "geoip:ru"),
    "geosite-category-ru": ("domain", "geosite:category-ru"),
}

# Throne field -> converter returning (v2rayNG field, value); None = not representable.
IGNORED = {"name", "type", "action", "outbound", "disabled"}


def convert(rule, label):
    """Convert one Throne rule to a list of v2rayNG ruleset items (empty = skipped)."""
    action = rule.get("action", "route")
    if action != "route":
        return []  # hijack-dns / sniff etc: v2rayNG handles DNS itself
    if rule.get("disabled"):
        return []
    out = rule.get("outbound")
    if out not in ("proxy", "direct", "block"):
        print(f"skip {label}: outbound {out!r} unsupported", file=sys.stderr)
        return []

    name = rule.get("name") or label
    if name.startswith("imported rule"):
        name = f"{out} {label}"
    item = {"remarks": name, "outboundTag": out}
    domain, ip = [], []
    rs_domain, rs_ip = [], []
    for key, val in rule.items():
        if key in IGNORED:
            continue
        vals = val if isinstance(val, list) else [val]
        if key == "domain_suffix":
            domain += [f"domain:{v}" for v in vals]
        elif key == "domain":
            domain += [f"full:{v}" for v in vals]
        elif key == "domain_keyword":
            domain += [f"keyword:{v}" for v in vals]
        elif key == "domain_regex":
            domain += [f"regexp:{v}" for v in vals]
        elif key == "ip_cidr":
            ip += list(vals)
        elif key == "ip_is_private":
            if val:
                ip.append("geoip:private")
        elif key == "rule_set":
            for rs in vals:
                if rs not in RULESETS:
                    print(f"note {label}: rule set {rs!r} has no v2rayNG tag, dropped", file=sys.stderr)
                    continue
                field, tag = RULESETS[rs]
                (rs_domain if field == "domain" else rs_ip).append(tag)
        elif key == "protocol":
            item["protocol"] = [str(v) for v in vals]
        elif key == "network":
            item["network"] = ",".join(str(v) for v in vals)
        elif key == "port":
            item["port"] = ",".join(str(v) for v in vals)
        elif key == "port_range":
            item["port"] = ",".join(str(v).replace(":", "-") for v in vals)
        else:
            # process_name/process_path (Android uses package names), invert, source_*, ...
            print(f"skip {label}: field {key!r} not supported by v2rayNG", file=sys.stderr)
            return []

    # sing-box ORs the entries of a rule_set list, but Xray ANDs domain and ip inside one
    # rule, so rule-set tags become one item per field. With other conditions present the
    # OR cannot be expressed, so the rule is skipped rather than made wrong.
    if rs_domain or rs_ip:
        if domain or ip or len(item) > 2:
            print(f"skip {label}: rule_set combined with other conditions", file=sys.stderr)
            return []
        items = []
        if rs_domain:
            items.append({"remarks": f"{name} (domains)", "outboundTag": out, "domain": rs_domain})
        if rs_ip:
            items.append({"remarks": f"{name} (IP)", "outboundTag": out, "ip": rs_ip})
        return items

    if domain:
        item["domain"] = domain
    if ip:
        item["ip"] = ip
    if len(item) == 2:  # only remarks + outboundTag => would match everything
        return []
    return [item]


def main() -> int:
    raw = urllib.request.urlopen(UPSTREAM, timeout=30).read().decode()
    prof = decode(raw)
    if prof.get("kind") != "throne-route-profile" or not isinstance(prof.get("rules"), list):
        print("Unexpected upstream format, aborting", file=sys.stderr)
        return 1
    upstream = prof["rules"]
    custom = json.load(open("custom_rules.json", encoding="utf-8"))

    # Same order as the Throne profile: custom rules go before the first rule-set rule.
    idx = next((i for i, r in enumerate(upstream) if "rule_set" in r), len(upstream))
    ordered = upstream[:idx] + custom + upstream[idx:]

    items = []
    for i, r in enumerate(ordered, 1):
        items += convert(r, f"rule #{i}")

    if os.path.exists(EXTRA):  # Android-specific native rules, placed before the geo rules
        extra = json.load(open(EXTRA, encoding="utf-8"))
        pos = next((n for n, it in enumerate(items) if any(str(x).startswith("geo") for x in it.get("ip", []) + it.get("domain", [])) and it["outboundTag"] == "direct" and "geoip:private" not in it.get("ip", [])), len(items))
        items[pos:pos] = extra

    open(OUT, "w", encoding="utf-8").write(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    print(f"OK: {len(items)} v2rayNG rules written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
