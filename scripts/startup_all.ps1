# RTK-1 Auto-Restart Startup Script — Objective 89
# Run all RTK-1 services on Windows startup / power restore
# Schedule via: Task Scheduler → Run at startup → Run whether logged on or not

param(
    [switch]$Stop,
    [switch]$Status
)

$RTK1_ROOT = "C:\Projects\RTK-1\ramon-loya-RTK-1"
$LOKI_ROOT  = "C:\loki"
$PROMETHEUS = "C:\prometheus\prometheus.exe"
$PROMETHEUS_CONFIG = "C:\prometheus\prometheus.yml"

function Start-RTK1Services {
    Write-Host "=== RTK-1 Service Startup ===" -ForegroundColor Cyan

    # 1. Loki
    Write-Host "[1/5] Starting Loki..." -ForegroundColor Yellow
    Start-Process -FilePath "$LOKI_ROOT\loki-windows-amd64.exe" `
        -ArgumentList "--config.file=$LOKI_ROOT\loki-config.yaml" `
        -WindowStyle Minimized -PassThru | Out-Null
    Start-Sleep -Seconds 3

    # 2. Alloy
    Write-Host "[2/5] Starting Grafana Alloy..." -ForegroundColor Yellow
    Start-Service -Name "Alloy" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # 3. Prometheus
    Write-Host "[3/5] Starting Prometheus..." -ForegroundColor Yellow
    if (Test-Path $PROMETHEUS) {
        Start-Process -FilePath $PROMETHEUS `
            -ArgumentList "--config.file=$PROMETHEUS_CONFIG" `
            -WindowStyle Minimized -PassThru | Out-Null
        Start-Sleep -Seconds 2
    } else {
        Write-Host "  [SKIP] Prometheus not found at $PROMETHEUS" -ForegroundColor DarkYellow
    }

    # 4. Grafana
    Write-Host "[4/5] Starting Grafana..." -ForegroundColor Yellow
    Start-Service -Name "Grafana" -ErrorAction SilentlyContinue

    # 5. RTK-1 FastAPI
    Write-Host "[5/5] Starting RTK-1 API..." -ForegroundColor Yellow
    $venv = "$RTK1_ROOT\venv_rtk\Scripts\uvicorn.exe"
    Start-Process -FilePath $venv `
        -ArgumentList "app.main:app --host 0.0.0.0 --port 8000" `
        -WorkingDirectory $RTK1_ROOT `
        -WindowStyle Minimized -PassThru | Out-Null
    Start-Sleep -Seconds 5

    # 6. Streamlit Portal
    Write-Host "[6/6] Starting Streamlit Portal..." -ForegroundColor Yellow
    $streamlit = "$RTK1_ROOT\venv_rtk\Scripts\streamlit.exe"
    Start-Process -FilePath $streamlit `
        -ArgumentList "run streamlit_app.py --server.port 8501" `
        -WorkingDirectory $RTK1_ROOT `
        -WindowStyle Minimized -PassThru | Out-Null

    Write-Host ""
    Write-Host "=== RTK-1 Stack Started ===" -ForegroundColor Green
    Write-Host "  API:        http://localhost:8000/docs"
    Write-Host "  Portal:     http://localhost:8501"
    Write-Host "  Grafana:    http://localhost:3000"
    Write-Host "  Prometheus: http://localhost:9090"
    Write-Host "  Loki:       http://localhost:3100/ready"
    Write-Host "  Alloy:      http://localhost:12345"
}

function Stop-RTK1Services {
    Write-Host "=== Stopping RTK-1 Services ===" -ForegroundColor Red
    Stop-Service -Name "Alloy" -ErrorAction SilentlyContinue
    Stop-Service -Name "Grafana" -ErrorAction SilentlyContinue
    Get-Process -Name "loki-windows-amd64" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "prometheus" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "streamlit" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "All services stopped." -ForegroundColor Green
}

function Show-RTK1Status {
    Write-Host "=== RTK-1 Service Status ===" -ForegroundColor Cyan
    $checks = @(
        @{Name="Loki";       Url="http://localhost:3100/ready"},
        @{Name="RTK-1 API";  Url="http://localhost:8000/docs"},
        @{Name="Grafana";    Url="http://localhost:3000"},
        @{Name="Prometheus"; Url="http://localhost:9090"},
        @{Name="Alloy";      Url="http://localhost:12345"},
        @{Name="Streamlit";  Url="http://localhost:8501"},
    )
    foreach ($check in $checks) {
        try {
            $resp = Invoke-WebRequest -Uri $check.Url -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            Write-Host "  [UP]   $($check.Name) — $($check.Url)" -ForegroundColor Green
        } catch {
            Write-Host "  [DOWN] $($check.Name) — $($check.Url)" -ForegroundColor Red
        }
    }
}

# Entry point
if ($Stop)   { Stop-RTK1Services }
elseif ($Status) { Show-RTK1Status }
else         { Start-RTK1Services }