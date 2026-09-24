#!/usr/bin/env bash
# Accord — one-time workspace setup helper.
# Validates + deploys the DAB and runs Phase 0 (foundation). Operator supplies the profile.
# NEVER auto-selects a profile. Usage: scripts/setup_new_workspace.sh <profile> [target]
set -euo pipefail

PROFILE="${1:?Usage: setup_new_workspace.sh <profile> [target]  — never auto-selected}"
TARGET="${2:-dev}"

echo "==> Accord setup on profile='$PROFILE' target='$TARGET'"

echo "==> 1/3 Validate bundle"
databricks bundle validate -t "$TARGET" --profile "$PROFILE"

echo "==> 2/3 Deploy bundle"
databricks bundle deploy -t "$TARGET" --profile "$PROFILE"

echo "==> 3/3 Run foundation (F1-F3) — creates UC objects + synthetic data + landing feeds"
databricks bundle run foundation_job -t "$TARGET" --profile "$PROFILE"

cat <<'EOF'

Done. Next:
  - Phase 1: deploy + run the Lakeflow pipeline (pipeline/)
  - Phase 2: train + register + serve the model (ml/)
  - Phase 3: build the Genie space (genie/)
  - Phase 4: deploy the app (app/)
See docs/BUILD_TRACKER.md for status and docs/superpowers/plans/ for each phase.
EOF
