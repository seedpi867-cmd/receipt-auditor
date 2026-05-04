# Recovery Drills

## Completed Local Drill - file-write receipt reconstruction

- status: `passed`
- receipt: `receipts/file-write-recovery-drill.json`
- before_sha256: `83330fa8f0f2f7d01994eb1e69bba205c252aef7cee04ed48764e863baed4769`
- after_sha256: `ca8b240dc0c71c0b19a08ff713117a3bdd1271f20a4d8cdf3ee666b9635c26ee`
- restored_sha256: `83330fa8f0f2f7d01994eb1e69bba205c252aef7cee04ed48764e863baed4769`
- verified: `True`

This drill mutates only `output/audit/receipts/file-write-drill-sandbox.txt` and proves that the receipt contains enough state to reconstruct the pre-write file exactly.

## Completed Local Drill - scheduler pause/resume fixture

- status: `passed`
- receipt: `receipts/scheduler-pause-resume-drill.json`
- before_sha256: `1ad99a79a19c3ac8a0b6f0b902ba4c589bc9ff86eadeccd505f492e871a0b8fd`
- paused_sha256: `58f62276d8861163f78d5d1a1a4ed594d5ecdbd185f9deebc5a2acd6c287269c`
- resumed_sha256: `1ad99a79a19c3ac8a0b6f0b902ba4c589bc9ff86eadeccd505f492e871a0b8fd`
- unrelated_service_preserved: `True`
- verified: `True`

This drill mutates only `output/audit/receipts/scheduler-drill-state.json` and proves that a scheduler can be paused and resumed from a receipt while preserving unrelated service state.

## Manual Drills Still Needed

- Pick one high or critical actuator and prove its token can be revoked.
- Pick one deploy path and prove rollback from a bad deploy.
- Pick one social/email path and prove exact message logs exist.
- Pick one shell-command bypass and prove the command transcript is captured.
