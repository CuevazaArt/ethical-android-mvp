# Preview commits on origin/master-* branches that are not in HEAD (read-only).
# Does not merge. Use before Rule C-1 sync — see docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md
$ErrorActionPreference = "Stop"
git fetch origin
Write-Host "=== Commits on peer master-* not in HEAD (first 8 each) ==="
$refs = git branch -r | Where-Object { $_ -match 'origin/master-' -and $_ -notmatch 'HEAD' } | Sort-Object
foreach ($ref in $refs) {
    $r = $ref.Trim()
    Write-Host ""
    Write-Host "--- $r ---"
    git log --oneline "HEAD..$r" 2>$null | Select-Object -First 8
}
Write-Host ""
Write-Host "Done. Review output, then merge selectively if clean (see MULTI_OFFICE_GIT_WORKFLOW.md)."
