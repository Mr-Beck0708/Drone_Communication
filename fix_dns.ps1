# Fix DNS to use Google's Public DNS servers
Write-Host "Setting DNS to Google Public DNS..." -ForegroundColor Cyan

$adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.InterfaceDescription -like "*Wi-Fi*" }

foreach ($adapter in $adapters) {
    Write-Host "Configuring: $($adapter.Name)" -ForegroundColor Yellow
    try {
        Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ServerAddresses ("8.8.8.8", "8.8.4.4")
        Write-Host "DNS set successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed: $_" -ForegroundColor Red
    }
}

Write-Host "`nTesting GitHub connection..." -ForegroundColor Cyan
$testDNS = Resolve-DnsName github.com -ErrorAction SilentlyContinue
if ($testDNS) {
    Write-Host "GitHub DNS: SUCCESS - IP: $($testDNS[0].IPAddress)" -ForegroundColor Green
}
else {
    Write-Host "GitHub DNS: FAILED" -ForegroundColor Red
}

$testConn = Test-NetConnection github.com -Port 443 -WarningAction SilentlyContinue
if ($testConn.TcpTestSucceeded) {
    Write-Host "GitHub Connection: SUCCESS" -ForegroundColor Green
}
else {
    Write-Host "GitHub Connection: FAILED" -ForegroundColor Red
}

Write-Host "`nDone! GitHub should work on all networks now." -ForegroundColor Green
