from __future__ import annotations
import json
from pathlib import Path

def markdown_report(summary):
    lines = ["# LuxeDigital QA Report", "", f"- **Source:** `{summary.source}`", f"- **Files scanned:** {summary.files_scanned}", f"- **Errors:** {summary.errors}", f"- **Warnings:** {summary.warnings}", f"- **Passed checks:** {summary.passed_checks}", "", "## Findings", ""]
    if not summary.findings: lines.append("No errors or warnings found.")
    for f in summary.findings: lines.extend([f"### {f.level} — {f.code}", f"**File:** `{f.path}`", "", f.message, ""])
    return "\n".join(lines)

def write_markdown(summary, path): Path(path).write_text(markdown_report(summary), encoding="utf-8")
def write_json(summary, path): Path(path).write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")
