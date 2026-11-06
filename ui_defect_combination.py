"""
Interfaz de administración para la tabla defect_combination.
Permite listar, crear, editar y eliminar combinaciones de códigos de defecto
para ST60 (Screwing).

Uso:
    - Standalone:  python ui_defect_combination.py
    - Desde otra ventana:  DefectCombinationUI(master=ventana_padre)
"""

import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox

import conexion


# ==========================================================
# CONSTANTES
# ==========================================================
ESTADOS_VALIDOS = ("BAJO", "ALTO", "BUENO")


# ==========================================================
# VENTANA PRINCIPAL
# ==========================================================
class DefectCombinationUI(tk.Toplevel):

    def __init__(self, master=None, on_close=None):
        super().__init__(master)
        self.title("Administrar combinaciones de defectos — ST60")
        self.geometry("950x550")
        self.iconbitmap("favicon.ico")
        self.resizable(False, False)

        # Guardar callback opcional de cierre
        self._on_close_callback = on_close

        # Interceptar el cierre de la ventana (botón X o Alt+F4)
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

        # ID de la combinación actualmente seleccionada
        self.combination_id_actual = None

        self._construir_widgets()
        self._cargar_datos()

    # ------------------------------------------------------
    # CIERRE SEGURO
    # ------------------------------------------------------
    def safe_exit(self):
        """Cierra la ventana de forma segura y libera recursos."""
        try:
            logging.info("Cerrando ventana de administración de defect_combination...")
            print("Cerrando ventana de administración de defect_combination...")

            # Limpieza de tabla (opcional)
            try:
                if hasattr(self, "tabla"):
                    self.tabla.delete(*self.tabla.get_children())
            except Exception:
                pass

            # Notificar a la ventana padre si se pasó un callback
            if callable(self._on_close_callback):
                try:
                    self._on_close_callback()
                except Exception as e:
                    logging.error(f"Error ejecutando callback de cierre: {e}")

        except Exception as e:
            logging.error(f"Error al cerrar ventana: {e}")
            print(f"Error al cerrar ventana: {e}")

        finally:
            # Destruir la ventana Toplevel
            try:
                self.destroy()
            except Exception as e:
                logging.error(f"Error destruyendo ventana: {e}")

            # Si esta ventana es la raíz (modo standalone), terminar la app
            try:
                if self.master is None or isinstance(self.master, tk.Tk):
                    if self.master is not None:
                        self.master.quit()      # rompe mainloop()
                        self.master.destroy()   # destruye la raíz
                    sys.exit(0)
            except SystemExit:
                raise
            except Exception as e:
                logging.error(f"Error cerrando raíz: {e}")

    # ------------------------------------------------------
    # Construcción de widgets
    # ------------------------------------------------------
    def _construir_widgets(self):

        # --- Frame superior: formulario ---
        frame_form = tk.LabelFrame(self, text="Datos de la combinación",
                                    padx=10, pady=10)
        frame_form.place(x=10, y=10, width=930, height=150)

        # Fila 1: estados
        tk.Label(frame_form, text="Torque:").grid(row=0, column=0,
                                                   sticky="w", padx=5, pady=5)
        self.cmb_torque = ttk.Combobox(frame_form, values=ESTADOS_VALIDOS,
                                        state="readonly", width=12)
        self.cmb_torque.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_torque.set("BAJO")

        tk.Label(frame_form, text="Ángulo:").grid(row=0, column=2,
                                                   sticky="w", padx=5, pady=5)
        self.cmb_angulo = ttk.Combobox(frame_form, values=ESTADOS_VALIDOS,
                                        state="readonly", width=12)
        self.cmb_angulo.grid(row=0, column=3, padx=5, pady=5)
        self.cmb_angulo.set("BAJO")

        tk.Label(frame_form, text="Rundown:").grid(row=0, column=4,
                                                    sticky="w", padx=5, pady=5)
        self.cmb_rundown = ttk.Combobox(frame_form, values=ESTADOS_VALIDOS,
                                         state="readonly", width=12)
        self.cmb_rundown.grid(row=0, column=5, padx=5, pady=5)
        self.cmb_rundown.set("BAJO")

        # Fila 2: código + descripción
        tk.Label(frame_form, text="Código defecto:").grid(row=1, column=0,
                                                           sticky="w", padx=5, pady=5)
        self.ent_codigo = tk.Entry(frame_form, width=15)
        self.ent_codigo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Descripción:").grid(row=1, column=2,
                                                        sticky="w", padx=5, pady=5)
        self.ent_descripcion = tk.Entry(frame_form, width=60)
        self.ent_descripcion.grid(row=1, column=3, columnspan=3,
                                   padx=5, pady=5, sticky="we")

        # Fila 3: botones
        self.btn_nuevo = tk.Button(frame_form, text="Nuevo", width=12,
                                    command=self._limpiar_formulario)
        self.btn_nuevo.grid(row=2, column=0, padx=5, pady=10)

        self.btn_guardar = tk.Button(frame_form, text="Guardar", width=12,
                                      bg="#4CAF50", fg="white",
                                      command=self._guardar)
        self.btn_guardar.grid(row=2, column=1, padx=5, pady=10)

        self.btn_actualizar = tk.Button(frame_form, text="Actualizar", width=12,
                                         bg="#2196F3", fg="white",
                                         command=self._actualizar)
        self.btn_actualizar.grid(row=2, column=2, padx=5, pady=10)

        self.btn_eliminar = tk.Button(frame_form, text="Eliminar", width=12,
                                       bg="#F44336", fg="white",
                                       command=self._eliminar)
        self.btn_eliminar.grid(row=2, column=3, padx=5, pady=10)

        self.btn_ver_unknown = tk.Button(frame_form, text="Ver desconocidas",
                                          width=18,
                                          command=self._ver_desconocidas)
        # self.btn_ver_unknown.grid(row=2, column=4, columnspan=2, padx=5, pady=10)

        # --- Frame inferior: tabla ---
        frame_tabla = tk.LabelFrame(self, text="Combinaciones registradas",
                                     padx=10, pady=10)
        frame_tabla.place(x=10, y=170, width=930, height=360)

        # Definición de columnas (id se mantiene internamente pero NO se muestra)
        columnas = ("id", "torque", "angulo", "rundown", "codigo", "descripcion")
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            displaycolumns=("torque", "angulo", "rundown", "codigo", "descripcion"),
            show="headings",
            height=15
        )

        # Encabezados (solo de las columnas visibles)
        self.tabla.heading("torque",      text="Torque")
        self.tabla.heading("angulo",      text="Ángulo")
        self.tabla.heading("rundown",     text="Rundown")
        self.tabla.heading("codigo",      text="Código")
        self.tabla.heading("descripcion", text="Descripción")

        # Anchos (id oculto con width=0)
        self.tabla.column("id",          width=0,   stretch=False)
        self.tabla.column("torque",      width=110, anchor="center")
        self.tabla.column("angulo",      width=110, anchor="center")
        self.tabla.column("rundown",     width=110, anchor="center")
        self.tabla.column("codigo",      width=110, anchor="center")
        self.tabla.column("descripcion", width=460, anchor="w")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scroll vertical
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical",
                                command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Evento de selección
        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccionar)

    # ------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------
    def _cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = conexion.select_defect_combination()
        for reg in registros:
            # reg = (id, torque, angulo, rundown, codigo, descripcion)
            self.tabla.insert("", "end", values=reg)

    # ------------------------------------------------------
    # Selección de fila
    # ------------------------------------------------------
    def _on_seleccionar(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        valores = self.tabla.item(seleccion[0], "values")
        # valores = (id, torque, angulo, rundown, codigo, descripcion)
        #            ↑ sigue existiendo aunque no se muestre
        self.combination_id_actual = int(valores[0])

        self.cmb_torque.set(valores[1])
        self.cmb_angulo.set(valores[2])
        self.cmb_rundown.set(valores[3])

        self.ent_codigo.delete(0, tk.END)
        self.ent_codigo.insert(0, valores[4])

        self.ent_descripcion.delete(0, tk.END)
        self.ent_descripcion.insert(0, valores[5] if valores[5] else "")

    # ------------------------------------------------------
    # Limpiar formulario
    # ------------------------------------------------------
    def _limpiar_formulario(self):
        self.combination_id_actual = None
        self.cmb_torque.set("BAJO")
        self.cmb_angulo.set("BAJO")
        self.cmb_rundown.set("BAJO")
        self.ent_codigo.delete(0, tk.END)
        self.ent_descripcion.delete(0, tk.END)

        # Quitar selección de la tabla
        try:
            self.tabla.selection_remove(self.tabla.selection())
        except Exception:
            pass

    # ------------------------------------------------------
    # Validación
    # ------------------------------------------------------
    def _validar(self):
        codigo = self.ent_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Validación",
                                    "El código de defecto es obligatorio.")
            return None

        return {
            "torque":      self.cmb_torque.get().strip().upper(),
            "angulo":      self.cmb_angulo.get().strip().upper(),
            "rundown":     self.cmb_rundown.get().strip().upper(),
            "codigo":      codigo,
            "descripcion": self.ent_descripcion.get().strip(),
        }

    # ------------------------------------------------------
    # Guardar (INSERT)
    # ------------------------------------------------------
    def _guardar(self):
        datos = self._validar()
        if not datos:
            return

        nuevo_id = conexion.insert_defect_combination(
            datos["torque"], datos["angulo"], datos["rundown"],
            datos["codigo"], datos["descripcion"]
        )

        if nuevo_id:
            messagebox.showinfo("Éxito",
                                 f"Combinación registrada correctamente.")
            self._cargar_datos()
            self._limpiar_formulario()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo registrar. Verifica que no exista ya esa combinación."
            )

    # ------------------------------------------------------
    # Actualizar (UPDATE)
    # ------------------------------------------------------
    def _actualizar(self):
        if self.combination_id_actual is None:
            messagebox.showwarning("Aviso",
                                    "Selecciona una combinación de la tabla primero.")
            return

        datos = self._validar()
        if not datos:
            return

        ok = conexion.update_defect_combination(
            self.combination_id_actual,
            datos["torque"], datos["angulo"], datos["rundown"],
            datos["codigo"], datos["descripcion"]
        )

        if ok:
            messagebox.showinfo("Éxito", "Combinación actualizada.")
            self._cargar_datos()
            self._limpiar_formulario()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo actualizar. Verifica los datos o si ya existe esa combinación."
            )

    # ------------------------------------------------------
    # Eliminar (DELETE)
    # ------------------------------------------------------
    def _eliminar(self):
        if self.combination_id_actual is None:
            messagebox.showwarning("Aviso",
                                    "Selecciona una combinación de la tabla primero.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la combinación seleccionada?"
        )
        if not confirmar:
            return

        ok = conexion.delete_defect_combination(self.combination_id_actual)

        if ok:
            messagebox.showinfo("Éxito", "Combinación eliminada.")
            self._cargar_datos()
            self._limpiar_formulario()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la combinación.")

    # ------------------------------------------------------
    # Ver combinaciones desconocidas (auditoría)
    # ------------------------------------------------------
    def _ver_desconocidas(self):
        ventana = tk.Toplevel(self)
        ventana.title("Combinaciones desconocidas (ME99)")
        ventana.geometry("800x400")
        ventana.iconbitmap("favicon.ico")

        columnas = ("id", "torque", "angulo", "rundown",
                    "serial", "part_id", "fecha")
        tabla = ttk.Treeview(
            ventana,
            columns=columnas,
            displaycolumns=("torque", "angulo", "rundown",
                            "serial", "part_id", "fecha"),
            show="headings"
        )

        for col, txt, ancho in [
            ("torque",  "Torque",     80),
            ("angulo",  "Ángulo",     80),
            ("rundown", "Rundown",    80),
            ("serial",  "Serial",     220),
            ("part_id", "Part ID",    80),
            ("fecha",   "Detectado",  160),
        ]:
            tabla.heading(col, text=txt)
            tabla.column(col, width=ancho, anchor="center")

        # Columna id oculta
        tabla.column("id", width=0, stretch=False)

        registros = conexion.select_defect_combination_unknown(limite=200)
        for reg in registros:
            tabla.insert("", "end", values=reg)

        tabla.pack(fill="both", expand=True)

        btn_cerrar = tk.Button(ventana, text="Cerrar", width=12,
                                command=ventana.destroy)
        btn_cerrar.pack(pady=8)


# ==========================================================
# Entrada directa (standalone)
# ==========================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    root = tk.Tk()
    root.withdraw()  # oculta la ventana raíz fantasma

    app_window = DefectCombinationUI(root)
    app_window.mainloop()