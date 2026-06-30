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
        self.root.geometry("600x480") 
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

        # MACHINE NAME
        tk.Label(inner, text="MACHINE NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        self.machine_name = tk.Entry(inner, **entry_kwargs)
        self.machine_name.grid(row=1, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        # ID OPERATOR
        tk.Label(inner, text="ID OPERATOR", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=1, sticky="w", padx=(15,0))
        self.id_operator = tk.Entry(inner, **entry_kwargs)
        self.id_operator.grid(row=1, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # PROGRAM NAME + VERSION (reemplaza MODEL ID)
        tk.Label(inner, text="PROGRAM NAME + VERSION", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=0, sticky="w")
        self.program_name_version = tk.Entry(inner, **entry_kwargs)
        self.program_name_version.grid(row=3, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        # PROCESS NAME
        tk.Label(inner, text="PROCESS NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=1, sticky="w", padx=(15,0))
        self.process_name = tk.Entry(inner, **entry_kwargs)
        self.process_name.grid(row=3, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        # COMPONENT - Radio Button
        tk.Label(inner, text="COMPONENT", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=4, column=0, sticky="w")
        
        # Frame para los radio buttons
        radio_frame = tk.Frame(inner, bg=BG_MAIN)
        radio_frame.grid(row=5, column=0, sticky="w", pady=(2, 15))
        
        # Variable para el radio button (default = "NO")
        self.component_var = tk.StringVar(value="NO")
        
        # Radio buttons
        self.radio_yes = tk.Radiobutton(radio_frame, text="YES", variable=self.component_var, 
                                       value="YES", bg=BG_MAIN, font=FONT_LABEL)
        self.radio_yes.pack(side="left", padx=(0, 10))
        
        self.radio_no = tk.Radiobutton(radio_frame, text="NO", variable=self.component_var, 
                                      value="NO", bg=BG_MAIN, font=FONT_LABEL)
        self.radio_no.pack(side="left")

        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8), bg=BG_MAIN, fg="#888888")
        status_bar.pack(side="bottom", anchor="w", padx=24, pady=5)

    def cargar(self):
        try:
            datos = conexion.configuradorst80() 
            
            if datos and datos != "FAILED":
                def insertar_seguro(entry_widget, valor):
                    if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, str(valor).strip())

                if len(datos) >= 5:
                    # MACHINE NAME (índice 0)
                    insertar_seguro(self.machine_name, datos[0])
                    # ID OPERATOR (índice 1)
                    insertar_seguro(self.id_operator, datos[1])
                    # PROGRAM NAME + VERSION (índice 2) - antes era model_id
                    insertar_seguro(self.program_name_version, datos[2])
                    # PROCESS NAME (índice 3)
                    insertar_seguro(self.process_name, datos[3])
                    # COMPONENT (índice 4) - qty_components
                    # Convertir el valor a YES/NO para el radio button
                    valor_component = datos[4]
                    # Si el valor es 1, True, "YES", "1", etc. -> seleccionar YES
                    if valor_component in [1, "1", "YES", "yes", "Yes", True]:
                        self.component_var.set("YES")
                    else:
                        self.component_var.set("NO")
                    
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")
    
    def guardar(self):
        mach = self.machine_name.get().strip()
        ope  = self.id_operator.get().strip()
        prog = self.program_name_version.get().strip()
        proc = self.process_name.get().strip()
        
        # Convertir selección del radio button a 1 (YES) o 0 (NO)
        comp_value = 1 if self.component_var.get() == "YES" else 0
 
        try:
            datos_actuales = conexion.configuradorst80()
            
            if datos_actuales == "FAILED" or datos_actuales == ("", "", "", "", ""):
                exito = conexion.insert_configuratorst80(mach, ope, prog, proc, comp_value)
                mensaje = "Configuración inicial creada con éxito."
            else:
                exito = conexion.update_configuratorst80(mach, ope, prog, proc, comp_value)
                mensaje = "Configuración actualizada correctamente."
            
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