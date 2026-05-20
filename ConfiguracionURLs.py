import tkinter as tk
from tkinter import messagebox
import conexion
import importlib
importlib.reload(conexion)

class FormularioApiConfig:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración de URLs APIs")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass

        # Nombres exactos como están en la columna 'name' de url_data
        self.APIS_BASE = [
            "INTERLOCKING",
            "TRACEABILITY",
        ]
        self.API_SHOP_ORDER = "SHOP ORDER"

        self.entries = {}
        self.station = self._leer_estacion()
        print(f"DEBUG estación: '{self.station}'")
        self._setup_ui()
        self.cargar_configuracion()

    def _leer_estacion(self):
        try:
            resultado = conexion.get_station()
            if resultado:
                return str(resultado).strip().upper()
        except Exception as e:
            print(f"Error al leer estación: {e}")
        return ""

    def _apis_para_estacion(self):
        """Devuelve la lista de nombres de API según la estación activa."""
        if self.station.startswith("ST10"):
            return [self.API_SHOP_ORDER] + self.APIS_BASE
        else:
            return self.APIS_BASE

    def _setup_ui(self):
        apis = self._apis_para_estacion()
        altura = 180 + (len(apis) * 72)
        self.root.geometry(f"650x{altura}")

        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        header = tk.Frame(self.root, bg="#1565C0", padx=24, pady=18)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(header, text="Configuración de URLs APIs",
                 font=("Segoe UI", 16, "bold"),
                 bg="#1565C0", fg="#FFFFFF").pack(anchor="w")

        estacion_label = self.station if self.station else "Sin estación"
        tk.Label(header, text=f"Estación activa: {estacion_label}  —  Todas las APIs son obligatorias.",
                 font=("Segoe UI", 9), bg="#1565C0", fg="#BBDEFB").pack(anchor="w", pady=(4, 0))

        # --- BOTONES ---
        btn_frame = tk.Frame(self.root, bg="#F0F0F0", pady=10, padx=24)
        btn_frame.grid(row=1, column=0, sticky="ew")

        tk.Button(btn_frame, text="💾  Guardar Todas",
                  command=self.guardar_todo,
                  bg="#1565C0", fg="#FFFFFF",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", bd=0,
                  padx=18, pady=7,
                  cursor="hand2",
                  activebackground="#0D47A1",
                  activeforeground="#FFFFFF").pack(side="right")

        tk.Button(btn_frame, text="✕  Cancelar",
                  command=self.root.destroy,
                  bg="#FFFFFF", fg="#555555",
                  font=("Segoe UI", 9),
                  relief="solid", bd=1,
                  padx=16, pady=6,
                  cursor="hand2").pack(side="right", padx=(0, 8))

        self.container = tk.Frame(self.root, bg="#FFFFFF", padx=28, pady=16)
        self.container.grid(row=2, column=0, sticky="nsew")

        for nombre in apis:
            self._crear_campo_url(nombre)

    def _crear_campo_url(self, nombre):
        frame = tk.Frame(self.container, bg="#FFFFFF")
        frame.pack(fill="x", pady=8)

        tk.Label(frame, text=nombre,
                 font=("Segoe UI", 8, "bold"),
                 bg="#FFFFFF", fg="#1565C0").pack(anchor="w")

        entry = tk.Entry(frame,
                         bg="#F8FBFF", fg="#222222",
                         font=("Consolas", 10),
                         relief="solid", bd=1,
                         insertbackground="#1565C0",
                         highlightthickness=1,
                         highlightcolor="#1565C0",
                         highlightbackground="#CCCCCC")
        entry.pack(fill="x", ipady=7, pady=(3, 0))

        entry.bind("<FocusIn>",  lambda e, w=entry: w.config(highlightbackground="#1565C0"))
        entry.bind("<FocusOut>", lambda e, w=entry: w.config(highlightbackground="#CCCCCC"))

        self.entries[nombre] = entry

    def cargar_configuracion(self):
        """
        Lee url_data completa y filtra solo las APIs que corresponden
        a la estación activa. Columnas: [0]id [1]tc_id [2]name [3]url_data ...
        """
        try:
            registros = conexion.select_api_configs()  # SELECT * FROM url_data
            # Construir dict {name: url_data} con lo que vino de la DB
            dict_db = {str(r[2]).strip(): r[3] for r in registros}

            apis_visibles = self._apis_para_estacion()

            for nombre in apis_visibles:
                entry = self.entries[nombre]
                url = dict_db.get(nombre, "")
                entry.delete(0, tk.END)
                entry.insert(0, url)

        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def guardar_todo(self):
        if not messagebox.askyesno("Confirmar", "¿Desea guardar todos los cambios?"):
            return
        try:
            for nombre, entry in self.entries.items():
                url = entry.get().strip()
                if url:
                    conexion.update_api_by_name(nombre, url)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioApiConfig(root)
    root.mainloop()