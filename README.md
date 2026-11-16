# custom-routes

Throne route profile = upstream `Bypass_Russia` + your own rules, rebuilt automatically.

**Fetch URL for Throne:**
`https://raw.githubusercontent.com/DanilMartyniuk/custom-routes/main/My_Bypass_Russia`

## How it works
- `merge.py` downloads the upstream profile, inserts the rules from `custom_rules.json`
  before the Russian geo rule-set rule (so your rules win), and writes `My_Bypass_Russia`.
- A GitHub Action runs every 6 hours, on manual trigger, and when `custom_rules.json` changes.
- Press **Fetch** in Throne to pull the latest merged profile.

## Adding rules
Edit `custom_rules.json` (a JSON list). `type`, `action` and `name` are filled in
automatically if omitted. Use the same field names Throne exports for each rule kind, e.g.:

```json
[
  {"outbound": "proxy", "domain_suffix": ["example.com"]}
]
```
(Field names such as `domain_suffix` / `process_name` must match Throne's format —
create one rule in the Throne GUI and copy its exported JSON.)

## v2rayNG (Android)
`merge_v2rayng.py` converts the same rules (upstream + `custom_rules.json`) into a v2rayNG
ruleset: `My_Bypass_Russia_v2rayNG.json`. It is rebuilt by the same Action.

v2rayNG cannot import rules from a URL, only from the clipboard or a QR code:
1. Open `https://raw.githubusercontent.com/DanilMartyniuk/custom-routes/main/My_Bypass_Russia_v2rayNG.json`
   in the phone's browser and copy all the text.
2. v2rayNG → Routing settings → ⋮ menu → **Import rulesets from clipboard**.
   (This replaces all rules except ones you have locked.)

Notes:
- Rule sets are mapped only to tags in v2rayNG's default geo files (`geoip:ru`,
  `geosite:category-ru`). `geosite-ru` etc. have no equivalent there and are dropped.
- Rules with conditions v2rayNG can't express (e.g. `process_name`; on Android it means
  package names) are skipped and reported in the Action log. Put Android-only rules in
  `custom_rules_v2rayng.json` (native v2rayNG format, a JSON array); they are inserted
  before the geo rules.
