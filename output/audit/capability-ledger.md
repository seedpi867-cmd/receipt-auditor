# Capability Ledger

- generated: `2026-05-04T00:52:48.542476+00:00`
- target: `/home/seed/receipt-auditor`
- target_id: `f96f59a2f7b7`

| Blast | Class | Path | Missing Receipt Fields | Evidence |
|---|---|---|---|---|
| critical | credential-surface | `config.sh` | none | # Codex (OpenAI) — free with OAuth login |
| critical | credential-surface | `tools/receipt_auditor.py` | none | "credential-surface": re.compile(r"\b(oauth\|token\|secret\|password\|credential\|cookie\|api[_-]?key)\b", re.I), |
| high | network-write | `brain-loop.sh` | none | # ── POST-CYCLE ─────────────────────────────────────── |
| high | deploy | `tools/receipt_auditor.py` | none | "deploy": re.compile(r"\b(vercel\|deploy\|rsync\|scp\|systemctl\s+restart\|docker\s+push)\b", re.I), |
| high | network-write | `tools/receipt_auditor.py` | none | recovery_path: delete generated output/audit files; no external mutation is performed |
| medium | scheduler | `brain-loop.sh` | none | while true; do |
| medium | shell-command | `brain-loop.sh` | none | #!/bin/bash |
| medium | social-or-email | `brain-loop.sh` | none | # ── POST-CYCLE ─────────────────────────────────────── |
| medium | shell-command | `config.sh` | none | # config.sh — Point this at whatever LLM CLI you have. |
| medium | scheduler | `install.sh` | none | # Quick install — creates a systemd service so the agent runs on boot |
| medium | shell-command | `install.sh` | none | #!/bin/bash |
| medium | scheduler | `tools/receipt_auditor.py` | none | "scheduler": re.compile(r"\b(cron\|systemd\|timer\|while true\|sleep\s+\$?\{?[A-Z_]*SECONDS\|schedule)\b", re.I), |
| medium | shell-command | `tools/receipt_auditor.py` | none | ".bash", |
| medium | social-or-email | `tools/receipt_auditor.py` | none | "network-write": re.compile(r"\b(POST\|PUT\|PATCH\|DELETE\|requests\.(post\|put\|patch\|delete)\|curl\b.*\b-X\b)", re.I), |
| low | file-write | `brain-loop.sh` | none | echo "[agent] Calling LLM..." \| tee -a "$LOG" |
| low | file-write | `install.sh` | none | sudo mv /tmp/${SERVICE_NAME}.service /etc/systemd/system/ |
| low | file-write | `tools/receipt_auditor.py` | none | "file-write": re.compile(r"\b(open\(.+['\"]w\|write_text\|append_text\|tee -a\|>>\|mv\b\|rm\b)\b"), |
