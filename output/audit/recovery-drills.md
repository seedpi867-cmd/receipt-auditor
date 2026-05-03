# Recovery Drills

## Completed Local Drill - file-write receipt reconstruction

- status: `passed`
- receipt: `receipts/file-write-recovery-drill.json`
- before_sha256: `83330fa8f0f2f7d01994eb1e69bba205c252aef7cee04ed48764e863baed4769`
- after_sha256: `ca8b240dc0c71c0b19a08ff713117a3bdd1271f20a4d8cdf3ee666b9635c26ee`
- restored_sha256: `83330fa8f0f2f7d01994eb1e69bba205c252aef7cee04ed48764e863baed4769`
- verified: `True`

This drill mutates only `output/audit/receipts/file-write-drill-sandbox.txt` and proves that the receipt contains enough state to reconstruct the pre-write file exactly.

## Manual Drills Still Needed

- Pick one high or critical actuator and prove its token can be revoked.
- Pick one deploy path and prove rollback from a bad deploy.
- Pick one social/email path and prove exact message logs exist.
- Pick one scheduler and prove it can be paused without killing unrelated services.
- Pick one shell-command bypass and prove the command transcript is captured.
