param(
    [string]$AppDir = "src/clients/flutter_desktop_shell",
    [string]$OutDir = "dist/desktop/windows",
    [switch]$SkipClean
)

$ErrorActionPreference = "Stop"

function Step([string]$message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Ensure-Command([string]$name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' was not found in PATH."
    }
}

function Invoke-Checked([string]$exe, [string[]]$cliArgs) {
    $rendered = "$exe " + ($cliArgs -join " ")
    Write-Host "[cmd] $rendered" -ForegroundColor DarkGray
    & $exe @cliArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit=$LASTEXITCODE): $rendered"
    }
}

Step "Checking required tooling"
Ensure-Command "flutter"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$appPath = Resolve-Path (Join-Path $repoRoot $AppDir)
$outPath = Join-Path $repoRoot $OutDir
if (-not (Test-Path $appPath)) {
    throw "Flutter app directory not found: $appPath"
}

Step "Tool versions"
Invoke-Checked "flutter" @("--version")

Step "Preparing Flutter desktop app"
Push-Location $appPath
try {
    if (-not $SkipClean) {
        Invoke-Checked "flutter" @("clean")
    }
    Invoke-Checked "flutter" @("pub", "get")
    Invoke-Checked "flutter" @("test")
    Invoke-Checked "flutter" @("build", "windows", "--release")
}
finally {
    Pop-Location
}

$releaseRoot = Join-Path $appPath "build/windows/x64/runner/Release"
if (-not (Test-Path $releaseRoot)) {
    throw "Release folder not found: $releaseRoot"
}

Step "Collecting release artifacts into $outPath"
if (Test-Path $outPath) {
    Remove-Item -Recurse -Force $outPath
}
New-Item -ItemType Directory -Force -Path $outPath | Out-Null
Copy-Item -Recurse -Force (Join-Path $releaseRoot "*") $outPath

$artifactManifest = Join-Path $outPath "ARTIFACTS.txt"
$artifactLines = @(
    "Ethos Desktop Shell - Windows Release Artifact Manifest",
    "Generated: $(Get-Date -Format o)",
    "",
    "Expected payload after successful build:",
    "- flutter_desktop_shell.exe",
    "- data/ (Flutter assets + icudtl.dat + app assets)",
    "- flutter_windows.dll",
    "- vcruntime*.dll (depends on machine/runtime)",
    "- msvcp*.dll (depends on machine/runtime)",
    "",
    "Smoke launch command:",
    ".\flutter_desktop_shell.exe --dart-define=KERNEL_BASE_URL=http://127.0.0.1:8000"
)
$artifactLines | Set-Content -Path $artifactManifest -Encoding UTF8

$rollbackChecklist = Join-Path $outPath "ROLLBACK_CHECKLIST.txt"
$rollbackLines = @(
    "Ethos Desktop Shell - Rollback Checklist",
    "Generated: $(Get-Date -Format o)",
    "",
    "1) Stop running desktop shell process.",
    "2) Backup current release folder (if any).",
    "3) Restore last known-good artifact folder.",
    "4) Launch flutter_desktop_shell.exe and verify /api/ping + /api/status.",
    "5) If health check fails, revert to previous backup and log incident.",
    "",
    "Verification command (from artifact folder):",
    ".\flutter_desktop_shell.exe --dart-define=KERNEL_BASE_URL=http://127.0.0.1:8000"
)
$rollbackLines | Set-Content -Path $rollbackChecklist -Encoding UTF8

Step "Build baseline ready"
Write-Host "Release folder: $outPath" -ForegroundColor Green
Write-Host "Artifact manifest: $artifactManifest" -ForegroundColor Green
Write-Host "Rollback checklist: $rollbackChecklist" -ForegroundColor Green
