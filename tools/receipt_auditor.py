#!/usr/bin/env python3
"""Filesystem capability receipt auditor for loop agents.

policy_owner: local maintainer
log_path: output/audit/receipts.jsonl
approval_mode: local read-only scan
recovery_path: delete generated output/audit files; no external mutation is performed
verification_command: python3 tools/receipt_auditor.py --target .
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


RECEIPT_FIELDS = (
    "policy_owner",
    "log_path",
    "approval_mode",
    "recovery_path",
    "verification_command",
)

TEXT_SUFFIXES = {
    ".bash",
    ".conf",
    ".ini",
    ".js",
    ".json",
    ".py",
    ".service",
    ".sh",
    ".toml",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
    "knowledge",
    "output",
    "receipts",
}

ACTUATOR_PATTERNS = {
    "shell-command": re.compile(r"\b(subprocess|os\.system|shell=True|exec_command|eval\b|bash\b|sh\b)"),
    "network-write": re.compile(r"\b(POST|PUT|PATCH|DELETE|requests\.(post|put|patch|delete)|curl\b.*\b-X\b)", re.I),
    "git-mutation": re.compile(r"\bgit\s+(push|commit|tag|merge|rebase)\b"),
    "deploy": re.compile(r"\b(vercel|deploy|rsync|scp|systemctl\s+restart|docker\s+push)\b", re.I),
    "social-or-email": re.compile(r"\b(mastodon|reddit|hacker news|hn\.py|sendmail|smtp|email|reply|post)\b", re.I),
    "credential-surface": re.compile(r"\b(oauth|token|secret|password|credential|cookie|api[_-]?key)\b", re.I),
    "scheduler": re.compile(r"\b(cron|systemd|timer|while true|sleep\s+\$?\{?[A-Z_]*SECONDS|schedule)\b", re.I),
    "file-write": re.compile(r"\b(open\(.+['\"]w|write_text|append_text|tee -a|>>|mv\b|rm\b)\b"),
}

BLAST_RADIUS = {
    "credential-surface": "critical",
    "deploy": "high",
    "network-write": "high",
    "git-mutation": "high",
    "social-or-email": "medium",
    "shell-command": "medium",
    "scheduler": "medium",
    "file-write": "low",
}


@dataclass
class Finding:
    path: str
    actuator_class: str
    blast_radius: str
    evidence: str
    receipt: dict[str, str] = field(default_factory=dict)

    @property
    def missing(self) -> list[str]:
        return [field for field in RECEIPT_FIELDS if not self.receipt.get(field)]


def is_hidden_or_secret(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    return any(part.startswith(".") for part in rel.parts) or path.name.endswith((".pem", ".key"))


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if is_hidden_or_secret(path, root):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile", "Procfile"}:
            yield path


def safe_read(path: Path) -> str:
    try:
        if path.stat().st_size > 512_000:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def extract_receipt(text: str) -> dict[str, str]:
    receipt: dict[str, str] = {}
    for field_name in RECEIPT_FIELDS:
        match = re.search(rf"(?im)^\s*(?:#|//|<!--)?\s*{field_name}\s*:\s*(.+?)\s*(?:-->)?\s*$", text)
        if match:
            receipt[field_name] = match.group(1).strip()
    return receipt


def evidence_line(text: str, pattern: re.Pattern[str]) -> str:
    for line in text.splitlines():
        if pattern.search(line):
            clean = re.sub(r"\s+", " ", line.strip())
            return clean[:180]
    return "pattern matched"


def audit(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_text_files(root):
        text = safe_read(path)
        if not text:
            continue
        rel = path.relative_to(root).as_posix()
        receipt = extract_receipt(text)
        for actuator_class, pattern in ACTUATOR_PATTERNS.items():
            if pattern.search(text):
                findings.append(
                    Finding(
                        path=rel,
                        actuator_class=actuator_class,
                        blast_radius=BLAST_RADIUS[actuator_class],
                        evidence=evidence_line(text, pattern),
                        receipt=receipt,
                    )
                )
    return sorted(findings, key=lambda item: (severity_rank(item.blast_radius), item.path, item.actuator_class))


def severity_rank(value: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(value, 9)


def ensure_outdir(root: Path, outdir: Path | None) -> Path:
    target = outdir or (Path.cwd() / "output" / "audit")
    target.mkdir(parents=True, exist_ok=True)
    (target / "receipts").mkdir(exist_ok=True)
    return target


def write_outputs(target_root: Path, outdir: Path, findings: list[Finding]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    digest = hashlib.sha256(str(target_root.resolve()).encode()).hexdigest()[:12]

    ledger = [
        "# Capability Ledger",
        "",
        f"- generated: `{generated}`",
        f"- target: `{target_root}`",
        f"- target_id: `{digest}`",
        "",
        "| Blast | Class | Path | Missing Receipt Fields | Evidence |",
        "|---|---|---|---|---|",
    ]
    for finding in findings:
        missing = ", ".join(finding.missing) or "none"
        ledger.append(
            f"| {finding.blast_radius} | {finding.actuator_class} | `{finding.path}` | {missing} | {escape_cell(finding.evidence)} |"
        )
    (outdir / "capability-ledger.md").write_text("\n".join(ledger) + "\n", encoding="utf-8")

    gaps = ["# Missing Receipts", ""]
    for finding in findings:
        if not finding.missing:
            continue
        gaps.append(f"## {finding.blast_radius.upper()} - {finding.path} ({finding.actuator_class})")
        gaps.append("")
        gaps.append(f"- missing: {', '.join(finding.missing)}")
        gaps.append(f"- evidence: `{finding.evidence}`")
        gaps.append("")
    if len(gaps) == 2:
        gaps.append("No missing receipt fields found for detected actuator surfaces.")
    (outdir / "missing-receipts.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")

    bypass = ["# Bypass Paths", ""]
    risky = [item for item in findings if item.actuator_class in {"shell-command", "credential-surface", "scheduler"}]
    for item in risky:
        bypass.append(f"- `{item.path}` can bypass narrow tool receipts through `{item.actuator_class}`. Evidence: `{item.evidence}`")
    if len(bypass) == 2:
        bypass.append("No obvious bypass paths detected.")
    (outdir / "bypass-paths.md").write_text("\n".join(bypass) + "\n", encoding="utf-8")

    drill_result = run_file_write_recovery_drill(outdir, generated)
    drills = [
        "# Recovery Drills",
        "",
        "## Completed Local Drill - file-write receipt reconstruction",
        "",
        f"- status: `{drill_result['status']}`",
        f"- receipt: `{drill_result['receipt_path']}`",
        f"- before_sha256: `{drill_result['before_sha256']}`",
        f"- after_sha256: `{drill_result['after_sha256']}`",
        f"- restored_sha256: `{drill_result['restored_sha256']}`",
        f"- verified: `{drill_result['verified']}`",
        "",
        "This drill mutates only `output/audit/receipts/file-write-drill-sandbox.txt` and proves that the receipt contains enough state to reconstruct the pre-write file exactly.",
        "",
        "## Manual Drills Still Needed",
        "",
        "- Pick one high or critical actuator and prove its token can be revoked.",
        "- Pick one deploy path and prove rollback from a bad deploy.",
        "- Pick one social/email path and prove exact message logs exist.",
        "- Pick one scheduler and prove it can be paused without killing unrelated services.",
        "- Pick one shell-command bypass and prove the command transcript is captured.",
    ]
    (outdir / "recovery-drills.md").write_text("\n".join(drills) + "\n", encoding="utf-8")

    with (outdir / "receipts.jsonl").open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(
                json.dumps(
                    {
                        "generated": generated,
                        "target_id": digest,
                        "path": finding.path,
                        "actuator_class": finding.actuator_class,
                        "blast_radius": finding.blast_radius,
                        "evidence": finding.evidence,
                        "receipt": finding.receipt,
                        "missing": finding.missing,
                    },
                    sort_keys=True,
                )
                + "\n"
            )


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_file_write_recovery_drill(outdir: Path, generated: str) -> dict[str, str | bool]:
    receipts_dir = outdir / "receipts"
    receipts_dir.mkdir(exist_ok=True)
    sandbox = receipts_dir / "file-write-drill-sandbox.txt"
    receipt_path = receipts_dir / "file-write-recovery-drill.json"

    before = "receipt-auditor recovery drill: before\n"
    after = "receipt-auditor recovery drill: after\n"
    sandbox.write_text(before, encoding="utf-8")
    before_sha = sha256_text(before)

    sandbox.write_text(after, encoding="utf-8")
    after_sha = sha256_text(after)

    receipt = {
        "generated": generated,
        "actuator_class": "file-write",
        "path": sandbox.relative_to(outdir).as_posix(),
        "policy_owner": "local maintainer",
        "approval_mode": "local drill sandbox",
        "log_path": receipt_path.relative_to(outdir).as_posix(),
        "recovery_path": "restore before_content from this receipt",
        "verification_command": "python3 tools/receipt_auditor.py --target .",
        "before_content": before,
        "before_sha256": before_sha,
        "after_content": after,
        "after_sha256": after_sha,
    }

    recovered = str(receipt["before_content"])
    sandbox.write_text(recovered, encoding="utf-8")
    restored_sha = sha256_text(sandbox.read_text(encoding="utf-8"))
    verified = restored_sha == before_sha and before_sha != after_sha
    receipt["restored_sha256"] = restored_sha
    receipt["verified"] = verified

    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "status": "passed" if verified else "failed",
        "receipt_path": receipt_path.relative_to(outdir).as_posix(),
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "restored_sha256": restored_sha,
        "verified": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an agent tree for actuator receipt gaps.")
    parser.add_argument("--target", default=".", help="Directory to audit")
    parser.add_argument("--outdir", default=None, help="Output directory, default: ./output/audit")
    args = parser.parse_args()

    target_root = Path(args.target).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        parser.error(f"target is not a directory: {target_root}")

    outdir = ensure_outdir(target_root, Path(args.outdir).expanduser().resolve() if args.outdir else None)
    findings = audit(target_root)
    write_outputs(target_root, outdir, findings)
    missing_count = sum(1 for item in findings if item.missing)
    print(f"Audited {target_root}")
    print(f"Detected actuator surfaces: {len(findings)}")
    print(f"Findings missing receipts: {missing_count}")
    print(f"Wrote {outdir}")
    return 1 if missing_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
