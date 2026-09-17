# Agent prompt — SelfFootprint

Paste this at the start of an AI coding session.

```
You are working on SelfFootprint, a local-first authorized self-audit tool.

Read SPEC.md and ETHICS.md first. Do not violate them.

Hard rules:
- Scan only identifiers the operator claims to own. Consent checkbox stays mandatory.
- Do not add "investigate a third party" features, people graphs, or face search.
- Do not scrape Truecaller, Facebook, Instagram, Naukri, Justdial, or data brokers.
  Generate search + opt-out links instead.
- Every finding needs a source URL. No source = delete the finding.
- Bind to 127.0.0.1 by default.
- Prefer small reliable collectors over many flaky ones.

Stack: Python 3.12, FastAPI, httpx, vanilla JS. No React unless asked.

After any change: run a scan against example.com / a throwaway email and confirm
/api/scan still returns JSON.
```
