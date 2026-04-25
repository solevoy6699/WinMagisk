import customtkinter as ctk
import subprocess
import sys
import os
import shutil
import math
import json
import ctypes
import platform
from PIL import Image
from tkinter import messagebox, filedialog
from functools import partial
import threading
import time

def safe_open(path):
    try:
        if path.lower().startswith(("http://","https://")):
            os.startfile(path)
        else:
            os.startfile(path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть: {e}")

def fade_in(window, steps=8, delay=0.015):
    try:
        # Only attempt if supported
        for i in range(steps):
            alpha = (i+1)/steps
            try: window.attributes("-alpha", alpha)
            except: pass
            time.sleep(delay)
        try: window.attributes("-alpha", 1.0)
        except: pass
    except: pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

THEME = {
    "bg": "#050505",
    "glass": "#121212",
    "glass_border": "#252525",
    "accent": "#00d2ff",
    "text": "#FFFFFF",
    "gray": "#BBBBBB"
}

# Extended theme
THEME.update({
    "bg_grad_top": "#050505",
    "bg_grad_bottom": "#0b0b0b",
    "card_bg": "#0f1113",
    "card_border": "#1f1f1f",
    "accent_glow": "#00e6ff"
})

LANGS = {
    "RUS": {
        "home": "Главная",
        "mods": "Модули",
        "settings": "Опции",
        "status": "Информация о системе",
        "installed": "Установлено",
        "run_act": "Активировать винду",
        "install_mem": "+ Модуль",
        "execute": "Выполнить",
        "launch": "Запуск",
        "lang": "Язык интерфейса",
        "font_sel": "Шрифт интерфейса",
        "sb_error_title": "Ошибка безопасности",
        "sb_error_msg": "Отключите Secure Boot в BIOS и Антивирус!"
    },
    "ENG": {
        "home": "Home",
        "mods": "Modules",
        "settings": "Settings",
        "status": "System Information",
        "installed": "Installed",
        "run_act": "Activate Windows",
        "install_mem": "+ Module",
        "execute": "Execute",
        "launch": "Launch",
        "lang": "Language",
        "font_sel": "UI Font",
        "sb_error_title": "Security Error",
        "sb_error_msg": "Disable Secure Boot in BIOS and Antivirus!"
    }
}

class WinMagisk(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.fonts_dir = os.path.join(self.assets_dir, "fonts")
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.user_modules_path = os.path.join(self.base_dir, "modules", "user_modules")
        os.makedirs(self.user_modules_path, exist_ok=True)

        if not is_admin(): self.request_admin()
        self.config = self.load_config()
        self.lang = self.config.get("lang", "RUS")
        self.current_font = self.config.get("font", "Arial")

        self.load_custom_fonts()
        self.run_pre_checks()

        self.title("WinMagisk v1")
        self.geometry("920x720")
        self.configure(fg_color=THEME["bg"])
        try:
            self.attributes("-alpha", 1.0)
        except: pass

        self.is_rotating = False
        self._current_frame = None

        try:
            self.orig_logo = Image.open(os.path.join(self.assets_dir, "logo.png")).convert("RGBA")
        except: self.orig_logo = None

        self.bg_canvas = ctk.CTkFrame(self, fg_color=THEME["bg"])
        self.bg_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        self.sidebar = ctk.CTkFrame(self.bg_canvas, width=160, fg_color=THEME["glass"], corner_radius=0,
                                   border_width=1, border_color=THEME["glass_border"])
        self.sidebar.place(relx=0, rely=0, relheight=1.0)
        self.content_area = ctk.CTkFrame(self.bg_canvas, fg_color="transparent")
        self.content_area.place(relx=0.175, rely=0, relwidth=0.825, relheight=1.0)

        self.setup_navigation()
        self.show_home()

    def run_pre_checks(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SecureBoot\State")
            value, _ = winreg.QueryValueEx(key, "UEFISecureBootEnabled")
            if value == 1:
                messagebox.showerror(LANGS[self.lang]["sb_error_title"], LANGS[self.lang]["sb_error_msg"])
                sys.exit()
        except: pass

    def open_power_menu(self, widget):
        m = ctk.CTkOptionMenu(
            self,
            values=["Перезагрузка", "Завершение работы", "Перезагрузка в BIOS", "Безопасный режим", "Перезагрузить драйверы"],
            command=self.handle_power_action
        )
        try:
            m._dropdown_menu.post(widget.winfo_rootx(), widget.winfo_rooty() + widget.winfo_height())
        except: pass

    def get_real_system_info(self):
        info = {"ver": f"{platform.system()} {platform.release()}", "build": platform.version().split('.')[-1], "sb": "OFF", "act": "CHECKING..."}
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SecureBoot\State")
            val, _ = winreg.QueryValueEx(key, "UEFISecureBootEnabled")
            info["sb"] = "ON" if val == 1 else "OFF"
        except: pass
        try:
            cmd = "cscript //nologo C:\\Windows\\System32\\slmgr.vbs /dli"
            out = subprocess.check_output(cmd, shell=True).decode('cp866', errors='ignore').lower()
            info["act"] = "ACTIVATED" if "licensed" in out or "лицензия" in out else "NOT ACTIVATED"
        except: info["act"] = "UNDEFINED"
        return info

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f: return json.load(f)
            except: return {}
        return {}

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"font": self.current_font, "lang": self.lang}, f, ensure_ascii=False)
        except: pass

    def request_admin(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except: pass
        sys.exit()

    def load_custom_fonts(self):
        if os.path.exists(self.fonts_dir):
            for f in os.listdir(self.fonts_dir):
                if f.endswith((".ttf", ".otf")):
                    try:
                        ctypes.windll.gdi32.AddFontResourceExW(os.path.join(self.fonts_dir, f), 0x10, 0)
                    except: pass

    def setup_navigation(self):
        for child in self.sidebar.winfo_children(): 
            child.destroy()
        
        items = [
            ("home", self.show_home, "🏠"), 
            ("mods", self.show_mods, "🧩"), 
            ("settings", self.show_settings, "⚙️")
        ]
        
        for i, (key, cmd, icon_obj) in enumerate(items):
            ico = None
            display_text = LANGS[self.lang][key]
            
            if icon_obj.endswith(".png"):
                try:
                    ico = ctk.CTkImage(Image.open(os.path.join(self.assets_dir, icon_obj)), size=(28,28))
                except:
                    ico = None
            else:
                display_text = f"{icon_obj}  {display_text}"

            btn = ctk.CTkButton(
                self.sidebar, 
                text=display_text, 
                image=ico, 
                compound="left",
                command=cmd, 
                fg_color="transparent", 
                text_color=THEME["text"],
                hover_color="#0e0e0e", 
                font=("Segoe UI Emoji", 14), 
                anchor="w",
                width=140,
                height=56
            )
            btn.place(x=10, y=20 + i*70)

    def animate_transition(self, new_builder):
        try:
            new_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            new_builder(new_frame)
            
            if self._current_frame:
                self._current_frame.destroy()
            
            self._current_frame = new_frame
            self._current_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            
        except Exception as e:
            print(f"Ошибка при переключении кадра: {e}")
    def show_home(self):
        def build(parent):
            sys_info = self.get_real_system_info()

            top_bar = ctk.CTkFrame(parent, fg_color="transparent")
            top_bar.pack(fill="x", padx=20, pady=(10, 0))

            try:
                restart_ico = ctk.CTkImage(Image.open(os.path.join(self.assets_dir, "restart.png")), size=(20, 20))
            except: restart_ico = None

            restart_btn = ctk.CTkButton(
                top_bar, text="", image=restart_ico,
                command=lambda: self.open_power_menu(restart_btn),
                width=44,
                height=36,
                corner_radius=10,
                fg_color=THEME["glass"], 
                hover_color=THEME["glass_border"]
            )
            restart_btn.pack(side="right")

            header = ctk.CTkFrame(parent, fg_color="transparent")
            header.pack(fill="x", pady=(8, 10), padx=12)
            if self.orig_logo:
                img = ctk.CTkImage(self.orig_logo, size=(64,64))
                lbl = ctk.CTkLabel(header, image=img, text="", cursor="hand2")
                lbl.pack(side="left", padx=12)
                lbl.bind("<Button-1>", self.trigger_spin)
                self.logo_label = lbl
            ctk.CTkLabel(header, text="WinMagisk", font=(self.current_font, 36, "bold"), text_color=THEME["accent"]).pack(side="left", padx=10)

            card = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=12, border_width=1, border_color=THEME["card_border"])
            card.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(card, text=LANGS[self.lang]["status"], font=(self.current_font, 16, "bold"), text_color=THEME["accent_glow"]).pack(anchor="w", pady=(12,0), padx=12)
            txt = f"OS: {sys_info['ver']}  |  BUILD: {sys_info['build']}\nSTATUS: {sys_info['act']}    SECURE BOOT: {sys_info['sb']}"
            ctk.CTkLabel(card, text=txt, font=(self.current_font, 13), text_color=THEME["text"], justify="left").pack(padx=12, pady=10, anchor="w")

            strip = ctk.CTkFrame(parent, fg_color="transparent")
            strip.pack(fill="x", padx=16)
            ctk.CTkButton(strip, text=LANGS[self.lang]["run_act"], fg_color=THEME["accent_glow"], text_color="#000", font=(self.current_font, 16, "bold"), height=58, corner_radius=12,
                          command=lambda: subprocess.Popen([sys.executable, os.path.join(self.base_dir, "modules", "gui_activator.py")])
            ).pack(fill="x", expand=True, padx=(0,10))

            social_frame = ctk.CTkFrame(parent, fg_color="transparent")
            social_frame.pack(fill="x", padx=16, pady=8)

            try:
                tg_ico = ctk.CTkImage(Image.open(os.path.join(self.assets_dir, "tg.png")), size=(20, 20))
            except: tg_ico = None

            try:
                gh_ico = ctk.CTkImage(Image.open(os.path.join(self.assets_dir, "github.png")), size=(20, 20))
            except: gh_ico = None

            ctk.CTkButton(social_frame, text="Telegram (@fuck_colevoy69)", image=tg_ico, compound="left", fg_color="#0088cc", height=40, font=(self.current_font, 12, "bold"),
                          command=lambda: safe_open("https://t.me/fuck_colevoy69")).pack(side="left", fill="x", expand=True, padx=(0,6))
            
            ctk.CTkButton(social_frame, text="GitHub", image=gh_ico, compound="left", fg_color="#333333", height=40, font=(self.current_font, 12, "bold"),
                          command=lambda: safe_open("https://github.com/solevoy6699")).pack(side="left", fill="x", expand=True, padx=(6,0))

        self.animate_transition(build)

    def show_mods(self):
        def build(parent):
            header = ctk.CTkFrame(parent, fg_color="transparent")
            header.pack(fill="x", pady=(15,10), padx=20)
            ctk.CTkLabel(header, text=LANGS[self.lang]["mods"], font=(self.current_font, 28)).pack(side="left")
            ctk.CTkButton(header, text=LANGS[self.lang]["install_mem"], command=self.install_module_dialog,
                          fg_color=THEME["accent"], text_color="black", width=160).pack(side="right")
            scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=10)
            try:
                entries = os.listdir(self.user_modules_path)
            except:
                entries = []
            for d in entries:
                path = os.path.join(self.user_modules_path, d)
                if os.path.isdir(path): self.create_module_item(scroll, path)
        self.animate_transition(build)

    def create_module_item(self, parent, path):
        name = os.path.basename(path).upper()
        desc = ""
        readme = os.path.join(path, "README.md")
        if os.path.exists(readme):
            try:
                with open(readme, "r", encoding="utf-8") as rf:
                    desc = rf.read().splitlines()[0][:120]
            except: desc = ""
        card = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=10, border_width=1, border_color=THEME["card_border"])
        card.pack(fill="x", pady=8, padx=8)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(top, text=name, font=(self.current_font, 16, "bold"), text_color=THEME["accent_glow"]).pack(side="left")
        ctk.CTkLabel(top, text=desc, font=(self.current_font, 12), text_color=THEME["gray"]).pack(side="left", padx=12)
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text=LANGS[self.lang]["launch"], width=100, command=lambda p=path: self.run_mod(p)).pack(side="right")
        ctk.CTkButton(btn_frame, text="Open", width=80, fg_color="transparent", command=lambda p=path: safe_open(p)).pack(side="right", padx=8)

    def show_settings(self):
        def build(parent):
            ctk.CTkLabel(parent, text=LANGS[self.lang]["settings"], font=(self.current_font, 32)).pack(pady=20, padx=25, anchor="w")
            l_box = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=12)
            l_box.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(l_box, text=LANGS[self.lang]["lang"]).pack(side="left", padx=20, pady=15)
            ctk.CTkButton(l_box, text=self.lang, width=80, command=self.toggle_language).pack(side="right", padx=20)
            f_box = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=12)
            f_box.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f_box, text=LANGS[self.lang]["font_sel"]).pack(side="left", padx=20, pady=15)
            m = ctk.CTkOptionMenu(f_box, values=self.get_font_list(), command=self.change_font)
            m.set(self.current_font); m.pack(side="right", padx=20)

            t_box = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], corner_radius=12)
            t_box.pack(fill="x", padx=20, pady=12)
            ctk.CTkLabel(t_box, text="Theme", font=(self.current_font, 12)).pack(side="left", padx=12, pady=12)
            theme_btn = ctk.CTkButton(t_box, text="Toggle Dark", width=120, command=self.toggle_theme)
            theme_btn.pack(side="right", padx=12)
        self.animate_transition(build)

    def handle_power_action(self, action):
        if not action: return
        if action != "Перезагрузить драйверы":
            if not messagebox.askyesno("WinMagisk", f"Выполнить: {action}?"): return
        try:
            if action == "Перезагрузка": os.system("shutdown /r /t 0")
            elif action == "Завершение работы": os.system("shutdown /s /t 0")
            elif action == "Перезагрузка в BIOS": os.system("shutdown /r /fw /t 0")
            elif action == "Безопасный режим":
                subprocess.run(["bcdedit", "/set", "{current}", "safeboot", "minimal"], shell=True)
                os.system("shutdown /r /t 0")
            elif action == "Перезагрузить драйверы":
                subprocess.run(["powershell", "-Command", "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('^+(B)')"], shell=True)
                messagebox.showinfo("WinMagisk", "Драйверы перезагружены")
        except Exception as e: messagebox.showerror("Ошибка", str(e))

    def change_font(self, new_font):
        self.current_font = new_font; self.save_config(); self.setup_navigation(); self.show_settings()

    def toggle_language(self):
        self.lang = "ENG" if self.lang == "RUS" else "RUS"; self.save_config(); self.setup_navigation(); self.show_settings()

    def run_mod(self, path):
        mapping = {"run.ps1": ["powershell", "-ExecutionPolicy", "Bypass", "-File"], "run.exe": [], "run.py": [sys.executable], "run.bat": ["cmd", "/c"]}
        for file, prefix in mapping.items():
            full = os.path.join(path, file)
            if os.path.exists(full):
                try:
                    subprocess.Popen(prefix + [full], shell=True)
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
                return
        messagebox.showerror("WinMagisk", "Запускной файл не найден!")

    def trigger_spin(self, event):
        if not self.is_rotating: self.is_rotating = True; self.spin_animation(0, 45)

    def spin_animation(self, step, total):
        if not self.orig_logo: return
        angle = math.sin((step/total) * math.pi) * 360
        rotated = self.orig_logo.rotate(-angle, resample=Image.BICUBIC)
        try:
            self.logo_label.configure(image=ctk.CTkImage(rotated, size=(64, 64)))
        except: pass
        if step < total: self.after(15, lambda: self.spin_animation(step + 1, total))
        else: self.is_rotating = False

    def get_font_list(self):
        fonts = ["Arial", "Consolas"]
        if os.path.exists(self.fonts_dir):
            fonts += [os.path.splitext(f)[0] for f in os.listdir(self.fonts_dir) if f.endswith((".ttf", ".otf"))]
        return list(dict.fromkeys(fonts))

    def install_module_dialog(self):
        path = filedialog.askdirectory()
        if path:
            try:
                shutil.copytree(path, os.path.join(self.user_modules_path, os.path.basename(path)), dirs_exist_ok=True)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            self.show_mods()

    def toggle_theme(self):
        if THEME["accent"] == "#00d2ff":
            THEME["accent"] = "#ff9d00"; THEME["accent_glow"] = "#ffb64d"; THEME["card_bg"]="#111214"
        else:
            THEME["accent"] = "#00d2ff"; THEME["accent_glow"] = "#00e6ff"; THEME["card_bg"]="#0f1113"
        self.setup_navigation(); self.show_settings()

if __name__ == "__main__":
    try:
        app = WinMagisk()
        print("Приложение создано, запускаю mainloop...")
        app.mainloop()
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ: {e}")
        input("Нажми Enter чтобы выйти...")
