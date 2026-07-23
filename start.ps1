# DevSkillMapper Local Deploy Script

$PYTHON = "D:\python\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DevSkillMapper Local Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Using Python: $PYTHON" -ForegroundColor Gray
Write-Host ""

# Start LLM server
Write-Host "[1/5] Starting LLM server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\test\team--17\llama-cpp; .\llama-server.exe -m Qwen3.5-9B-Q4_K_M.gguf --host 127.0.0.1 --port 8080"

# Wait for LLM server to start
Write-Host "Waiting for LLM server..." -ForegroundColor Gray
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -ErrorAction Stop | Out-Null
        Write-Host "LLM server ready!" -ForegroundColor Green
        break
    } catch {
        Write-Host "Waiting... ($i/15)" -ForegroundColor Gray
    }
}

# Start backend API server
Write-Host "[2/5] Starting backend API server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\test\team--17; & '$PYTHON' -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

# Wait for backend to be ready
Write-Host "Waiting for backend API..." -ForegroundColor Gray
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8001/api/health" -ErrorAction Stop
        if ($health.status -eq "ok") {
            Write-Host "Backend API ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Waiting... ($i/15)" -ForegroundColor Gray
    }
}

# Start ngrok
Write-Host "[3/5] Starting ngrok tunnel..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8001"

# Wait for ngrok to start
Write-Host "[4/5] Getting public URL..." -ForegroundColor Yellow
$ngrokUrl = ""
for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
        if ($response.tunnels.Count -gt 0) {
            $ngrokUrl = $response.tunnels[0].public_url
            Write-Host "Found: $ngrokUrl" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Waiting for ngrok... ($i/10)" -ForegroundColor Gray
    }
}

if (-not $ngrokUrl) {
    $ngrokUrl = "https://raving-tubeless-greeting.ngrok-free.dev"
}

# Update .env.production
Write-Host "[5/5] Updating frontend config..." -ForegroundColor Yellow
"VITE_API_BASE_URL=$ngrokUrl" | Out-File -FilePath ".env.production" -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Startup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  - LLM Server: http://localhost:8080" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "  - Public URL: $ngrokUrl" -ForegroundColor Yellow
Write-Host "  - Frontend: http://localhost:5000" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to start frontend"
npm run dev
