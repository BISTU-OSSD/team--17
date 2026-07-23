# Start backend service on port 8001

# Change to project root directory (parent of scripts/)
Set-Location $PSScriptRoot\..

# Check if server.py exists
if (-not (Test-Path "server.py")) {
    [Console]::Error.WriteLine("server.py not found in $(Get-Location). Please run this script from the project root directory.")
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
    [Console]::Error.WriteLine("No virtual environment found. Using system Python.")
}

# Check if uvicorn is installed
if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine("uvicorn not found. Please install dependencies: pip install -r requirements.txt")
    exit 1
}

Write-Host "Starting backend service on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
