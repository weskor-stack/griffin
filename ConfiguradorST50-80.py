import os
import glob 
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
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
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración de APIs")
        self.root.geometry("700x370") 
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
        
        tk.Label(header, text="⚙ Configurador de URLs para APIs", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))
        safe_insert = "Todas las APIs son obligatorias."
        tk.Label(header, text=safe_insert, font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))
        
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

        # Fila 0 y 1: UNITS e INTERLOCKING
        tk.Label(inner, text="UNITS", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        tk.Label(inner, text="INTERLOCKING", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=1, sticky="w", padx=(15,0))
        
        self.units = tk.Entry(inner, **entry_kwargs)
        self.units.grid(row=1, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.interlocking = tk.Entry(inner, **entry_kwargs)
        self.interlocking.grid(row=1, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # Fila 2 y 3: TRACEABILITY (Ancho completo)
        tk.Label(inner, text="TRACEABILITY", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=0, sticky="w")
        
        self.traceability = tk.Entry(inner, **entry_kwargs)
        self.traceability.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=5, pady=(2, 15))

        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8), bg=BG_MAIN, fg="#888888")
        status_bar.pack(side="bottom", anchor="w", padx=24, pady=5)

    def cargar(self):
        try:
            # Llamamos a select_api_configs() para traer las filas de url_data
            registros = conexion.select_api_configs() 
            
            if registros and registros != "FAILED":
                # Creamos un diccionario { 'NAME': 'url' } para buscar de forma segura por texto exacto
                dict_urls = {str(r[2]).strip().upper(): r[3] for r in registros}

                # Insertamos la URL correspondiente buscando por la clave exacta de tu BD
                self.units.delete(0, tk.END)
                self.units.insert(0, dict_urls.get("UNITS", ""))

                self.interlocking.delete(0, tk.END)
                self.interlocking.insert(0, dict_urls.get("INTERLOCKING", ""))

                self.traceability.delete(0, tk.END)
                self.traceability.insert(0, dict_urls.get("TRACEABILITY", ""))
                    
        except Exception as e:
            print(f"Error interno al cargar datos de APIs: {e}")
    
    def guardar(self):
        try:
            # Mandamos la actualización de forma independiente para cada nombre de API
            conexion.update_api_by_name("UNITS", self.units.get().strip())
            conexion.update_api_by_name("INTERLOCKING", self.interlocking.get().strip())
            conexion.update_api_by_name("TRACEABILITY", self.traceability.get().strip())
            
            messagebox.showinfo("Éxito", "Configuración de APIs guardada correctamente.", parent=self.root)
            self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("Error DB", f"No se pudo guardar: {e}", parent=self.root)

    def cancelar(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()