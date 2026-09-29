param(
  [string]$Url = "http://localhost:8080/health",
  [int]$Retries = 3,
  [int]$SleepSecs = 3
)

for ($i = 1; $i -le $Retries; $i++) {
  Write-Host "[healthcheck] essai $i/$Retries -> $Url"
  try {
    $res = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
    if ($res.StatusCode -eq 200 -and $res.Content -match '"status"\s*:\s*"ok"') {
      Write-Host "[healthcheck] OK"
      exit 0
    }
  } catch {
    Write-Host "[healthcheck] echec: $($_.Exception.Message)"
  }
  Start-Sleep -Seconds $SleepSecs
}

Write-Error "[healthcheck] ECHEC apres $Retries essais"
exit 1
