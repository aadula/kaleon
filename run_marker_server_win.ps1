# Windows launcher (e.g. NVIDIA/CUDA host): venv, PORT 3010, then Flask without re-delegating.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:PORT) {
    $env:PORT = "3010"
}
$env:MARKER_SERVER_NO_DELEGATE = "1"

$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
}

python (Join-Path $PSScriptRoot "marker_server.py")
