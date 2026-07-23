# Start backend service on port 8001

$ErrorActionPreference = "Stop"

# Change to project root directory (parent of scripts/)
Set-Location $PSScriptRoot\..

# Check if server.py exists
if (-not (Test-Path "server.py")) {
    Write-Error "server.py not found in $(Get-Location)"
    Write-Host "Please run this script from the project root directory."
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Warning "No virtual environment found. Using system Python."
}

# Check if uvicorn is installed
if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
    Write-Error "uvicorn not found"
    Write-Host "Please install dependencies: pip install -r requirements.txt"
    exit 1
}

Write-Host "Starting backend service on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
