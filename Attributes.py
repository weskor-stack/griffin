import tkinter as tk
from tkinter import ttk, messagebox
import conexion
import importlib
importlib.reload(conexion)
from datetime import datetime

# --- COLORES Y FUENTES DE LA ESTÉTICA ---
BG_HEADER      = "#1565C0"  # Azul fuerte
BG_BUTTON_BAR  = "#F3F3F3"  # Gris claro
BG_MAIN        = "#FFFFFF"  # Blanco
FG_WHITE       = "#FFFFFF"  # Texto blanco
FG_BLUE_LABEL  = "#00479E"  # Azul para textos de etiquetas
BORDER_COLOR   = "#000000"  # Borde negro
BTN_GREEN      = "#1D8A21"
BTN_RED        = "#D32F2F"

FONT_HEAD      = ("Segoe UI", 18, "bold")
FONT_SUBHEAD   = ("Segoe UI", 10)
FONT_LABEL     = ("Segoe UI", 8, "bold")
FONT_MONO      = ("Consolas", 10)
FONT_BTN       = ("Segoe UI", 9, "bold")

class FormularioPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Attributes")
        self.root.geometry("900x550")
        self.root.configure(bg=BG_MAIN)
        try: self.root.iconbitmap("favicon.ico")
        except: pass
        self.data = {}

        # ====== ESTILOS ======
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=BG_BUTTON_BAR, foreground="black", relief="flat")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10), background=BG_MAIN, fieldbackground=BG_MAIN, borderwidth=1, bordercolor=BORDER_COLOR)
        # Resaltado azul suave al seleccionar una fila
        style.map("Treeview", background=[("selected", "#D0E8FF")], foreground=[("selected", "black")])

        # ====== HEADER (Banda azul) ======
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        
        tk.Label(header, text="⚙ Gestión de Atributos", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))
        tk.Label(header, text="Administración de límites y valores esperados.", font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        # ====== BOTONES (Banda gris) ======
        frame_botones = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        frame_botones.pack(fill="x")

        # Contenedor interno para los botones
        btn_inner = tk.Frame(frame_botones, bg=BG_BUTTON_BAR)
        btn_inner.pack(side="left", padx=24, pady=10)

        # Botones con diseño plano
        tk.Button(btn_inner, text="➕ Agregar", font=FONT_BTN, bg=BTN_GREEN, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.abrir_agregar).grid(row=0, column=0, padx=(0, 10))
        tk.Button(btn_inner, text="✏️ Actualizar", font=FONT_BTN, bg=BG_HEADER, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.abrir_actualizar).grid(row=0, column=1, padx=10)
        tk.Button(btn_inner, text="🗑️ Eliminar", font=FONT_BTN, bg=BTN_RED, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.eliminar).grid(row=0, column=2, padx=10)

        # ====== TABLA ======
        tabla_frame = tk.Frame(self.root, bg=BG_MAIN)
        tabla_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=("Nombre", "Lower", "Upper", "Value", "Time"), # Agregada columna Time
            show="headings",
            selectmode="browse"
        )

        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Lower", text="Lower-limit")
        self.tabla.heading("Upper", text="Upper-limit")
        self.tabla.heading("Value", text="Value_expected")
        self.tabla.heading("Time", text="Time") # Header para Time
        
        self.tabla.column("Nombre", width=180)
        self.tabla.column("Lower", width=120, anchor="center")
        self.tabla.column("Upper", width=120, anchor="center")
        self.tabla.column("Value", width=120, anchor="center")
        self.tabla.column("Time", width=100, anchor="center") # Ancho para Time
        
        self.tabla.pack(fill="both", expand=True)

        self.tabla.tag_configure("par", background="#F9F9F9")
        self.tabla.tag_configure("impar", background="#FFFFFF")

        self.cargar_datos()

    # ====== CARGAR DATOS ======
    def cargar_datos(self):
        self.tabla.delete(*self.tabla.get_children())
        self.data.clear()

        try:
            registros = conexion.select_attributes()
            for i, registro in enumerate(registros):
                tag = "par" if i % 2 == 0 else "impar"
                item = self.tabla.insert("", "end", values=(
                    registro[1],  
                    registro[4],  
                    registro[3],  
                    registro[5], 
                    registro[7], # Índice correspondiente a Time
                ), tags=(tag,))

                self.data[item] = {
                    "attribute_id":        registro[0],
                    "name":                registro[1],
                    "unit":                registro[2],
                    "upper_limit":         registro[3],
                    "lower_limit":         registro[4],
                    "value_expected":      registro[5],
                    "time":                registro[7], # Guardamos Time en la data
                    "create_registration": registro[8], # Asumiendo que user_id es [7] y fecha es [8]
                }
        except Exception as e:
            print(f"Error al cargar datos: {e}")

    # ====== FUNCIONES ======
    def abrir_agregar(self):
        VentanaFormulario(self, "Agregar")

    def abrir_actualizar(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un registro para actualizar.")
            return
        selected = selected[0]
        datos = self.data[selected]
        VentanaFormulario(self, "Actualizar", selected, datos)

    def agregar_datos(self, datos):
        try:
            # Asegúrate de que tu función en conexion.py reciba este nuevo parámetro 'time'
            attribute_id = conexion.insert_attribute(
                datos["name"],
                datos["unit"],
                datos["upper_limit"],
                datos["lower_limit"],
                datos["value_expected"],
                datos["time"], 
                datos["create_registration"]
            )
            datos["attribute_id"] = attribute_id

            count = len(self.tabla.get_children())
            tag = "par" if count % 2 == 0 else "impar"
            item = self.tabla.insert("", "end", values=(
                datos["name"],
                datos["lower_limit"],
                datos["upper_limit"],
                datos["value_expected"],
                datos["time"],
            ), tags=(tag,))
            self.data[item] = datos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")

    def actualizar_datos(self, item, datos):
        try:
            attribute_id = self.data[item]["attribute_id"]

            # Asegúrate de que tu función en conexion.py reciba este nuevo parámetro 'time'
            conexion.update_attribute(
                attribute_id,
                datos["name"],
                datos["unit"],
                datos["upper_limit"],
                datos["lower_limit"],
                datos["value_expected"],
                datos["time"],
            )

            self.tabla.item(item, values=(
                datos["name"],
                datos["lower_limit"],
                datos["upper_limit"],
                datos["value_expected"],
                datos["time"],
            ))

            datos["attribute_id"] = attribute_id
            self.data[item] = datos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def eliminar(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un registro para eliminar.")
            return

        selected = selected[0]

        if selected not in self.data:
            return

        attribute_id = self.data[selected].get("attribute_id")
        if not attribute_id:
            return

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este registro?")
        if respuesta:
            try:
                conexion.delete_attribute(attribute_id)
                self.tabla.delete(selected)
                del self.data[selected]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")


class VentanaFormulario:
    def __init__(self, principal, modo, item=None, datos=None):
        self.principal = principal
        self.modo = modo
        self.item = item
        
        self.ventana = tk.Toplevel(principal.root)
        self.ventana.title(f"{modo} Registro")
        self.ventana.geometry("380x550") # AUMENTÉ EL ALTO PARA EL CAMPO TIME
        self.ventana.configure(bg=BG_MAIN)
        try: self.ventana.iconbitmap("favicon.ico")
        except: pass

        # --- Encabezado de la ventana emergente ---
        header = tk.Frame(self.ventana, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text=f"📋 {modo} Atributo", font=("Segoe UI", 14, "bold"), bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=20, pady=15)

        # --- Contenedor del formulario ---
        form_frame = tk.Frame(self.ventana, bg=BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=30, pady=(15, 0))

        # Variables
        self.nombre = tk.StringVar()
        self.unit = tk.StringVar()
        self.lower = tk.StringVar()
        self.upper = tk.StringVar()
        self.value = tk.StringVar()
        self.time = tk.StringVar() # Nueva variable Time

        if datos:
            self.nombre.set(datos.get("name", ""))
            self.unit.set(datos.get("unit", ""))
            self.lower.set(datos.get("lower_limit", ""))
            self.upper.set(datos.get("upper_limit", ""))
            self.value.set(datos.get("value_expected", ""))
            self.time.set(datos.get("time", ""))

        # Configuración común para Entradas (Borde plano, Consolas)
        entry_kwargs = {"bg": BG_MAIN, "fg": "black", "relief": "flat", "font": FONT_MONO, 
                        "highlightthickness": 1, "highlightbackground": BORDER_COLOR, "highlightcolor": BG_HEADER}

        # Campos
        self.crear_campo(form_frame, "Nombre", self.nombre)
        self.crear_campo(form_frame, "Unit", self.unit)
        self.crear_campo(form_frame, "Lower-limit", self.lower)
        self.crear_campo(form_frame, "Upper-limit", self.upper)
        self.crear_campo(form_frame, "Value_expected", self.value)
        self.crear_campo(form_frame, "Time", self.time) # Nuevo campo visual

        # Botón Guardar 
        btn_frame = tk.Frame(self.ventana, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="💾 Guardar", font=FONT_BTN, bg=BTN_GREEN, fg="white", relief="flat", cursor="hand2", padx=20, pady=6, command=self.guardar).pack(pady=10)

    def crear_campo(self, parent, texto, variable):
        tk.Label(parent, text=texto.upper(), bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w", pady=(5, 0))
        entry = tk.Entry(parent, textvariable=variable, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=BG_HEADER)
        entry.pack(fill="x", ipady=4, pady=(2, 10))

    def guardar(self):
        # # Validar campos vacíos (incluyendo time)
        # if not all([self.nombre.get(), self.lower.get(), self.upper.get(), self.value.get(), self.time.get()]):
        #     messagebox.showwarning("Incompleto", "Por favor, llene los campos principales.")
        #     return

        datos = {
            "name":                self.nombre.get(),
            "unit":                self.unit.get(),
            "upper_limit":         self.upper.get(),
            "lower_limit":         self.lower.get(),
            "value_expected":      self.value.get(),
            "time":                self.time.get(), # Se envía Time a datos
            "create_registration": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if self.modo == "Agregar":
            self.principal.agregar_datos(datos)
        else:
            self.principal.actualizar_datos(self.item, datos)

        self.ventana.destroy()

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioPrincipal(root)
    root.mainloop()