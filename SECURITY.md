# Security

SelfFootprint is meant to run on the operator’s machine and talk only to public endpoints the operator triggered.

## Report a vulnerability

Open a **private** advisory on GitHub if you can, or file an issue without a proof-of-concept payload and say you want to follow up privately.

Please do **not** open a public issue that includes a working exploit, someone else’s personal identifiers, or leaked credentials.

## Things that are by design

- The app binds to `127.0.0.1` by default.
- There is no user database.
- Scan input is not persisted.
- Optional API keys live in `.env` on your disk.

## Things that are not in scope

- Abuse of public OSINT sources
- Using this tool against people who did not consent
