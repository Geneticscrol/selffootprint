# SPEC.md — SelfFootprint v0.1

Written by the project owner. Agents must follow this file.

## One-sentence product

A localhost app that takes *my* identifiers, lists public traces with sources, scores risk, and prints a one-week remediation plan.

## Non-goals for v0.1

- No user accounts, no multi-tenant SaaS.
- No dark-web crawling.
- No facial recognition.
- No scraping of Truecaller, Facebook, Instagram, Naukri, or data brokers.
- No “related people” graph.
- No mobile number OSINT beyond validation + search links.

## Inputs

```json
{
  "consent": true,
  "full_name": "optional",
  "emails": ["you@domain"],
  "usernames": ["handle"],
  "phones": ["+91..."],
  "domains": ["example.in"],
  "city": "optional, used only for search-link templates"
}
```

Reject the request if `consent` is not true. Reject if every identifier field is empty.

## Outputs

A report object with score 0-100, band, findings (each with source URL), plan, and manual_checks.

## Scoring

Start at 0. Cap at 100.

- Critical finding +35
- High +18
- Medium +8
- Low +3

Bands: 0–19 low, 20–44 moderate, 45–69 high, 70+ critical.

A finding without `source` is invalid.

## UX

- Dark, dense, operational. Not a consumer-privacy cartoon.
- Consent is a blocking checkbox.
- Findings grouped by severity.
- Export JSON + Markdown.

## Agent rules

- Do not add targeting features.
- Do not add scrapers for people-search sites.
- Prefer fewer reliable collectors over twenty flaky ones.
- If a network check is ambiguous, mark `severity: low` and say so.
