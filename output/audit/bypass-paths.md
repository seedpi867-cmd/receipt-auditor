# Bypass Paths

- `config.sh` can bypass narrow tool receipts through `credential-surface`. Evidence: `# Codex (OpenAI) — free with OAuth login`
- `tools/receipt_auditor.py` can bypass narrow tool receipts through `credential-surface`. Evidence: `"credential-surface": re.compile(r"\b(oauth|token|secret|password|credential|cookie|api[_-]?key)\b", re.I),`
- `brain-loop.sh` can bypass narrow tool receipts through `scheduler`. Evidence: `while true; do`
- `brain-loop.sh` can bypass narrow tool receipts through `shell-command`. Evidence: `#!/bin/bash`
- `config.sh` can bypass narrow tool receipts through `shell-command`. Evidence: `# config.sh — Point this at whatever LLM CLI you have.`
- `install.sh` can bypass narrow tool receipts through `scheduler`. Evidence: `# Quick install — creates a systemd service so the agent runs on boot`
- `install.sh` can bypass narrow tool receipts through `shell-command`. Evidence: `#!/bin/bash`
- `tools/receipt_auditor.py` can bypass narrow tool receipts through `scheduler`. Evidence: `"scheduler": re.compile(r"\b(cron|systemd|timer|while true|sleep\s+\$?\{?[A-Z_]*SECONDS|schedule)\b", re.I),`
- `tools/receipt_auditor.py` can bypass narrow tool receipts through `shell-command`. Evidence: `".bash",`
