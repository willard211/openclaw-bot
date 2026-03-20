$ErrorActionPreference = "Stop"

$root = "C:\Users\31072\openclaw-trade-employee"
$python = "C:\Users\31072\AppData\Local\Programs\Python\Python310\python.exe"

if (!(Test-Path $python)) {
  throw "Python not found: $python"
}

Write-Host "Starting API server..." -ForegroundColor Cyan
$server = Start-Process -FilePath $python -ArgumentList "app\server.py" -WorkingDirectory $root -PassThru

Start-Sleep -Seconds 2

if (Get-Command ngrok -ErrorAction SilentlyContinue) {
  Write-Host "Starting ngrok on port 8787..." -ForegroundColor Cyan
  $ngrok = Start-Process -FilePath "ngrok" -ArgumentList "http 8787" -WorkingDirectory $root -PassThru
  Start-Sleep -Seconds 3
  try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels"
    $https = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
    if ($https) {
      Write-Host ""
      Write-Host "Webhook URL (paste to Meta): $($https.public_url)/webhook/whatsapp" -ForegroundColor Green
      Write-Host "Verify Token (from .env): set WHATSAPP_VERIFY_TOKEN" -ForegroundColor Yellow
    }
  } catch {
    Write-Host "ngrok started, but tunnel URL read failed. Open http://127.0.0.1:4040 manually." -ForegroundColor Yellow
  }
  Write-Host ""
  Write-Host "Running. Stop with:" -ForegroundColor Cyan
  Write-Host "  Stop-Process -Id $($server.Id),$($ngrok.Id) -Force"
} else {
  Write-Host "ngrok not found. Install ngrok and run: ngrok http 8787" -ForegroundColor Yellow
  Write-Host "Server PID: $($server.Id)" -ForegroundColor Green
}
