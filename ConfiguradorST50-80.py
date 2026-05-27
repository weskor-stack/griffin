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
        self.root.title("Configuración")
        self.root.geometry("600x450") 
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
        
        # ACTUALIZADO: Texto del encabezado visual
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

        # Fila 1: MACHINE NAME e ID OPERATOR
        tk.Label(inner, text="MACHINE NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        tk.Label(inner, text="ID OPERATOR", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=1, sticky="w", padx=(15,0))
        
        self.machine_name = tk.Entry(inner, **entry_kwargs)
        self.machine_name.grid(row=1, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.id_operator = tk.Entry(inner, **entry_kwargs)
        self.id_operator.grid(row=1, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # Fila 2: MODEL ID y PROCESS NAME
        tk.Label(inner, text="MODEL ID", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=0, sticky="w")
        tk.Label(inner, text="PROCESS NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=1, sticky="w", padx=(15,0))
        
        self.model_id = tk.Entry(inner, **entry_kwargs)
        self.model_id.grid(row=3, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.process_name = tk.Entry(inner, **entry_kwargs)
        self.process_name.grid(row=3, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # Fila 3: COMPONENT
        tk.Label(inner, text="COMPONENT", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=4, column=0, sticky="w")
        
        self.component = tk.Entry(inner, **entry_kwargs)
        self.component.grid(row=5, column=0, sticky="ew", ipady=5, pady=(2, 15))

        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8), bg=BG_MAIN, fg="#888888")
        status_bar.pack(side="bottom", anchor="w", padx=24, pady=5)

    def cargar(self):
        try:
            # Apunta a la función renombrada con guion bajo
            datos = conexion.configuradorst50_80() 
            
            if datos and datos != "FAILED":
                def insertar_seguro(entry_widget, valor):
                    if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, str(valor).strip())

                if len(datos) >= 5:
                    insertar_seguro(self.machine_name, datos[0]) 
                    insertar_seguro(self.id_operator, datos[1])  
                    insertar_seguro(self.model_id, datos[2])     
                    insertar_seguro(self.process_name, datos[3])  
                    insertar_seguro(self.component, datos[4])     
                        
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")
    
    def guardar(self):
        mach = self.machine_name.get().strip()
        ope  = self.id_operator.get().strip()
        mod  = self.model_id.get().strip()
        proc = self.process_name.get().strip()
        comp = self.component.get().strip()
 
        try:
            # Apunta a la función renombrada con guion bajo
            exito = conexion.update_configuratorst50_80(mach, ope, mod, proc, comp)
            
            if exito:
                messagebox.showinfo("Éxito", "Configuración guardada correctamente.", parent=self.root)
                self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("Error DB", str(e), parent=self.root)

    def cancelar(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()