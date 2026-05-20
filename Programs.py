import tkinter as tk
from tkinter import ttk, messagebox
import conexion
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

class FormularioProgramas:
    def __init__(self, root):
        self.root = root
        self.data = {}
        self.contador_id = 1
        
        self.root.title("Gestión de Programas")
        self.root.geometry("800x500")
        self.root.configure(bg=BG_MAIN)
        try: self.root.iconbitmap("favicon.ico")
        except: pass

        # ===== ESTILO =====
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=BG_BUTTON_BAR, foreground="black", relief="flat")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10), background=BG_MAIN, fieldbackground=BG_MAIN, borderwidth=1, bordercolor=BORDER_COLOR)
        style.map("Treeview", background=[("selected", "#D0E8FF")], foreground=[("selected", "black")])

        # ====== HEADER (Banda azul) ======
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        
        tk.Label(header, text="⚙ Gestión de Programas", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))
        tk.Label(header, text="Administración del catálogo de programas.", font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        # ===== BOTONES (Banda gris) =====
        frame_botones = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        frame_botones.pack(fill="x")

        btn_inner = tk.Frame(frame_botones, bg=BG_BUTTON_BAR)
        btn_inner.pack(side="left", padx=24, pady=10)

        tk.Button(btn_inner, text="➕ Agregar", font=FONT_BTN, bg=BTN_GREEN, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.abrir_agregar).grid(row=0, column=0, padx=(0, 10))
        tk.Button(btn_inner, text="✏️ Actualizar", font=FONT_BTN, bg=BG_HEADER, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.abrir_actualizar).grid(row=0, column=1, padx=10)
        tk.Button(btn_inner, text="🗑️ Eliminar", font=FONT_BTN, bg=BTN_RED, fg="white", relief="flat", cursor="hand2", padx=15, pady=5, command=self.eliminar).grid(row=0, column=2, padx=10)

        # ===== TABLA =====
        tabla_frame = tk.Frame(self.root, bg=BG_MAIN)
        tabla_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=("Nombre", "Descripcion"),
            show="headings"
        )

        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Descripcion", text="Descripción")
        self.tabla.pack(fill="both", expand=True)

        self.tabla.tag_configure("par", background="#F9F9F9")
        self.tabla.tag_configure("impar", background="#FFFFFF")

        # Cargar datos
        self.cargar_datos()
        self.root.update_idletasks()

    def cargar_datos(self):
        self.tabla.delete(*self.tabla.get_children())
        self.data.clear()

        try:
            registros = conexion.select_programs()
            for i, registro in enumerate(registros):
                tag = "par" if i % 2 == 0 else "impar"
                item = self.tabla.insert("", "end", values=(registro[1], registro[2]), tags=(tag,))
                self.data[item] = {
                    "Program_id": registro[0],
                    "Name": registro[1],
                    "Description": registro[2]
                }
            self.ajustar_columnas()
        except Exception as e:
            print(f"Error al cargar datos: {e}")

    def ajustar_columnas(self):
        for col in self.tabla["columns"]:
            max_len = len(col)
            for item in self.tabla.get_children():
                valor = str(self.tabla.item(item, "values")[self.tabla["columns"].index(col)])
                if len(valor) > max_len:
                    max_len = len(valor)
            ancho = (max_len + 2) * 8
            self.tabla.column(col, width=ancho)

    # ===== FUNCIONES =====
    def abrir_agregar(self):
        VentanaPrograma(self, "Agregar")

    def abrir_actualizar(self):
        selected = self.tabla.focus()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un programa para actualizar.")
            return
        datos = self.data[selected]
        VentanaPrograma(self, "Actualizar", selected, datos)

    def agregar(self, datos):
        try:
            program_id = conexion.insert_program(
                datos["Name"],
                datos["Description"],
                datos["Create_registration"]
            )

            if program_id:
                datos["Program_id"] = program_id
                count = len(self.tabla.get_children())
                tag = "par" if count % 2 == 0 else "impar"
                item = self.tabla.insert("", "end", values=(datos["Name"], datos["Description"]), tags=(tag,))
                self.data[item] = datos
                self.ajustar_columnas()
            else:
                messagebox.showerror("Error", "No se pudo obtener el ID de la base de datos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")

    def actualizar(self, item, datos):
        try:
            program_id = self.data[item]["Program_id"]  
            conexion.update_program(program_id, datos["Name"], datos["Description"])
            self.tabla.item(item, values=(datos["Name"], datos["Description"]))
            datos["Program_id"] = program_id  # Reinyectarlo
            self.data[item] = datos
            self.ajustar_columnas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def eliminar(self):
        selected = self.tabla.selection() 
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un programa para eliminar.")
            return 

        item_id = selected[0] 
        if item_id not in self.data:
            return 

        program_id = self.data[item_id].get("Program_id")
        if not program_id:
            return

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este programa?")
        if respuesta:
            try:
                conexion.delete_program(program_id)
                self.tabla.delete(item_id)
                del self.data[item_id]
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {e}")


class VentanaPrograma:
    def __init__(self, principal, modo, item=None, datos=None):
        self.principal = principal
        self.modo = modo
        self.item = item

        self.ventana = tk.Toplevel(principal.root)
        self.ventana.title(f"{modo} Programa")
        self.ventana.geometry("450x380")
        self.ventana.configure(bg=BG_MAIN)
        try: self.ventana.iconbitmap("favicon.ico")
        except: pass

        # --- Encabezado ---
        header = tk.Frame(self.ventana, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text=f"📋 {modo} Programa", font=("Segoe UI", 14, "bold"), bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=20, pady=15)

        # --- Formulario ---
        form_frame = tk.Frame(self.ventana, bg=BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=30, pady=15)

        self.name = tk.StringVar()
        if datos:
            self.name.set(datos["Name"])

        # Nombre
        tk.Label(form_frame, text="NOMBRE DEL PROGRAMA", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w", pady=(5, 0))
        tk.Entry(form_frame, textvariable=self.name, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=BG_HEADER).pack(fill="x", ipady=4, pady=(2, 15))

        # Descripción
        tk.Label(form_frame, text="DESCRIPCIÓN", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w", pady=(5, 0))
        self.desc_text = tk.Text(form_frame, height=5, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=BG_HEADER)
        self.desc_text.pack(fill="x", pady=(2, 10))

        if datos:
            self.desc_text.insert("1.0", datos["Description"])

        # --- Botón Guardar ---
        btn_frame = tk.Frame(self.ventana, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x", side="bottom")
        tk.Button(btn_frame, text="💾 Guardar", font=FONT_BTN, bg=BTN_GREEN, fg="white", relief="flat", cursor="hand2", padx=20, pady=6, command=self.guardar).pack(pady=10)

    def guardar(self):
        # if not self.name.get().strip():
        #     messagebox.showwarning("Incompleto", "El nombre del programa es obligatorio.")
        #     return

        descripcion = self.desc_text.get("1.0", "end").strip()
        datos = {
            "Name": self.name.get(),
            "Description": descripcion,
            "Create_registration": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if self.modo == "Agregar":
            self.principal.agregar(datos)
        elif self.modo == "Actualizar":
            self.principal.actualizar(self.item, datos)

        self.ventana.destroy()

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioProgramas(root)
    root.mainloop()