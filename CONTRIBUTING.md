# Contributing

Thanks for wanting to make SelfFootprint better. Read [`ETHICS.md`](ETHICS.md) and [`SPEC.md`](SPEC.md) before you write code.

## What we want

- New *cited* collectors that stay inside authorized self-audit
- Better India-specific opt-out links in `data/brokers.json`
- UI clarity, accessibility, export formats
- Tests around scoring and consent rejection

## What we will close

- “Investigate anyone” mode
- Scrapers for Truecaller, Facebook, Instagram, Naukri, Justdial, Spokeo
- Face search, people graphs, dark-web modules
- Anything that binds to `0.0.0.0` by default

## How to send a change

1. Fork and branch from `main`.
2. Keep findings sourced. No `source` URL → the finding is invalid.
3. If you add a collector, document the ToS situation in a docstring.
4. Open a PR that says what a reviewer should click.

If you are using an AI agent, start the session with [`AGENT.md`](AGENT.md).
