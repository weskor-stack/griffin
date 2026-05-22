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
        self.root.geometry("600x600") 
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

        tk.Label(inner, text="PROGRAM NAME + VERSION", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        tk.Label(inner, text="MACHINE ID", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=0, column=1, sticky="w", padx=(15,0))
        
        self.program_name = tk.Entry(inner, **entry_kwargs)
        self.program_name.grid(row=1, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.machine_id = tk.Entry(inner, **entry_kwargs)
        self.machine_id.grid(row=1, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        tk.Label(inner, text="PROCESS NAME", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=0, sticky="w")
        tk.Label(inner, text="QTY COMPONENTS", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=2, column=1, sticky="w", padx=(15,0))
        
        self.process_name = tk.Entry(inner, **entry_kwargs)
        self.process_name.grid(row=3, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.qty_components = tk.Entry(inner, **entry_kwargs)
        self.qty_components.grid(row=3, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        tk.Label(inner, text="CLIENT ID", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=4, column=0, sticky="w")
        tk.Label(inner, text="OPERATOR ID", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=4, column=1, sticky="w", padx=(15,0))
        
        self.client_id = tk.Entry(inner, **entry_kwargs)
        self.client_id.grid(row=5, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.operator_id = tk.Entry(inner, **entry_kwargs)
        self.operator_id.grid(row=5, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        tk.Label(inner, text="PASSWORD", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=6, column=0, sticky="w")
        tk.Label(inner, text="WORKSTATION ID", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).grid(row=6, column=1, sticky="w", padx=(15,0))
        
        self.password = tk.Entry(inner, **entry_kwargs)
        self.password.grid(row=7, column=0, sticky="ew", ipady=5, pady=(2, 15))
        
        self.workstation_id = tk.Entry(inner, **entry_kwargs)
        self.workstation_id.grid(row=7, column=1, sticky="ew", padx=(15, 0), ipady=5, pady=(2, 15))

        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8), bg=BG_MAIN, fg="#888888")
        status_bar.pack(side="bottom", anchor="w", padx=24, pady=5)


    def cargar(self):
        try:
            datos = conexion.configurador() 
            
            if datos and datos != "FAILED":
                def insertar_seguro(entry_widget, valor):
                    if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                        entry_widget.insert(0, str(valor).strip())

                if len(datos) >= 8:
                    insertar_seguro(self.machine_id, datos[0])
                    insertar_seguro(self.process_name, datos[1])
                    insertar_seguro(self.operator_id, datos[2])
                    insertar_seguro(self.workstation_id, datos[3])
                    insertar_seguro(self.program_name, datos[4])
                    insertar_seguro(self.qty_components, datos[5])
                    insertar_seguro(self.client_id, datos[6])
                    insertar_seguro(self.password, datos[7])
                        
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")

    def guardar(self):
        prog = self.program_name.get().strip()
        mach = self.machine_id.get().strip()
        proc = self.process_name.get().strip()
        qty  = self.qty_components.get().strip()
        cli  = self.client_id.get().strip()
        ope  = self.operator_id.get().strip()
        pas  = self.password.get().strip()
        work = self.workstation_id.get().strip()
 
        if not all([prog, mach, proc, qty, cli, ope, pas, work]):
            messagebox.showwarning("Error", "Faltan campos obligatorios.", parent=self.root)
            return
 
        try:
            exito = conexion.update_configurator(prog, mach, proc, qty, cli, ope, pas, work)
            
            if exito:
                messagebox.showinfo("Éxito", "Configuración actualizada correctamente.", parent=self.root)
                self.root.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la base de datos.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error DB", str(e), parent=self.root)

    def cancelar(self):
        """Cierra el formulario sin guardar los cambios."""
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()