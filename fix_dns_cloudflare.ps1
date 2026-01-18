# Fix DNS using Cloudflare DNS (better for some networks)
Write-Host "Setting DNS to Cloudflare DNS (1.1.1.1, 1.0.0.1)..." -ForegroundColor Cyan

$adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and ($_.Name -like "*Wi-Fi*" -or $_.InterfaceDescription -like "*Wi-Fi*") }

foreach ($adapter in $adapters) {
    Write-Host "Configuring: $($adapter.Name)" -ForegroundColor Yellow
    try {
        Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ServerAddresses ("1.1.1.1", "1.0.0.1")
        Write-Host "DNS set successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed: $_" -ForegroundColor Red
    }
}

Write-Host "`nFlushing DNS cache..." -ForegroundColor Cyan
ipconfig /flushdns | Out-Null

Write-Host "`nTesting GitHub with Cloudflare DNS..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$testDNS = nslookup github.com 1.1.1.1 2>&1 | Out-String
Write-Host $testDNS

Write-Host "`nDone! Try GitHub now." -ForegroundColor Green
