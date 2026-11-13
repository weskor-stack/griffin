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
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Light.TCombobox", 
                    fieldbackground=BG_MAIN, 
                    background=BG_MAIN, 
                    foreground="black", 
                    selectbackground="#E0E0E0", 
                    selectforeground="black",
                    bordercolor=BORDER_COLOR, 
                    arrowcolor="black", 
                    relief="flat", 
                    padding=5)

class ConfiguradorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración")
        self.root.geometry("640x575")
        self.root.minsize(580, 575)
        self.root.configure(bg=BG_MAIN)
        self.root.focus_force()
        self.root.attributes("-topmost", False)

        apply_theme()
        self._build_ui()
        self.cargar()

    def _build_ui(self):
        try: self.root.iconbitmap("favicon.ico")
        except: pass

        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="⚙ Configurador", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE
        ).pack(anchor="w", padx=24, pady=(20, 5))
        self.subtitle_var = tk.StringVar(value="Todos los campos son obligatorios.")
        tk.Label(
            header, textvariable=self.subtitle_var, font=FONT_SUBHEAD,
            bg=BG_HEADER, fg=FG_WHITE
        ).pack(anchor="w", padx=24, pady=(0, 20))

        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")
        tk.Button(
            btn_frame, text="💾 Guardar Cambios", command=self.guardar,
            bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat",
            cursor="hand2", padx=15, pady=6
        ).pack(side="right", padx=(10, 24), pady=10)
        tk.Button(
            btn_frame, text="✕ Cancelar", command=self.cancelar,
            bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1,
            cursor="hand2", padx=15, pady=5
        ).pack(side="right", pady=10)

        inner = tk.Frame(self.root, bg=BG_MAIN)
        inner.pack(fill="both", expand=True, padx=24, pady=20)
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        campos = (
            ("machine_id", "MACHINE NAME"),
            ("client_id", "CLIENT ID"),
            ("operator", "OPERATTOR ID"),
            ("password", "PASSWORD"),
            ("program_name_version", "PROGRAM NAME VERSION"),
            ("process_name", "PROCESS NAME"),
            ("station", "DISPENSING PROCESS"),
            ("product", "DEFECT CODE"),
            ("shop_order", "MINUTE DURATION"),
            ("location", "MOVE TO LOCATION"),
            ("shop_flor", "PCB PROCESS"),
        )
        self.entries = {}
        for indice, (columna_db, etiqueta) in enumerate(campos):
            fila, columna = divmod(indice, 2)
            padx = (15, 0) if columna else 0
            tk.Label(
                inner, text=etiqueta, bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL
            ).grid(row=fila * 2, column=columna, sticky="w", padx=padx)
            entry = tk.Entry(
                inner, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO,
                highlightthickness=1, highlightbackground=BORDER_COLOR,
            )
            entry.grid(
                row=fila * 2 + 1, column=columna, sticky="ew",
                padx=padx, ipady=5, pady=(2, 10)
            )
            self.entries[columna_db] = entry

        self.status_var = tk.StringVar(value="Listo")
        tk.Label(
            self.root, textvariable=self.status_var, font=("Segoe UI", 8),
            bg=BG_MAIN, fg="#888888"
        ).pack(side="bottom", anchor="w", padx=24, pady=5)

    def cargar(self):
        try:
            datos = conexion.configuradorst50_v2()
            if datos and datos != "FAILED":
                for entry, valor in zip(self.entries.values(), datos):
                    if valor is not None and str(valor).strip() not in ["(NULL)", "None", ""]:
                        entry.delete(0, tk.END)
                        entry.insert(0, str(valor).strip())
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")

    def guardar(self):
        valores = tuple(entry.get().strip() for entry in self.entries.values())

        try:
            datos_actuales = conexion.configuradorst50_v2()
            if datos_actuales == "FAILED":
                messagebox.showerror(
                    "Error DB", "No se pudo consultar la configuración.", parent=self.root
                )
                return

            if datos_actuales is None:
                exito = conexion.insert_configuratorst50_v2(*valores)
                mensaje = "Configuración inicial creada con éxito."
            else:
                exito = conexion.update_configuratorst50_v2(*valores)
                mensaje = "Configuración actualizada correctamente."

            if exito is not True:
                messagebox.showerror(
                    "Error DB",
                    "La función de guardado no confirmó la operación.",
                    parent=self.root
                )
                return

            messagebox.showinfo("Éxito", mensaje, parent=self.root)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error DB", str(e), parent=self.root)

    def cancelar(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()
