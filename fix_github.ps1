# ==============================================================================
# GitHub DNS Fix - Complete Solution
# ==============================================================================
# This script provides multiple solutions to fix GitHub connectivity issues
# Run this script as Administrator for best results
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  GitHub Connectivity Fix Tool  " -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Solution 1: Add GitHub IPs to hosts file (Works without admin for Git)
Write-Host "[Solution 1] Adding GitHub IPs to hosts file..." -ForegroundColor Yellow

$githubIPs = @"

# GitHub DNS Fix - Added $(Get-Date)
140.82.121.3    github.com
140.82.121.4    github.com
140.82.121.6    api.github.com
185.199.108.133 raw.githubusercontent.com
185.199.109.133 raw.githubusercontent.com
185.199.110.133 raw.githubusercontent.com
185.199.111.133 raw.githubusercontent.com
"@

try {
    $hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
    $currentHosts = Get-Content $hostsPath -Raw
    
    if ($currentHosts -notmatch "github.com") {
        Add-Content -Path $hostsPath -Value $githubIPs -ErrorAction Stop
        Write-Host "  SUCCESS: GitHub IPs added to hosts file`n" -ForegroundColor Green
    }
    else {
        Write-Host "  INFO: GitHub entries already exist in hosts file`n" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  FAILED: Need Administrator rights`n" -ForegroundColor Red
    Write-Host "  Run this as Administrator or manually add these lines to:" -ForegroundColor Yellow
    Write-Host "  C:\Windows\System32\drivers\etc\hosts`n" -ForegroundColor Yellow
    Write-Host $githubIPs -ForegroundColor White
}

# Solution 2: Try resetting DNS (requires admin)
Write-Host "`n[Solution 2] Resetting DNS to automatic..." -ForegroundColor Yellow

try {
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Name -like "*Wi-Fi*" }
    foreach ($adapter in $adapters) {
        Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ResetServerAddresses -ErrorAction Stop
        Write-Host "  SUCCESS: Reset DNS for $($adapter.Name)`n" -ForegroundColor Green
    }
}
catch {
    Write-Host "  FAILED: Need Administrator rights`n" -ForegroundColor Red
}

# Solution 3: Flush DNS cache
Write-Host "[Solution 3] Flushing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "  SUCCESS: DNS cache cleared`n" -ForegroundColor Green

# Test GitHub connectivity
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Testing GitHub Connection  " -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Test 1: Ping github.com" -ForegroundColor Yellow
$pingResult = ping github.com -n 1 2>&1
if ($pingResult -match "Reply from|bytes=") {
    Write-Host "  SUCCESS`n" -ForegroundColor Green
}
else {
    Write-Host "  FAILED: $($pingResult | Select-String 'could not|timed out')`n" -ForegroundColor Red
}

Write-Host "Test 2: Git connection to GitHub" -ForegroundColor Yellow
$gitTest = git ls-remote https://github.com/Mr-Beck0708/Drone_Communication.git HEAD 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  SUCCESS: Git can connect to GitHub!`n" -ForegroundColor Green
}
else {
    Write-Host "  FAILED: $gitTest`n" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Next Steps  " -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "If GitHub still doesn't work, try these:" -ForegroundColor White
Write-Host "1. Right-click PowerShell -> Run as Administrator" -ForegroundColor Gray
Write-Host "2. Run this script again with admin rights" -ForegroundColor Gray
Write-Host "3. Or switch to TP-Link WiFi 2 network`n" -ForegroundColor Gray
