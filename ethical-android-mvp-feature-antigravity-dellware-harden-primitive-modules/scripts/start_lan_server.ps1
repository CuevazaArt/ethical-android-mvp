<#
.SYNOPSIS
  Start Ethos Kernel chat server bound to all interfaces (LAN-friendly).

.DESCRIPTION
  Sets CHAT_HOST=0.0.0.0 so phones on the same WiFi can reach ws://<PC_IP>:PORT/ws/chat
  Requires: venv activated, pip install -r requirements.txt from repo root.

.EXAMPLE
  .\scripts\start_lan_server.ps1
  .\scripts\start_lan_server.ps1 -Port 8765
#>
param(
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$env:CHAT_HOST = "0.0.0.0"
$env:CHAT_PORT = "$Port"

Write-Host "CHAT_HOST=$($env:CHAT_HOST) CHAT_PORT=$($env:CHAT_PORT)" -ForegroundColor Cyan
Write-Host "Health: http://127.0.0.1:${Port}/health  |  WebSocket: ws://127.0.0.1:${Port}/ws/chat" -ForegroundColor DarkGray

try {
    $ips = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } |
        Select-Object -ExpandProperty IPAddress -Unique
    if ($ips) {
        Write-Host "LAN IPv4 (open on phone browser):" -ForegroundColor Green
        foreach ($ip in $ips) { Write-Host "  http://${ip}:${Port}/health" }
    }
} catch {
    Write-Host "Tip: run ipconfig to find your PC IPv4 on WiFi." -ForegroundColor Yellow
}

$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
& $py -m src.runtime
