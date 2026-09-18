<p align="center">
  <img src="docs/screenshot-input.svg" alt="SelfFootprint — authorized self-audit on localhost" width="920"/>
</p>

<h1 align="center">SelfFootprint</h1>
<p align="center"><strong>Minimize what can be known about you.</strong></p>

<p align="center">
  Local-first, authorized <em>self-audit</em> for people and small units.<br/>
  Map the public traces your own identifiers leave. Score the exposure. Get a plan you can finish this week.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-c6f54d?style=flat-square" alt="MIT"/></a>
  <a href="ETHICS.md"><img src="https://img.shields.io/badge/use-authorized%20self--audit%20only-111?style=flat-square" alt="Authorized use"/></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/runs%20on-localhost-6ee7a8?style=flat-square" alt="localhost"/>
  <img src="https://img.shields.io/badge/version-0.2.0-8aa08c?style=flat-square" alt="v0.2.0"/>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-it-does">What it does</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="ETHICS.md">Ethics</a> ·
  <a href="#faq">FAQ</a>
</p>

---

## Why this exists

Most OSINT tools are built for operators looking **outward**. SelfFootprint is built for the person looking **inward**.

It is not a stalking kit. There is no “investigate anyone” mode. The consent checkbox is not decorative — the API rejects the request without it.

## Screenshots

<img src="docs/screenshot-input.svg" alt="Input form with consent gate" width="920"/>

<img src="docs/screenshot-report.svg" alt="Scored report with sourced findings" width="920"/>

<img src="docs/architecture.svg" alt="Architecture" width="920"/>

## Quick start

```bash
git clone https://github.com/Geneticscrol/selffootprint.git
cd selffootprint
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

Windows:

```bat
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

Open [http://127.0.0.1:8787](http://127.0.0.1:8787). Tick consent. Scan **your** identifiers.

Docker: `docker compose up --build`

## What it does

| Collector | Input | Result |
|---|---|---|
| Gravatar | email | Public avatar tied to the email hash |
| GitHub | email or username | Public profile, commit emails |
| Username probe | handle | Allowlisted existence checks |
| DNS / DoH + RDAP | domain | Public records |
| crt.sh | domain | Extra CT hostnames |
| Wayback | domain | Archive snapshots |
| XposedOrNot / HIBP | email | Breach collections |
| Brokers | name / phone / email | Search + opt-out links |
| Public PDFs | full name | Operator-opened `filetype:pdf` searches |
| Unit pack | team handles | Shared-handle collisions |

Findings without a `source` URL are dropped.

Re-scan diffs land in `scans/` (gitignored). Signed HTML is HMAC-SHA256 via `/api/scan.html`.

## What it refuses to do

Read [`ETHICS.md`](ETHICS.md). No targeting UI, no face search, no broker scraping, bind stays `127.0.0.1`.

## License

MIT. See [`LICENSE`](LICENSE).
