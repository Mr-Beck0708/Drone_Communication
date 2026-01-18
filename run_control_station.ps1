# PowerShell script to run Control Station on Windows
# Quick launcher for the Control Station application

param(
    [Parameter(Mandatory = $false)]
    [string]$DroneHost = "192.168.29.123",
    
    [Parameter(Mandatory = $false)]
    [int]$Port = 8443,
    
    [Parameter(Mandatory = $false)]
    [string]$OperatorId = "OP-001"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "CONTROL STATION - WiFi Network Intelligence" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connecting to Drone at: $DroneHost`:$Port" -ForegroundColor Yellow
Write-Host "Operator ID: $OperatorId" -ForegroundColor Yellow
Write-Host ""
Write-Host "Post-Quantum Cryptography: ENABLED" -ForegroundColor Green
Write-Host "  - Hybrid Key Exchange: X448 + Kyber768" -ForegroundColor White
Write-Host "  - Signatures: Dilithium3" -ForegroundColor White
Write-Host "  - Encryption: ChaCha20-Poly1305" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

# Run the control station app
Write-Host "Starting Control Station..." -ForegroundColor Green
Write-Host ""

python control_station_app.py --host $DroneHost --port $Port --operator-id $OperatorId
