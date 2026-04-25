# --- WinMagisk Activation Engine v1.0 ---
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    WINMAGISK UNIVERSAL ACTIVATOR ENGINE       " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Список GVLK ключей (официальные ключи Microsoft для KMS)
$keys = @{
    "Professional"      = "W269N-WFGWX-YVC9B-4J6C9-T83GX"
    "Professional N"    = "MH37W-N47XK-V7XM9-C7227-GCQG9"
    "Enterprise"        = "NPPR9-FWDCX-D2C8J-H872K-2YT43"
    "Enterprise N"      = "DPH2V-TTNVB-4X9Q3-TJR4H-KHJW4"
    "Education"         = "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2"
    "Core"              = "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99" # Home
    "Core Single Lang"  = "7HNRX-D7KGG-3K4RQ-4WPJ4-YTDFH"
}

# 2. Определяем редакцию системы
$edition = (Get-CimInstance Win32_OperatingSystem).Caption
Write-Host "[*] Система: $edition" -ForegroundColor White

$selectedKey = ""
foreach ($name in $keys.Keys) {
    if ($edition -like "*$name*") {
        $selectedKey = $keys[$name]
        break
    }
}

if (-not $selectedKey) {
    Write-Host "[!] Редакция не найдена в базе, пробуем Pro ключ..." -ForegroundColor Yellow
    $selectedKey = $keys["Professional"]
}

# 3. Процесс активации через slmgr
Write-Host "[>] Установка ключа: $selectedKey" -ForegroundColor Gray
& slmgr.vbs /ipk $selectedKey | Out-Null

Write-Host "[>] Подключение к серверу KMS..." -ForegroundColor Gray
# Используем один из стабильных мировых серверов
& slmgr.vbs /skms kms8.msguides.com | Out-Null

Write-Host "[>] Финализация активации..." -ForegroundColor Cyan
$result = & slmgr.vbs /ato

if ($result -like "*успешно*" -or $result -like "*successful*") {
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "    АКТИВАЦИЯ ВЫПОЛНЕНА УСПЕШНО!               " -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
} else {
    Write-Host "[!] Ошибка. Проверьте интернет или антивирус." -ForegroundColor Red
}

Write-Host "Это окно закроется через 5 секунд..."
Start-Sleep -Seconds 5