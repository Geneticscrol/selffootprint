from __future__ import annotations

import hashlib, json, os, re
from pathlib import Path
from urllib.parse import quote_plus
import dns.resolver
import httpx
from .models import Finding, ManualCheck, ScanRequest

DATA = Path(__file__).resolve().parent.parent / "data"
UA = "SelfFootprint/0.1 (+https://github.com/Geneticscrol/selffootprint; authorized-self-audit)"


def _client() -> httpx.Client:
    return httpx.Client(timeout=12.0, follow_redirects=True, headers={"User-Agent": UA})


def _add(findings, **kw):
    findings.append(Finding(**kw))


def _norm_phone(raw: str) -> str:
    d = re.sub(r"\D", "", raw)
    if d.startswith("91") and len(d) == 12:
        d = d[2:]
    if d.startswith("0") and len(d) == 11:
        d = d[1:]
    return d


def collect_gravatar(req, findings, skipped):
    if not req.emails:
        skipped.append("gravatar: no email"); return
    with _client() as c:
        for email in req.emails:
            digest = hashlib.md5(email.strip().lower().encode()).hexdigest()
            src = f"https://gravatar.com/{digest}"
            try:
                r = c.get(f"https://www.gravatar.com/avatar/{digest}?d=404")
                hit = r.status_code == 200
                _add(findings, id=f"gravatar:{email}", collector="gravatar", source=src,
                     severity="medium" if hit else "low",
                     title=("Public Gravatar exists for " if hit else "No Gravatar for ") + email,
                     detail="A globally-addressable avatar is tied to this email hash." if hit else "Keep it that way.",
                     remediation="lock-gravatar" if hit else "keep-clean")
            except httpx.HTTPError as e:
                skipped.append(f"gravatar:{email}:{type(e).__name__}")


def collect_github(req, findings, skipped):
    handles = list(req.usernames)
    with _client() as c:
        hdr = {"Accept": "application/vnd.github+json"}
        for email in req.emails:
            try:
                r = c.get("https://api.github.com/search/users", params={"q": f"{email} in:email"}, headers=hdr)
                if r.status_code == 403:
                    skipped.append("github:search rate-limited"); continue
                if r.status_code != 200:
                    continue
                for user in (r.json().get("items") or [])[:5]:
                    login = user.get("login") or ""
                    if not login:
                        continue
                    handles.append(login)
                    _add(findings, id=f"github-email:{email}:{login}", severity="high",
                         title=f"GitHub user {login} is tied to {email}",
                         detail="Commit history may still expose this address.",
                         source=user.get("html_url") or f"https://github.com/{login}",
                         remediation="github-email-privacy", collector="github")
            except httpx.HTTPError as e:
                skipped.append(f"github-search:{type(e).__name__}")
        seen = set()
        for handle in handles:
            h = handle.lstrip("@").strip()
            if not h or h in seen:
                continue
            seen.add(h)
            try:
                r = c.get(f"https://api.github.com/users/{h}", headers=hdr)
                if r.status_code != 200:
                    continue
                u = r.json()
                bits = [x for x in (u.get("name"), u.get("company"), u.get("location"), u.get("blog")) if x]
                _add(findings, id=f"github-profile:{h}",
                     severity="medium" if bits else "low",
                     title=f"GitHub profile {h} is public",
                     detail=("Visible fields: " + ", ".join(bits)) if bits else "Minimal public fields.",
                     source=u.get("html_url") or f"https://github.com/{h}",
                     remediation="github-hygiene", collector="github")
                ev = c.get(f"https://api.github.com/users/{h}/events/public", headers=hdr)
                if ev.status_code != 200:
                    continue
                emails = set()
                for event in ev.json()[:30]:
                    for commit in (event.get("payload") or {}).get("commits") or []:
                        em = ((commit.get("author") or {}).get("email") or "").strip()
                        if em and "users.noreply.github.com" not in em:
                            emails.add(em)
                for em in sorted(emails)[:8]:
                    _add(findings, id=f"github-commit-email:{h}:{em}", severity="high",
                         title=f"Commit email {em} visible on {h}",
                         detail="Switch git to the GitHub no-reply address.",
                         source=f"https://github.com/{h}",
                         remediation="github-email-privacy", collector="github")
            except httpx.HTTPError as e:
                skipped.append(f"github-profile:{h}:{type(e).__name__}")


def collect_usernames(req, findings, skipped):
    if not req.usernames:
        skipped.append("usernames: none provided"); return
    platforms = json.loads((DATA / "platforms.json").read_text())
    with _client() as c:
        for handle in req.usernames:
            u = handle.lstrip("@").strip()
            hits = []
            for p in platforms:
                url = p["url"].format(u=u)
                try:
                    r = c.get(url)
                    if r.status_code in p.get("ok", [200]) and r.status_code < 400:
                        hits.append(url)
                        _add(findings, id=f"username:{p['id']}:{u}", severity="low",
                             title=f"Handle {u} exists on {p['name']}",
                             detail="Same handle across sites is how strangers stitch an identity.",
                             source=url.replace("/about.json", ""),
                             remediation="handle-hygiene", collector="usernames")
                except httpx.HTTPError:
                    continue
            if len(hits) >= 4:
                _add(findings, id=f"username-cluster:{u}", severity="medium",
                     title=f"Handle {u} repeats on {len(hits)} allowlisted sites",
                     detail="Split high-risk communities from your real name.",
                     source=hits[0], remediation="handle-hygiene", collector="usernames")


def collect_dns_whois(req, findings, skipped):
    if not req.domains:
        skipped.append("dns: no domain"); return
    resolver = dns.resolver.Resolver(); resolver.lifetime = 5
    for domain in req.domains:
        d = domain.lower().removeprefix("http://").removeprefix("https://").split("/")[0]
        records = {}
        for rtype in ("A", "AAAA", "MX", "NS", "TXT"):
            try:
                records[rtype] = [rr.to_text() for rr in resolver.resolve(d, rtype)]
            except Exception:
                pass
        if records:
            detail = "; ".join(f"{k}={','.join(v[:4])}" for k, v in records.items())
            _add(findings, id=f"dns:{d}", severity="low", title=f"Public DNS for {d}",
                 detail=detail[:500], source=f"https://dns.google/query?name={d}&type=A",
                 remediation="domain-privacy", collector="dns")
        joined = " ".join(records.get("TXT") or []).lower()
        if "spf" in joined or "google-site-verification" in joined:
            _add(findings, id=f"dns-txt-vendor:{d}", severity="low",
                 title=f"TXT records advertise vendors for {d}",
                 detail="Verification strings reveal which SaaS you run.",
                 source=f"https://dns.google/query?name={d}&type=TXT",
                 remediation="domain-privacy", collector="dns")
        try:
            with _client() as c:
                r = c.get(f"https://rdap.org/domain/{d}")
            if r.status_code == 200:
                roles = []
                for ent in r.json().get("entities") or []:
                    roles += ent.get("roles") or []
                _add(findings, id=f"rdap:{d}",
                     severity="medium" if "registrant" in roles else "low",
                     title=f"RDAP record exists for {d}",
                     detail="Roles: " + (", ".join(sorted(set(roles))) or "none listed"),
                     source=f"https://rdap.org/domain/{d}",
                     remediation="domain-privacy", collector="whois")
        except httpx.HTTPError as e:
            skipped.append(f"rdap:{d}:{type(e).__name__}")


def collect_crtsh(req, findings, skipped):
    if not req.domains:
        skipped.append("crtsh: no domain"); return
    with _client() as c:
        for domain in req.domains:
            d = domain.lower().split("/")[0]
            try:
                r = c.get("https://crt.sh/", params={"q": d, "output": "json"})
                if r.status_code != 200:
                    skipped.append(f"crtsh:{d}:http {r.status_code}"); continue
                names = set()
                for row in r.json()[:200]:
                    for n in (row.get("name_value") or "").split("\n"):
                        n = n.strip().lstrip("*.")
                        if n:
                            names.add(n)
                extra = sorted(n for n in names if n != d)[:25]
                if extra:
                    _add(findings, id=f"crtsh:{d}", severity="medium",
                         title=f"CT lists {len(extra)} extra hostnames for {d}",
                         detail="Hostnames: " + ", ".join(extra),
                         source=f"https://crt.sh/?q={d}",
                         remediation="domain-privacy", collector="crtsh")
            except Exception as e:
                skipped.append(f"crtsh:{d}:{type(e).__name__}")


def collect_wayback(req, findings, skipped):
    if not req.domains:
        skipped.append("wayback: no domain"); return
    with _client() as c:
        for t in req.domains:
            host = t.lower().split("/")[0]
            try:
                r = c.get("https://web.archive.org/cdx/search/cdx", params={
                    "url": host, "output": "json", "limit": 5,
                    "fl": "timestamp,original,statuscode", "filter": "statuscode:200"})
                if r.status_code != 200:
                    skipped.append(f"wayback:{host}:http {r.status_code}"); continue
                rows = r.json()
                if len(rows) > 1:
                    _add(findings, id=f"wayback:{host}", severity="low",
                         title=f"Internet Archive has snapshots of {host}",
                         detail=f"Latest sampled snapshot {rows[1][0]}.",
                         source=f"https://web.archive.org/web/*/{host}",
                         remediation="wayback-takedown", collector="wayback")
            except Exception as e:
                skipped.append(f"wayback:{host}:{type(e).__name__}")


def collect_breaches(req, findings, skipped):
    if not req.emails:
        skipped.append("breach: no email"); return
    hibp = os.getenv("HIBP_API_KEY", "").strip()
    with _client() as c:
        for email in req.emails:
            try:
                r = c.get(f"https://api.xposedornot.com/v1/check-email/{email}")
                if r.status_code == 200:
                    data = r.json() if isinstance(r.json(), dict) else {}
                    breaches = data.get("breaches") or data.get("BreachEvents") or []
                    if isinstance(data.get("data"), dict):
                        breaches = breaches or data["data"].get("breaches") or []
                    if isinstance(breaches, dict):
                        breaches = list(breaches.keys())
                    if breaches:
                        names = breaches if isinstance(breaches[0], str) else [str(b) for b in breaches]
                        _add(findings, id=f"xon:{email}", severity="critical",
                             title=f"{email} appears in public breach collections",
                             detail="Sources: " + ", ".join(names[:12]),
                             source="https://xposedornot.com/",
                             remediation="rotate-credentials", collector="breach")
            except httpx.HTTPError as e:
                skipped.append(f"xposedornot:{email}:{type(e).__name__}")
            if not hibp:
                skipped.append("hibp: no HIBP_API_KEY"); continue
            try:
                r = c.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                          params={"truncateResponse": "false"},
                          headers={"hibp-api-key": hibp, "user-agent": UA})
                if r.status_code == 200:
                    names = [b.get("Name", "?") for b in r.json()]
                    _add(findings, id=f"hibp:{email}", severity="critical",
                         title=f"Have I Been Pwned lists {email}",
                         detail="Breaches: " + ", ".join(names[:15]),
                         source="https://haveibeenpwned.com/",
                         remediation="rotate-credentials", collector="breach")
                elif r.status_code not in (404,):
                    skipped.append(f"hibp:{email}:http {r.status_code}")
            except httpx.HTTPError as e:
                skipped.append(f"hibp:{email}:{type(e).__name__}")


def collect_manual(req) -> list[ManualCheck]:
    brokers = json.loads((DATA / "brokers.json").read_text())
    name = req.full_name or (req.usernames[0] if req.usernames else "")
    email = req.emails[0] if req.emails else ""
    domain = req.domains[0] if req.domains else (email.split("@")[-1] if "@" in email else "")
    phone = _norm_phone(req.phones[0]) if req.phones else ""
    checks = []
    for b in brokers:
        url = (b["search_url"].replace("{name_q}", quote_plus(name))
               .replace("{name_dash}", quote_plus(name.replace(" ", "-")))
               .replace("{city_q}", quote_plus(req.city))
               .replace("{email}", quote_plus(email))
               .replace("{domain}", quote_plus(domain))
               .replace("{phone_digits}", phone))
        checks.append(ManualCheck(
            title=f"{b['name']} — search then opt out", url=url,
            why=b["why"] + f" Opt-out: {b.get('opt_out', '')}", region=b.get("region", "")))
    if req.usernames:
        u = req.usernames[0].lstrip("@")
        checks.append(ManualCheck(title="X / Twitter handle", url=f"https://x.com/{u}",
                                  why="Lock DMs, strip location and birthday.", region="GLOBAL"))
        checks.append(ManualCheck(title="Instagram handle", url=f"https://www.instagram.com/{u}/",
                                  why="Public tagged photos are a face-search gift.", region="GLOBAL"))
    return checks


COLLECTORS = [
    ("Gravatar", collect_gravatar), ("GitHub", collect_github),
    ("Usernames", collect_usernames), ("DNS / RDAP", collect_dns_whois),
    ("crt.sh", collect_crtsh), ("Wayback", collect_wayback),
    ("Breaches", collect_breaches),
]


def run_scan(req: ScanRequest):
    findings, skipped = [], []
    for name, fn in COLLECTORS:
        try:
            fn(req, findings, skipped)
        except Exception as exc:
            skipped.append(f"{name}:{type(exc).__name__}: {exc}")
    return findings, collect_manual(req), skipped
