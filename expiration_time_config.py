import tkinter as tk
from tkinter import ttk, messagebox
import conexion

# ── Constantes visuales (mismas que Attributes.py) ──────────────────────────
BG_HEADER      = "#1565C0"
BG_BUTTON_BAR  = "#F3F3F3"
BG_MAIN        = "#FFFFFF"
BTN_GREEN      = "#1D8A21"
BTN_RED        = "#D32F2F"
BTN_BLUE       = "#1565C0"
FG_WHITE       = "#FFFFFF"
FG_DARK        = "#212121"
FONT_TITLE     = ("Segoe UI", 14, "bold")
FONT_LABEL     = ("Segoe UI", 9)
FONT_BTN       = ("Segoe UI", 9, "bold")
FONT_TABLE     = ("Segoe UI", 9)

# ── Columnas del Treeview ────────────────────────────────────────────────────
COLUMNS = ("Dispensing_Process_Name", "Defect_Code", "Minute_Duration", "Move_to_loc")
COL_HEADERS = {
    "Dispensing_Process_Name": "Dispensing Process Name",
    "Defect_Code":             "Defect Code",
    "Minute_Duration":         "Minute Duration",
    "Move_to_loc":             "Move to Loc",
}
COL_WIDTHS = {
    "Dispensing_Process_Name": 220,
    "Defect_Code":             140,
    "Minute_Duration":         120,
    "Move_to_loc":             160,
}


# ════════════════════════════════════════════════════════════════════════════
#  Ventana popup — Agregar / Actualizar
# ════════════════════════════════════════════════════════════════════════════
class VentanaFormulario(tk.Toplevel):
    def __init__(self, parent, modo="add", registro=None):
        """
        :param parent:   FormularioPrincipal (ventana raíz)
        :param modo:     "add" | "update"
        :param registro: tupla (id, process_name, defect_code, minute_duration, move_loc) solo para "update"
        """
        super().__init__(parent.root)
        self.parent    = parent
        self.modo      = modo
        self.registro  = registro

        titulo = "Agregar Expiration Time" if modo == "add" else "Actualizar Expiration Time"
        self.title(titulo)
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        self.grab_set()

        try:
            self.iconbitmap("favicon.ico")
        except Exception:
            pass

        self._build_ui()
        self._center()

        if modo == "update" and registro:
            self._fill_fields(registro)

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_HEADER, padx=20, pady=14)
        header.pack(fill="x")
        titulo = "Agregar registro" if self.modo == "add" else "Actualizar registro"
        tk.Label(header, text=titulo, font=FONT_TITLE,
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w")

        # Body
        body = tk.Frame(self, bg=BG_MAIN, padx=24, pady=18)
        body.pack(fill="both", expand=True)

        labels = [
            ("Dispensing Process Name:", "entry_process"),
            ("Defect Code:",             "entry_defect"),
            ("Minute Duration:",         "entry_duration"),
            ("Move to Loc:",             "entry_move"),
        ]

        for i, (lbl_text, attr) in enumerate(labels):
            tk.Label(body, text=lbl_text, font=FONT_LABEL,
                     bg=BG_MAIN, fg=FG_DARK, anchor="w").grid(
                         row=i, column=0, sticky="w", pady=(0, 4))
            entry = tk.Entry(body, font=("Consolas", 10),
                             bg="#F8FBFF", fg=FG_DARK,
                             relief="solid", bd=1, width=34,
                             insertbackground=BG_HEADER,
                             highlightthickness=1,
                             highlightcolor=BG_HEADER,
                             highlightbackground="#CCCCCC")
            entry.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=(0, 10), ipady=5)
            entry.bind("<FocusIn>",  lambda e, w=entry: w.config(highlightbackground=BG_HEADER))
            entry.bind("<FocusOut>", lambda e, w=entry: w.config(highlightbackground="#CCCCCC"))
            setattr(self, attr, entry)

        body.columnconfigure(1, weight=1)

        # Botones
        btn_frame = tk.Frame(self, bg=BG_BUTTON_BAR, padx=20, pady=10)
        btn_frame.pack(fill="x")

        accion = "Guardar" if self.modo == "add" else "Actualizar"
        tk.Button(btn_frame, text=f"✔  {accion}",
                  command=self._guardar,
                  bg=BTN_GREEN, fg=FG_WHITE,
                  font=FONT_BTN, relief="flat",
                  padx=16, pady=6, cursor="hand2",
                  activebackground="#145214",
                  activeforeground=FG_WHITE).pack(side="right")

        tk.Button(btn_frame, text="✕  Cancelar",
                  command=self.destroy,
                  bg=BG_MAIN, fg="#555555",
                  font=FONT_LABEL, relief="solid", bd=1,
                  padx=14, pady=5, cursor="hand2").pack(side="right", padx=(0, 8))

    # ── Rellena campos en modo update ────────────────────────────────────────
    def _fill_fields(self, registro):
        # registro: (id, process_name, defect_code, minute_duration, move_loc)
        _, process_name, defect_code, minute_duration, move_loc = registro
        self.entry_process.insert(0, process_name  or "")
        self.entry_defect.insert( 0, defect_code   or "")
        self.entry_duration.insert(0, str(minute_duration) if minute_duration is not None else "")
        self.entry_move.insert(   0, move_loc      or "")

    # ── Guardar / Actualizar ─────────────────────────────────────────────────
    def _guardar(self):
        process_name   = self.entry_process.get().strip()
        defect_code    = self.entry_defect.get().strip()
        minute_duration = self.entry_duration.get().strip()
        move_loc       = self.entry_move.get().strip()

        # Validaciones
        if not process_name or not defect_code or not minute_duration or not move_loc:
            messagebox.showwarning("Campos requeridos",
                                   "Todos los campos son obligatorios.", parent=self)
            return

        try:
            minute_duration = int(minute_duration)
        except ValueError:
            messagebox.showwarning("Valor inválido",
                                   "Minute Duration debe ser un número entero.", parent=self)
            return

        try:
            if self.modo == "add":
                conexion.insert_expiration_time(process_name, defect_code, minute_duration, move_loc)
                messagebox.showinfo("Éxito", "Registro agregado correctamente.", parent=self)
            else:
                expiration_time_id = self.registro[0]
                conexion.update_expiration_time(expiration_time_id, process_name, defect_code, minute_duration, move_loc)
                messagebox.showinfo("Éxito", "Registro actualizado correctamente.", parent=self)

            self.parent.cargar_tabla()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el registro:\n{e}", parent=self)

    # ── Centrar en pantalla ───────────────────────────────────────────────────
    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")


# ════════════════════════════════════════════════════════════════════════════
#  Ventana principal — Lista + botones CRUD
# ════════════════════════════════════════════════════════════════════════════
class FormularioPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Expiration Time Configuration")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap("favicon.ico")
        except Exception:
            pass

        self._build_ui()
        self.cargar_tabla()
        self._center()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG_HEADER, padx=24, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Expiration Time",
                 font=FONT_TITLE, bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w")
        tk.Label(header, text="Administra los registros de tiempo de expiración para Conduit ST20.",
                 font=FONT_LABEL, bg=BG_HEADER, fg="#BBDEFB").pack(anchor="w", pady=(2, 0))

        # Barra de botones
        btn_bar = tk.Frame(self.root, bg=BG_BUTTON_BAR, padx=20, pady=10)
        btn_bar.pack(fill="x")

        tk.Button(btn_bar, text="＋  Agregar",
                  command=self._abrir_agregar,
                  bg=BTN_GREEN, fg=FG_WHITE,
                  font=FONT_BTN, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#145214",
                  activeforeground=FG_WHITE).pack(side="left")

        tk.Button(btn_bar, text="✎  Editar",
                  command=self._abrir_editar,
                  bg=BTN_BLUE, fg=FG_WHITE,
                  font=FONT_BTN, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#0D47A1",
                  activeforeground=FG_WHITE).pack(side="left", padx=(8, 0))

        tk.Button(btn_bar, text="✕  Eliminar",
                  command=self._eliminar,
                  bg=BTN_RED, fg=FG_WHITE,
                  font=FONT_BTN, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#B71C1C",
                  activeforeground=FG_WHITE).pack(side="left", padx=(8, 0))

        # Tabla
        table_frame = tk.Frame(self.root, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=BG_MAIN,
                        foreground=FG_DARK,
                        rowheight=26,
                        fieldbackground=BG_MAIN,
                        font=FONT_TABLE)
        style.configure("Treeview.Heading",
                        background=BG_HEADER,
                        foreground=FG_WHITE,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", "#BBDEFB")],
                  foreground=[("selected", FG_DARK)])
        style.map("Treeview.Heading",
                  background=[("active", "#0D47A1")])

        self.tree = ttk.Treeview(table_frame,
                                 columns=COLUMNS,
                                 show="headings",
                                 selectmode="browse")

        for col in COLUMNS:
            self.tree.heading(col, text=COL_HEADERS[col])
            self.tree.column(col, width=COL_WIDTHS[col], anchor="w", stretch=False)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._abrir_editar())

    # ── Carga / refresca tabla ────────────────────────────────────────────────
    def cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        registros = conexion.select_expiration_time()
        for row in registros:
            # row: (expiration_time_id, process_name, defect_code, minute_duration, move_loc)
            self.tree.insert("", "end",
                             iid=str(row[0]),
                             values=(row[1], row[2], row[3], row[4]))

    # ── Selección actual ──────────────────────────────────────────────────────
    def _get_seleccion(self):
        """Retorna la tupla completa del registro seleccionado o None."""
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        valores = self.tree.item(iid, "values")
        # (id, process_name, defect_code, minute_duration, move_loc)
        return (int(iid), valores[0], valores[1], valores[2], valores[3])

    # ── Acciones CRUD ─────────────────────────────────────────────────────────
    def _abrir_agregar(self):
        VentanaFormulario(self, modo="add")

    def _abrir_editar(self):
        registro = self._get_seleccion()
        if not registro:
            messagebox.showwarning("Sin selección",
                                   "Selecciona un registro para editar.")
            return
        VentanaFormulario(self, modo="update", registro=registro)

    def _eliminar(self):
        registro = self._get_seleccion()
        if not registro:
            messagebox.showwarning("Sin selección",
                                   "Selecciona un registro para eliminar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar el registro:\n\n"
            f"  Proceso: {registro[1]}\n"
            f"  Defect:  {registro[2]}\n\n"
            f"Esta acción no se puede deshacer."
        )
        if not confirmar:
            return

        try:
            conexion.delete_expiration_time(registro[0])
            self.cargar_tabla()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el registro:\n{e}")

    # ── Centrar en pantalla ───────────────────────────────────────────────────
    def _center(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioPrincipal(root)
    root.mainloop()
