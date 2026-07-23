# 自动启动后端 + ngrok 并配置前端

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DevSkillMapper 本地部署启动器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 启动后端服务（后台运行）
Write-Host "[1/3] 启动后端服务..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "D:\test\team--17"
    python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
}
Start-Sleep -Seconds 3

# 2. 启动 ngrok（后台运行）
Write-Host "[2/3] 启动 ngrok 内网穿透..." -ForegroundColor Yellow
$ngrokJob = Start-Job -ScriptBlock {
    ngrok http 8001 --log stdout
}
Start-Sleep -Seconds 5

# 3. 获取 ngrok URL
Write-Host "[3/3] 获取公网访问地址..." -ForegroundColor Yellow
try {
    $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $ngrokUrl = $tunnels.tunnels[0].public_url

    # 更新 .env.production
    $envContent = "# Production environment - auto configured`nVITE_API_BASE_URL=$ngrokUrl"
    Set-Content -Path ".env.production" -Value $envContent

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   启动成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "后端服务: http://localhost:8001" -ForegroundColor Cyan
    Write-Host "ngrok控制台: http://localhost:4040" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "公网访问地址: $ngrokUrl" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host ""
    Write-Host "前端访问地址: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "其他用户访问前端时，API请求会自动通过ngrok转发到你的电脑" -ForegroundColor Gray
    Write-Host ""
    Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Red
    Write-Host ""

    # 保持脚本运行
    while ($true) {
        Start-Sleep -Seconds 10
        # 检查服务是否还在运行
        if ($backendJob.State -ne "Running") {
            Write-Host "[警告] 后端服务已停止，正在重启..." -ForegroundColor Yellow
            $backendJob = Start-Job -ScriptBlock {
                Set-Location "D:\test\team--17"
                python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
            }
        }
        if ($ngrokJob.State -ne "Running") {
            Write-Host "[警告] ngrok已停止，正在重启..." -ForegroundColor Yellow
            $ngrokJob = Start-Job -ScriptBlock {
                ngrok http 8001 --log stdout
            }
            Start-Sleep -Seconds 5
            $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction SilentlyContinue
            if ($tunnels.tunnels) {
                $ngrokUrl = $tunnels.tunnels[0].public_url
                $envContent = "# Production environment - auto configured`nVITE_API_BASE_URL=$ngrokUrl"
                Set-Content -Path ".env.production" -Value $envContent
                Write-Host "新的公网地址: $ngrokUrl" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "[错误] 无法获取ngrok URL，请检查ngrok是否正常运行" -ForegroundColor Red
    Write-Host "错误详情: $_" -ForegroundColor Red
}

# 清理
Write-Host "正在停止服务..." -ForegroundColor Yellow
Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
Stop-Job -Job $ngrokJob -ErrorAction SilentlyContinue
Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
Remove-Job -Job $ngrokJob -ErrorAction SilentlyContinue
Write-Host "服务已停止" -ForegroundColor Green
