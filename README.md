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
