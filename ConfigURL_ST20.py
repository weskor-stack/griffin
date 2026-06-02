import tkinter as tk
from tkinter import ttk, messagebox
import conexion
import importlib
importlib.reload(conexion)

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


class FormularioApiConfig:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración de URLs - ST20")
        self.root.geometry("600x620")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        self.root.focus_force()
        self.root.attributes("-topmost", False)
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass

        # ST20 invoca 5 APIs. Orden segun el flujo de secuencia del PDF TLA_E34_ST20
        # (correccion solicitada por Edgar: CONDUIT antes de TRACEABILITY):
        #   Seq 3 PARENTAGE -> Seq 4 UNIT -> Seq 5 INTERLOCKING -> Seq 6 CONDUIT -> Seq 7 TRACEABILITY
        # Los nombres deben coincidir EXACTAMENTE con la columna 'name' de url_data.
        self.APIS_BASE = [
            "PARENTAGE",
            "UNIT",
            "INTERLOCKING",
            "CONDUIT",
            "TRACEABILITY",
        ]

        self.entries = {}
        apply_theme()
        self._setup_ui()
        self.cargar_configuracion()

    def _setup_ui(self):
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        header = tk.Frame(self.root, bg=BG_HEADER, padx=24, pady=18)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(header, text="⚙ Configurador de URLs - ST20",
                 font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w")

        tk.Label(header, text="Todas las APIs son obligatorias (orden de secuencia)",
                 font=FONT_SUBHEAD, bg=BG_HEADER, fg="#BBDEFB").pack(anchor="w", pady=(4, 0))

        # --- BOTONES ---
        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR, pady=10, padx=24)
        btn_frame.grid(row=1, column=0, sticky="ew")

        tk.Button(btn_frame, text="💾 Guardar Cambios",
                  command=self.guardar_todo,
                  bg=BG_HEADER, fg=FG_WHITE,
                  font=FONT_BTN,
                  relief="flat", bd=0,
                  padx=18, pady=7,
                  cursor="hand2",
                  activebackground="#0D47A1",
                  activeforeground=FG_WHITE).pack(side="right")

        tk.Button(btn_frame, text="✕ Cancelar",
                  command=self.root.destroy,
                  bg=BG_MAIN, fg="black",
                  font=FONT_BTN,
                  relief="solid", bd=1,
                  padx=16, pady=6,
                  cursor="hand2").pack(side="right", padx=(0, 8))

        # --- CONTENEDOR ---
        self.container = tk.Frame(self.root, bg=BG_MAIN, padx=28, pady=16)
        self.container.grid(row=2, column=0, sticky="nsew")

        for nombre in self.APIS_BASE:
            self._crear_campo_vertical(nombre)

    def _crear_campo_vertical(self, nombre):
        """Crea un campo ocupando todo el ancho disponible en una fila nueva."""
        frame = tk.Frame(self.container, bg=BG_MAIN)
        frame.pack(fill="x", pady=10)

        tk.Label(frame, text=nombre,
                 font=FONT_LABEL,
                 bg=BG_MAIN, fg=FG_BLUE_LABEL).pack(anchor="w")

        entry = tk.Entry(frame,
                         bg=BG_MAIN, fg="black",
                         font=FONT_MONO,
                         relief="flat", bd=0,
                         insertbackground=BG_HEADER,
                         highlightthickness=1,
                         highlightcolor=BG_HEADER,
                         highlightbackground=BORDER_COLOR)
        entry.pack(fill="x", ipady=7, pady=(3, 0))

        self.entries[nombre] = entry

    def cargar_configuracion(self):
        """Lee url_data y precarga el valor de cada API de ST20.
           Columnas de select_api_configs(): [0]id [1]tc_id [2]name [3]url_data ..."""
        try:
            registros = conexion.select_api_configs()  # SELECT * FROM url_data

            if registros and registros != "FAILED":
                dict_db = {}
                for r in registros:
                    nombre_api = str(r[2]).strip().upper()
                    valor_url = r[3]

                    if valor_url is None or str(valor_url).strip().upper() == "NONE":
                        valor_url = ""
                    else:
                        valor_url = str(valor_url).strip()

                    # Si ya hay un valor cargado y el nuevo viene vacío, no lo pisa
                    if nombre_api in dict_db and dict_db[nombre_api] != "" and valor_url == "":
                        continue

                    dict_db[nombre_api] = valor_url

                for nombre in self.APIS_BASE:
                    nombre_limpio = nombre.strip().upper()
                    if nombre in self.entries:
                        entry = self.entries[nombre]
                        url = dict_db.get(nombre_limpio, "")
                        entry.delete(0, tk.END)
                        entry.insert(0, url)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def guardar_todo(self):
        if not messagebox.askyesno("Confirmar", "¿Desea guardar todos los cambios?"):
            return
        try:
            registros_existentes = conexion.select_api_configs()

            apis_en_bd = set()
            if registros_existentes and registros_existentes != "FAILED":
                for r in registros_existentes:
                    apis_en_bd.add(str(r[2]).strip().upper())

            for nombre, entry in self.entries.items():
                nombre_api = nombre.upper()
                url = entry.get().strip()

                if nombre_api not in apis_en_bd:
                    # insert_api_by_name_st50_80 es genérico sobre url_data (INSERT name, url_data)
                    conexion.insert_api_by_name_st50_80(nombre_api, url)
                else:
                    conexion.update_api_by_name(nombre_api, url)

            messagebox.showinfo("Éxito", "Configuración de APIs guardada correctamente.", parent=self.root)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioApiConfig(root)
    root.mainloop()
