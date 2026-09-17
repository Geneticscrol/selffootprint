from pydantic import BaseModel, Field, field_validator


class ScanRequest(BaseModel):
    consent: bool
    full_name: str = ""
    emails: list[str] = Field(default_factory=list)
    usernames: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    city: str = ""
    team_handles: list[str] = Field(default_factory=list)
    save_snapshot: bool = True

    @field_validator("emails", "usernames", "phones", "domains", "team_handles", mode="before")
    @classmethod
    def split_and_clean(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            parts = [p.strip() for p in v.replace(";", ",").split(",")]
            return [p for p in parts if p]
        return [str(x).strip() for x in v if str(x).strip()]

    @field_validator("full_name", "city", mode="before")
    @classmethod
    def strip_str(cls, v):
        return (v or "").strip()


class Finding(BaseModel):
    id: str
    severity: str
    title: str
    detail: str
    source: str
    remediation: str
    collector: str


class ManualCheck(BaseModel):
    title: str
    url: str
    why: str
    region: str = ""


class ScanReport(BaseModel):
    score: int
    band: str
    findings: list[Finding]
    plan: list[str]
    manual_checks: list[ManualCheck]
    skipped: list[str] = Field(default_factory=list)
    fingerprint: str = ""
    signature: str = ""
    diff: dict | None = None
