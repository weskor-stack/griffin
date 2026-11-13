import tkinter as tk
from tkinter import messagebox, ttk
import conexion

BG_HEADER = "#1565C0"
BG_BUTTON_BAR = "#F3F3F3"
BG_MAIN = "#FFFFFF"
FG_WHITE = "#FFFFFF"
FG_BLUE_LABEL = "#00479E"
BORDER_COLOR = "#000000"
FONT_HEAD = ("Segoe UI", 18, "bold")
FONT_SUBHEAD = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 8, "bold")
FONT_MONO = ("Consolas", 10)
FONT_BTN = ("Segoe UI", 9, "bold")

def apply_theme():
    ttk.Style().theme_use("clam")

class FormularioApiConfig:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración de URLs")
        self.root.geometry("600x530")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        self.root.focus_force()
        self.root.attributes("-topmost", False)
        try:
            self.root.iconbitmap("favicon.ico")
        except tk.TclError:
            pass

        self.APIS_BASE = ["CONDUIT", "UNIT", "INTERLOCKING", "TRACEABILITY"]
        self.entries = {}
        apply_theme()
        self._setup_ui()
        self.cargar_configuracion()

    def _setup_ui(self):
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.root, bg=BG_HEADER, padx=24, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header, text="⚙ Configurador de URLs",
            font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE
        ).pack(anchor="w")
        tk.Label(
            header, text="Todas las APIs son obligatorias",
            font=FONT_SUBHEAD, bg=BG_HEADER, fg="#BBDEFB"
        ).pack(anchor="w", pady=(4, 0))

        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR, pady=10, padx=24)
        btn_frame.grid(row=1, column=0, sticky="ew")
        tk.Button(
            btn_frame, text="💾 Guardar Cambios", command=self.guardar_todo,
            bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat", bd=0,
            padx=18, pady=7, cursor="hand2", activebackground="#0D47A1",
            activeforeground=FG_WHITE
        ).pack(side="right")
        tk.Button(
            btn_frame, text="✕ Cancelar", command=self.root.destroy,
            bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1,
            padx=16, pady=6, cursor="hand2"
        ).pack(side="right", padx=(0, 8))

        self.container = tk.Frame(self.root, bg=BG_MAIN, padx=28, pady=16)
        self.container.grid(row=2, column=0, sticky="nsew")
        for nombre in self.APIS_BASE:
            self._crear_campo_vertical(nombre)

    def _crear_campo_vertical(self, nombre):
        frame = tk.Frame(self.container, bg=BG_MAIN)
        frame.pack(fill="x", pady=10)

        tk.Label(
            frame, text=nombre, font=FONT_LABEL, bg=BG_MAIN, fg=FG_BLUE_LABEL
        ).pack(anchor="w")
        entry = tk.Entry(
            frame, bg=BG_MAIN, fg="black", font=FONT_MONO, relief="flat", bd=0,
            insertbackground=BG_HEADER, highlightthickness=1,
            highlightcolor=BG_HEADER, highlightbackground=BORDER_COLOR
        )
        entry.pack(fill="x", ipady=7, pady=(3, 0))
        self.entries[nombre] = entry

    def cargar_configuracion(self):
        try:
            registros = conexion.select_api_configs_st50_80_v2()
            if registros and registros != "FAILED":
                dict_db = {}
                for registro in registros:
                    nombre_api = str(registro[2]).strip().upper()
                    valor_url = registro[3]
                    if valor_url is None or str(valor_url).strip().upper() == "NONE":
                        valor_url = ""
                    else:
                        valor_url = str(valor_url).strip()

                    if not valor_url and dict_db.get(nombre_api):
                        continue
                    dict_db[nombre_api] = valor_url

                for nombre, entry in self.entries.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, dict_db.get(nombre, ""))
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def guardar_todo(self):
        if not messagebox.askyesno(
            "Confirmar", "¿Desea guardar todos los cambios?", parent=self.root
        ):
            return

        try:
            registros = conexion.select_api_configs_st50_80_v2()
            if registros == "FAILED":
                messagebox.showerror(
                    "Error", "No se pudo consultar la configuración.", parent=self.root
                )
                return

            apis_en_bd = {str(registro[2]).strip().upper() for registro in registros}
            for nombre, entry in self.entries.items():
                url = entry.get().strip()
                if nombre in apis_en_bd:
                    conexion.update_api_by_name_st50_80_v2(nombre, url)
                else:
                    conexion.insert_api_by_name_st50_80_v2(nombre, url)

            messagebox.showinfo(
                "Éxito", "Configuración de APIs guardada correctamente.", parent=self.root
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar la configuración: {e}", parent=self.root
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioApiConfig(root)
    root.mainloop()
