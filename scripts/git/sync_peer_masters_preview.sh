#!/usr/bin/env bash
# Preview commits on origin/master-* branches that are not in HEAD (read-only).
# Does not merge. Use before Rule C-1 sync — see docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md
set -euo pipefail
git fetch origin
echo "=== Commits on peer master-* not in HEAD (first 8 each) ==="
for ref in $(git branch -r | grep 'origin/master-' | grep -v HEAD | sort); do
  echo ""
  echo "--- $ref ---"
  git log --oneline HEAD.."$ref" 2>/dev/null | head -8 || true
done
echo ""
echo "Done. Review output, then merge selectively if clean (see MULTI_OFFICE_GIT_WORKFLOW.md)."
