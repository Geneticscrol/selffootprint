from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = ROOT / "scans"
KEY_PATH = ROOT / "scans" / ".signing_key"


def _key() -> bytes:
    env = os.getenv("REPORT_SIGNING_KEY", "").strip()
    if env:
        return env.encode()
    SCAN_DIR.mkdir(exist_ok=True)
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    raw = os.urandom(32)
    KEY_PATH.write_bytes(raw)
    return raw


def fingerprint(req_payload: dict) -> str:
    basis = {
        "emails": sorted(req_payload.get("emails") or []),
        "usernames": sorted(req_payload.get("usernames") or []),
        "phones": sorted(req_payload.get("phones") or []),
        "domains": sorted(req_payload.get("domains") or []),
        "full_name": req_payload.get("full_name") or "",
        "team": sorted(req_payload.get("team_handles") or []),
    }
    raw = json.dumps(basis, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def sign_payload(obj: dict) -> str:
    body = json.dumps(obj, sort_keys=True, default=str).encode()
    return hmac.new(_key(), body, hashlib.sha256).hexdigest()


def load_previous(fp: str):
    path = SCAN_DIR / f"{fp}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_snapshot(fp: str, report: dict) -> Path:
    SCAN_DIR.mkdir(exist_ok=True)
    path = SCAN_DIR / f"{fp}.json"
    path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return path


def diff_findings(old_ids, new_ids) -> dict:
    old, new = set(old_ids), set(new_ids)
    return {
        "added": sorted(new - old),
        "removed": sorted(old - new),
        "unchanged": sorted(old & new),
        "compared_at": datetime.now(timezone.utc).isoformat(),
    }
