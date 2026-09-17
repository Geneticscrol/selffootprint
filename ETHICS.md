# Ethics and acceptable use

SelfFootprint exists so people can reduce their own public attack surface.

## Allowed

- Scanning identifiers you own (your email, your handle, your phone, your domain).
- Scanning a system you administer, with written authorization stored outside this tool.
- Teaching OPSEC / privacy classes with consenting volunteers.
- Research on *your own* exposure.

## Not allowed

- Investigating a person who has not authorized the scan.
- Doxxing, stalking, workplace surveillance of colleagues, or “background checks” sold as a service.
- Feeding results into harassment, blackmail, or targeting.
- Circumventing authentication, CAPTCHAs, or site bans.
- Mass-scanning of phone books, electoral rolls, or leaked databases.

## Design constraints we will not remove

1. The UI requires an explicit “these identifiers are mine / authorized” checkbox.
2. People-search and Truecaller-class sites are opened as links. We do not scrape them.
3. Reports include a provenance field. If a collector cannot cite a public URL or a local check, the finding is dropped.
4. Default bind address is localhost.

## If you fork this

Keep the consent gate. If you add a collector that hits a site, document the ToS situation in the collector docstring. Prefer generating a search URL over fetching HTML.
