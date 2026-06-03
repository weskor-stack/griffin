import tkinter as tk
from tkinter import ttk, messagebox
import conexion

# --- COLORES Y FUENTES DE LA ESTÉTICA ---
BG_HEADER      = "#1565C0"
BG_BUTTON_BAR  = "#F3F3F3"
BG_MAIN        = "#FFFFFF"
FG_WHITE       = "#FFFFFF"
FG_BLUE_LABEL  = "#00479E"
BORDER_COLOR   = "#000000"
FONT_HEAD      = ("Segoe UI", 18, "bold")
FONT_SUBHEAD   = ("Segoe UI", 10)
FONT_LABEL     = ("Segoe UI", 8, "bold")
FONT_MONO      = ("Consolas", 10)
FONT_BTN       = ("Segoe UI", 9, "bold")


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
    """Configurador de items para ST40 - 9 campos (Tabla 2.2 del PDF TLA_E34_ST40)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Configuración - ST40")
        self.root.geometry("640x620")
        self.root.configure(bg=BG_MAIN)
        self.root.focus_force()
        self.root.attributes("-topmost", False)

        apply_theme()
        self._build_ui()
        self.cargar()

    def _build_ui(self):
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass

        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")

        tk.Label(header, text="⚙ Configurador - ST40", font=FONT_HEAD,
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))

        self.subtitle_var = tk.StringVar(value="Todos los campos son obligatorios (Tabla 2.2).")
        tk.Label(header, textvariable=self.subtitle_var, font=FONT_SUBHEAD,
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="💾 Guardar Cambios", command=self.guardar,
                  bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat",
                  cursor="hand2", padx=15, pady=6).pack(side="right", padx=(10, 24), pady=10)

        tk.Button(btn_frame, text="✕ Cancelar", command=self.cancelar,
                  bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1,
                  cursor="hand2", padx=15, pady=5).pack(side="right", pady=10)

        inner = tk.Frame(self.root, bg=BG_MAIN)
        inner.pack(fill="both", expand=True, padx=24, pady=20)
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        entry_kwargs = {"bg": BG_MAIN, "fg": "black", "relief": "flat", "font": FONT_MONO,
                        "highlightthickness": 1, "highlightbackground": BORDER_COLOR,
                        "highlightcolor": BG_HEADER}

        # Campos en el orden de la Tabla 2.2. (label, atributo). PASSWORD se muestra visible.
        self.campos = [
            ("MACHINE NAME",  "machine_name"),
            ("CLIENT ID",     "client_id"),
            ("ID OPERATOR",   "id_operator"),
            ("PASSWORD",      "password"),
            ("MODEL ID",      "model_id"),
            ("PROCESS NAME",  "process_name"),
            ("PRINT MACRO",   "print_macro"),
            ("LOCATION",      "location"),
            ("SHOP FLOOR ID", "shop_flor"),
        ]

        self.entries = {}
        # Acomodo en rejilla de 2 columnas: cada par ocupa fila de label + fila de entry.
        for idx, (label, attr) in enumerate(self.campos):
            col = idx % 2
            fila_label = (idx // 2) * 2
            fila_entry = fila_label + 1
            padx_l = (15, 0) if col == 1 else (0, 0)

            tk.Label(inner, text=label, bg=BG_MAIN, fg=FG_BLUE_LABEL,
                     font=FONT_LABEL).grid(row=fila_label, column=col, sticky="w", padx=padx_l)

            entry = tk.Entry(inner, **entry_kwargs)
            entry.grid(row=fila_entry, column=col, sticky="ew", padx=padx_l, ipady=5, pady=(2, 15))
            self.entries[attr] = entry

        self.status_var = tk.StringVar(value="Listo")
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8),
                 bg=BG_MAIN, fg="#888888").pack(side="bottom", anchor="w", padx=24, pady=5)

    def cargar(self):
        """Precarga los 9 valores desde configurador_st40().
           Orden: machine_id, client_id, operator, password, model_id,
                  process_name, print_macro, location, shop_flor"""
        try:
            datos = conexion.configurador_st40()
            if datos and datos != "FAILED":
                orden = ["machine_name", "client_id", "id_operator", "password",
                         "model_id", "process_name", "print_macro", "location", "shop_flor"]
                for i, attr in enumerate(orden):
                    if i < len(datos):
                        valor = datos[i]
                        if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                            e = self.entries[attr]
                            e.delete(0, tk.END)
                            e.insert(0, str(valor).strip())
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")

    def guardar(self):
        v = {attr: self.entries[attr].get().strip() for attr in self.entries}
        try:
            datos_actuales = conexion.configurador_st40()
            vacio = (datos_actuales == "FAILED"
                     or datos_actuales == ("", "", "", "", "", "", "", "", ""))

            args = (v["machine_name"], v["client_id"], v["id_operator"], v["password"],
                    v["model_id"], v["process_name"], v["print_macro"], v["location"], v["shop_flor"])

            if vacio:
                exito = conexion.insert_configurador_st40(*args)
                mensaje = "Configuración inicial ST40 creada con éxito."
            else:
                exito = conexion.update_configurador_st40(*args)
                mensaje = "Configuración ST40 actualizada correctamente."

            if exito:
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
