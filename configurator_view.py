import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import conexion

# import customtkinter as ctk
# import conexion

class ConfiguratorView(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Configurator Settings")
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Variables para los campos
        self.url_var = ctk.StringVar()
        self.program_id_var = ctk.StringVar()
        self.device_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.tsp_var = ctk.StringVar()
        
        # Variables para los checkboxes
        self.csv_var = ctk.IntVar(value=0)
        self.json_var = ctk.IntVar(value=0)
        self.xml_var = ctk.IntVar(value=0)
        
        self.create_widgets()
        self.load_existing_data()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = 500
        height = 550
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Configurator Settings",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # ============ CAMPOS DE CONFIGURACIÓN ============
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # URL
        ctk.CTkLabel(config_frame, text="URL:", anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        url_entry = ctk.CTkEntry(config_frame, textvariable=self.url_var, width=350)
        url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Program ID
        ctk.CTkLabel(config_frame, text="Program ID:", anchor="w").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        program_entry = ctk.CTkEntry(config_frame, textvariable=self.program_id_var, width=350)
        program_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Device
        ctk.CTkLabel(config_frame, text="Device:", anchor="w").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        device_entry = ctk.CTkEntry(config_frame, textvariable=self.device_var, width=350)
        device_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Program Password
        ctk.CTkLabel(config_frame, text="Password:", anchor="w").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        password_entry = ctk.CTkEntry(config_frame, textvariable=self.password_var, width=350, show="*")
        password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # TSP
        ctk.CTkLabel(config_frame, text="TSP:", anchor="w").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        tsp_entry = ctk.CTkEntry(config_frame, textvariable=self.tsp_var, width=350)
        tsp_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Configurar expansión de columnas
        config_frame.columnconfigure(1, weight=1)
        
        # ============ CHECKBOXES DE EXPORTACIÓN ============
        # Separador
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray70")
        separator.pack(fill="x", padx=10, pady=20)
        
        # Título para checkboxes
        export_label = ctk.CTkLabel(
            main_frame,
            text="Export Formats:",
            font=("Arial", 12, "bold")
        )
        export_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Frame para checkboxes
        checkbox_frame = ctk.CTkFrame(main_frame)
        checkbox_frame.pack(fill="x", padx=20, pady=5)
        
        # Checkboxes
        ctk.CTkCheckBox(
            checkbox_frame,
            text="CSV",
            variable=self.csv_var,
            onvalue=1,
            offvalue=0
        ).pack(side="left", padx=20, pady=10)
        
        ctk.CTkCheckBox(
            checkbox_frame,
            text="JSON",
            variable=self.json_var,
            onvalue=1,
            offvalue=0
        ).pack(side="left", padx=20, pady=10)
        
        ctk.CTkCheckBox(
            checkbox_frame,
            text="XML",
            variable=self.xml_var,
            onvalue=1,
            offvalue=0
        ).pack(side="left", padx=20, pady=10)
        
        # ============ BOTONES ============
        # Separador
        separator2 = ctk.CTkFrame(main_frame, height=2, fg_color="gray70")
        separator2.pack(fill="x", padx=10, pady=30)
        
        # Frame para botones
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Botón Save
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=120,
            height=35,
            font=("Arial", 12)
        )
        save_button.pack(side="left", padx=(0, 10))
        
        # Botón Cancel
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            height=35,
            fg_color="gray40",
            hover_color="gray30",
            font=("Arial", 12)
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        # Centrar botones
        button_frame.pack_propagate(False)
        button_frame.configure(height=50)
    
    def load_existing_data(self):
        """Carga los datos existentes SIN MODIFICAR la base de datos"""
        try:
            print("[INFO] Cargando datos existentes...")
            
            # 1. Cargar configuración del configurator
            config_data = conexion.get_configurator_data()
            if config_data:
                print(f"[DEBUG] Datos de configurator: {config_data}")
                # Asumiendo: (URL, Program_id, device, program_password, tsp)
                self.url_var.set(config_data[1] if config_data[1] is not None else "")
                self.program_id_var.set(config_data[2] if config_data[2] is not None else "")
                self.device_var.set(config_data[3] if config_data[3] is not None else "")
                self.password_var.set(config_data[4] if config_data[4] is not None else "")
                self.tsp_var.set(config_data[5] if config_data[5] is not None else "")
            else:
                print("[INFO] No hay datos de configurator guardados")
            
            # 2. Cargar estados de exportación (SOLO LECTURA)
            export_status = conexion.get_export_status()
            print(f"[DEBUG] Estados de exportación: {export_status}")
            
            # Establecer valores de checkboxes basados en lo que existe
            self.csv_var.set(1 if export_status.get('CSV') == 1 else 0)
            self.json_var.set(1 if export_status.get('JSON') == 1 else 0)
            self.xml_var.set(1 if export_status.get('XML') == 1 else 0)
            
            print(f"[INFO] Checkboxes configurados: CSV={self.csv_var.get()}, JSON={self.json_var.get()}, XML={self.xml_var.get()}")
            
        except Exception as e:
            print(f"[ERROR] Error cargando datos: {e}")
    
    def save_settings(self):
        """Guarda la configuración SOLO cuando el usuario hace clic en Save"""
        try:
            print("[INFO] Guardando configuración...")
            
            # 1. Validar campos
            if not self.url_var.get().strip():
                from tkinter import messagebox
                messagebox.showwarning("Advertencia", "The URL is mandatory.")
                return
            
            # 2. Guardar configuración del configurator
            success = conexion.update_configurator(
                self.url_var.get().strip(),
                self.program_id_var.get().strip(),
                self.device_var.get().strip(),
                self.password_var.get().strip(),
                self.tsp_var.get().strip()
            )
            
            if not success:
                raise Exception("Error saving configurator settings")
            
            # 3. Guardar estados de exportación
            formats_to_save = [
                ('CSV', self.csv_var),
                ('JSON', self.json_var), 
                ('XML', self.xml_var)
            ]
            
            for file_type, var in formats_to_save:
                status = 1 if var.get() == 1 else 2
                success = conexion.update_export_status(file_type, status)
                if not success:
                    print(f"[WARNING] No se pudo guardar {file_type}")
            
            # 4. Mostrar éxito
            from tkinter import messagebox
            messagebox.showinfo("Éxito", "Settings saved successfully")
            
            # 5. Cerrar ventana
            self.destroy()
            
        except Exception as e:
            print(f"[ERROR] Error guardando configuración: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"The settings could not be saved.:\n{str(e)}")


# ============ SOLO PARA PRUEBAS LOCALES ============
# Comenta o elimina esta sección cuando integres con tu aplicación principal

"""
if __name__ == "__main__":
    # Solo para pruebas locales
    import sys
    
    # Crear ventana principal de prueba
    test_root = ctk.CTk()
    test_root.withdraw()  # Ocultar ventana principal
    
    # Crear configurator
    config_window = ConfiguratorView(test_root)
    
    # Ejecutar
    test_root.mainloop()
"""

# Añade esta función temporal en configurator_view.py para debug
def test_configurator():
    """Prueba completa del configurator"""
    print("\n=== PRUEBA COMPLETA CONFIGURATOR ===")
    
    # 1. Obtener estado actual
    print("\n1. Estado actual desde DB:")
    status = conexion.get_export_status()
    print(f"   {status}")
    
    # 2. Simular checkboxes
    print("\n2. Simulando checkboxes (todos activos):")
    csv_val = 1
    json_val = 1
    xml_val = 1
    
    print(f"   CSV: {csv_val} (debería guardar status 1)")
    print(f"   JSON: {json_val} (debería guardar status 1)")
    print(f"   XML: {xml_val} (debería guardar status 1)")
    
    # 3. Actualizar en DB
    print("\n3. Actualizando en base de datos:")
    for file_type, value in [('CSV', csv_val), ('JSON', json_val), ('XML', xml_val)]:
        status = 1 if value == 1 else 2
        success = conexion.update_export_status(file_type, status)
        print(f"   {file_type}: {'✓' if success else '✗'}")
    
    # 4. Verificar cambios
    print("\n4. Verificando cambios:")
    final_status = conexion.get_export_status()
    print(f"   Estado final: {final_status}")
    
    # 5. Crear ventana de prueba
    print("\n5. Creando ventana de configuración...")
    root = ctk.CTk()
    config_window = ConfiguratorView(root)
    root.mainloop()

test_configurator()