import os
import glob 
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import conexion
import shopo_order_api

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
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración")
        self.root.geometry("600x300") 
        self.root.configure(bg=BG_MAIN) 
        self.root.attributes("-topmost", True)  
        self.root.focus_force()  
        
        self.root.grab_set() 

        try:
            ruta_icono = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
            self.root.after(200, lambda: self.root.iconbitmap(ruta_icono))
        except Exception as e:
            print(f"⚠️ Aviso: No se pudo cargar el favicon en el configurador. Error: {e}")

        apply_theme()
        self._build_ui()
        self.cargar()

    def _build_ui(self):
        try: self.root.iconbitmap("favicon.ico")
        except: pass
        
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        
        tk.Label(header, text="⚙ Configurador", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))
        
        self.subtitle_var = tk.StringVar(value="Todos los campos son obligatorios.")
        tk.Label(header, textvariable=self.subtitle_var, font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")
        
        btn_guardar = tk.Button(btn_frame, text="💾 Guardar Cambios", command=self.guardar, bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat", cursor="hand2", padx=15, pady=6)
        btn_guardar.pack(side="right", padx=(10, 24), pady=10)
        
        btn_cancelar = tk.Button(btn_frame, text="✕ Cancelar", command=self.cancelar, bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1, cursor="hand2", padx=15, pady=5)
        btn_cancelar.pack(side="right", pady=10)

        inner = tk.Frame(self.root, bg=BG_MAIN)
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        entry_kwargs = {"bg": BG_MAIN, "fg": "black", "relief": "flat", "font": FONT_MONO, 
                        "highlightthickness": 1, "highlightbackground": BORDER_COLOR, "highlightcolor": BG_HEADER}

        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        tk.Label(inner, text="SHOP ORDER", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        tk.Label(inner, text="QUANTITY", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=1, sticky="w", padx=(15,0))
        
        self.shop_order = tk.Entry(inner, **entry_kwargs)
        self.shop_order.grid(row=1, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        def validate_numbers(P):
            return P.isdigit() or P == ""

        vcmd_qty = (self.root.register(validate_numbers), '%P')
        
        self.quantity = tk.Entry(inner, validate="key", validatecommand=vcmd_qty, **entry_kwargs)
        self.quantity.grid(row=1, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

    def cargar(self):
        try:
            datos = conexion.configurador_shop_order_st40() 
            
            if datos and datos != "FAILED":
                def insertar_seguro(entry_widget, valor):
                    if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                        entry_widget.insert(0, str(valor).strip())

                if len(datos) >= 2:
                    insertar_seguro(self.shop_order, datos[0])
                    insertar_seguro(self.quantity, datos[1])
                        
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")
    
    def guardar(self):
        shop = self.shop_order.get().strip()
        qty = self.quantity.get().strip()

        # print("\n" + "="*40)
        # print("INICIANDO PROCESO DE GUARDADO")
        # print(f"Datos capturados -> Shop Order: '{shop}' | Qty: '{qty}'")

        if not shop or not qty:
            print("⚠️ Error: Campos incompletos.")
            messagebox.showwarning("Campos incompletos", "Por favor, llena todos los campos obligatorios.", parent=self.root)
            return

        try:
            #print("Obteniendo conexión a la base de datos...")
            conn = conexion.get_connection()
            
            url_api = ""
            url_api = conexion.obtener_url_api()

            #print("💾 Guardando en la tabla configurador...")
            exito_db = conexion.update_configurador_shop_order_st40(shop, qty, conn)
            #print(f"✅ Resultado de guardado en BD: {exito_db}")
            
            if exito_db:
                #print("📡 Llamando al archivo shopo_order_api...")
                exito_api, nombre_archivo, total_regs = shopo_order_api.consultar_api_y_guardar(url_api[0][0], shop, qty)
                
                #print(f"📊 Respuesta API -> Éxito: {exito_api} | Archivo: {nombre_archivo} | Registros: {total_regs}")
                
                if exito_api:
                    messagebox.showinfo(
                        "Éxito", 
                        f"Configuración guardada en DB.\n\nArchivo generado correctamente:\n📄 {nombre_archivo}\n📊 Registros: {total_regs}", 
                        parent=self.root
                    )
                    self.root.destroy()
                else:
                    #print("⚠️ La API falló. Revisar los prints del archivo shopo_order_api.py")
                    messagebox.showwarning(
                        "Advertencia", 
                        "La configuración se guardó en la base de datos, pero falló la conexión con la API o la generación del archivo. Revisa la consola para más detalles.", 
                        parent=self.root
                    )
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN FATAL ATRAPADA: {e}")
            messagebox.showerror("Error del Sistema", str(e), parent=self.root)

    def cancelar(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()