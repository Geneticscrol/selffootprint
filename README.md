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
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-c6f54d?style=flat-square" alt="Apache 2.0"/></a>
  <a href="ETHICS.md"><img src="https://img.shields.io/badge/use-authorized%20self--audit%20only-111?style=flat-square" alt="Authorized use"/></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/runs%20on-localhost-6ee7a8?style=flat-square" alt="localhost"/>
  <img src="https://img.shields.io/badge/version-0.1.0-8aa08c?style=flat-square" alt="v0.1.0"/>
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

It answers three questions:

1. What can a stranger reconstruct from *my* email, handle, phone, and domain?
2. Which of those traces actually matter in an Indian context (Truecaller, Naukri, Justdial, court PDFs, resume indexes)?
3. What do I delete, lock, or rotate **this week**?

It is not a stalking kit. There is no “investigate anyone” mode. The consent checkbox is not decorative — the API rejects the request without it.

## Screenshots

### 1. You declare identifiers you own

<img src="docs/screenshot-input.svg" alt="Input form with consent gate" width="920"/>

### 2. You get a scored report and a plan

<img src="docs/screenshot-report.svg" alt="Scored report with sourced findings" width="920"/>

### 3. How the pieces fit

<img src="docs/architecture.svg" alt="Architecture: UI → FastAPI → collectors → scoring" width="920"/>

> Want a live walkthrough? Record a 60–90s clip of your own self-scan and drop it at `docs/demo.mp4`.

## Quick start

### Linux / macOS

```bash
git clone https://github.com/Geneticscrol/selffootprint.git
cd selffootprint
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

### Windows (PowerShell or Scoop Python)

```bat
git clone https://github.com/Geneticscrol/selffootprint.git
cd selffootprint
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

If you previously hit `ModuleNotFoundError: dns`:

```bat
python -m pip install dnspython
```

DNS still works without it (falls back to DNS-over-HTTPS).

Open [http://127.0.0.1:8787](http://127.0.0.1:8787). Tick the consent box. Scan **your** identifiers.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

## What it does

Collectors are passive, public, or operator-initiated. People-search sites that forbid scraping are **links you open**, not bots we run.

| Collector | Input | Result |
|---|---|---|
| Gravatar | email | Public avatar tied to the email hash |
| GitHub | email or username | Public profile fields, commit emails on public events |
| Username probe | handle | Existence check on a small allowlist (GitHub, GitLab, HN, HF, …) |
| DNS / DoH + RDAP | domain | Records and whether a registrant role is still published |
| crt.sh | domain | Extra hostnames from certificate transparency |
| Wayback CDX | domain | Whether the Archive still has snapshots |
| XposedOrNot | email | Public breach collections (no key) |
| Have I Been Pwned | email | Optional, needs `HIBP_API_KEY` |
| India + global brokers | name / phone / email | Search + opt-out URLs (Truecaller, Naukri, Justdial, IntelX, …) |

Every finding must include a `source` URL. The scorer drops anything that does not.

### Scoring

| Severity | Weight | Examples |
|---|---|---|
| critical | +35 | Email in a public breach set |
| high | +18 | Commit email on GitHub events |
| medium | +8 | Gravatar, extra CT hostnames, handle cluster |
| low | +3 | Public DNS, a single username hit |

Bands: `0–19` low · `20–44` moderate · `45–69` high · `70–100` critical.

The plan is split into **this week** (critical/high) and **this month** (everything else). Export is Markdown via `/api/scan.md`.

## What it refuses to do

Read [`ETHICS.md`](ETHICS.md) before you add a collector.

- No third-party targeting UI
- No face search
- No scraping Truecaller, Facebook, Instagram, Naukri, or data brokers
- No dark-web crawling
- No “related people” graph
- Default bind address is `127.0.0.1`

If you fork this and remove the consent gate, you are no longer shipping SelfFootprint.

## Architecture

```
browser  →  FastAPI (localhost:8787)
                ├─ collectors.py   public checks + manual link pack
                ├─ scoring.py      weights + playbooks
                └─ report          JSON or Markdown
```

Optional: set `OLLAMA_URL` in `.env` when you want a local model to rewrite the plan in plain language. v0.1 ships the deterministic playbooks either way.

## Configuration

Copy [`.env.example`](.env.example):

| Variable | Required | Purpose |
|---|---|---|
| `HIBP_API_KEY` | no | Official Have I Been Pwned v3 key |
| `OLLAMA_URL` | no | e.g. `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | no | default `llama3.2` |
| `HOST` / `PORT` | no | keep `127.0.0.1` / `8787` unless you know why |

No telemetry. No account system. Scan payloads are not written to disk.

## Project layout

```
selffootprint/
├── AGENT.md              prompt you paste into an AI coding session
├── ETHICS.md             acceptable use — do not delete
├── SPEC.md               product contract for contributors and agents
├── app/
│   ├── main.py           FastAPI
│   ├── collectors.py     public collectors
│   ├── scoring.py        score + remediation playbooks
│   └── templates/        single-page UI
├── data/
│   ├── brokers.json      India + global opt-out pack
│   └── platforms.json    username allowlist
└── docs/                 screenshots used in this README
```

## Development

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

Smoke a scan without the browser:

```bash
curl -s http://127.0.0.1:8787/health
```

Working with an AI coding agent? Paste [`AGENT.md`](AGENT.md) at the top of the session.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md).

## Roadmap

- [x] Local web UI + consent gate
- [x] Cited collectors + Markdown export
- [x] India broker / opt-out pack
- [x] DNS works without `dnspython`
- [ ] 90-second demo video in `docs/demo.mp4`
- [ ] Scheduled re-scan with a diff
- [ ] Unit pack: shared-handle collision across a small team
- [ ] Public-PDF filename collision checks (government docs only)
- [ ] Signed HTML report

## FAQ

**Can I scan someone else?**  
Only with written authorization you keep *outside* this tool. The default and intended use is you, scanning you.

**Does this replace Have I Been Pwned / Maigret / Clearfront?**  
No. Those tools look outward or cover thousands of sites. SelfFootprint is the inward loop: score + remediation + India-specific manual checks, on localhost.

**Why are some results “skipped”?**  
Rate limits (GitHub), missing optional keys (HIBP), or a slow third party (Wayback). Skips are listed; they are not silent failures.

**Is the score scientific?**  
It is a triage number so you know where to start. Treat the findings and the plan as the product, not the integer.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

---

<p align="center">Scan yourself first. Publish the demo second.</p>
