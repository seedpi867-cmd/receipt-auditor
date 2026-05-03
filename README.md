# receipt-auditor

An autonomous loop agent that audits other agents for missing capability receipts.

It is built from [`brain-loop`](https://github.com/seedpi867-cmd/brain-loop): one bash loop, files as state, any LLM CLI. The useful part is the auditor personality plus a local scanner that turns an agent directory into a receipt ledger.

## What It Checks

`receipt-auditor` looks for actuator surfaces: deploy scripts, social posting tools, write APIs, shell commands, OAuth/token references, cron/systemd files, and git mutation paths. It does not read hidden credential files and it does not need network access to audit a local tree.

For every likely actuator it asks for five receipt fields:

- `policy_owner`: who or what is allowed to authorize this action
- `log_path`: where exact invocations are recorded
- `approval_mode`: deny, dry-run, human approval, scoped automatic, or unrestricted
- `recovery_path`: how to undo, rotate, revoke, or restore after a bad action
- `verification_command`: how to prove the action happened or did not happen

Missing fields are ranked by blast radius.

## Quick Start

```bash
git clone https://github.com/seedpi867-cmd/receipt-auditor.git
cd receipt-auditor
python3 tools/receipt_auditor.py --target /path/to/agent
```

Outputs are written to `output/audit/`:

- `capability-ledger.md`
- `missing-receipts.md`
- `bypass-paths.md`
- `recovery-drills.md`
- `receipts.jsonl`

## Run As A Loop Agent

Edit `context/target.md` with the directory you want audited, then run:

```bash
nano config.sh
chmod +x brain-loop.sh
./brain-loop.sh
```

The loop reads `AGENT.md`, `INSTRUCTIONS.md`, `data/tasks.md`, and `context/*`, then acts through your configured LLM CLI.

## Receipt Hints

The scanner recognizes receipt metadata embedded in comments or markdown near a tool:

```text
policy_owner: maintainer
log_path: data/outreach/hn-activity.md
approval_mode: scoped automatic
recovery_path: revoke token and delete post
verification_command: python3 tools/hn.py status
```

The point is not bureaucracy. The point is state. If an autonomous system can mutate the world, the mutation needs a durable receipt.

## Files

```text
receipt-auditor/
├── brain-loop.sh
├── config.sh
├── AGENT.md
├── INSTRUCTIONS.md
├── tools/receipt_auditor.py
├── data/tasks.md
├── data/memory.md
├── context/
├── output/
└── knowledge/
```

## License

MIT
