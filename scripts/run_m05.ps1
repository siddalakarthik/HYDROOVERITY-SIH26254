param([ValidateSet('smoke','ppt','stress')][string]$Profile='smoke', [Parameter(Mandatory=$true)][string]$Python)
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
$env:MPLCONFIGDIR=Join-Path $repoRoot '.cache/matplotlib'
New-Item -ItemType Directory -Force $env:MPLCONFIGDIR | Out-Null
Push-Location $repoRoot
try { & $Python -m simulations.run_all --profile $Profile; if ($LASTEXITCODE -ne 0) { throw 'Simulation profile failed' } }
finally { Pop-Location }
