import customtkinter as ctk
import platform
import subprocess
import os

THEME = {
    "bg": "#0a0a0a",
    "card": "#151515",
    "accent": "#00d2ff",
    "text": "#ffffff"
}

class ActivationMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WinMagisk - Activation Master")
        self.geometry("450x620")
        self.configure(fg_color=THEME["bg"])
        self.resizable(False, False)

        self.edition = self.get_edition()
        
        self.methods = {
            "MAS (HWID)": {
                "desc": "Лучший метод для Win 10/11.\nАктивирует систему НАВСЕГДА.",
                "cmd": "irm https://get.activated.win | iex"
            },
            "KMS Script": {
                "desc": "Классический метод.\nПодходит для Windows 7/8.1 и Office.",
                "cmd": "slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX; slmgr /skms kms8.msguides.com; slmgr /ato"
            },
            "Digital License": {
                "desc": "Привязка цифровой лицензии\nк вашему железу через сервера MS.",
                "cmd": "slmgr.vbs /ato"
            }
        }
        
        self.setup_ui()

    def get_edition(self):
        try: return platform.win32_edition()
        except: return "Windows 10/11"

    def setup_ui(self):
        ctk.CTkLabel(self, text="ACTIVATION", font=("Impact", 35), text_color=THEME["accent"]).pack(pady=(20, 0))
        ctk.CTkLabel(self, text="MASTER ENGINE", font=("Impact", 15), text_color=THEME["text"]).pack()

        info_card = ctk.CTkFrame(self, fg_color=THEME["card"], corner_radius=10)
        info_card.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(info_card, text=f"{platform.system()} {platform.release()} | {self.edition}", font=("Arial", 12, "bold")).pack(pady=10)

        ctk.CTkLabel(self, text="ВЫБЕРИТЕ МЕТОД:", font=("Arial", 12, "bold"), text_color="#777").pack(pady=(10, 5))
        
        self.method_var = ctk.StringVar(value="MAS (HWID)")
        self.method_menu = ctk.CTkOptionMenu(
            self, 
            values=list(self.methods.keys()),
            variable=self.method_var,
            command=self.update_description,
            fg_color=THEME["card"],
            button_color=THEME["accent"],
            button_hover_color="#0088aa",
            dynamic_resizing=False,
            width=200
        )
        self.method_menu.pack(pady=5)

        self.desc_label = ctk.CTkLabel(
            self, 
            text=self.methods["MAS (HWID)"]["desc"], 
            font=("Arial", 13, "italic"), 
            text_color=THEME["accent"]
        )
        self.desc_label.pack(pady=10)

        instr_frame = ctk.CTkFrame(self, fg_color="transparent")
        instr_frame.pack(padx=30, pady=10)
        instr_text = (
            "ИНСТРУКЦИЯ:\n"
            "1. Выключите Антивирус\n"
            "2. Выберите метод выше\n"
            "3. Нажмите кнопку START\n"
            "4. Не закрывайте окно консоли"
        )
        ctk.CTkLabel(instr_frame, text=instr_text, font=("Consolas", 11), justify="left", text_color="#bbb").pack()

        self.btn = ctk.CTkButton(
            self, text="START ACTIVATION", 
            font=("Impact", 22),
            fg_color=THEME["accent"], 
            text_color="black",
            height=55,
            hover_color="#0088aa",
            command=self.start_process
        )
        self.btn.pack(side="bottom", fill="x", padx=30, pady=30)

    def update_description(self, choice):
        self.desc_label.configure(text=self.methods[choice]["desc"])

    def start_process(self):
        method = self.method_var.get()
        command = self.methods[method]["cmd"]
        
        self.btn.configure(state="disabled", text="RUNNING...")
        
        try:
            subprocess.Popen(["powershell", "-Command", command], shell=True)
            self.after(3000, self.destroy)
        except Exception as e:
            self.btn.configure(text="EXECUTION ERROR", fg_color="red")

if __name__ == "__main__":
    app = ActivationMaster()
    app.mainloop()