# Windows launcher for Chandra-backed server (PORT defaults to 3010).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:PORT) {
    $env:PORT = "3010"
}
$env:CHANDRA_SERVER_NO_DELEGATE = "1"

$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
}

python (Join-Path $PSScriptRoot "marker_server.py")
