import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import conexion
import importlib
importlib.reload(conexion)

# ── Constantes visuales (mismas que Attributes.py) ───────────────────────────
BG_HEADER      = "#1565C0"
BG_BUTTON_BAR  = "#F3F3F3"
BG_MAIN        = "#FFFFFF"
BTN_GREEN      = "#1D8A21"
BTN_RED        = "#D32F2F"
BTN_BLUE       = "#1565C0"
FG_WHITE       = "#FFFFFF"
FG_DARK        = "#212121"
FG_BLUE_LABEL  = "#00479E"
BORDER_COLOR   = "#000000"

FONT_HEAD      = ("Segoe UI", 18, "bold")
FONT_SUBHEAD   = ("Segoe UI", 10)
FONT_LABEL     = ("Segoe UI", 8, "bold")
FONT_MONO      = ("Consolas", 10)
FONT_BTN       = ("Segoe UI", 9, "bold")

# ── Columnas Treeview (orden PDF Tabla 2.3) ──────────────────────────────────
COLUMNS = ("Step_Name", "Unit_of_Measurement", "Low_Limit", "High_Limit", "Defect_Code")
COL_HEADERS = {
    "Step_Name":           "Step Name",
    "Unit_of_Measurement": "Unit of Measurement",
    "Low_Limit":           "Low Limit",
    "High_Limit":          "High Limit",
    "Defect_Code":         "Defect Code",
}
COL_WIDTHS = {
    "Step_Name":           200,
    "Unit_of_Measurement": 160,
    "Low_Limit":           100,
    "High_Limit":          100,
    "Defect_Code":         130,
}


# ════════════════════════════════════════════════════════════════════════════
#  Ventana popup — Agregar / Actualizar
# ════════════════════════════════════════════════════════════════════════════
class VentanaFormulario:
    def __init__(self, principal, modo, item=None, datos=None):
        """
        :param principal: FormularioPrincipal
        :param modo:      "Agregar" | "Actualizar"
        :param item:      iid del Treeview (solo para Actualizar)
        :param datos:     dict con los valores actuales (solo para Actualizar)
        """
        self.principal = principal
        self.modo      = modo
        self.item      = item

        self.ventana = tk.Toplevel(principal.root)
        self.ventana.title(f"{modo} Atributo ST20")
        self.ventana.geometry("400x420")
        self.ventana.configure(bg=BG_MAIN)
        self.ventana.resizable(False, False)
        self.ventana.grab_set()

        try:
            self.ventana.iconbitmap("favicon.ico")
        except Exception:
            pass

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self.ventana, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text=f"📋 {modo} Atributo",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=20, pady=15)

        # ── Formulario ───────────────────────────────────────────────────────
        form_frame = tk.Frame(self.ventana, bg=BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=30, pady=(15, 0))

        self.var_name   = tk.StringVar()
        self.var_unit   = tk.StringVar()
        self.var_low    = tk.StringVar()
        self.var_high   = tk.StringVar()
        self.var_defect = tk.StringVar()

        if datos:
            self.var_name.set(datos.get("name",        ""))
            self.var_unit.set(datos.get("unit",        ""))
            self.var_low.set( datos.get("lower_limit", ""))
            self.var_high.set(datos.get("upper_limit", ""))
            self.var_defect.set(datos.get("defect_code", ""))

        campos = [
            ("Step Name",           self.var_name),
            ("Unit of Measurement", self.var_unit),
            ("Low Limit",           self.var_low),
            ("High Limit",          self.var_high),
            ("Defect Code",         self.var_defect),
        ]
        for label_text, var in campos:
            self._crear_campo(form_frame, label_text, var)

        # ── Botón Guardar ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.ventana, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="💾  Guardar",
                  font=FONT_BTN,
                  bg=BTN_GREEN, fg=FG_WHITE,
                  relief="flat", cursor="hand2",
                  padx=20, pady=5,
                  command=self._guardar).pack(pady=5)

    def _crear_campo(self, parent, texto, variable):
        tk.Label(parent, text=texto.upper(),
                 bg=BG_MAIN, fg=FG_BLUE_LABEL,
                 font=FONT_LABEL).pack(anchor="w", pady=(5, 0))
        entry = tk.Entry(parent, textvariable=variable,
                         bg=BG_MAIN, fg=FG_DARK,
                         relief="flat", font=FONT_MONO,
                         highlightthickness=1,
                         highlightbackground=BORDER_COLOR,
                         highlightcolor=BG_HEADER)
        entry.pack(fill="x", ipady=4, pady=(2, 8))

    def _guardar(self):
        name        = self.var_name.get().strip()
        unit        = self.var_unit.get().strip()
        lower_limit = self.var_low.get().strip()
        upper_limit = self.var_high.get().strip()
        defect_code = self.var_defect.get().strip()

        if not name:
            messagebox.showwarning("Campo requerido",
                                   "Step Name es obligatorio.", parent=self.ventana)
            return

        datos = {
            "name":        name,
            "unit":        unit,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
            "defect_code": defect_code,
        }

        if self.modo == "Agregar":
            self.principal.agregar_datos(datos)
        else:
            self.principal.actualizar_datos(self.item, datos)

        self.ventana.destroy()


# ════════════════════════════════════════════════════════════════════════════
#  Ventana principal — Lista + botones CRUD
# ════════════════════════════════════════════════════════════════════════════
class FormularioPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Attributes ST20")
        self.root.geometry("800x520")
        self.root.configure(bg=BG_MAIN)
        self.data = {}

        try:
            self.root.iconbitmap("favicon.ico")
        except Exception:
            pass

        # ── Estilos Treeview ─────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background=BG_BUTTON_BAR,
                        foreground="black",
                        relief="flat")
        style.configure("Treeview",
                        rowheight=30,
                        font=("Segoe UI", 10),
                        background=BG_MAIN,
                        fieldbackground=BG_MAIN,
                        borderwidth=1,
                        bordercolor=BORDER_COLOR)
        style.map("Treeview",
                  background=[("selected", "#D0E8FF")],
                  foreground=[("selected", "black")])

        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="⚙ Gestión de Atributos ST20",
                 font=FONT_HEAD, bg=BG_HEADER, fg=FG_WHITE).pack(
                     anchor="w", padx=24, pady=(20, 5))
        tk.Label(header, text="Administración de mediciones: Step Name, Límites y Defect Code (Tabla 2.3).",
                 font=FONT_SUBHEAD, bg=BG_HEADER, fg=FG_WHITE).pack(
                     anchor="w", padx=24, pady=(0, 20))

        # ── Botones ──────────────────────────────────────────────────────────
        frame_botones = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        frame_botones.pack(fill="x")

        btn_inner = tk.Frame(frame_botones, bg=BG_BUTTON_BAR)
        btn_inner.pack(side="left", padx=24, pady=10)

        tk.Button(btn_inner, text="➕ Agregar",
                  font=FONT_BTN, bg=BTN_GREEN, fg=FG_WHITE,
                  relief="flat", cursor="hand2",
                  padx=15, pady=5,
                  command=self.abrir_agregar).grid(row=0, column=0, padx=(0, 10))

        tk.Button(btn_inner, text="✏️ Actualizar",
                  font=FONT_BTN, bg=BG_HEADER, fg=FG_WHITE,
                  relief="flat", cursor="hand2",
                  padx=15, pady=5,
                  command=self.abrir_actualizar).grid(row=0, column=1, padx=10)

        tk.Button(btn_inner, text="🗑️ Eliminar",
                  font=FONT_BTN, bg=BTN_RED, fg=FG_WHITE,
                  relief="flat", cursor="hand2",
                  padx=15, pady=5,
                  command=self.eliminar).grid(row=0, column=2, padx=10)

        # ── Tabla ────────────────────────────────────────────────────────────
        tabla_frame = tk.Frame(self.root, bg=BG_MAIN)
        tabla_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.tabla = ttk.Treeview(tabla_frame,
                                  columns=COLUMNS,
                                  show="headings",
                                  selectmode="browse")

        for col in COLUMNS:
            self.tabla.heading(col, text=COL_HEADERS[col])
            self.tabla.column(col, width=COL_WIDTHS[col], anchor="w")

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical",
                                  command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabla.tag_configure("par",   background="#F9F9F9")
        self.tabla.tag_configure("impar", background="#FFFFFF")

        self.cargar_datos()

    # ── Carga / refresca tabla ────────────────────────────────────────────────
    def cargar_datos(self):
        self.tabla.delete(*self.tabla.get_children())
        self.data.clear()

        try:
            registros = conexion.select_attributes_st20()
            # [0]=attribute_id [1]=name [2]=unit [3]=upper_limit [4]=lower_limit [5]=defect_code
            for i, registro in enumerate(registros):
                tag = "par" if i % 2 == 0 else "impar"
                item = self.tabla.insert("", "end", values=(
                    registro[1],  # Step_Name
                    registro[2],  # Unit_of_Measurement
                    registro[4],  # Low_Limit  (lower_limit)
                    registro[3],  # High_Limit (upper_limit)
                    registro[5],  # Defect_Code
                ), tags=(tag,))

                self.data[item] = {
                    "attribute_id": registro[0],
                    "name":         registro[1],
                    "unit":         registro[2],
                    "upper_limit":  registro[3],
                    "lower_limit":  registro[4],
                    "defect_code":  registro[5],
                }
        except Exception as e:
            print(f"Error al cargar datos: {e}")

    # ── Acciones ─────────────────────────────────────────────────────────────
    def abrir_agregar(self):
        VentanaFormulario(self, "Agregar")

    def abrir_actualizar(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un registro para actualizar.")
            return
        selected = selected[0]
        VentanaFormulario(self, "Actualizar", item=selected, datos=self.data[selected])

    def agregar_datos(self, datos):
        try:
            attribute_id = conexion.insert_attribute_st20(
                datos["name"],
                datos["unit"],
                datos["upper_limit"],
                datos["lower_limit"],
                datos["defect_code"],
            )
            datos["attribute_id"] = attribute_id

            count = len(self.tabla.get_children())
            tag = "par" if count % 2 == 0 else "impar"
            item = self.tabla.insert("", "end", values=(
                datos["name"],
                datos["unit"],
                datos["lower_limit"],
                datos["upper_limit"],
                datos["defect_code"],
            ), tags=(tag,))
            self.data[item] = datos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")

    def actualizar_datos(self, item, datos):
        try:
            attribute_id = self.data[item]["attribute_id"]
            conexion.update_attribute_st20(
                attribute_id,
                datos["name"],
                datos["unit"],
                datos["upper_limit"],
                datos["lower_limit"],
                datos["defect_code"],
            )
            self.tabla.item(item, values=(
                datos["name"],
                datos["unit"],
                datos["lower_limit"],
                datos["upper_limit"],
                datos["defect_code"],
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

        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de que desea eliminar el registro:\n\n"
            f"  Step Name: {self.data[selected]['name']}\n\n"
            f"Esta acción no se puede deshacer."
        )
        if respuesta:
            try:
                conexion.delete_attribute(attribute_id)
                self.tabla.delete(selected)
                del self.data[selected]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioPrincipal(root)
    root.mainloop()
