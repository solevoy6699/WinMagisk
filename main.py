import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import subprocess
import sys
import os
import shutil
import math
import json
import ctypes
import logging
import platform
import threading

def resource_path(relative_path):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)

class SplashScreen:
    WIDTH, HEIGHT = 500, 300
    APP_NAME = "WinMagisk"
    ICON_PATH = resource_path("assets/logo.png")
    ICON_SIZE = 100

    TEXT_COLOR = (255, 255, 255)
    OVERLAY_COLOR = (15, 15, 25, 200)
    ACCENT_COLOR = (100, 160, 255, 180)

    def __init__(self, on_finish_callback):
        self.root = tk.Tk()
        self.on_finish = on_finish_callback
        self._setup_window()
        self._build_bg()
        self._build_canvas()
        self._load_icon()
        self._setup_widgets()

        self.x_pos = float(self.WIDTH // 2)
        self._ICON_TARGET = (self.WIDTH - 295) // 2 + self.ICON_SIZE // 2
        self._TEXT_GAP = 10
        self._SLIDE_START = float(self.WIDTH // 2)
        self._SLIDE_DIST = self._SLIDE_START - self._ICON_TARGET

        self.root.after(300, self._start)
        self.root.mainloop()

    def _setup_window(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - self.WIDTH) // 2, (sh - self.HEIGHT) // 2
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _build_bg(self):
        img = Image.new("RGBA", (self.WIDTH, self.HEIGHT))
        draw = ImageDraw.Draw(img)
        for y in range(self.HEIGHT):
            t = y / self.HEIGHT
            draw.line([(0, y), (self.WIDTH, y)], fill=(int(10+20*t), int(10+15*t), int(25+35*t), 255))
        
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), self.OVERLAY_COLOR)
        bg = Image.alpha_composite(img, overlay)
        ImageDraw.Draw(bg).rectangle([0, self.HEIGHT-4, self.WIDTH, self.HEIGHT], fill=self.ACCENT_COLOR)
        self._bg_image, self._bg_photo = bg, ImageTk.PhotoImage(bg)

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")

    def _load_icon(self):
        try:
            self._original_icon = Image.open(self.ICON_PATH).resize((self.ICON_SIZE, self.ICON_SIZE), Image.LANCZOS).convert("RGBA")
        except:
            self._original_icon = Image.new("RGBA", (self.ICON_SIZE, self.ICON_SIZE), (0, 200, 255, 255))

    def _setup_widgets(self):
        cy = self.HEIGHT // 2
        self.photo_ref = ImageTk.PhotoImage(self._original_icon.filter(ImageFilter.GaussianBlur(radius=10)))
        self.img_item = self.canvas.create_image(self.WIDTH // 2, cy, image=self.photo_ref)
        self.text_item = self.canvas.create_text(0, cy, text="", font=("Segoe UI", 28, "bold"), fill="white", anchor="w", state="hidden")
        self.version_item = self.canvas.create_text(self.WIDTH - 12, self.HEIGHT - 14, text="v2.0", font=("Segoe UI", 9), fill="#667799", anchor="e", state="hidden")

    def _start(self): self._unblur_icon(10)

    def _unblur_icon(self, step):
        frame = self._original_icon.filter(ImageFilter.GaussianBlur(radius=step)) if step > 0 else self._original_icon
        self.photo_ref = ImageTk.PhotoImage(frame)
        self.canvas.itemconfig(self.img_item, image=self.photo_ref)
        if step > 0: self.root.after(65, self._unblur_icon, step - 1)
        else: self.root.after(1000, self._begin_slide)

    def _begin_slide(self):
        self.canvas.itemconfig(self.text_item, state="normal")
        self._animate_slide()

    def _animate_slide(self):
        diff = self.x_pos - self._ICON_TARGET
        step = max(diff * 0.12, 0.8)
        self.x_pos -= step
        if self.x_pos <= self._ICON_TARGET: self.x_pos = self._ICON_TARGET
        self.canvas.coords(self.img_item, self.x_pos, self.HEIGHT // 2)
        
        progress = (self._SLIDE_START - self.x_pos) / self._SLIDE_DIST
        chars = min(int(progress * (len(self.APP_NAME) + 1)), len(self.APP_NAME))
        self.canvas.coords(self.text_item, self.x_pos + self.ICON_SIZE // 2 + self._TEXT_GAP, self.HEIGHT // 2)
        self.canvas.itemconfig(self.text_item, text=self.APP_NAME[:chars])

        if self.x_pos > self._ICON_TARGET: self.root.after(12, self._animate_slide)
        else:
            self.canvas.itemconfig(self.version_item, state="normal")
            self.root.after(2000, self._fade_out)

    def _fade_out(self):
        alpha = self.root.attributes("-alpha")
        if alpha > 0:
            self.root.attributes("-alpha", alpha - 0.05)
            self.root.after(20, self._fade_out)
        else:
            self.root.destroy()
            self.on_finish()

LOG_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WinMagisk", "winmagisk.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("WinMagisk")

SOCIAL_LINKS = {"Telegram": "https://t.me/fuck_colevoy69", "GitHub": "https://github.com/solevoy6699"}
MODULE_MANIFEST = "module.json"
MODULE_RUNNERS  = ["run.ps1", "run.bat", "run.exe", "run.py"]

THEME = {
    "bg":         "#08090b",
    "surface":    "#0f1115",
    "surface2":   "#161a20",
    "border":     "#1e2228",
    "accent":     "#00c8ff",
    "accent2":    "#0088cc",
    "accent_dim": "#003d5c",
    "text":       "#e8eaf0",
    "text_muted": "#5a6070",
    "text_dim":   "#8892a0",
    "nav_bg":     "#0c0e12",
    "nav_border": "#1a1e26",
    "danger":     "#ff4455",
    "success":    "#00e676",
    "warning":    "#ffaa00",
    "purple":     "#bb86fc",
}

LANGS = {
    "RUS": {
        "home": "Главная", "mods": "Модули", "settings": "Настройки",
        "status": "Система", "run_act": "Активировать Windows",
        "install_mem": "+ Модуль", "launch": "Запуск", "lang": "Язык",
        "font_sel": "Шрифт", "sb_error_title": "Ошибка безопасности",
        "sb_error_msg": "Отключите Secure Boot в BIOS!",
        "no_runner": "Файл запуска не найден",
        "no_manifest": "Нет module.json — модуль не может быть установлен.",
        "copy_error": "Ошибка копирования",
        "confirm_activation": "Подтверждение активации",
        "confirm_activation_msg": "Будет выполнена команда:\n\n{cmd}\n\nПродолжить?",
        "no_modules": "Модули не установлены",
        "secure_boot_on": "Secure Boot: ВКЛЮЧЁН",
        "secure_boot_off": "Secure Boot: выключен",
        "unlock_win": "Разблокировать Windows",
    },
    "ENG": {
        "home": "Home", "mods": "Modules", "settings": "Settings",
        "status": "System", "run_act": "Activate Windows",
        "install_mem": "+ Module", "launch": "Launch", "lang": "Language",
        "font_sel": "Font", "sb_error_title": "Security Error",
        "sb_error_msg": "Disable Secure Boot in BIOS!",
        "no_runner": "Launch file not found",
        "no_manifest": "No module.json — module cannot be installed.",
        "copy_error": "Copy error",
        "confirm_activation": "Confirm Activation",
        "confirm_activation_msg": "The following command will run:\n\n{cmd}\n\nContinue?",
        "no_modules": "No modules installed",
        "secure_boot_on": "Secure Boot: ON",
        "secure_boot_off": "Secure Boot: off",
        "unlock_win": "Unlock Windows",
    },
}

def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)

def safe_open(path):
    try:
        os.startfile(path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть: {e}")

def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def get_appdata_dir():
    path = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WinMagisk")
    os.makedirs(path, exist_ok=True)
    return path


class ActivationWindow(ctk.CTkToplevel):
    METHODS = {
        "MAS (HWID)": {
            "desc": "Лучший метод для Win 10/11.\nАктивирует систему НАВСЕГДА.",
            "cmd": "irm https://get.activated.win | iex",
        },
        "KMS Script": {
            "desc": "Для Win 7/8.1 и Office.",
            "cmd": "slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX; slmgr /skms kms8.msguides.com; slmgr /ato",
        },
        "Digital License": {
            "desc": "Цифровая лицензия через Microsoft.",
            "cmd": "slmgr.vbs /ato",
        },
    }

    def __init__(self, master, current_font, lang):
        super().__init__(master)
        self.current_font = current_font
        self.lang = lang
        self.title("WinMagisk — Activation")
        self.geometry("480x560")
        self.configure(fg_color=THEME["bg"])
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self._setup_ui()

    def _setup_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=0, height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⚡  АКТИВАЦИЯ", font=("Consolas", 22, "bold"),
                     text_color=THEME["accent"]).pack(expand=True)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        chip = ctk.CTkFrame(body, fg_color=THEME["surface2"], corner_radius=8)
        chip.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(chip, text=f"  🖥  {platform.system()} {platform.release()}",
                     font=("Consolas", 12), text_color=THEME["text_dim"],
                     anchor="w").pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(body, text="МЕТОД АКТИВАЦИИ", font=("Consolas", 10),
                     text_color=THEME["text_muted"], anchor="w").pack(fill="x", pady=(0, 4))

        self.method_var = ctk.StringVar(value="MAS (HWID)")
        ctk.CTkOptionMenu(body, values=list(self.METHODS.keys()), variable=self.method_var,
                          command=self._update_desc, fg_color=THEME["surface2"],
                          button_color=THEME["accent_dim"], button_hover_color=THEME["accent2"],
                          text_color=THEME["text"], font=("Consolas", 13),
                          dropdown_fg_color=THEME["surface"], corner_radius=8, height=40,
                          ).pack(fill="x", pady=(0, 12))

        self.desc_frame = ctk.CTkFrame(body, fg_color=THEME["surface2"],
                                       border_width=1, border_color=THEME["accent_dim"],
                                       corner_radius=10)
        self.desc_frame.pack(fill="x", pady=(0, 20))
        self.desc_label = ctk.CTkLabel(self.desc_frame,
                                       text=self.METHODS["MAS (HWID)"]["desc"],
                                       font=("Consolas", 12), text_color=THEME["text_dim"],
                                       justify="left")
        self.desc_label.pack(padx=14, pady=12, anchor="w")

        self.start_btn = ctk.CTkButton(body, text="▶  АКТИВИРОВАТЬ",
                                       font=("Consolas", 16, "bold"),
                                       fg_color=THEME["accent"], hover_color=THEME["accent2"],
                                       text_color="#000000", height=52, corner_radius=10,
                                       command=self._confirm_and_start)
        self.start_btn.pack(fill="x", side="bottom", pady=8)

    def _update_desc(self, choice):
        self.desc_label.configure(text=self.METHODS[choice]["desc"])

    def _confirm_and_start(self):
        choice = self.method_var.get()
        cmd = self.METHODS[choice]["cmd"]
        msg = LANGS[self.lang]["confirm_activation_msg"].format(cmd=cmd)
        if not messagebox.askyesno(LANGS[self.lang]["confirm_activation"], msg, parent=self):
            return
        logger.info("Запуск активации: %s", choice)
        self.start_btn.configure(state="disabled", text="⏳  ВЫПОЛНЯЕТСЯ...")
        subprocess.Popen(["powershell", "-Command", cmd], shell=True)
        self.after(3000, self.destroy)


class UnlockWindow(ctk.CTkToplevel):

    TWEAKS = [
        ("perf",       "⚡ Производительность", "Режим производительности",
         "Визуальные эффекты, схема питания, таймер прерываний", True),
        ("telemetry",  "🔒 Конфиденциальность", "Отключить телеметрию и слежку",
         "Cortana, рекламный ID, диагностика, история активности", True),
        ("godmode",    "🔒 Конфиденциальность", "God Mode на рабочем столе",
         "Папка с доступом ко всем настройкам Windows", True),
        ("longpaths",  "📁 Файловая система",   "Длинные пути (>260 символов)",
         "Снимает ограничение MAX_PATH в Windows", True),
        ("explorer",   "📁 Файловая система",   "Твики проводника",
         "Расширения, скрытые файлы, старое меню Win11", True),
        ("network",    "🌐 Сеть",               "Оптимизация сети",
         "100% полоса пропускания, TCP оптимизация, отключить прокси", True),
        ("services",   "🛠 Службы",             "Отключить ненужные службы",
         "Телеметрия, Error Reporting, Remote Registry и др.", True),
        ("gaming",     "🎮 Игры",               "Игровые оптимизации",
         "Game Mode, HAGS, отключить Game DVR/Bar", True),
        ("dotnet",     "🧩 Компоненты",         ".NET 3.5 + DirectPlay",
         "Поддержка старых программ и игр", False),
        ("sandbox",    "🧩 Компоненты",         "Windows Sandbox + Hyper-V",
         "Виртуализация и изолированная среда", False),
        ("admin",      "👤 Аккаунты",           "Включить скрытого администратора",
         "Активирует встроенный аккаунт Administrator", False),
    ]

    def __init__(self, master, current_font, lang, script_path):
        super().__init__(master)
        self.current_font = current_font
        self.lang         = lang
        self.script_path  = script_path
        self.title("WinMagisk — Windows Unlocker")
        self.geometry("620x720")
        self.configure(fg_color=THEME["bg"])
        self.resizable(False, True)
        self.attributes("-topmost", True)
        self._vars = {}
        self._running = False
        self._setup_ui()

    def _setup_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=0, height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="both", expand=True, padx=20)
        ctk.CTkLabel(hdr_inner, text="🔓  WINDOWS UNLOCKER",
                     font=("Consolas", 20, "bold"),
                     text_color=THEME["purple"]).pack(side="left", pady=0)
        ctk.CTkLabel(hdr_inner,
                     text=f"{platform.system()} {platform.release()}",
                     font=("Consolas", 11), text_color=THEME["text_muted"]).pack(side="right")

        warn = ctk.CTkFrame(self, fg_color="#1a1200", corner_radius=0)
        warn.pack(fill="x")
        ctk.CTkLabel(warn, text="⚠  Рекомендуется создать точку восстановления перед применением",
                     font=("Consolas", 10), text_color=THEME["warning"]).pack(pady=6)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=THEME["surface2"])
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        current_cat = None
        for tweak_id, cat, name, desc, default in self.TWEAKS:
            # Category label
            if cat != current_cat:
                current_cat = cat
                ctk.CTkLabel(scroll, text=cat, font=("Consolas", 11, "bold"),
                             text_color=THEME["text_muted"], anchor="w").pack(
                    fill="x", padx=4, pady=(12, 4))

            card = ctk.CTkFrame(scroll, fg_color=THEME["surface"],
                                border_width=1, border_color=THEME["border"],
                                corner_radius=10)
            card.pack(fill="x", pady=3)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            text_col = ctk.CTkFrame(inner, fg_color="transparent")
            text_col.pack(side="left", fill="y", expand=True)
            ctk.CTkLabel(text_col, text=name, font=("Consolas", 13),
                         text_color=THEME["text"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_col, text=desc, font=("Consolas", 10),
                         text_color=THEME["text_muted"], anchor="w").pack(anchor="w")

            var = ctk.BooleanVar(value=default)
            self._vars[tweak_id] = var
            ctk.CTkSwitch(inner, text="", variable=var,
                          progress_color=THEME["purple"],
                          button_color=THEME["accent"],
                          width=46).pack(side="right")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkButton(btn_row, text="Выбрать все", font=("Consolas", 11),
                      fg_color=THEME["surface2"], hover_color=THEME["border"],
                      text_color=THEME["text_muted"], height=28, corner_radius=7,
                      command=lambda: [v.set(True) for v in self._vars.values()]).pack(
            side="left", padx=(0, 6))
        ctk.CTkButton(btn_row, text="Снять все", font=("Consolas", 11),
                      fg_color=THEME["surface2"], hover_color=THEME["border"],
                      text_color=THEME["text_muted"], height=28, corner_radius=7,
                      command=lambda: [v.set(False) for v in self._vars.values()]).pack(
            side="left")

        self.log_box = ctk.CTkTextbox(self, height=100, font=("Consolas", 10),
                                      fg_color=THEME["surface"],
                                      border_color=THEME["border"],
                                      text_color=THEME["text_muted"],
                                      state="disabled")
        self.log_box.pack(fill="x", padx=16, pady=(0, 8))

        self.apply_btn = ctk.CTkButton(
            self, text="🔓  ПРИМЕНИТЬ ТВИКИ",
            font=("Consolas", 15, "bold"),
            fg_color=THEME["purple"], hover_color="#9c6cd4",
            text_color="#000", height=50, corner_radius=10,
            command=self._apply,
        )
        self.apply_btn.pack(fill="x", padx=16, pady=(0, 16))

    def _log(self, text, color=None):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _apply(self):
        if self._running:
            return
        selected = [tid for tid, var in self._vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("WinMagisk", "Выберите хотя бы один твик.", parent=self)
            return

        self._running = True
        self.apply_btn.configure(state="disabled", text="⏳  ПРИМЕНЯЕТСЯ...")
        self._log("Запуск...")

        ps_cmd = self._build_ps_command(selected)
        logger.info("Применение твиков: %s", selected)

        def run():
            try:
                proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                     "-Command", ps_cmd],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        self.after(0, lambda l=line: self._log(l))
                proc.wait()
                self.after(0, self._done)
            except Exception as e:
                self.after(0, lambda: self._log(f"Ошибка: {e}"))
                self.after(0, self._done)

        threading.Thread(target=run, daemon=True).start()

    def _done(self):
        self._running = False
        self._log("✓ Готово! Рекомендуется перезагрузка.")
        self.apply_btn.configure(state="normal", text="✓  ПРИМЕНЕНО — перезагрузить?",
                                 fg_color=THEME["success"], text_color="#000",
                                 command=self._reboot)

    def _reboot(self):
        if messagebox.askyesno("WinMagisk", "Перезагрузить Windows сейчас?", parent=self):
            os.system("shutdown /r /t 5 /c \"WinMagisk: применение твиков\"")

    def _build_ps_command(self, selected):
        blocks = {
            "perf": r"""
Write-Host ">> Производительность" -ForegroundColor Cyan
$vfx = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
New-Item -Path $vfx -Force | Out-Null
Set-ItemProperty -Path $vfx -Name "VisualFXSetting" -Value 3
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0"
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
bcdedit /set useplatformtick yes 2>$null
bcdedit /set disabledynamictick yes 2>$null
Write-Host "   OK: Производительность" -ForegroundColor Green
""",
            "telemetry": r"""
Write-Host ">> Телеметрия и конфиденциальность" -ForegroundColor Cyan
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f | Out-Null
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\AppCompat" /v AITEnable /t REG_DWORD /d 0 /f | Out-Null
Stop-Service DiagTrack -Force -ErrorAction SilentlyContinue
Set-Service DiagTrack -StartupType Disabled -ErrorAction SilentlyContinue
Write-Host "   OK: Телеметрия отключена" -ForegroundColor Green
""",
            "godmode": r"""
Write-Host ">> God Mode" -ForegroundColor Cyan
$gm = "$env:USERPROFILE\Desktop\GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}"
if (-not (Test-Path $gm)) { New-Item -ItemType Directory -Path $gm | Out-Null }
Write-Host "   OK: God Mode на рабочем столе" -ForegroundColor Green
""",
            "longpaths": r"""
Write-Host ">> Длинные пути файловой системы" -ForegroundColor Cyan
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f | Out-Null
Write-Host "   OK: Длинные пути включены" -ForegroundColor Green
""",
            "explorer": r"""
Write-Host ">> Твики проводника" -ForegroundColor Cyan
$adv = "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
reg add $adv /v HideFileExt /t REG_DWORD /d 0 /f | Out-Null
reg add $adv /v Hidden /t REG_DWORD /d 1 /f | Out-Null
reg add $adv /v ShowSuperHidden /t REG_DWORD /d 1 /f | Out-Null
reg add $adv /v LaunchTo /t REG_DWORD /d 1 /f | Out-Null
reg add $adv /v ShowSyncProviderNotifications /t REG_DWORD /d 0 /f | Out-Null
$build = [System.Environment]::OSVersion.Version.Build
if ($build -ge 22000) {
    reg add "HKCU\SOFTWARE\CLASSES\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /t REG_SZ /d "" /f | Out-Null
    Write-Host "   OK: Классическое меню Win11 восстановлено" -ForegroundColor Green
}
Write-Host "   OK: Проводник настроен" -ForegroundColor Green
""",
            "network": r"""
Write-Host ">> Оптимизация сети" -ForegroundColor Cyan
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f | Out-Null
netsh int tcp set global autotuninglevel=normal 2>$null | Out-Null
netsh int tcp set global chimney=enabled 2>$null | Out-Null
netsh int tcp set global rss=enabled 2>$null | Out-Null
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoDetect /t REG_DWORD /d 0 /f | Out-Null
Write-Host "   OK: Сеть оптимизирована" -ForegroundColor Green
""",
            "services": r"""
Write-Host ">> Ненужные службы" -ForegroundColor Cyan
$svcs = @("DiagTrack","dmwappushservice","MapsBroker","lfsvc","RetailDemo","RemoteRegistry","WerSvc","wisvc")
foreach ($s in $svcs) {
    Stop-Service $s -Force -ErrorAction SilentlyContinue
    Set-Service $s -StartupType Disabled -ErrorAction SilentlyContinue
    Write-Host "   -- Отключено: $s" -ForegroundColor DarkGray
}
Write-Host "   OK: Службы отключены" -ForegroundColor Green
""",
            "gaming": r"""
Write-Host ">> Игровые оптимизации" -ForegroundColor Cyan
reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f | Out-Null
reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f | Out-Null
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f | Out-Null
reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f | Out-Null
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f | Out-Null
Write-Host "   OK: Игровые твики применены" -ForegroundColor Green
""",
            "dotnet": r"""
Write-Host ">> .NET 3.5 + DirectPlay" -ForegroundColor Cyan
Enable-WindowsOptionalFeature -Online -FeatureName "NetFx3" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
Enable-WindowsOptionalFeature -Online -FeatureName "DirectPlay" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
Write-Host "   OK: .NET 3.5 и DirectPlay включены" -ForegroundColor Green
""",
            "sandbox": r"""
Write-Host ">> Windows Sandbox + Hyper-V" -ForegroundColor Cyan
Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Hyper-V-All" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
Write-Host "   OK: Sandbox и Hyper-V включены" -ForegroundColor Green
""",
            "admin": r"""
Write-Host ">> Встроенный аккаунт Administrator" -ForegroundColor Cyan
net user administrator /active:yes 2>$null | Out-Null
Write-Host "   OK: Администратор активирован" -ForegroundColor Green
""",
        }
        parts = ["$ErrorActionPreference = 'SilentlyContinue'"]
        for tid in selected:
            if tid in blocks:
                parts.append(blocks[tid])
        parts.append("Write-Host '--- Все выбранные твики применены ---' -ForegroundColor Magenta")
        return "\n".join(parts)


class WinMagisk(ctk.CTk):
    NAV_ITEMS = [
        ("home",     "🏠", "show_home"),
        ("mods",     "🧩", "show_mods"),
        ("settings", "⚙️", "show_settings"),
    ]

    def __init__(self):
        super().__init__()
        self.assets_dir        = resource_path("assets")
        self.fonts_dir         = os.path.join(self.assets_dir, "fonts")
        self.appdata_dir       = get_appdata_dir()
        self.config_path       = os.path.join(self.appdata_dir, "config.json")
        self.user_modules_path = os.path.join(self.appdata_dir, "modules")
        self.script_path       = resource_path("winunlock.ps1")
        os.makedirs(self.user_modules_path, exist_ok=True)

        if not is_admin():
            self._request_admin()

        self.config       = self._load_config()
        self.lang         = self.config.get("lang", "RUS")
        self.current_font = self.config.get("font", "Consolas")
        self._current_frame = None
        self.is_rotating    = False
        self.logo_label     = None
        self.orig_logo      = None
        self._active_nav    = "home"
        self._nav_buttons   = {}

        self._load_custom_fonts()
        self._run_pre_checks()

        self.title("WinMagisk")
        self.geometry("860x680")
        self.minsize(760, 580)
        self.configure(fg_color=THEME["bg"])

        try:
            self.orig_logo = Image.open(os.path.join(self.assets_dir, "logo.png")).convert("RGBA")
        except Exception:
            pass

        self._build_layout()
        self.show_home()


    def _build_layout(self):
        self.root_frame = ctk.CTkFrame(self, fg_color=THEME["bg"], corner_radius=0)
        self.root_frame.pack(fill="both", expand=True)
        self.content_area = ctk.CTkFrame(self.root_frame, fg_color="transparent", corner_radius=0)
        self.content_area.pack(fill="both", expand=True, side="top")
        self._build_nav_bar()

    def _build_nav_bar(self):
        self.nav_bar = ctk.CTkFrame(self.root_frame, fg_color=THEME["nav_bg"],
                                    corner_radius=0, border_width=1,
                                    border_color=THEME["nav_border"], height=68)
        self.nav_bar.pack(fill="x", side="bottom")
        self.nav_bar.pack_propagate(False)
        self._nav_buttons = {}
        for key, icon, method in self.NAV_ITEMS:
            col = ctk.CTkFrame(self.nav_bar, fg_color="transparent", corner_radius=0)
            col.pack(side="left", expand=True, fill="both")
            btn = ctk.CTkButton(col, text=f"{icon}\n{LANGS[self.lang][key]}",
                                font=("Segoe UI Emoji", 11),
                                fg_color="transparent", hover_color=THEME["surface"],
                                text_color=THEME["text_muted"], corner_radius=0,
                                command=lambda m=method, k=key: self._nav_click(m, k))
            btn.pack(fill="both", expand=True, padx=2, pady=4)
            self._nav_buttons[key] = btn
        self._highlight_nav("home")

    def _nav_click(self, method, key):
        self._active_nav = key
        self._highlight_nav(key)
        getattr(self, method)()

    def _highlight_nav(self, active_key):
        for key, btn in self._nav_buttons.items():
            if key == active_key:
                btn.configure(text_color=THEME["accent"], fg_color=THEME["surface"])
            else:
                btn.configure(text_color=THEME["text_muted"], fg_color="transparent")

    def _animate_transition(self, builder):
        new_frame = ctk.CTkFrame(self.content_area, fg_color="transparent", corner_radius=0)
        builder(new_frame)
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = new_frame
        self._current_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)


    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Consolas", 10),
                     text_color=THEME["text_muted"], anchor="w").pack(fill="x", padx=24, pady=(14, 4))

    def _card(self, parent, **kwargs):
        return ctk.CTkFrame(parent, fg_color=THEME["surface"],
                            border_width=1, border_color=THEME["border"],
                            corner_radius=12, **kwargs)

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=THEME["border"], height=1,
                     corner_radius=0).pack(fill="x", padx=24, pady=2)


    def _get_system_info(self):
        info = {"ver": f"{platform.system()} {platform.release()}",
                "build": platform.version().split(".")[-1], "sb": False}
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SYSTEM\CurrentControlSet\Control\SecureBoot\State")
            info["sb"] = winreg.QueryValueEx(key, "UEFISecureBootEnabled")[0] == 1
        except Exception:
            pass
        return info


    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Ошибка чтения конфига: %s", e)
        return {}

    def _save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"font": self.current_font, "lang": self.lang}, f, ensure_ascii=False)
        except Exception as e:
            logger.error("Ошибка сохранения конфига: %s", e)

    def _request_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    def _load_custom_fonts(self):
        if not os.path.isdir(self.fonts_dir):
            return
        for f in os.listdir(self.fonts_dir):
            if f.endswith((".ttf", ".otf")):
                try:
                    ctypes.windll.gdi32.AddFontResourceExW(os.path.join(self.fonts_dir, f), 0x10, 0)
                except Exception:
                    pass

    def _run_pre_checks(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SYSTEM\CurrentControlSet\Control\SecureBoot\State")
            if winreg.QueryValueEx(key, "UEFISecureBootEnabled")[0] == 1:
                messagebox.showerror(LANGS[self.lang]["sb_error_title"],
                                     LANGS[self.lang]["sb_error_msg"])
                sys.exit()
        except Exception:
            pass


    def show_home(self):
        def build(parent):
            scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                            scrollbar_button_color=THEME["surface2"])
            scroll.pack(fill="both", expand=True)

            top = ctk.CTkFrame(scroll, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=(16, 8))
            logo_row = ctk.CTkFrame(top, fg_color="transparent")
            logo_row.pack(side="left", fill="y")

            if self.orig_logo:
                self.logo_img = ctk.CTkImage(self.orig_logo, size=(48, 48))
                self.logo_label = ctk.CTkLabel(logo_row, image=self.logo_img,
                                               text="", cursor="hand2")
                self.logo_label.pack(side="left")
                self.logo_label.bind("<Button-1>", self._trigger_spin)

            title_col = ctk.CTkFrame(logo_row, fg_color="transparent")
            title_col.pack(side="left", padx=12)
            ctk.CTkLabel(title_col, text="WinMagisk", font=("Consolas", 26, "bold"),
                         text_color=THEME["accent"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(title_col, text="by solevoy69", font=("Consolas", 10),
                         text_color=THEME["text_muted"], anchor="w").pack(anchor="w")

            self.pwr_menu_var = ctk.StringVar(value="⏻")
            ctk.CTkOptionMenu(top, values=["Перезагрузка", "Завершение", "В BIOS"],
                              command=self._handle_power, width=52, height=36,
                              fg_color=THEME["surface2"], button_color=THEME["surface2"],
                              button_hover_color=THEME["border"], text_color=THEME["text_dim"],
                              dropdown_fg_color=THEME["surface"],
                              variable=self.pwr_menu_var, font=("Consolas", 16),
                              corner_radius=8).pack(side="right", pady=4)

            self._section_label(scroll, "СИСТЕМА")
            sys_info = self._get_system_info()
            info_card = self._card(scroll)
            info_card.pack(fill="x", padx=20, pady=(0, 4))
            row1 = ctk.CTkFrame(info_card, fg_color="transparent")
            row1.pack(fill="x", padx=16, pady=(12, 0))
            ctk.CTkLabel(row1, text="🖥  " + sys_info["ver"], font=("Consolas", 13),
                         text_color=THEME["text"], anchor="w").pack(side="left")
            ctk.CTkLabel(row1, text=f"BUILD {sys_info['build']}", font=("Consolas", 11),
                         text_color=THEME["text_muted"], anchor="e").pack(side="right")
            row2 = ctk.CTkFrame(info_card, fg_color="transparent")
            row2.pack(fill="x", padx=16, pady=(6, 14))
            sb_color = THEME["danger"] if sys_info["sb"] else THEME["success"]
            sb_text = LANGS[self.lang]["secure_boot_on"] if sys_info["sb"] else LANGS[self.lang]["secure_boot_off"]
            sb_badge = ctk.CTkFrame(row2, fg_color=THEME["surface2"], corner_radius=6)
            sb_badge.pack(side="left")
            ctk.CTkLabel(sb_badge, text=sb_text, font=("Consolas", 11),
                         text_color=sb_color).pack(padx=10, pady=4)

            self._section_label(scroll, "ИНСТРУМЕНТЫ")

            unlock_card = self._card(scroll)
            unlock_card.pack(fill="x", padx=20, pady=(0, 4))
            unlock_inner = ctk.CTkFrame(unlock_card, fg_color="transparent")
            unlock_inner.pack(fill="x", padx=16, pady=16)

            left = ctk.CTkFrame(unlock_inner, fg_color="transparent")
            left.pack(side="left", fill="y", expand=True)

            icon_bg = ctk.CTkFrame(left, fg_color="#1e1030", width=44, height=44, corner_radius=12)
            icon_bg.pack(side="left")
            icon_bg.pack_propagate(False)
            ctk.CTkLabel(icon_bg, text="🔓", font=("Segoe UI Emoji", 22)).pack(expand=True)

            text_col = ctk.CTkFrame(left, fg_color="transparent")
            text_col.pack(side="left", padx=12, fill="y")
            ctk.CTkLabel(text_col, text=LANGS[self.lang]["unlock_win"],
                         font=("Consolas", 14, "bold"),
                         text_color=THEME["purple"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_col,
                         text="Производительность • Конфиденциальность • Игры",
                         font=("Consolas", 10), text_color=THEME["text_muted"],
                         anchor="w").pack(anchor="w")

            ctk.CTkButton(unlock_inner, text="Открыть  →",
                          font=("Consolas", 12, "bold"),
                          fg_color=THEME["purple"], hover_color="#9c6cd4",
                          text_color="#000", height=36, width=120, corner_radius=9,
                          command=self._open_unlock).pack(side="right")

            # Activation
            act_card = self._card(scroll)
            act_card.pack(fill="x", padx=20, pady=(0, 4))
            act_inner = ctk.CTkFrame(act_card, fg_color="transparent")
            act_inner.pack(fill="x", padx=16, pady=14)

            left2 = ctk.CTkFrame(act_inner, fg_color="transparent")
            left2.pack(side="left", fill="y", expand=True)
            icon_bg2 = ctk.CTkFrame(left2, fg_color="#001a2e", width=44, height=44, corner_radius=12)
            icon_bg2.pack(side="left")
            icon_bg2.pack_propagate(False)
            ctk.CTkLabel(icon_bg2, text="⚡", font=("Segoe UI Emoji", 22)).pack(expand=True)
            text_col2 = ctk.CTkFrame(left2, fg_color="transparent")
            text_col2.pack(side="left", padx=12, fill="y")
            ctk.CTkLabel(text_col2, text="Активация Windows",
                         font=("Consolas", 14, "bold"),
                         text_color=THEME["accent"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_col2, text="HWID • KMS • Digital License",
                         font=("Consolas", 10), text_color=THEME["text_muted"],
                         anchor="w").pack(anchor="w")
            ctk.CTkButton(act_inner, text="Открыть  →",
                          font=("Consolas", 12, "bold"),
                          fg_color=THEME["accent"], hover_color=THEME["accent2"],
                          text_color="#000000", height=36, width=120, corner_radius=9,
                          command=self._open_activation).pack(side="right")

            self._section_label(scroll, "ССЫЛКИ")
            soc_card = self._card(scroll)
            soc_card.pack(fill="x", padx=20, pady=(0, 20))
            for i, (name, url, color) in enumerate([
                ("Telegram", SOCIAL_LINKS["Telegram"], "#229ED9"),
                ("GitHub",   SOCIAL_LINKS["GitHub"],   "#444"),
            ]):
                r = ctk.CTkFrame(soc_card, fg_color="transparent")
                r.pack(fill="x", padx=16, pady=(12 if i == 0 else 4, 12 if i == 1 else 4))
                ctk.CTkLabel(r, text=name, font=("Consolas", 13),
                             text_color=THEME["text"], anchor="w").pack(side="left")
                ctk.CTkButton(r, text="Перейти  →", font=("Consolas", 11),
                              fg_color=color, hover_color=THEME["surface2"],
                              text_color=THEME["text"], height=30, width=100, corner_radius=7,
                              command=lambda u=url: safe_open(u)).pack(side="right")
                if i == 0:
                    self._divider(soc_card)

        self._animate_transition(build)

    def _open_unlock(self):
        UnlockWindow(self, self.current_font, self.lang, self.script_path)

    def _open_activation(self):
        ActivationWindow(self, self.current_font, self.lang)


    def show_mods(self):
        def build(parent):
            hdr = ctk.CTkFrame(parent, fg_color=THEME["surface"], corner_radius=0, height=60)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
            hdr_inner.pack(fill="both", expand=True, padx=20)
            ctk.CTkLabel(hdr_inner, text=LANGS[self.lang]["mods"],
                         font=("Consolas", 18, "bold"), text_color=THEME["text"]).pack(side="left")
            ctk.CTkButton(hdr_inner, text="＋  " + LANGS[self.lang]["install_mem"],
                          font=("Consolas", 12), height=32, width=130,
                          fg_color=THEME["accent_dim"], hover_color=THEME["accent2"],
                          text_color=THEME["accent"], corner_radius=8,
                          command=self._install_module_dialog).pack(side="right", pady=14)

            scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                            scrollbar_button_color=THEME["surface2"])
            scroll.pack(fill="both", expand=True)

            try:
                entries = [d for d in os.listdir(self.user_modules_path)
                           if os.path.isdir(os.path.join(self.user_modules_path, d))]
            except Exception:
                entries = []

            if not entries:
                empty = ctk.CTkFrame(scroll, fg_color="transparent")
                empty.pack(expand=True, fill="both", pady=80)
                ctk.CTkLabel(empty, text="🧩", font=("Segoe UI Emoji", 40),
                             text_color=THEME["text_muted"]).pack()
                ctk.CTkLabel(empty, text=LANGS[self.lang]["no_modules"],
                             font=("Consolas", 14), text_color=THEME["text_muted"]).pack(pady=8)
            else:
                self._section_label(scroll, f"УСТАНОВЛЕНО: {len(entries)}")
                for d in entries:
                    self._create_module_card(scroll, os.path.join(self.user_modules_path, d))

        self._animate_transition(build)

    def _create_module_card(self, parent, path):
        name = os.path.basename(path)

        manifest = {}
        mf = os.path.join(path, MODULE_MANIFEST)
        if os.path.exists(mf):
            try:
                with open(mf, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                pass

        display_name = manifest.get("name", name.upper())
        description  = manifest.get("description", path)
        version      = manifest.get("version", "")

        card = self._card(parent)
        card.pack(fill="x", padx=20, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        icon = ctk.CTkFrame(inner, fg_color=THEME["accent_dim"],
                            width=38, height=38, corner_radius=19)
        icon.pack(side="left")
        icon.pack_propagate(False)
        ctk.CTkLabel(icon, text=name[0].upper(), font=("Consolas", 14, "bold"),
                     text_color=THEME["accent"]).pack(expand=True)

        name_col = ctk.CTkFrame(inner, fg_color="transparent")
        name_col.pack(side="left", padx=12, fill="y", expand=True)
        name_row = ctk.CTkFrame(name_col, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")
        ctk.CTkLabel(name_row, text=display_name, font=("Consolas", 13, "bold"),
                     text_color=THEME["text"], anchor="w").pack(side="left")
        if version:
            ctk.CTkLabel(name_row, text=f"  v{version}", font=("Consolas", 10),
                         text_color=THEME["text_muted"]).pack(side="left")
        ctk.CTkLabel(name_col, text=description, font=("Consolas", 9),
                     text_color=THEME["text_muted"], anchor="w").pack(anchor="w")

        ctk.CTkButton(inner, text="▶  " + LANGS[self.lang]["launch"],
                      font=("Consolas", 12), height=32, width=100,
                      fg_color=THEME["surface2"], hover_color=THEME["accent_dim"],
                      text_color=THEME["accent"], corner_radius=8,
                      command=lambda p=path: self._run_mod(p)).pack(side="right")


    def show_settings(self):
        def build(parent):
            hdr = ctk.CTkFrame(parent, fg_color=THEME["surface"], corner_radius=0, height=60)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            ctk.CTkLabel(hdr, text=LANGS[self.lang]["settings"],
                         font=("Consolas", 18, "bold"), text_color=THEME["text"]).pack(
                side="left", padx=20)

            scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                            scrollbar_button_color=THEME["surface2"])
            scroll.pack(fill="both", expand=True)

            self._section_label(scroll, "ИНТЕРФЕЙС")
            lang_card = self._card(scroll)
            lang_card.pack(fill="x", padx=20, pady=(0, 4))

            lang_row = ctk.CTkFrame(lang_card, fg_color="transparent")
            lang_row.pack(fill="x", padx=16, pady=14)
            ctk.CTkLabel(lang_row, text="🌐  " + LANGS[self.lang]["lang"],
                         font=("Consolas", 13), text_color=THEME["text"],
                         anchor="w").pack(side="left")
            ctk.CTkButton(lang_row, text=self.lang, font=("Consolas", 12, "bold"),
                          fg_color=THEME["accent_dim"], hover_color=THEME["accent2"],
                          text_color=THEME["accent"], height=32, width=70, corner_radius=8,
                          command=self._toggle_lang).pack(side="right")

            self._divider(lang_card)

            font_row = ctk.CTkFrame(lang_card, fg_color="transparent")
            font_row.pack(fill="x", padx=16, pady=14)
            ctk.CTkLabel(font_row, text="🔤  " + LANGS[self.lang]["font_sel"],
                         font=("Consolas", 13), text_color=THEME["text"],
                         anchor="w").pack(side="left")
            font_menu = ctk.CTkOptionMenu(font_row, values=["Consolas", "Arial", "Segoe UI"],
                                          command=self._change_font,
                                          fg_color=THEME["surface2"],
                                          button_color=THEME["accent_dim"],
                                          button_hover_color=THEME["accent2"],
                                          text_color=THEME["text"],
                                          font=("Consolas", 12),
                                          dropdown_fg_color=THEME["surface"],
                                          width=130, height=32, corner_radius=8)
            font_menu.set(self.current_font)
            font_menu.pack(side="right")

            self._section_label(scroll, "О ПРОГРАММЕ")
            about_card = self._card(scroll)
            about_card.pack(fill="x", padx=20, pady=(0, 24))
            for label, value in [("Версия", "2.0"), ("Автор", "solevoy69"), ("Лицензия", "MIT")]:
                row = ctk.CTkFrame(about_card, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=6)
                ctk.CTkLabel(row, text=label, font=("Consolas", 12),
                             text_color=THEME["text_muted"], anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=value, font=("Consolas", 12),
                             text_color=THEME["text"], anchor="e").pack(side="right")

        self._animate_transition(build)


    def _handle_power(self, act):
        cmds = {"Перезагрузка": "shutdown /r /t 0",
                "Завершение":   "shutdown /s /t 0",
                "В BIOS":       "shutdown /r /fw /t 0"}
        if act in cmds:
            os.system(cmds[act])
        self.pwr_menu_var.set("⏻")

    def _trigger_spin(self, _=None):
        if not self.is_rotating:
            self.is_rotating = True
            self._spin(0)

    def _spin(self, step):
        if self.logo_label is None or not self.logo_label.winfo_exists():
            self.is_rotating = False
            return
        angle = math.sin((step / 45) * math.pi) * 360
        rot = self.orig_logo.rotate(-angle, resample=Image.BICUBIC)
        self.logo_label.configure(image=ctk.CTkImage(rot, size=(48, 48)))
        if step < 45:
            self.after(15, lambda: self._spin(step + 1))
        else:
            self.is_rotating = False

    def _change_font(self, f):
        self.current_font = f
        self._save_config()
        self._setup_navigation_labels()
        self.show_settings()

    def _toggle_lang(self):
        self.lang = "ENG" if self.lang == "RUS" else "RUS"
        self._save_config()
        self._rebuild_nav()
        self.show_settings()

    def _rebuild_nav(self):
        self.nav_bar.destroy()
        self._build_nav_bar()
        self._highlight_nav(self._active_nav)

    def _setup_navigation_labels(self):
        for key, btn in self._nav_buttons.items():
            icon = next(ic for k, ic, _ in self.NAV_ITEMS if k == key)
            btn.configure(text=f"{icon}\n{LANGS[self.lang][key]}")

    def _install_module_dialog(self):
        p = filedialog.askdirectory()
        if not p:
            return
        if not os.path.exists(os.path.join(p, MODULE_MANIFEST)):
            messagebox.showerror("WinMagisk", LANGS[self.lang]["no_manifest"])
            return
        dest = os.path.join(self.user_modules_path, os.path.basename(p))
        try:
            shutil.copytree(p, dest, dirs_exist_ok=True)
            logger.info("Модуль установлен: %s", os.path.basename(p))
        except Exception as e:
            messagebox.showerror(LANGS[self.lang]["copy_error"], str(e))
            return
        self.show_mods()

    def _run_mod(self, path):
        name = os.path.basename(path)
        for fname in MODULE_RUNNERS:
            full = os.path.join(path, fname)
            if os.path.exists(full):
                try:
                    if fname.endswith(".py"):
                        subprocess.Popen([sys.executable, full])
                    elif fname.endswith(".exe"):
                        subprocess.Popen([full])
                    else:
                        subprocess.Popen(["powershell", full], shell=True)
                except Exception as e:
                    messagebox.showerror("WinMagisk", str(e))
                return
        messagebox.showerror("WinMagisk", LANGS[self.lang]["no_runner"])


def start_main_app():
    ctk.set_appearance_mode("dark")
    app = WinMagisk()
    app.mainloop()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    else:
        SplashScreen(on_finish_callback=start_main_app)
