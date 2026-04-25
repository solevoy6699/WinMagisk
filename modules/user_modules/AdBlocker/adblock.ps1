$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$sourceUrl = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
Invoke-WebRequest -Uri $sourceUrl -OutFile "$env:TEMP\new_hosts"
if (Test-Path $hostsPath) {
    Set-ItemProperty $hostsPath -Name IsReadOnly -Value $false
}
Move-Item "$env:TEMP\new_hosts" $hostsPath -Force
ipconfig /flushdns