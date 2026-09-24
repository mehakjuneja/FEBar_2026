# docs/runbook/ — Walkthroughs & demo script

Operational walkthroughs that aren't a single build object — the end-to-end **demo script** for the
roleplay, plus governance/ops walkthroughs (UC lineage, column masking on vendor remit data,
Lakehouse Monitoring on the match tables) that reinforce the **Product** domain.

Populate as the build lands:
- `demo_script.md` — the exact click-path for the roleplay: Summary → Reconciliation review (filter
  + bulk approve) → Exceptions → Line detail (AI rec + root cause) → Ask Accord (Genie).
- `governance_walkthrough.md` — lineage bronze→silver→gold; UC column mask on `vendor_master.remit_to`.

See [`../BUILD_TRACKER.md`](../BUILD_TRACKER.md) for status.
