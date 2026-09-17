const form = document.getElementById("form");
const out = document.getElementById("out");
const go = document.getElementById("go");

function payloadFromForm() {
  const fd = new FormData(form);
  return {
    consent: fd.get("consent") === "on",
    full_name: fd.get("full_name") || "",
    city: fd.get("city") || "",
    emails: fd.get("emails") || "",
    usernames: fd.get("usernames") || "",
    phones: fd.get("phones") || "",
    domains: fd.get("domains") || "",
  };
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  go.disabled = true;
  go.textContent = "Scanning public traces…";
  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payloadFromForm()),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    render(data);
  } catch (err) {
    alert(err.message);
  } finally {
    go.disabled = false;
    go.textContent = "Run self-audit";
  }
});

document.getElementById("md").addEventListener("click", async () => {
  const res = await fetch("/api/scan.md", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payloadFromForm()),
  });
  const text = await res.text();
  const blob = new Blob([text], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "selffootprint-report.md";
  a.click();
});

function render(data) {
  out.hidden = false;
  document.getElementById("score").textContent = data.score;
  document.getElementById("band").textContent = data.band;
  document.getElementById("plan").textContent = data.plan.join("\n");
  document.getElementById("findings").innerHTML = data.findings
    .map(
      (f) => `<article class="card ${f.severity}">
        <strong>${escapeHtml(f.title)}</strong>
        <div class="muted">${f.severity} · ${f.collector}</div>
        <p>${escapeHtml(f.detail)}</p>
        <a href="${f.source}" target="_blank" rel="noopener">source</a>
      </article>`
    )
    .join("");
  document.getElementById("manual").innerHTML = data.manual_checks
    .map(
      (m) => `<article class="card">
        <a href="${m.url}" target="_blank" rel="noopener">${escapeHtml(m.title)}</a>
        <p class="muted">${escapeHtml(m.why)}</p>
      </article>`
    )
    .join("");
  document.getElementById("skipped").innerHTML = (data.skipped || [])
    .map((s) => `<li>${escapeHtml(s)}</li>`)
    .join("");
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
