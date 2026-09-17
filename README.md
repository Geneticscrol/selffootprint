# SelfFootprint

**Minimize what can be known about you.**

SelfFootprint is a local-first, authorized **self-audit** tool. You enter identifiers you own. It maps the public traces those identifiers leave, scores the exposure, and gives a remediation plan you can actually follow.

It is not a stalking kit. There is no “investigate anyone” mode.

## Why this exists

Most OSINT tools are built for operators looking *outward*. SelfFootprint is built for the person (or small unit) looking *inward*:

- What can a stranger reconstruct from my email, handle, phone, and domain?
- Which of those traces are high-risk in an Indian context?
- What do I delete, lock, or rotate this week?

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8787
```

Open [http://127.0.0.1:8787](http://127.0.0.1:8787).

Docker:

```bash
docker compose up --build
```

## What v0.1 actually does

Passive, public, or user-initiated checks only:

| Collector | Needs | What you get |
|---|---|---|
| Gravatar | email | Public avatar / profile hash exposure |
| GitHub | email or username | Public profile, leaked commit emails |
| Username probe | handle | Existence checks on a small allowlist of sites |
| DNS / WHOIS | domain | Registrations, nameservers, public registrant crumbs |
| crt.sh | domain | Certificate-transparency hostnames |
| Wayback | domain or URL-shaped input | Archived snapshots of your own sites |
| Breach lookup | email | XposedOrNot (free) + optional Have I Been Pwned key |
| Search dorks | any | Ready-to-run queries — **you** open them |
| India + global brokers | name / phone / email | Opt-out links and people-search hygiene |

Nothing is sent to a SelfFootprint cloud. Optional API keys stay in your `.env`.

## Rules of the road

Read [`ETHICS.md`](ETHICS.md) before you run a scan.

- Scan only identifiers you own or have written authorization to audit.
- Do not use this to target journalists, activists, partners, or strangers.
- Collectors that would require scraping ToS-protected people-search sites are **links**, not bots.

## Stack

- Python 3.11+, FastAPI, httpx
- Single-page UI, no account system
- JSON report export
- Optional `OLLAMA_URL` to rewrite the plan in plain language

## Roadmap

- [ ] Browser extension “scan this logged-in profile’s privacy settings”
- [ ] DigiLocker / government-PDF filename collision checks (public docs only)
- [ ] Unit pack: shared-handle collision across a small team
- [ ] Scheduled re-scan with a diff
- [ ] Signed HTML/PDF report

## License

Apache-2.0. See [`LICENSE`](LICENSE).
