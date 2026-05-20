import tkinter as tk
from tkinter import ttk
import conexion
from datetime import datetime

# --- COLORES Y FUENTES DE LA ESTÉTICA ---
BG_HEADER      = "#1565C0"
BG_BUTTON_BAR  = "#F3F3F3"
BG_MAIN        = "#FFFFFF"
FG_WHITE       = "#FFFFFF"
FG_BLUE_LABEL  = "#00479E"
BORDER_COLOR   = "#000000"

FONT_HEAD      = ("Segoe UI", 16, "bold")
FONT_LABEL     = ("Segoe UI", 8, "bold")
FONT_MONO      = ("Consolas", 10)
FONT_BTN       = ("Segoe UI", 9, "bold")

class TypeTestCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("Tipo de Prueba")
        self.root.geometry("600x400")
        try: self.root.iconbitmap("favicon.ico")
        except: pass
        self.root.configure(bg=BG_MAIN)
        
        self.data = {}
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=BG_BUTTON_BAR, foreground="black", relief="flat")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background=BG_MAIN, fieldbackground=BG_MAIN, borderwidth=1, bordercolor=BORDER_COLOR)
        style.map("Treeview", background=[("selected", "#D0E8FF")], foreground=[("selected", "black")])

        # ====== HEADER ======
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="⚙ Tipo de Prueba", font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=15, pady=15)

        # ====== BARRA DE BOTONES ======
        frame = tk.Frame(root, bg=BG_BUTTON_BAR)
        frame.pack(fill="x")
        
        btn_inner = tk.Frame(frame, bg=BG_BUTTON_BAR)
        btn_inner.pack(side="left", padx=15, pady=10)

        tk.Button(btn_inner, text="➕ Agregar", font=FONT_BTN, bg="#1D8A21", fg="white", relief="flat", cursor="hand2", padx=15, pady=5,
                  command=self.abrir_agregar).grid(row=0, column=0, padx=5)

        tk.Button(btn_inner, text="✏️ Actualizar", font=FONT_BTN, bg="#105FA0", fg="white", relief="flat", cursor="hand2", padx=15, pady=5,
                  command=self.abrir_actualizar).grid(row=0, column=1, padx=5)

        # ====== TABLA ======
        tabla_frame = tk.Frame(self.root, bg=BG_MAIN)
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=("Nombre", "Status"),
            show="headings"
        )
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Status", text="Status")
        self.tabla.column("Nombre", width=300)
        self.tabla.column("Status", width=100, anchor="center")
        self.tabla.pack(fill="both", expand=True)

        # Cargar datos al final cuando tabla y data ya existen
        self.cargar_datos()

    def status_texto(self, status_id):
        return "Enabled" if status_id == 1 else "Not enabled"
    
    # ====== CARGAR DATOS ======

    def cargar_datos(self):
        self.tabla.delete(*self.tabla.get_children())
        self.data.clear()
        registros = conexion.select_type_test()

        for registro in registros:
            item = self.tabla.insert("", "end", values=(registro[1], self.status_texto(registro[2])))
            self.data[item] = {
                
            "test_type_id": registro[0],  
            "nombre":       registro[1],
            "status":       registro[2]

        }
   
    # ===== AGREGAR =====
    def abrir_agregar(self):
        VentanaAgregar(self)
        try: self.root.iconbitmap("favicon.ico")
        except: pass

    def agregar(self, nombre):
    # Todos a 2 en BD y en UI
        for item in self.tabla.get_children():
            test_type_id = self.data[item]["test_type_id"]  # corregido
        conexion.update_type_test(test_type_id, self.data[item]["nombre"], 2)
        valores = list(self.tabla.item(item, "values"))

        valores[1] = self.status_texto(2)
        self.tabla.item(item, values=(nombre, self.status_texto(2)))
        self.data[item]["status"] = 2

    # Insertar nuevo con status 1
        test_type_id = conexion.insert_type_test(
        nombre,
        1,
        1,  # user_id, ajusta según tu lógica
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

        item = self.tabla.insert("", "end", values=(nombre, 1))
        self.data[item] = {
        "test_type_id": test_type_id,
        "nombre":       nombre,
        "status":       1
    }

    # ===== ACTUALIZAR =====
    def abrir_actualizar(self):
        selected = self.tabla.selection()
        if not selected:
            return
        selected = selected[0]
        datos = self.data[selected]
        VentanaActualizar(self, selected, datos)

    def actualizar(self, item, nombre, status):
        if status == 1:
            for i in self.tabla.get_children():
                if i != item:
                    test_type_id = self.data[i]["test_type_id"]
                    conexion.update_type_test(test_type_id, self.data[i]["nombre"], 2)  # <-- adentro del if
                    valores = list(self.tabla.item(i, "values"))
                    valores[1] = self.status_texto(2)
                    self.tabla.item(i, values=valores)
                    self.data[i]["status"] = 2

        test_type_id = self.data[item]["test_type_id"]
        conexion.update_type_test(test_type_id, nombre, status)
        self.tabla.item(item, values=(nombre, self.status_texto(status)))
        self.data[item] = {
        "test_type_id": test_type_id,
        "nombre":       nombre,
        "status":       status
    }

# ===== VENTANA AGREGAR =====
class VentanaAgregar:
    def __init__(self, principal):
        self.principal = principal
        self.ventana = tk.Toplevel()
        self.ventana.title("Agregar")
        self.ventana.geometry("300x200")
        self.ventana.configure(bg=BG_MAIN)
        try: self.ventana.iconbitmap("favicon.ico")
        except: pass
        
        self.nombre = tk.StringVar()

        header = tk.Frame(self.ventana, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="Agregar", font=("Segoe UI", 12, "bold"), bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=15, pady=10)

        form_frame = tk.Frame(self.ventana, bg=BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(form_frame, text="NOMBRE", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w", pady=(5,0))
        tk.Entry(form_frame, textvariable=self.nombre, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO, highlightthickness=1, highlightbackground=BORDER_COLOR).pack(fill="x", ipady=4, pady=(2, 10))
        
        tk.Button(self.ventana, text="Guardar", font=FONT_BTN, bg="#1D8A21", fg="white", relief="flat", cursor="hand2", padx=15, pady=5,
                  command=self.guardar).pack(pady=10)

    def guardar(self):
        if self.nombre.get():
            self.principal.agregar(self.nombre.get())
        self.ventana.destroy()

# ===== VENTANA ACTUALIZAR =====
class VentanaActualizar:
    def __init__(self, principal, item, datos):
        self.principal = principal
        self.item = item
        self.ventana = tk.Toplevel()
        self.ventana.title("Actualizar")
        self.ventana.geometry("300x260")
        self.ventana.configure(bg=BG_MAIN)
        try: self.ventana.iconbitmap("favicon.ico")
        except: pass
        
        self.nombre = tk.StringVar(value=datos["nombre"])
        self.status = tk.IntVar(value=datos["status"])

        header = tk.Frame(self.ventana, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="Actualizar", font=("Segoe UI", 12, "bold"), bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=15, pady=10)

        form_frame = tk.Frame(self.ventana, bg=BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(form_frame, text="NOMBRE", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w")
        tk.Entry(form_frame, textvariable=self.nombre, bg=BG_MAIN, fg="black", relief="flat", font=FONT_MONO, highlightthickness=1, highlightbackground=BORDER_COLOR).pack(fill="x", ipady=4, pady=(2, 10))
        
        tk.Label(form_frame, text="STATUS", bg=BG_MAIN, fg=FG_BLUE_LABEL, font=FONT_LABEL).pack(anchor="w", pady=(5,0))
        tk.Radiobutton(form_frame, text="Enabled", variable=self.status, value=1, bg=BG_MAIN, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Radiobutton(form_frame, text="Not Enabled", variable=self.status, value=2, bg=BG_MAIN, font=("Segoe UI", 9)).pack(anchor="w")  # 0 -> 2
        
        tk.Button(self.ventana, text="Guardar", font=FONT_BTN, bg="#4CAF50", fg="white", relief="flat", cursor="hand2", padx=15, pady=5,
                  command=self.guardar).pack(pady=10)

    def guardar(self):
        self.principal.actualizar(
            self.item,
            self.nombre.get(),
            self.status.get()
        )
        self.ventana.destroy()

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = TypeTestCRUD(root)
    root.mainloop()