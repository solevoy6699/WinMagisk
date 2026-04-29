# 🧩 Руководство по созданию модулей для WinMagisk

WinMagisk поддерживает модульную архитектуру. Это означает, что вы можете добавить любой скрипт или программу, и она автоматически появится в интерфейсе.

---

## 📁 Структура папок

Все модули должны находиться в директории:
~~`modules/user_modules/`~~ `C:\Users\Имя пользователя\AppData\Roaming\WinMagisk\modules` (Можно выбрать папку модуля в самом WinMagisk)

Каждый модуль должен иметь свою папку, внутри которой находится исполняемый файл с **фиксированным именем**.

Пример правильной структуры:
```text
Roaming/
└── WinMagisk/
    └── modules/
        └── MyCoolTweak/
            ├── module.json       <-- Манифест модуля с информацией о нём
            └── run.ps1       <-- Исполняемый файл (один из: .ps1 / .bat / .exe / .py)
```

🚀 Поддерживаемые типы файлов
WinMagisk автоматически распознает и запускает следующие файлы:
```text
Имя файла,Тип,Метод запуска
run.ps1,PowerShell,Запускается с обходом политики выполнения (Bypass)
run.bat,Batch,Обычный запуск через CMD
run.py,Python,Запускается через текущий интерпретатор системы
run.exe,Binary,Прямой запуск процесса
```

📝 Требования к коду модуля
1. Права администратора
WinMagisk запускает модули с теми же правами, с которыми запущен сам. Если ваш модуль требует прав SYSTEM или TRUSTED INSTALLER, вам нужно реализовать этот переход внутри самого модуля.

2. Интерфейс
Если ваш модуль — это консольный скрипт (.ps1, .bat), он откроется в новом окне терминала. Если это GUI-приложение, оно просто запустится поверх WinMagisk.

3. Завершение работы
Старайтесь делать так, чтобы после выполнения скрипт не закрывался мгновенно (используйте pause в .bat или Read-Host в .ps1), чтобы пользователь успел прочитать лог выполнения.

🛠 Пример простейшего модуля (run.ps1)
PowerShell
```code
Write-Host "[*] Оптимизация сетевых настроек..." -ForegroundColor Cyan
# Пример команды: сброс кэша DNS
ipconfig /flushdns
Write-Host "[+] Готово! Теперь интернет будет чуть быстрее." -ForegroundColor Green
Pause
```

Batch / CMD (run.bat)
```code
@echo off
title WinMagisk Batch Module
echo --- WinMagisk Batch Module ---
echo [*] Проверка целостности системных файлов (только чтение)...

sfc /verifyonly

echo.
echo [+] Проверка завершена.
pause
```

Python (run.py)
```code
import os
import platform
import sys

def main():
    print("--- WinMagisk Python Module ---")
    print(f"[*] Интерпретатор: {sys.executable}")
    print(f"[*] Архитектура: {platform.machine()}")
    print(f"[*] Пользователь: {os.getlogin()}")
    
    print("\n[+] Модуль успешно отработал.")
    input("\nНажми Enter для выхода...")

if __name__ == "__main__":
    main()
```

C++ / Executable (run.exe)
```code
#include <iostream>
#include <windows.h>

int main() {
    // Устанавливаем кодировку, чтобы русский текст не был "кракозябрами"
    setlocale(LC_ALL, "Russian");
    
    std::cout << "--- WinMagisk Binary Module ---" << std::endl;
    std::cout << "[*] Запущено прямое исполнение (EXE)" << std::endl;
    
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    std::cout << "[+] Количество ядер процессора: " << si.dwNumberOfProcessors << std::endl;
    
    std::cout << "\nНажми Enter, чтобы закрыть окно..." << std::endl;
    std::cin.get();
    return 0;
}
```
ОБЯЗАТЕЛЬНЫЙ module.json
```code
{
    "name": "Мой модуль",
    "version": "1.0",
    "author": "solevoy69",
    "description": "Описание того что делает модуль"
}
```
