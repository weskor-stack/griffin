import os
import glob 
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import conexion
import shopo_order_api  # Importación de tu script de la API

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
    style.map("Light.TCombobox", 
              fieldbackground=[("readonly", BG_MAIN)], 
              foreground=[("readonly", "black")], 
              bordercolor=[("focus", BG_HEADER), ("!focus", BORDER_COLOR)])

class ConfiguradorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración")
        self.root.geometry("600x550") # <- Aumentamos un poquito la altura
        self.root.configure(bg=BG_MAIN)
        apply_theme()
        self._build_ui()
        
        # ACTUALIZAMOS LOS NOMBRES DEL COMBOBOX
        self.station["values"] = ["ST10_LASER", "ST20_PRESSFIT", "ST30_HEATSTACKING"]
        
        # Cargar los datos desde la BD inmediatamente al abrir
        self.cargar()

    def _build_ui(self):
        try: self.root.iconbitmap("favicon.ico")
        except: pass
        
        # --- HEADER (Banda azul) ---
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        
        tk.Label(header, text="⚙ Configurador", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))
        
        self.subtitle_var = tk.StringVar(value="Estación activa: Ninguna — Todos los campos son obligatorios.")
        tk.Label(header, textvariable=self.subtitle_var, font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        # --- BARRA DE BOTONES (Banda gris) ---
        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")
        
        btn_guardar = tk.Button(btn_frame, text="💾 Guardar Todas", command=self.guardar, bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat", cursor="hand2", padx=15, pady=6)
        btn_guardar.pack(side="right", padx=(10, 24), pady=10)
        
        btn_limpiar = tk.Button(btn_frame, text="✕ Cancelar", command=self.limpiar, bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1, cursor="hand2", padx=15, pady=5)
        btn_limpiar.pack(side="right", pady=10)

        # --- PANEL PRINCIPAL (Formulario) ---
        inner = tk.Frame(self.root, bg=BG_MAIN)
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        entry_kwargs = {"bg": BG_MAIN, "fg": "black", "relief": "flat", "font": FONT_MONO, 
                        "highlightthickness": 1, "highlightbackground": BORDER_COLOR, "highlightcolor": BG_HEADER}

        # STATION
        tk.Label(inner, text="STATION", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        self.station = ttk.Combobox(inner, style="Light.TCombobox", state="readonly")
        self.station.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 15))
        self.station.bind("<<ComboboxSelected>>", self._on_station_change)

        # SHOP ORDER 
        self.lbl_shop = tk.Label(inner, text="SHOP ORDER", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL)
        self.shop_order = tk.Entry(inner, **entry_kwargs)
        
        # PRODUCTS 
        self.lbl_products = tk.Label(inner, text="PRODUCTS", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL)
        self.products = tk.Entry(inner, **entry_kwargs)

        # MACHINE / OPERATOR (Recorridos a las filas 6 y 7 para dar espacio)
        tk.Label(inner, text="MACHINE NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=6, column=0, sticky="w")
        tk.Label(inner, text="ID OPERATOR", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=6, column=1, sticky="w", padx=(15,0))
        
        self.machine = tk.Entry(inner, **entry_kwargs)
        self.machine.grid(row=7, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.operator = tk.Entry(inner, **entry_kwargs)
        self.operator.grid(row=7, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # PROCESS NAME (Recorrido a las filas 8 y 9)
        tk.Label(inner, text="PROCESS NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=8, column=0, sticky="w")
        self.process = tk.Entry(inner, **entry_kwargs)
        self.process.grid(row=9, column=0, columnspan=2, sticky="ew", ipady=5, pady=(2, 15))

        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8), bg=BG_MAIN, fg="#888888")
        status_bar.pack(side="bottom", anchor="w", padx=24, pady=5)

    def _on_station_change(self, event=None):
        seleccion = self.station.get().strip().upper()
        self.subtitle_var.set(f"Estación activa: {seleccion} — Todos los campos son obligatorios.")

        self.lbl_shop.grid_forget()
        self.shop_order.grid_forget()
        self.lbl_products.grid_forget()
        self.products.grid_forget()

        if "ST10" in seleccion:
            self.lbl_shop.grid(row=2, column=0, sticky="w")
            self.shop_order.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 15), ipady=5)
            
            self.lbl_products.grid(row=4, column=0, sticky="w")
            self.products.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(2, 15), ipady=5)
            
        elif "ST20" in seleccion or "ST30" in seleccion:
            self.lbl_products.grid(row=2, column=0, sticky="w")
            self.products.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 15), ipady=5)

    def cargar(self):
        """Carga TODOS los datos de la base de datos de forma segura."""
        try:
            datos = conexion.obtener_datos_fila_unica()
            if datos:
                longitud = len(datos)
                
                if longitud > 0 and datos[0]:
                    val = str(datos[0]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.machine.insert(0, val)
                
                if longitud > 1 and datos[1]:
                    val = str(datos[1]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.process.insert(0, val)
                
                if longitud > 2 and datos[2]:
                    val = str(datos[2]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.operator.insert(0, val)
                
                if longitud > 3 and datos[3]:
                    val = str(datos[3]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.station.set(val)
                        self._on_station_change(None) 
                
                if longitud > 4 and datos[4]:
                    val = str(datos[4]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.products.insert(0, val)
                
                if longitud > 5 and datos[5]:
                    val = str(datos[5]).strip()
                    if val not in ["(NULL)", "None", ""]:
                        self.shop_order.insert(0, val)
                        
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")

    def guardar(self):
        m = self.machine.get().strip()
        p = self.process.get().strip()
        o = self.operator.get().strip()
        s = self.station.get().strip() 
        shop = self.shop_order.get().strip()
        prod = self.products.get().strip()

        if not all([m, p, o, s]):
            messagebox.showwarning("Error", "Faltan campos obligatorios.")
            return

        # VALIDACIÓN ACTUALIZADA CON LOS NUEVOS NOMBRES
        if s == "ST10_LASER":
            if not shop:
                messagebox.showwarning("Error", "Shop Order es requerido para ST10_LASER.")
                return
            if not prod:
                messagebox.showwarning("Error", "Product es requerido para ST10_LASER.")
                return
            
            try:
                url_base = conexion.obtener_url_api()
                if not url_base:
                    messagebox.showerror("Error", "No se encontró la URL en la base de datos (tabla url_data).")
                    return
                
                exito, nombre, cantidad = shopo_order_api.consultar_api_y_guardar(api_url=url_base, shop_order=shop)
                
                if not exito or nombre is None or cantidad == 0:
                    messagebox.showerror("Error API", "Revisar contenido de API (resultado nulo o vacío).")
                    return # Detenemos el proceso de guardado
                    
            except Exception as e:
                messagebox.showerror("Error API", f"Error al ejecutar la API: {str(e)}")
                return
                
        elif s in ["ST20_PRESSFIT", "ST30_HEATSTACKING"]:
            if not prod:
                messagebox.showwarning("Error", "Product es requerido para esta estación.")
                return
            shop = ""

        try:
            conexion.insert_configurador(m, p, o, s, prod, shop)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error DB", str(e))

    def limpiar(self):
        for w in (self.machine, self.operator, self.process, self.shop_order, self.products):
            w.delete(0, tk.END)
        self.station.set("")
        self.lbl_shop.grid_forget()
        self.shop_order.grid_forget()
        self.lbl_products.grid_forget()
        self.products.grid_forget()
        self.subtitle_var.set("Estación activa: Ninguna — Todos los campos son obligatorios.")
        self.status_var.set("Campos limpiados")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()