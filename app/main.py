from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .collectors import run_scan
from .models import ScanRequest, ScanReport
from .scoring import assemble

load_dotenv()

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="SelfFootprint", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(ROOT / "templates" / "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/scan", response_model=ScanReport)
def scan(req: ScanRequest):
    if not req.consent:
        raise HTTPException(400, "Consent is required. Scan only identifiers you own.")
    has_id = any([req.emails, req.usernames, req.phones, req.domains, req.full_name])
    if not has_id:
        raise HTTPException(400, "Provide at least one identifier you own.")
    findings, manual, skipped = run_scan(req)
    return assemble(findings, manual, skipped)


@app.post("/api/scan.md")
def scan_markdown(req: ScanRequest):
    report = scan(req)
    lines = [
        f"# SelfFootprint report",
        f"",
        f"Score **{report.score}/100** ({report.band})",
        "",
        "## Findings",
    ]
    for f in report.findings:
        lines += [
            f"### {f.title}",
            f"- severity: {f.severity}",
            f"- source: {f.source}",
            f"- {f.detail}",
            "",
        ]
    lines += ["## Plan", ""]
    lines += list(report.plan)
    lines += ["", "## Manual checks", ""]
    for m in report.manual_checks:
        lines.append(f"- [{m.title}]({m.url}) — {m.why}")
    if report.skipped:
        lines += ["", "## Collectors skipped / failed", ""]
        lines += [f"- {s}" for s in report.skipped]
    return PlainTextResponse("\n".join(lines), media_type="text/markdown")
