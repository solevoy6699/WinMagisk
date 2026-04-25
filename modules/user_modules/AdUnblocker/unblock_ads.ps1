$path = "C:\Windows\System32\drivers\etc\hosts"
if (Test-Path $path) {
    Set-ItemProperty $path -Name IsReadOnly -Value $false
}
$content = @"
127.0.0.1       localhost
::1             localhost
"@
Set-Content -Path $path -Value $content -Force
ipconfig /flushdns