from .models import Finding, ScanReport, ManualCheck

WEIGHT = {"critical": 35, "high": 18, "medium": 8, "low": 3}

PLAYBOOKS = {
    "lock-gravatar": "Delete or blank the Gravatar profile tied to this email. Use a dedicated contact address that never touches avatars.",
    "keep-clean": "No action. Do not create a Gravatar later on a personal inbox.",
    "github-email-privacy": "GitHub → Settings → Emails → keep my email private. Set git user.email to the users.noreply.github.com address.",
    "github-hygiene": "Strip location, employer, and personal blog from the public profile if this account is tied to your real name.",
    "handle-hygiene": "Stop reusing the same handle on high-risk sites. Keep one real-name handle and one anonymous handle. Do not cross-link them.",
    "domain-privacy": "Enable registrar WHOIS privacy. Drop leftover staging hostnames. Remove personal names from TXT / administrative contacts.",
    "wayback-takedown": "Use the Internet Archive removal process for pages that still show a phone, address, or old resume.",
    "rotate-credentials": "Assume the password and any reused security questions are public. Rotate the inbox, then every account that shared that password. Turn on a password manager + hardware key.",
}


def score_findings(findings: list[Finding]) -> tuple[int, str]:
    seen = set()
    total = 0
    for f in findings:
        if f.remediation == "keep-clean":
            continue
        key = (f.severity, f.collector)
        bump = WEIGHT.get(f.severity, 0)
        if key in seen:
            bump = max(1, bump // 3)
        seen.add(key)
        total += bump
    total = min(100, total)
    if total >= 70:
        band = "critical"
    elif total >= 45:
        band = "high"
    elif total >= 20:
        band = "moderate"
    else:
        band = "low"
    return total, band


def build_plan(findings: list[Finding]) -> list[str]:
    week: list[str] = []
    month: list[str] = []
    for f in findings:
        text = PLAYBOOKS.get(f.remediation)
        if not text:
            continue
        target = week if f.severity in {"critical", "high"} else month
        if text not in target:
            target.append(text)
    plan = []
    if week:
        plan.append("This week:")
        plan.extend(f"  • {s}" for s in week)
    if month:
        plan.append("This month:")
        plan.extend(f"  • {s}" for s in month)
    if not plan:
        plan = ["No urgent public traces from automated collectors. Still run the manual broker checks once."]
    return plan


def assemble(findings: list[Finding], manual: list[ManualCheck], skipped: list[str]) -> ScanReport:
    clean = [f for f in findings if f.source]
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    clean.sort(key=lambda f: (order.get(f.severity, 9), f.id))
    score, band = score_findings(clean)
    return ScanReport(
        score=score,
        band=band,
        findings=clean,
        plan=build_plan(clean),
        manual_checks=manual,
        skipped=skipped,
    )
