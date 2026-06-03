param(
  [switch]$SkipTests = $true,
  [string]$Mvn = "E:\SE2\software-programming2\apache-maven-3.9.9\apache-maven-3.9.9\bin\mvn.cmd"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

try {
  $args = @("clean", "package")
  if ($SkipTests) { $args = @("-DskipTests") + $args }

  Write-Host "[build] Running: $Mvn $($args -join ' ')" -ForegroundColor Cyan
  & $Mvn @args
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
  Pop-Location
}
