# Git helper scripts

- **`sync_peer_masters_preview.sh`** / **`sync_peer_masters_preview.ps1`** — After `git fetch`, lists recent commits on each `origin/master-*` branch that are **not** in your current `HEAD` (`git log HEAD..<peer>`). **Read-only**; does not merge. Use before [Rule C-1](../../docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md) peer syncs.

Run from repository root (bash or PowerShell):

```bash
bash scripts/git/sync_peer_masters_preview.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/git/sync_peer_masters_preview.ps1
```

See also [`docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md`](../../docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md).
