param(
  [string]$Mvn = "E:\SE2\software-programming2\apache-maven-3.9.9\apache-maven-3.9.9\bin\mvn.cmd",
  [int]$IntegrationPort = 8080
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot

function Start-MavenExec {
  param(
    [Parameter(Mandatory=$true)][string]$WorkingDir,
    [Parameter(Mandatory=$true)][string]$Title,
    [Parameter(Mandatory=$true)][string[]]$CommandParts
  )

  if ($CommandParts.Count -lt 1) {
    throw "CommandParts must contain at least the mvn executable."
  }

  $mvnExe = $CommandParts[0]
  $mvnArgs = @()
  if ($CommandParts.Count -gt 1) { $mvnArgs = $CommandParts[1..($CommandParts.Count - 1)] }

  $mvnArgsStr = ($mvnArgs | ForEach-Object { "'" + ($_ -replace "'", "''") + "'" }) -join ' '
  $mvnExeEsc = $mvnExe -replace "'", "''"

  $cmd = "Set-Location -LiteralPath '$WorkingDir'; & '$mvnExeEsc' $mvnArgsStr"
  Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $cmd) -WorkingDirectory $WorkingDir -WindowStyle Normal | Out-Null
  Write-Host "[start] $Title -> $WorkingDir" -ForegroundColor Green
}

$integrationDir = Join-Path $root "projects\integration"
$collegeADir    = Join-Path $root "projects\A"
$collegeBDir    = Join-Path $root "projects\B"
$collegeCDir    = Join-Path $root "projects\C"

Start-MavenExec -WorkingDir $integrationDir -Title "Integration Server" -CommandParts @($Mvn, "exec:java", "-Dexec.args=$IntegrationPort")
Start-MavenExec -WorkingDir $collegeADir    -Title "College A"         -CommandParts @($Mvn, "exec:java")
Start-MavenExec -WorkingDir $collegeBDir    -Title "College B"         -CommandParts @($Mvn, "exec:java")
Start-MavenExec -WorkingDir $collegeCDir    -Title "College C"         -CommandParts @($Mvn, "exec:java")

Write-Host "" 
Write-Host "All processes started. Default ports: Integration=$IntegrationPort, A=8081, B=8082, C=8083" -ForegroundColor Cyan
