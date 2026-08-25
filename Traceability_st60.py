#servidor
from types import SimpleNamespace
import urllib.parse
import socket
import threading
# View
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from PIL import Image
from CustomTkinterMessagebox import *
from tkinter import StringVar, messagebox 
import tkinter.messagebox as tkmsg
from CTkTable import *
# PC name
import conduit_json
import get_name_PC
# MySQL conexión
import conexion
import conexionBitacora
from datetime import datetime, timezone, timedelta 
import commands
import data_json
import os
import requests
import sys
import time
import platform
import logging
import traceback
import Attributes
import Type_test
import interlocking_json
import traceability_json
import json

# --- VARIABLES GLOBALES PARA APIS DE TRAZABILIDAD ---
SERIAL_PADRE_GLOBAL = ""
PART_NUMBER_GLOBAL = ""
MEASUREMENT_KEY_GLOBAL = ""
START_SCREWING_ID_GLOBAL = 0

def json_pretty(data):
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)
    
def bloque_json_ui(nombre, request=None, response=None):
    texto_json = f"\n========== {nombre} ==========\n"

    if request is not None:
        texto_json += "\n--- REQUEST ---\n"
        texto_json += json_pretty(request) + "\n"

    if response is not None:
        texto_json += "\n--- RESPONSE ---\n"
        texto_json += json_pretty(response) + "\n"

    texto_json += "================================\n"

    return texto_json

def safe_insert_api(texto, color=None):
    try:
        if color:
            safe_insert(texto, color)
        else:
            safe_insert(texto)
    except Exception:
        pass


def registrar_json_api(nombre_api, tipo, data, color=None):
    """
    Imprime y registra JSON enviado/recibido.
    tipo puede ser: REQUEST, RESPONSE HTTP 200, ERROR, etc.
    """

    texto = (
        f"\n{nombre_api} {tipo}\n"
        f"{json_pretty(data)}\n"
    )

    print(texto)

    try:
        logger.info(texto)
    except Exception:
        pass

    safe_insert_api(texto, color)


def post_api_debug(nombre_api, url, payload, timeout=30):
    """
    Envía POST y registra:
    - URL
    - JSON enviado
    - HTTP status
    - JSON recibido
    """

    registrar_json_api(
        nombre_api,
        f"REQUEST -> {url}",
        payload
    )

    response = requests.post(
        url,
        json=payload,
        timeout=timeout
    )

    try:
        response_data = response.json()
    except Exception:
        response_data = response.text

    color = None
    if response.status_code not in [200, 201]:
        color = "red"

    registrar_json_api(
        nombre_api,
        f"RESPONSE HTTP {response.status_code}",
        response_data,
        color
    )

    return response, response_data


def conduit_ok(response, response_json):
    """
    Valida una respuesta de Conduit.
    Importante: HTTP 200/201 no siempre significa que el comando interno fue OK.
    """
    try:
        if response.status_code not in [200, 201]:
            return False

        if not isinstance(response_json, dict):
            return False

        status_node = response_json.get("status", {})
        if isinstance(status_node, dict):
            code = str(status_node.get("code", "")).strip().upper()
            if code and code != "OK":
                return False

        transaction_responses = response_json.get("transaction_responses", [])
        if transaction_responses:
            for transaction in transaction_responses:
                command_responses = transaction.get("command_responses", [])

                for command_response in command_responses:
                    command_status = command_response.get("status", {})
                    if isinstance(command_status, dict):
                        code = str(command_status.get("code", "")).strip().upper()
                        if code and code != "OK":
                            return False

                    results = command_response.get("results", [])
                    for result in results:
                        result_status = str(result.get("status", "")).strip().upper()
                        if result_status and result_status != "OK":
                            return False

        return True

    except Exception as e:
        print(f"[WARNING] Error validando Conduit: {e}")
        return False


def traceability_tiene_step_fail(payload_traceability):
    """Revisa si el payload de Traceability tiene al menos una medición FAIL/FAILED."""
    try:
        steps_dict = payload_traceability.get("test_steps", {})
        steps_list = []

        for _, lista in steps_dict.items():
            if isinstance(lista, list):
                steps_list.extend(lista)

        return any(
            str(step.get("status", "")).strip().upper() in ["FAIL", "FAILED", "NOK"]
            for step in steps_list
        )

    except Exception as e:
        print(f"[WARNING] Error revisando steps de Traceability: {e}")
        return False


def normalizar_commit_screwing_st60(cadena_original):
    """
    Normaliza commits Screwing ST60.

    Soporta:
    1) Cadena completa:
       commit,Screwing,T,...,A,...,PX,...,PY,...,4,SERIAL,1/

    2) Cadena parcial:
       commit,Screwing,T,...,Comentario,,,,,,,,,,,,,,,,,,,,,,,,,4,SERIAL,1/

    En el caso parcial, completa A/PX/PY como dummy para que commands.py no falle.
    El número antes del serial se respeta como número de tornillo.
    """

    cadena_original = str(cadena_original).strip()

    if not cadena_original.startswith("commit,Screwing,"):
        return cadena_original

    # Cortar exactamente hasta 1/
    if "1/" in cadena_original:
        cadena_original = cadena_original[:cadena_original.index("1/") + 2]

    clean = cadena_original.rstrip(",")
    options = clean.split(",")

    if len(options) < 10:
        return cadena_original

    # Buscar serial y número de tornillo
    serial = ""
    numero_tornillo = ""

    serial_index = -1

    for i in range(len(options) - 1, -1, -1):
        item = str(options[i]).strip()

        if ":" in item and item != "1/":
            serial = item
            serial_index = i
            break

    if not serial:
        print("[NORMALIZAR SCREWING] No se encontró serial en la cadena.")
        return cadena_original

    if serial_index > 0:
        numero_tornillo = str(options[serial_index - 1]).strip()

    if not numero_tornillo:
        numero_tornillo = "1"

    # Si ya viene completa con T, A, PX, PY, solo asegurar coma final
    try:
        if (
            len(options) >= 37
            and options[2].strip().upper() == "T"
            and options[10].strip().upper() == "A"
            and options[18].strip().upper() == "PX"
            and options[26].strip().upper() == "PY"
        ):
            print("[NORMALIZAR SCREWING] Cadena completa detectada, se respeta estructura original.")
            return clean + ","
    except Exception:
        pass

    # Tomar bloque T real
    torque = options[2:10]

    if len(torque) != 8:
        print(f"[NORMALIZAR SCREWING] Bloque torque inválido: {torque}")
        return cadena_original

    if str(torque[0]).strip().upper() != "T":
        print(f"[NORMALIZAR SCREWING] La medición inicial no es T: {torque[0]}")
        return cadena_original

    # Bloques dummy para que commands.py reciba la estructura completa
    angle = ["A", "0", "0", "0", "Numeric", "degrees", "PASSED", "None"]
    px    = ["PX", "0", "0", "0", "Numeric", "mm", "PASSED", "None"]
    py    = ["PY", "0", "0", "0", "Numeric", "mm", "PASSED", "None"]

    nueva = (
        ["commit", "Screwing"]
        + torque
        + angle
        + px
        + py
        + [numero_tornillo, serial, "1/", ""]
    )

    cadena_normalizada = ",".join(nueva)

    print("[NORMALIZAR SCREWING] Cadena parcial normalizada:")
    print(cadena_normalizada)
    print(f"[NORMALIZAR SCREWING] Tornillo={numero_tornillo}")
    print(f"[NORMALIZAR SCREWING] len={len(cadena_normalizada.split(','))}")

    return cadena_normalizada


def obtener_keys_reales_screwing(cadena_commit):
    """
    Detecta qué mediciones fueron realmente enviadas por el PLC.

    Cada bloque Screwing tiene 8 campos:
    key,value,low,high,type,unit,result,metadata

    Se ignora solo si:
    - metadata viene vacío / None / NULL / N/A
    - value, low y high vienen vacíos o 0
    """

    keys_reales = set()

    def es_vacio_o_cero(valor):
        try:
            if valor is None:
                return True

            valor_str = str(valor).strip().upper()

            if valor_str in ["", "NONE", "NULL", "N/A"]:
                return True

            return float(valor_str) == 0.0

        except Exception:
            return False

    try:
        clean = str(cadena_commit).strip().rstrip(",")
        options = clean.split(",")

        if len(options) < 10:
            return keys_reales

        bloques = [
            options[2:10],    # T
            options[10:18],   # A
            options[18:26],   # PX
            options[26:34],   # PY
        ]

        for bloque in bloques:
            if len(bloque) != 8:
                continue

            key = str(bloque[0]).strip().upper()
            value = bloque[1]
            low_limit = bloque[2]
            high_limit = bloque[3]
            metadata = str(bloque[7]).strip().upper()

            metadata_vacia = metadata in ["", "NONE", "NULL", "N/A"]

            bloque_dummy = (
                metadata_vacia and
                es_vacio_o_cero(value) and
                es_vacio_o_cero(low_limit) and
                es_vacio_o_cero(high_limit)
            )

            if not bloque_dummy:
                keys_reales.add(key)

    except Exception as e:
        print(f"[WARNING] Error detectando keys reales Screwing: {e}")

    return keys_reales


def filtrar_table_data_screwing(table_data, cadena_commit):
    """
    Filtra la tabla visual para mostrar solo mediciones reales del PLC.

    Ejemplo:
    - Si el PLC solo manda T, la UI solo muestra T.
    - Si después manda T/A/PX/PY con metadata real, también aparecen.
    """
    if not table_data:
        return table_data

    keys_reales = obtener_keys_reales_screwing(cadena_commit)
    print(f"[DEBUG TABLE] Keys reales Screwing: {keys_reales}")

    if not keys_reales:
        return table_data

    table_filtrada = []

    for row in table_data:
        try:
            measurement = str(row[0]).strip().upper()

            if measurement in keys_reales:
                table_filtrada.append(row)

        except Exception:
            pass

    return table_filtrada


def commit_screwing_tiene_falla(cadena_commit):
    """
    Detecta si una cadena commit,Screwing trae una medición real FAILED.

    commands.commit() puede regresar PASSED cuando el guardado en BD fue correcto,
    pero eso no significa que la medición haya pasado. Esta función solo sirve
    para mostrar en UI/bitácora que la medición falló; el PLC debe recibir PASSED
    si el comando commit fue procesado correctamente.
    """

    def es_vacio_o_cero(valor):
        try:
            if valor is None:
                return True

            valor_str = str(valor).strip().upper()

            if valor_str in ["", "NONE", "NULL", "N/A"]:
                return True

            return float(valor_str) == 0.0

        except Exception:
            return False

    try:
        clean = str(cadena_commit).strip().rstrip(",")
        options = clean.split(",")

        bloques = [
            options[2:10],    # T
            options[10:18],   # A
            options[18:26],   # PX
            options[26:34],   # PY
        ]

        for bloque in bloques:
            if len(bloque) != 8:
                continue

            key = str(bloque[0]).strip().upper()
            value = bloque[1]
            low_limit = bloque[2]
            high_limit = bloque[3]
            result = str(bloque[6]).strip().upper()
            metadata = str(bloque[7]).strip().upper()

            metadata_vacia = metadata in ["", "NONE", "NULL", "N/A"]

            bloque_dummy = (
                metadata_vacia and
                es_vacio_o_cero(value) and
                es_vacio_o_cero(low_limit) and
                es_vacio_o_cero(high_limit)
            )

            if bloque_dummy:
                continue

            if result in ["FAILED", "FAIL", "NOK"]:
                print(f"[SCREWING COMMIT] Falla detectada en {key}")
                return True

        return False

    except Exception as e:
        print(f"[WARNING] Error revisando falla Screwing commit: {e}")
        return False


def configurar_logging():
    """Configura el sistema de logging"""
    
    # Crear directorio logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Nombre del archivo de log con fecha
    log_filename = f"logs/server_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Obtener logger root
    logger = logging.getLogger()
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Configurar nivel
    logger.setLevel(logging.DEBUG)
    
    # Crear formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler 1: Archivo diario (DEBUG y superior)
    file_handler_daily = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler_daily.setLevel(logging.DEBUG)
    file_handler_daily.setFormatter(formatter)
    logger.addHandler(file_handler_daily)
    
    # Handler 2: Archivo general (INFO y superior)
    file_handler_general = logging.FileHandler("logs/server.log", encoding='utf-8')
    file_handler_general.setLevel(logging.INFO)
    file_handler_general.setFormatter(formatter)
    logger.addHandler(file_handler_general)
    
    # Handler 3: Consola (INFO y superior)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Reducir verbosidad de algunas librerías
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("flet").setLevel(logging.WARNING)
    
    # Forzar escritura inicial
    logger.info("=" * 70)
    logger.info("🔄 LOGGING CONFIGURADO - INICIO DE APLICACIÓN")
    logger.info(f"📁 Archivo diario: {log_filename}")
    logger.info(f"📁 Archivo general: logs/server.log")
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Forzar flush
    for handler in logger.handlers:
        handler.flush()
    
    return logger

def keep_alive_database():
    """Mantiene viva la conexión a la base de datos"""
    try:
        # Ejecutar una consulta simple cada 5 minutos
        with conexion.conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        logging.debug("Keep-alive ejecutado")
    except Exception as e:
        logging.warning(f"Keep-alive falló: {e}")
        # Intentar reconectar
        try:
            conexion.db_manager._connect()
        except:
            pass
    
    # Programar próximo keep-alive (5 minutos)
    root.after(300000, keep_alive_database)

logger = configurar_logging()


# Variable global para manejar el cierre
running = True
client_threads = []

config_window = None 

active_connections = []  # Para guardar todos los sockets de cliente

month = datetime.today().month
day = datetime.today().day

host = socket.gethostbyname(socket.gethostname())
port = 49152

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(5)

server = conexion.server_connection()


######################################################## View #############################################
# Configuración inicial
ctk.set_appearance_mode("system") # Modo de apariencia: system, light, dark
ctk.set_default_color_theme("dark-blue") # Tema de color: blue, dark-blue, green
# Crear la ventana principal
root = ctk.CTk()
# root.geometry("1366x768")
try:
    if platform.system() == 'Windows':
        root.after(100, lambda: root.wm_state('zoomed'))  # maximiza ventana en Windows
    else:
        root.after(150, lambda: root.attributes('-zoomed', True))  # Linux/macOS

    # root.after(100, lambda: root.wm_state('zoomed'))  # Windows
    # root.after(150, lambda: root.attributes('-zoomed', True))  # Linux/macOS
except:
    root.attributes('-zoomed', True)
root.title("")
root.iconbitmap("favicon.ico")
root.grid_columnconfigure((0, 1), weight=1)
root.grid_rowconfigure(0, weight=1)

def safe_exit():
    global running, current_operator, config_data, login_window, logout_window

    print("Cerrando aplicación...")
    logging.info(f"Cerrando aplicación...")

    running = False

    # Cerrar conexiones activas
    for conn in active_connections:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception as e:
            print(f"Error al cerrar conexión: {e}")
            logging.error(f"Error al cerrar conexión: {e}")

    # Cerrar socket principal
    try:
        sock.close()
        print("Socket principal cerrado.")
        logging.info("Socket principal cerrado.")
    except Exception as e:
        print(f"Error al cerrar socket: {e}")
        logging.error(f"Error al cerrar socket: {e}")

    # Esperar que los hilos terminen
    for t in client_threads:
        if t.is_alive():
            t.join(timeout=2)  # Aquí el timeout puede ser 2 o más

    try:
        root.destroy()
    except Exception as e:
        print(f"Error cerrando ventana: {e}")
        logging.error(f"Error cerrando ventana: {e}")

    sys.exit()

# root.protocol("WM_DELETE_WINDOW", safe_exit)
# datos de la estación
ip_address = StringVar()
port_address = StringVar()
model_name = StringVar()
station_name = StringVar()
piece_name = StringVar()

# Crear frame principal
frame = ctk.CTkFrame(master=root)
frame.pack(pady=30, padx=60, fill="both", expand=True)

lbl_station = ctk.CTkLabel(master=frame, text='Station:')
lbl_station.pack(side=ctk.LEFT, pady=10, padx=40, anchor='nw')

entry_station = ctk.CTkEntry(master=frame, width=300, justify="center", state="readonly", textvariable=station_name)
entry_station.pack(side=ctk.LEFT, pady=10, padx=0, anchor='nw')

lbl_model = ctk.CTkLabel(master=frame, text='Model:')
lbl_model.pack(side=ctk.LEFT, pady=10, padx=50, anchor='n')
entry_model = ctk.CTkEntry(master=frame, width=300, justify="center", state="readonly", textvariable=model_name)
entry_model.pack(side=ctk.LEFT, pady=10, padx=0, anchor='n')
        
lbl_ip_address = ctk.CTkLabel(master=frame, text='IP Address:')
lbl_ip_address.pack(side=ctk.LEFT, pady=10, padx=50, anchor='ne')

entry_ip_address = ctk.CTkEntry(master=frame, width=110, justify="center", state="readonly", textvariable=ip_address)
entry_ip_address.pack(side=ctk.LEFT, pady=10, padx=5, anchor='ne')
ip_address.set(host)

lbl_union = ctk.CTkLabel(master=frame, text=':')
lbl_union.pack(side=ctk.LEFT, pady=10, padx=0, anchor='ne')

entry_port = ctk.CTkEntry(master=frame, width=50, justify="center", state="readonly", textvariable=port_address)
entry_port.pack(side=ctk.LEFT, pady=10, padx=5, anchor='ne')
port_address.set(port)

lbl_piece = ctk.CTkLabel(master=frame, text='Piece:')
lbl_piece.place(x=450, y=60)

entry_piece = ctk.CTkEntry(master=frame, width=300, justify="center", state="readonly")
entry_piece.place(x=500, y=60)

texto = ctk.CTkTextbox(master=frame, height=230, width=700, state="disabled")
texto.place(x=50, y=150)
font=ctk.CTkFont(family='Arial', size=16)

lbl_comand = ctk.CTkLabel(master=frame, text='Command:')


lbl_comand.place(x=780, y=150)
# Load the image 
image_green = ctk.CTkImage(light_image=Image.open('verde.png'),
                                    dark_image=Image.open('verde.png'),
                                    size=(30, 30))
image_red = ctk.CTkImage(light_image=Image.open('rojo.png'),
                                    dark_image=Image.open('rojo.png'),
                                    size=(30, 30))

image_green_full = ctk.CTkImage(light_image=Image.open('verde_relleno.png'),
                                    dark_image=Image.open('verde_relleno.png'),
                                    size=(30, 30))

image_red_full = ctk.CTkImage(light_image=Image.open('rojo_relleno.png'),
                                    dark_image=Image.open('rojo_relleno.png'),
                                    size=(30, 30))
green_label = ctk.CTkLabel(master=frame, image=image_green, text="")
green_label.place(x=850, y=150)

pass_label = ctk.CTkLabel(master=frame, text="Pass")
pass_label.place(x=885, y=150)

red_label = ctk.CTkLabel(master=frame, image=image_red, text="")
red_label.place(x=930, y=150)

fail_label = ctk.CTkLabel(master=frame, text="Fail")
fail_label.place(x=970, y=150)

def ShowLabel(event=None): # Mostrar los widgets por medio de esta función al hacer clic
    button_hide.place(x=850, y=200)
    texto.place(x=50, y=150)
    green_label.place(x=850, y=150)
    pass_label.place(x=885, y=150)
    red_label.place(x=930, y=150)
    fail_label.place(x=970, y=150)
    lbl_comand.place(x=780, y=150)
    button_show.place_forget()

def HideLabel(event=None): # Ocultar los widgets por medio de esta función al hacer clic
    button_hide.place_forget()
    texto.place_forget()
    lbl_comand.place(x=500, y=150)
    button_show.place(x=570, y=200)
    green_label.place(x=570, y=150)
    pass_label.place(x=605, y=150)
    red_label.place(x=650, y=150)
    fail_label.place(x=690, y=150)


button_hide = ctk.CTkButton(master=frame, text="Hide", width=80, command=HideLabel)
button_hide.place(x=850, y=200)

button_show = ctk.CTkButton(master=frame, text="Show", width=80, command=ShowLabel) 

# lbl_history = ctk.CTkLabel(master=frame, text='History:')
# lbl_history.place(x=80, y=310)

image_tesla = ctk.CTkImage(light_image=Image.open('tesla.png'),
                                    dark_image=Image.open('tesla.png'),
                                    size=(120, 80))

image_amc = ctk.CTkImage(light_image=Image.open('amc.png'),
                                    dark_image=Image.open('amc.png'),
                                    size=(120, 28))

tesla_label = ctk.CTkLabel(master=frame, image=image_tesla, text="")
tesla_label.place(x=1120, y=520)

amc_label = ctk.CTkLabel(master=frame, image=image_amc, text="")
amc_label.place(x=1120, y=610)

# button_tcp = ctk.CTkButton(master=frame, text="TCP/IP", width=80)
# button_tcp.place(x=1050, y=250)


label_user = ctk.CTkLabel(master=frame, text="User:")
#label_user.place(x=1050, y=250)

label_users = ctk.CTkLabel(master=frame, text="Admin")
# label_users.place(x=1090, y=250)

headers = [["Measurement","Value","Lower limit","Upper limit","Type","Unit","Result"]]

# table = CTkTable(master=frame, row=8, column=7, header_color="#1f618d", values= headers)
# table.pack(expand=False, fill="both", padx=10, pady=10)
# table.configure(width=150)
# table.place(x=50, y=390)

########################################################
# CLASE PARA MANEJO SEGURO DE LA TABLA
########################################################
class SafeTableManager:
    """Versión simplificada con scrollbar automático"""
    def __init__(self, master_frame, x=50, y=390, width=900, height=300):
        self.master_frame = master_frame
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.header = [["Measurement","Value","Lower limit","Upper limit","Type","Unit","Result"]]
        self.data = []
        
        # Crear frame scrollable (CustomTkinter lo maneja automáticamente)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            master=master_frame,
            width=width,
            height=height,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_button_color="#012c49",
            scrollbar_button_hover_color="#012c49"
        )
        self.scrollable_frame.place(x=x, y=y)
        
        # Crear tabla inicial
        self._create_initial_table()
    
    def _create_initial_table(self):
        """Crea la tabla inicial con solo el header"""
        # Limpiar frame si tiene widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.table = CTkTable(
            master=self.scrollable_frame,
            row=1,  # Solo header
            column=7,
            header_color="#1f618d",
            values=self.header
        )
        
        self.table.edit_row(0, text_color="white")
        # Empaquetar tabla
        self.table.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Configurar columnas
        col_width = (self.width - 40) // 7  # -40 para padding y scrollbar
        for i in range(7):
            try:
                self.table.configure_column(i, width=col_width)
            except:
                pass
    
    def add_data(self, new_data):
        """Agrega datos a la tabla"""
        if not new_data:
            return
        
        # Agregar datos
        if isinstance(new_data[0], list):
            self.data.extend(new_data)
        else:
            self.data.append(new_data)
        
        # Actualizar en hilo principal
        root.after(0, self._update_display)
    
    def clear(self):
        """Limpia la tabla"""
        self.data = []
        root.after(0, self._create_initial_table)  # Volver al estado inicial
    
    def _update_display(self):
        """Actualiza la visualización"""
        try:
            # Preparar todos los datos
            all_data = self.header + self.data
            
            # Destruir tabla anterior
            self.table.destroy()
            
            # Crear nueva tabla con todos los datos
            self.table = CTkTable(
                master=self.scrollable_frame,
                row=len(all_data),
                column=7,
                header_color="#1f618d",
                values=all_data
            )
            
            self.table.edit_row(0, text_color="white")
            # Empaquetar
            self.table.pack(fill="x", expand=False, padx=5, pady=5)
            
            # Configurar columnas
            col_width = (self.width - 40) // 7
            for i in range(7):
                try:
                    self.table.configure_column(i, width=col_width)
                except:
                    pass
            
            # Mostrar información si hay muchas filas
            if len(self.data) > 20:
                safe_insert(f"[TABLE] {len(self.data)} rows (scroll to see all)\n", "blue")
                
        except Exception as e:
            print(f"[TABLE ERROR] {e}")

# Crear el manejador
table_manager = SafeTableManager(frame)

# Crear el manejador seguro de tabla
# table_manager = SafeTableManager()

########################################################
# FUNCIONES DE MANEJO DE TABLA
########################################################
def update_table_with_data(new_data):
    """Actualiza la tabla con nuevos datos de forma segura"""
    table_manager.add_data(new_data)

def clear_table_data():
    """Limpia la tabla de forma segura"""
    table_manager.clear()

####################################################################################################################################################################################
exit_event = threading.Event()

MAX_LINES = 100

def safe_insert(msg, text_color=None):
    # Determinar modo actual: "Dark" o "Light"
    mode = ctk.get_appearance_mode().lower()

    # Elegir color adecuado
    if isinstance(text_color, (tuple, list)) and len(text_color) == 2:
        color = text_color[1] if mode == "dark" else text_color[0]
    elif isinstance(text_color, str):
        color = text_color
    else:
        color = "white" if mode == "dark" else "black"

    # Limpiar todo el contenido anterior
    texto.configure(state="normal", font=font, text_color=color)
    texto.delete("1.0", ctk.END)  # Elimina todo
    texto.insert(ctk.END, msg + "\n")
    texto.see("end")
    texto.configure(state="disabled")


def worker(conn, addr):
    global SERIAL_PADRE_GLOBAL, PART_NUMBER_GLOBAL, PART_NUMBER, COMPONENT, component_sn, MEASUREMENT_KEY_GLOBAL, START_SCREWING_ID_GLOBAL    
    cadena = ""
    pieza = ""
    contador = 0
    part_number_parentage = ""
    serial_number_parentage = ""
    heater_part_number = ""

    try:
        stationName_data = conexion.model()
        print(stationName_data)
        stationName = stationName_data[2][0]
        modelName = stationName_data[1][1]
        model_name.set(modelName)
        station_name.set(stationName)
        safe_insert("PLC - Connected"+"\n")
        logging.info("PLC - Connected")
        green_label.configure(image=image_green_full)
        red_label.configure(image=image_red)
        conn.settimeout(5)  
        login_required_shown = False

        while True:
            try:
                datos = conn.recv(32768)
                if not datos:
                    raise ConnectionResetError("Cliente desconectado")
            except socket.timeout:
                continue
            except ConnectionResetError:
                safe_insert("PLC - Disconnected"+"\n", "red")
                logging.info("PLC - Disconnected")
                conexionBitacora.event("CDBF-001","Command received PLC-Disconnected",month,day)
                exit_event.set()
                break
            except Exception as e:
                safe_insert(f"Error conexión: {e}\n", "red")
                logging.error(f"Error conexión: {e}\n")
                exit_event.set()
                break
            
            datos = datos.replace(b'\x00', b'')
            cadena += datos.decode('utf-8')

            while "1/" in cadena:
                index = cadena.index("1/") + 2
                comando_completo = cadena[:index]
                cadena = cadena[index:]  

                option = comando_completo.strip().split(',')

                match option[0]:

                    case "start":
                        entry_piece.focus_set()
                        clear_table_data()
                        COMPONENT = ""
                        scanned_component = ""

                        config_local = conexion.configurador_st60()
                        if config_local and config_local != "FAILED" and len(config_local) >= 5:
                            program_version = str(config_local[0]).strip()
                            machine_id      = str(config_local[1]).strip()
                            process_name    = str(config_local[2]).strip()
                            client_id_db    = str(config_local[3]).strip()
                            operator_id     = str(config_local[4]).strip()
                        else:
                            machine_id      = ""
                            operator_id     = ""
                            process_name    = ""
                            client_id_db    = ""
                            program_version = ""

                        interlocking_ok = False

                        if len(option) == 2 and option[-1] == '1/':
                            entry_piece.configure(state=ctk.NORMAL, textvariable=piece_name)
                            piece_name.set("")
                            safe_insert("🔍 SCAN: Scan Heatsink Label (PN:SERIAL)", "green")
                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)

                            try:
                                start_time_scan = time.time()
                                heatsink_scanned = False
                                error_detectado  = False

                                while not heatsink_scanned:
                                    name_piece   = entry_piece.get().strip()
                                    time.sleep(0.05)
                                    elapsed_time = time.time() - start_time_scan

                                    if len(name_piece) == 0:
                                        if elapsed_time >= 240:
                                            entry_piece.configure(state="readonly", textvariable=piece_name)
                                            piece_name.set("")
                                            safe_insert("Timeout waiting for Heatsink scan.", "red")
                                            conn.send("reset".encode('UTF-8'))
                                            error_detectado = True
                                            break
                                        continue

                                    if len(name_piece) > 13:
                                        entry_piece.configure(state="disabled")

                                        if ":" in name_piece:
                                            partes_etiqueta = name_piece.split(":")
                                            
                                            prefijo = str(partes_etiqueta[0]).strip()
                                            if prefijo.upper().startswith("P"):
                                                prefijo = prefijo[1:]
                                            PART_NUMBER_GLOBAL  = "LFTM" + prefijo
                                            
                                            SERIAL_PADRE_GLOBAL = str(name_piece).strip()
                                            PART_NUMBER         = PART_NUMBER_GLOBAL
                                            
                                            safe_insert(f"✅ Extracción Manual OK -> PN: {PART_NUMBER_GLOBAL}  Serial: {SERIAL_PADRE_GLOBAL}", "green")
                                            heatsink_scanned = True
                                        else:
                                            entry_piece.configure(state=ctk.NORMAL)
                                            entry_piece.delete(0, ctk.END)
                                            safe_insert("❌ Formato de etiqueta inválido. Debe contener ':'", "red")
                                            conn.send("FAILED".encode('UTF-8'))
                                            error_detectado = True
                                            break

                                if error_detectado or not heatsink_scanned:
                                    break

                                entry_piece.configure(state=ctk.NORMAL)
                                entry_piece.delete(0, ctk.END)
                                piece_name.set("")

                                safe_insert("\n🔍 SCAN 2/2: Scan Component Serial Number", "green")
                                start_time_comp = time.time()
                                comp_scanned = False

                                while not comp_scanned:
                                    scanned_component = entry_piece.get().strip()
                                    time.sleep(0.05)
                                    elapsed_comp = time.time() - start_time_comp

                                    if len(scanned_component) == 0:
                                        if elapsed_comp >= 240:
                                            piece_name.set("")
                                            safe_insert("Timeout waiting for Component scan.", "red")
                                            conn.send("reset".encode('UTF-8'))
                                            error_detectado = True
                                            break
                                        continue

                                    if len(scanned_component) > 13:
                                        entry_piece.configure(state="disabled")
                                        COMPONENT = scanned_component
                                        safe_insert(f"✅ Component Registered: {COMPONENT}", "green")
                                        comp_scanned = True

                                if error_detectado or not comp_scanned:
                                    break

                                url_interlocking = conexion.obtener_url(2)
                                if not url_interlocking or url_interlocking == "FAILED":
                                    safe_insert("❌ Error obteniendo URL Interlocking de DB.", "red")
                                    conn.send("FAILED".encode('UTF-8'))
                                    break

                                payload_interlocking = interlocking_json.interlocking_st60(
                                    parent_serial_number = SERIAL_PADRE_GLOBAL,
                                    parent_part_number   = PART_NUMBER_GLOBAL
                                )

                                try:
                                    response_interlocking, data_interlocking = post_api_debug(
                                        nombre_api="INTERLOCKING",
                                        url=url_interlocking,
                                        payload=payload_interlocking,
                                        timeout=30
                                    )

                                    if not isinstance(data_interlocking, dict):
                                        data_interlocking = {}
                                    
                                    if response_interlocking.status_code != 200 or not data_interlocking.get("success", False):
                                        safe_insert("❌ Interlocking rechazó el ciclo.", "red")
                                        conn.send("FAILED".encode('UTF-8'))
                                        break

                                    interlocking_ok = True

                                except Exception as err_int:
                                    safe_insert(f"❌ HTTP Error Interlocking: {err_int}", "red")
                                    conn.send("FAILED".encode('UTF-8'))
                                    break

                                # --- LLAMADA A CONDUIT ---
                                url_conduit = conexion.obtener_url(4)
                                if not url_conduit or url_conduit == "FAILED":
                                    safe_insert("❌ Error obteniendo URL Conduit de DB.", "red")
                                    conn.send("FAILED".encode('UTF-8'))
                                    break

                                payload_conduit_amk = {
                                    "version":      "1.0",
                                    "keep_alive":   False,
                                    "refresh_unit": True,
                                    "source": {
                                        "workstation": {
                                            "station": process_name,
                                            "type":    "Process"
                                        },
                                        "client_id": client_id_db,
                                        "employee":  operator_id,
                                        "password":  ""
                                    },
                                    "transactions": [
                                        {
                                            "unit": {"unit_id": SERIAL_PADRE_GLOBAL},
                                            "commands": [{"name": "AddMeasurementKey"}]
                                        }
                                    ]
                                }

                                try:
                                    response_conduit, res_conduit_json = post_api_debug(
                                        nombre_api="CONDUIT ADD MEASUREMENT KEY",
                                        url=url_conduit,
                                        payload=payload_conduit_amk,
                                        timeout=30
                                    )

                                    if not isinstance(res_conduit_json, dict):
                                        res_conduit_json = {}

                                    status_node = res_conduit_json.get("status", {})
                                    if response_conduit.status_code == 200 and status_node.get("code") == "OK":

                                        
                                        conn.send(f"{SERIAL_PADRE_GLOBAL}, PASSED".encode('UTF-8'))

                                        parte_existente = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                        if not parte_existente or parte_existente == "FAILED":
                                            conexion.piece_store(SERIAL_PADRE_GLOBAL)

                                        try:
                                            if hasattr(conexion, "obtener_ultimo_id_screwing"):
                                                START_SCREWING_ID_GLOBAL = conexion.obtener_ultimo_id_screwing(SERIAL_PADRE_GLOBAL)
                                            else:
                                                START_SCREWING_ID_GLOBAL = 0

                                            print(
                                                f"[CICLO ST60] Inicio de ciclo. "
                                                f"Último ID Screwing previo: {START_SCREWING_ID_GLOBAL}"
                                            )

                                        except Exception as e:
                                            START_SCREWING_ID_GLOBAL = 0
                                            print(f"[CICLO ST60 WARNING] No se pudo obtener último ID Screwing: {e}")

                                        try:
                                            parte_actual = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                            station_actual = conexion.stations()

                                            if parte_actual and parte_actual != "FAILED" and station_actual:
                                                part_id = parte_actual[0]
                                                station_id = station_actual[0]

                                                if hasattr(conexion, "duration_start_st60"):
                                                    conexion.duration_start_st60(station_id, part_id)

                                                print(f"[DURATION] Inicio registrado station_id={station_id} part_id={part_id}")

                                        except Exception as e:
                                            print(f"[DURATION WARNING] No se pudo iniciar duration: {e}")

                                        conexionBitacora.event("SPP-001", f"Parent: {SERIAL_PADRE_GLOBAL}", month, day)
                                        piece_name.set(SERIAL_PADRE_GLOBAL)
                                        entry_piece.configure(state="readonly")
                                        green_label.configure(image=image_green_full)
                                        break

                                    else:
                                        safe_insert("❌ Conduit AddMeasurementKey Error.", "red")
                                        conn.send("FAILED, CONDUIT ERROR".encode('UTF-8'))
                                        break

                                except Exception as err_cd:
                                    safe_insert(f"❌ Exception Conduit: {err_cd}", "red")
                                    conn.send("FAILED, CONDUIT OFFLINE".encode('UTF-8'))
                                    break

                            except Exception as e:
                                entry_piece.configure(state=ctk.NORMAL)
                                safe_insert(f"❌ Exception Caught: {str(e)}", "red")
                                break

                        elif len(option) >= 3 and option[-1] == '1/':
                            name_piece = str(option[1]).strip()

                            try:
                                if ":" in name_piece:
                                    partes_etiqueta = name_piece.split(":")
                                    
                                    prefijo = str(partes_etiqueta[0]).strip()
                                    if prefijo.upper().startswith("P"):
                                        prefijo = prefijo[1:]
                                    PART_NUMBER_GLOBAL  = "LFTM" + prefijo
                                    
                                    SERIAL_PADRE_GLOBAL = str(name_piece).strip()
                                    PART_NUMBER         = PART_NUMBER_GLOBAL

                                    safe_insert(f"✅ Extracción PLC OK -> PN: {PART_NUMBER_GLOBAL}  Serial: {SERIAL_PADRE_GLOBAL}", "green")
                                else:
                                    safe_insert("❌ Error: La cadena enviada por el PLC no contiene ':' para separar PN y Serial", "red")
                                    conn.send("FAILED".encode('UTF-8'))
                                    break

                                # --- LLAMADA A INTERLOCKING ---
                                urls = conexion.obtener_url_api()

                                url_interlocking = urls[1][0]

                                payload_interlocking = interlocking_json.interlocking_st60(
                                    parent_serial_number = SERIAL_PADRE_GLOBAL,
                                    parent_part_number   = PART_NUMBER_GLOBAL
                                )

                                response_interlocking, data_interlocking = post_api_debug(
                                    nombre_api="INTERLOCKING",
                                    url=url_interlocking,
                                    payload=payload_interlocking,
                                    timeout=30
                                )

                                if not isinstance(data_interlocking, dict):
                                    data_interlocking = {}

                                # interlocking_json = response_interlocking.json()

                                if response_interlocking.status_code != 200 or not data_interlocking.get("success", False):
                                    conexionBitacora.event("SPP-002","|Command received| "+comando_completo+" part: "+name_piece+" "+str(data_interlocking.get("message", "")),month,day)
                                    conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)

                                    safe_insert(f"Command received-> {comando_completo} part: {name_piece}\nCommand FAILED\nUnit API response for {name_piece}: {json.dumps(response_interlocking, indent=4)}\nExtracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\nInterlocking JSON: {json.dumps(payload_interlocking, indent=4)}\nResponse: {json.dumps(conduit_json, indent=4)}", "red")
                                    logging.error(f"Command received-> {comando_completo} part: {name_piece}\nCommand FAILED\nUnit API response for {name_piece}: {json.dumps(response_interlocking, indent=4)}\nExtracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\nInterlocking JSON: {json.dumps(payload_interlocking, indent=4)}\nResponse: {json.dumps(conduit_json, indent=4)}")

                                    conn.send("FAILED".encode('UTF-8'))

                                    break

                                # --- LLAMADA A CONDUIT ---
                                url_conduit          = urls[3][0]
                                payload_conduit_amk  = {
                                    "version":      "1.0", "keep_alive": False, "refresh_unit": True,
                                    "source": {
                                        "workstation": {"station": process_name, "type": "Process"},
                                        "client_id":   client_id_db,
                                        "employee":    operator_id,
                                        "password":    ""
                                    },
                                    "transactions": [
                                        {
                                            "unit":      {"unit_id": SERIAL_PADRE_GLOBAL},
                                            "commands": [{"name": "AddMeasurementKey"}]
                                        }
                                    ]
                                }

                                response_conduit, res_conduit_json = post_api_debug(
                                    nombre_api="CONDUIT ADD MEASUREMENT KEY",
                                    url=url_conduit,
                                    payload=payload_conduit_amk,
                                    timeout=30
                                )

                                conduit_json = response_conduit.json()

                                if response_conduit.status_code == 200:
                                    conduit_json_response = conduit_json.get("transaction_responses", [])
                                    
                                    measkey = conduit_json_response[0]["command_responses"][0]["results"][0]["data"]["measurement_key"]

                                    entry_piece.configure(state="readonly", textvariable=piece_name)
                                    piece_name.set(SERIAL_PADRE_GLOBAL)
    
                                    parte_existente = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                    if parte_existente == "FAILED":
                                        conexion.piece_store2(SERIAL_PADRE_GLOBAL,measkey)

                                    conn.send(f"PASSED".encode('UTF-8'))
                                    conexionBitacora.event("SPP-001",f"|Command received| {comando_completo} part: {name_piece} - Route check passed", month,day)
                                    conexionBitacora.event("CHKROUTE-001",f"Route check passed for ISN: {name_piece}",month, day)
                                    conexionBitacora.event("CMD-P001", "|Command,PASSED|", month, day)

                                    safe_insert(f'''Command received-> {comando_completo} \npart: {name_piece}\nCommand PASSED\n
                                    Unit API response for {name_piece}: {json.dumps(conduit_json, indent=4)}\n
                                    Extracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\n
                                    Interlocking JSON: {json.dumps(payload_interlocking, indent=4)}\n
                                    Conduit JSON: {json.dumps(payload_conduit_amk, indent=4)}''', "green")

                                    logging.info(f'''Command received-> {comando_completo} \npart: {name_piece}\nCommand PASSED\n
                                    Unit API response for {name_piece}: {json.dumps(conduit_json, indent=4)}\n
                                    Extracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\n
                                    Interlocking JSON: {json.dumps(payload_interlocking, indent=4)}\n
                                    Conduit JSON: {json.dumps(payload_conduit_amk, indent=4)}''')

                                    green_label.configure(image=image_green_full)
                                    red_label.configure(image=image_red)
                                    break
                                else:
                                    conexionBitacora.event("SPP-002","|Command received| "+comando_completo+" part: "+name_piece,month,day)
                                    conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)

                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)

                                    safe_insert(f"Command received-> {comando_completo} part: {name_piece}\nCommand FAILED\nUnit API response for {name_piece}: {json.dumps(response_conduit, indent=4)}\nExtracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\nInterlocking JSON: {json.dumps(interlocking_json, indent=4)}\nResponse: {json.dumps(conduit_json, indent=4)}\nConduit JSON: {json.dumps(payload_conduit_amk, indent=4)}", "red")
                                    logging.error(f"Command received-> {comando_completo} part: {name_piece}\nCommand FAILED\nUnit API response for {name_piece}: {json.dumps(response_conduit, indent=4)}\nExtracted from Unit API - Part Number: {PART_NUMBER_GLOBAL}\nInterlocking JSON: {json.dumps(interlocking_json, indent=4)}\nResponse: {json.dumps(conduit_json, indent=4)}\nConduit JSON: {json.dumps(payload_conduit_amk, indent=4)}")
                                    conn.send("FAILED".encode('UTF-8'))
                                    break

                            except Exception as e:
                                safe_insert(f"❌ Exception: {str(e)}", "red")
                                logging.error(f"Error en case start PLC: {str(e)}")
                                conn.send("FAILED".encode('UTF-8'))
                                break
                        cadena = ""

                    case "verify":
                        pieza_padre = piece_name.get()
                        
                        if hasattr(conexion, 'verificar_cantidad_componentes'):
                            qty_ok = conexion.verificar_cantidad_componentes(pieza_padre)
                        else:
                            qty_ok = True
                        
                        if not qty_ok:
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            safe_insert("Verify Failed: Componentes incompletos.", "red")
                            logging.warning("Verify Failed: Componentes incompletos.")
                        else:
                            url_interlock = conexion.obtener_url_api()
                            res_interlock = interlocking_json.ejecutar(SERIAL_PADRE_GLOBAL, PART_NUMBER_GLOBAL, url_interlock)
                            if res_interlock == "SUCCESS":
                                try:
                                    conn.send("SUCCESS".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                safe_insert("Verify & Interlocking: SUCCESS", "green")
                            else:
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                safe_insert("Interlocking API Denied", "red")
                            try:
                                conn.send("SUCCESS".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            safe_insert("Verify & Interlocking: SUCCESS", "green")
                        cadena = ""

                    case "end_process":
                        print("\n[END PROCESS] Iniciando evaluación...")

                        socket_status_raw = "PASSED"
                        tornillo_afectado = ""
                        intento_actual = 1
                        serial_plc = SERIAL_PADRE_GLOBAL

                        cadena_original = ""
                        for item in option:
                            cadena_original += str(item) + ","

                        try:
                            if len(option) == 0 or option[-1] != "1/":
                                safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    "Command FAILED - formato end_process inválido\n",
                                    "red"
                                )

                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event("END-F001", "END_PROCESS,FAILED,FORMATO_INVALIDO", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                            socket_status_raw = str(option[1]).strip().upper() if len(option) > 1 else "PASSED"
                            tornillo_afectado = str(option[2]).strip().upper() if len(option) > 2 else ""
                            
                            if tornillo_afectado.isdigit():
                                tornillo_afectado = f"TORNILLO_{tornillo_afectado}"

                            raw_intento = str(option[3]).strip().lower() if len(option) > 3 else "1"
                            raw_intento = raw_intento.replace("intento", "").strip()

                            try:
                                intento_actual = int(raw_intento)
                            except ValueError:
                                intento_actual = 1

                            serial_plc = str(option[4]).strip() if len(option) > 4 else SERIAL_PADRE_GLOBAL

                            # Normalizar status
                            if socket_status_raw in ["FAILED", "FAIL", "NOK"]:
                                socket_status_raw = "FAILED"
                            elif socket_status_raw in ["PASSED", "PASS", "OK"]:
                                socket_status_raw = "PASSED"
                            else:
                                socket_status_raw = "FAILED"

                            print(
                                f"[DEBUG] Status: {socket_status_raw}  "
                                f"Tornillo: {tornillo_afectado}  "
                                f"Intento: {intento_actual}  "
                                f"Serial PLC: {serial_plc}"
                            )

                            if not SERIAL_PADRE_GLOBAL:
                                safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    "Command FAILED - No hay serial activo. Ejecuta START primero.\n",
                                    "red"
                                )

                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event("END-F002", "END_PROCESS,FAILED,SIN_SERIAL_ACTIVO", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                            if serial_plc and serial_plc != SERIAL_PADRE_GLOBAL:
                                print(
                                    f"[WARNING] Serial PLC diferente al global. "
                                    f"PLC={serial_plc} GLOBAL={SERIAL_PADRE_GLOBAL}"
                                )

                            # Obtener URLs
                            urls = conexion.obtener_url_api()
                            if urls == None:
                                safe_insert("[END PROCESS] No se encontró URL de Traceability\n", "red")
                                conn.send("FAILED".encode("UTF-8"))
                                break

                            url_traceability = urls[2][0]
                            url_conduit = urls[3][0]

                            # Máximo de intentos ST60
                            # Primero intenta tomarlo desde DB.
                            # Si falla o no existe tabla attempts, usa 3 como respaldo.
                            try:
                                max_intentos = int(conexion.obtener_max_attempts())

                                if max_intentos <= 0:
                                    max_intentos = 3

                            except Exception as e:
                                print(f"[WARNING] No se pudo obtener max_intentos desde DB. Usando 3. Error: {e}")
                                max_intentos = 3

                            if intento_actual < 1:
                                intento_actual = 1

                            print(
                                f"[REINTENTO ST60] Tornillo={tornillo_afectado} "
                                f"Intento PLC={intento_actual}/{max_intentos}"
                            )
                            atributos_map = {}

                            try:
                                atributos = conexion.select_attributes_st50_80()

                                for attr in atributos:
                                    try:
                                        # select_attributes_st50_80() regresa:
                                        # attr[0] = attribute_id
                                        # attr[1] = name
                                        # attr[2] = unit
                                        # attr[3] = lower_limit
                                        # attr[4] = upper_limit
                                        # attr[5] = defect_code
                                        # attr[6] = defect_code_high

                                        nombre_attr = str(attr[1]).strip()
                                        key_name = nombre_attr.lower()

                                        config_attr = {
                                            "name": nombre_attr,
                                            "unit": str(attr[2]).strip() if len(attr) > 2 and attr[2] is not None else "",
                                            "lower_limit": float(attr[3]) if len(attr) > 3 and attr[3] is not None else None,
                                            "upper_limit": float(attr[4]) if len(attr) > 4 and attr[4] is not None else None,
                                            "defect_code_low": str(attr[5]).strip() if len(attr) > 5 and attr[5] is not None else "",
                                            "defect_code_high": str(attr[6]).strip() if len(attr) > 6 and attr[6] is not None else "",
                                        }

                                        aliases = [
                                            key_name,
                                            key_name.replace("_", " "),
                                            key_name.replace(" ", "_"),
                                            key_name.split(" ")[0],
                                            key_name.split("_")[0],
                                        ]

                                        for alias in aliases:
                                            if alias:
                                                atributos_map[alias] = config_attr

                                    except Exception as e:
                                        print(f"[WARNING] Error cargando atributo {attr}: {e}")

                                print("\n========== ATRIBUTOS MAP ==========")
                                for k, v in atributos_map.items():
                                    print(
                                        f"{k} -> "
                                        f"LOW={v.get('defect_code_low')}  "
                                        f"HIGH={v.get('defect_code_high')}"
                                    )
                                print("==================================\n")

                            except Exception as e:
                                print(f"[WARNING] No se pudieron cargar atributos: {e}")

                            # Consultar estado actual de screwing desde BD
                            # Solo toma registros posteriores al START actual.
                            # Si hay reintentos del mismo tornillo, toma el último registro.
                            all_screwing_attempts = conexion.screwing_current_state(
                                SERIAL_PADRE_GLOBAL,
                                START_SCREWING_ID_GLOBAL
                            )

                            print(f"[DEBUG] screwing_current_state: {len(all_screwing_attempts)} registros encontrados.")

                            print("\n========== ESTADO ACTUAL SCREWING ==========")
                            for row in all_screwing_attempts:
                                try:
                                    print(
                                        f"ID={row[0]}  VALUE={row[1]}  LOW={row[2]}  HIGH={row[3]}  "
                                        f"RESULT={row[6]}  DESCRIPTION={row[10]}"
                                    )
                                except Exception:
                                    print(row)
                            print("============================================\n")

                            if not all_screwing_attempts:
                                safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    "Command FAILED - No hay mediciones screwing guardadas\n",
                                    "red"
                                )

                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event("END-F003", "END_PROCESS,FAILED,SIN_MEDICIONES", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                            # Fecha UTC para Traceability
                            now_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

                            measkey_data = conexion.obtener_parte2(option[-2])
                            measkey_data = measkey_data[4]
                            # Crear JSON Traceability
                            payload_traceability = traceability_json.traceability_st60(
                                serial_padre=SERIAL_PADRE_GLOBAL,
                                part_number_padre=PART_NUMBER_GLOBAL,
                                measurement_key=measkey_data,
                                all_screwing_attempts=all_screwing_attempts,
                                atributos_map=atributos_map,
                                now_utc=now_utc,
                                machine_id=machine_id,
                                operator_id=operator_id,
                                process_name=process_name,
                                password=""
                            )

                            # Si el PLC manda FAILED, el JSON no puede salir como PASS.
                            try:
                                hay_step_fail = traceability_tiene_step_fail(payload_traceability)

                                if socket_status_raw == "FAILED":
                                    payload_traceability["status"] = "FAIL"

                                    if not hay_step_fail:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "TRACEABILITY BLOQUEADO: end_process viene FAILED, "
                                            "pero no se encontró ninguna medición FAIL con datos.\n" +
                                            "Revisa que el commit del reintento se haya recibido y guardado antes del end_process.\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY NO ENVIADO",
                                                request=payload_traceability,
                                                response=None
                                            ),
                                            "red"
                                        )

                                        print("[ERROR] Payload Traceability sin step FAIL:")
                                        print(json_pretty(payload_traceability))

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)
                                        break

                                elif socket_status_raw == "PASSED":
                                    if hay_step_fail:
                                        payload_traceability["status"] = "FAIL"
                                    else:
                                        payload_traceability["status"] = "PASS"

                            except Exception as e:
                                safe_insert(f"Error validando payload Traceability: {e}", "red")
                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as send_error:
                                    safe_insert(f"Error enviando: {send_error}", "red")
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                            if socket_status_raw == "FAILED" and intento_actual < max_intentos:
                                print(
                                    f"[FLUJO ST60] Reintento de tornillo. "
                                    f"Se enviará Traceability + RecordDefect + RepairAllDefects. "
                                    f"NO se enviará Conduit End. Intento {intento_actual}/{max_intentos}"
                                )
                            elif socket_status_raw == "FAILED" and intento_actual >= max_intentos:
                                print(
                                    f"[FLUJO ST60] Último intento fallido. "
                                    f"Se enviará Traceability + RecordDefect + Conduit End. "
                                    f"Intento {intento_actual}/{max_intentos}"
                                )
                            else:
                                print("[FLUJO ST60] Pieza PASSED. Se enviará Traceability + Conduit End.")

                            response_traceability, response_traceability_json = post_api_debug(
                                nombre_api="TRACEABILITY",
                                url=url_traceability,
                                payload=payload_traceability,
                                timeout=30
                            )

                            try:
                                logger.info(json.dumps(response_traceability.json(), indent=2))
                            except Exception:
                                logger.info(response_traceability.text)

                            if response_traceability.status_code not in [200, 201]:
                                safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    "Traceability FAILED\n\n" +
                                    bloque_json_ui(
                                        "TRACEABILITY",
                                        request=payload_traceability,
                                        response=response_traceability_json
                                    ),
                                    "red"
                                )

                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event("END-F004", "TRACEABILITY,FAILED", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                            def calcular_defect_code():
                                """
                                Toma el defect_code del payload de Traceability.
                                Si el step falló pero viene sin defect_code, intenta recuperarlo
                                desde atributos_map usando alias de Torque, Angles, Rundown Angle y Position Y.
                                """

                                try:
                                    steps_dict = payload_traceability.get("test_steps", {})
                                    failed_steps = []

                                    for _, lista in steps_dict.items():
                                        if not isinstance(lista, list):
                                            continue

                                        for step in lista:
                                            status_step = str(step.get("status", "")).strip().upper()

                                            fuera_de_limite = False
                                            try:
                                                valor_step = float(step.get("value", 0))
                                                low_step = float(step.get("lowLimit", 0))
                                                high_step = float(step.get("highLimit", 0))
                                                fuera_de_limite = valor_step < low_step or valor_step > high_step
                                            except Exception:
                                                valor_step = 0
                                                low_step = 0
                                                high_step = 0
                                                fuera_de_limite = False

                                            if status_step not in ["FAIL", "FAILED", "NOK"] and not fuera_de_limite:
                                                continue

                                            name_step = str(step.get("name", "")).strip()
                                            desc_step = str(step.get("description", "")).strip()
                                            defect_code = str(step.get("defect_code", "")).strip()

                                            if not defect_code:
                                                candidatos = []

                                                for texto_step in [name_step, desc_step]:
                                                    texto_norm = str(texto_step or "").strip().lower()
                                                    texto_norm = texto_norm.replace("_", " ").replace("-", " ")
                                                    texto_norm = " ".join(texto_norm.split())

                                                    if texto_norm:
                                                        candidatos.append(texto_norm)
                                                        candidatos.append(texto_norm.replace(" ", "_"))
                                                        candidatos.append(texto_norm.replace(" ", ""))

                                                        if " " in texto_norm:
                                                            candidatos.append(texto_norm.split(" ")[0])

                                                candidatos_extra = []

                                                for candidato in candidatos:
                                                    if candidato in ["t", "torque"]:
                                                        candidatos_extra.extend(["torque"])

                                                    elif candidato in ["a", "angle", "angles", "angulo", "ángulo"]:
                                                        candidatos_extra.extend(["angles", "angle"])

                                                    elif candidato in [
                                                        "px",
                                                        "rda",
                                                        "ra",
                                                        "rundown",
                                                        "rundown angle",
                                                        "rundownangle",
                                                        "rundown_angle",
                                                        "position x",
                                                        "positionx",
                                                        "position_x"
                                                    ]:
                                                        candidatos_extra.extend([
                                                            "rundown angle",
                                                            "rundown_angle",
                                                            "rundownangle",
                                                            "px",
                                                            "rda",
                                                            "position x",
                                                            "position_x",
                                                            "positionx"
                                                        ])

                                                    elif candidato in ["py", "position y", "position_y", "positiony"]:
                                                        candidatos_extra.extend(["position y", "position_y", "positiony"])

                                                candidatos.extend(candidatos_extra)

                                                config_attr = {}

                                                for candidato in candidatos:
                                                    if candidato in atributos_map:
                                                        config_attr = atributos_map[candidato]
                                                        break

                                                if config_attr:
                                                    defect_low = str(config_attr.get("defect_code_low", "")).strip()
                                                    defect_high = str(config_attr.get("defect_code_high", "")).strip()

                                                    if valor_step < low_step:
                                                        defect_code = defect_low
                                                    elif valor_step > high_step:
                                                        defect_code = defect_high
                                                    else:
                                                        defect_code = defect_low if defect_low else defect_high

                                                    print(
                                                        f"[DEBUG] Defect code recuperado: "
                                                        f"name={name_step}, value={valor_step}, "
                                                        f"low={low_step}, high={high_step}, defect={defect_code}"
                                                    )

                                            failed_steps.append({
                                                "name": name_step.upper(),
                                                "description": desc_step.upper(),
                                                "defect_code": defect_code,
                                                "fuera_de_limite": fuera_de_limite
                                            })

                                    if tornillo_afectado:
                                        for step in failed_steps:
                                            if not step["defect_code"]:
                                                continue

                                            if tornillo_afectado in step["name"] or tornillo_afectado in step["description"]:
                                                print(f"[DEBUG] Defect code tomado por tornillo: {step['defect_code']}")
                                                return step["defect_code"]

                                    failed_con_codigo = [
                                        step for step in failed_steps
                                        if str(step.get("defect_code", "")).strip()
                                    ]

                                    if len(failed_con_codigo) == 1:
                                        print(f"[DEBUG] Defect code único tomado: {failed_con_codigo[0]['defect_code']}")
                                        return failed_con_codigo[0]["defect_code"]

                                    if len(failed_con_codigo) > 1:
                                        print(
                                            "[WARNING] Varias fallas. "
                                            f"Usando última falla con código: {failed_con_codigo[-1]['defect_code']}"
                                        )
                                        return failed_con_codigo[-1]["defect_code"]

                                    print("[ERROR] No se pudo determinar defect_code para RecordDefect.")
                                    print("[ERROR] Failed steps encontrados:")
                                    print(json_pretty(failed_steps))

                                    return ""

                                except Exception as e:
                                    print(f"[ERROR] Error calculando defect_code desde Traceability: {e}")
                                    return ""

                            # Si END_PROCESS viene FAILED
                            # Traceability ya fue enviado.
                            # Ahora toca Conduit RecordDefect.
                            # Si quedan intentos: RepairAllDefects.
                            # Si ya no quedan intentos: End.
                            if socket_status_raw == "FAILED":
                                step_defect = calcular_defect_code()

                                if not step_defect or str(step_defect).strip() == "":
                                    safe_insert(
                                        "Command received-> " + cadena_original + "\n" +
                                        "Command FAILED - No se pudo calcular defect_code para RecordDefect\n\n" +

                                        bloque_json_ui(
                                            "TRACEABILITY",
                                            request=payload_traceability,
                                            response=response_traceability_json
                                        ),
                                        "red"
                                    )

                                    print("[ERROR] step_defect vacío. No se enviará RecordDefect.")

                                    try:
                                        conn.send("FAILED".encode("UTF-8"))
                                    except Exception as e:
                                        safe_insert(f"Error enviando: {e}", "red")

                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break

                                payload_record_defect = {
                                    "version": "1.0",
                                    "keep_alive": False,
                                    "refresh_unit": True,
                                    "source": {
                                        "workstation": {
                                            "station": process_name,
                                            "type": "Process"
                                        },
                                        "client_id": client_id_db,
                                        "employee": operator_id,
                                        "password": ""
                                    },
                                    "transactions": [
                                        {
                                            "unit": {
                                                "unit_id": SERIAL_PADRE_GLOBAL
                                            },
                                            "commands": [
                                                {
                                                    "name": "RecordDefect",
                                                    "defect_code": step_defect
                                                }
                                            ]
                                        }
                                    ]
                                }

                                response_record, response_record_json = post_api_debug(
                                    nombre_api="CONDUIT RECORD DEFECT",
                                    url=url_conduit,
                                    payload=payload_record_defect,
                                    timeout=30
                                )

                                if not conduit_ok(response_record, response_record_json):
                                    safe_insert(
                                        "Command received-> " + cadena_original + "\n" +
                                        "Traceability OK  RecordDefect FAILED\n" +
                                        "Command FAILED\n\n" +
                                        bloque_json_ui(
                                            "TRACEABILITY",
                                            request=payload_traceability,
                                            response=response_traceability_json
                                        ) +
                                        bloque_json_ui(
                                            "CONDUIT RECORD DEFECT",
                                            request=payload_record_defect,
                                            response=response_record_json
                                        ),
                                        "red"
                                    )

                                    try:
                                        conn.send("FAILED".encode("UTF-8"))
                                    except Exception as e:
                                        safe_insert(f"Error enviando: {e}", "red")

                                    conexionBitacora.event("END-F005", "CONDUIT_RECORD_DEFECT,FAILED", month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break

                                # Aún quedan intentos
                                if intento_actual < max_intentos:
                                    payload_repair = {
                                        "version": "1.0",
                                        "keep_alive": False,
                                        "refresh_unit": True,
                                        "source": {
                                            "workstation": {
                                                "station": process_name,
                                                "type": "Process"
                                            },
                                            "client_id": client_id_db,
                                            "employee": operator_id,
                                            "password": ""
                                        },
                                        "transactions": [
                                            {
                                                "unit": {
                                                    "unit_id": SERIAL_PADRE_GLOBAL
                                                },
                                                "commands": [
                                                    {
                                                        "name": "RepairAllDefects"
                                                    }
                                                ]
                                            }
                                        ]
                                    }

                                    response_repair, response_repair_json = post_api_debug(
                                        nombre_api="CONDUIT REPAIR ALL DEFECTS",
                                        url=url_conduit,
                                        payload=payload_repair,
                                        timeout=30
                                    )

                                    if conduit_ok(response_repair, response_repair_json):
                                        safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    f"Traceability OK  RecordDefect OK  RepairAllDefects OK  Intento {intento_actual}/{max_intentos}\n" +
                                    "Command START-AGAIN\n\n" +

                                    bloque_json_ui(
                                        "TRACEABILITY",
                                        request=payload_traceability,
                                        response=response_traceability_json
                                    ) +

                                    bloque_json_ui(
                                        "CONDUIT RECORD DEFECT",
                                        request=payload_record_defect,
                                        response=response_record_json
                                    ) +

                                    bloque_json_ui(
                                        "CONDUIT REPAIR ALL DEFECTS",
                                        request=payload_repair,
                                        response=response_repair_json
                                    ),
                                    "orange"
                                )
                                        try:
                                            conn.send("PASSED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("END-P001", "END_PROCESS,FAILED,START_AGAIN", month, day)

                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                                    else:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "Conduit RepairAllDefects FAILED\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT RECORD DEFECT",
                                                request=payload_record_defect,
                                                response=response_record_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT REPAIR ALL DEFECTS",
                                                request=payload_repair,
                                                response=response_repair_json
                                            ),
                                            "red"
                                        )

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("END-F006", "CONDUIT_REPAIR_ALL_DEFECTS,FAILED", month, day)
                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                                # Ya se agotaron intentos
                                else:
                                    if intento_actual < max_intentos:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            f"Intento {intento_actual}/{max_intentos}: se bloqueó Conduit End porque aún hay reintentos.\n" +
                                            "Command START-AGAIN\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT RECORD DEFECT",
                                                request=payload_record_defect,
                                                response=response_record_json
                                            ),
                                            "orange"
                                        )

                                        try:
                                            conn.send("START-AGAIN".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)
                                        break

                                    payload_end_failed = {
                                        "version": "1.0",
                                        "keep_alive": False,
                                        "refresh_unit": True,
                                        "source": {
                                            "workstation": {
                                                "station": process_name,
                                                "type": "Process"
                                            },
                                            "client_id": client_id_db,
                                            "employee": operator_id,
                                            "password": ""
                                        },
                                        "transactions": [
                                            {
                                                "unit": {
                                                    "unit_id": SERIAL_PADRE_GLOBAL
                                                },
                                                "commands": [
                                                    {
                                                        "name": "End"
                                                    }
                                                ]
                                            }
                                        ]
                                    }

                                    response_end_failed, response_end_failed_json = post_api_debug(
                                        nombre_api="CONDUIT END FAILED",
                                        url=url_conduit,
                                        payload=payload_end_failed,
                                        timeout=30
                                    )

                                    if conduit_ok(response_end_failed, response_end_failed_json):
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            f"Traceability OK  RecordDefect OK  Conduit End OK  Pieza FAILED  Intento {intento_actual}/{max_intentos}\n" +
                                            "pieza FAILED\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT RECORD DEFECT",
                                                request=payload_record_defect,
                                                response=response_record_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT END FAILED",
                                                request=payload_end_failed,
                                                response=response_end_failed_json
                                            ),
                                            "red"
                                        )

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando RELEASE_PIECE FAILED: {e}", "red")

                                        try:
                                            parte_actual = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                            station_actual = conexion.stations()

                                            if parte_actual and parte_actual != "FAILED" and station_actual:
                                                part_id = parte_actual[0]
                                                station_id = station_actual[0]

                                                if hasattr(conexion, "duration_end_st60"):
                                                    conexion.duration_end_st60(station_id, part_id, "FAIL")

                                                print(
                                                    f"[DURATION] Fin registrado station_id={station_id} "
                                                    f"part_id={part_id} status=FAIL"
                                                )

                                        except Exception as e:
                                            print(f"[DURATION WARNING] No se pudo cerrar duration: {e}")

                                        SERIAL_PADRE_GLOBAL = ""
                                        PART_NUMBER_GLOBAL = ""
                                        MEASUREMENT_KEY_GLOBAL = ""
                                        START_SCREWING_ID_GLOBAL = 0
                                        COMPONENT = ""

                                        print("[INFO] Pieza liberada localmente como FAILED.")

                                        conexionBitacora.event("END-F007", "END_PROCESS,FAILED,MAX_ATTEMPTS", month, day)

                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                                    else:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "Conduit End FAILED\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT RECORD DEFECT",
                                                request=payload_record_defect,
                                                response=response_record_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT END FAILED",
                                                request=payload_end_failed,
                                                response=response_end_failed_json
                                            ),
                                            "red"
                                        )

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("END-F008", "CONDUIT_END,FAILED", month, day)
                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                            # Si END_PROCESS viene PASSED
                            # Traceability ya fue enviado.
                            # Ahora toca Conduit End y liberar pieza OK.
                            else:
                                payload_end_passed = {
                                    "version": "1.0",
                                    "keep_alive": False,
                                    "refresh_unit": True,
                                    "source": {
                                        "workstation": {
                                            "station": process_name,
                                            "type": "Process"
                                        },
                                        "client_id": client_id_db,
                                        "employee": operator_id,
                                        "password": ""
                                    },
                                    "transactions": [
                                        {
                                            "unit": {
                                                "unit_id": SERIAL_PADRE_GLOBAL
                                            },
                                            "commands": [
                                                {
                                                    "name": "End"
                                                }
                                            ]
                                        }
                                    ]
                                }

                                response_end_passed, response_end_passed_json = post_api_debug(
                                    nombre_api="CONDUIT END PASSED",
                                    url=url_conduit,
                                    payload=payload_end_passed,
                                    timeout=30
                                )

                                if conduit_ok(response_end_passed, response_end_passed_json):
                                    safe_insert(
                                        "Command received-> " + cadena_original + "\n" +
                                        "Traceability OK  Conduit End OK  Pieza PASSED\n" +
                                        "Command PASSED\n\n" +
                                        bloque_json_ui(
                                            "TRACEABILITY",
                                            request=payload_traceability,
                                            response=response_traceability_json
                                        ) +
                                        bloque_json_ui(
                                            "CONDUIT END PASSED",
                                            request=payload_end_passed,
                                            response=response_end_passed_json
                                        ),
                                        "green"
                                    )

                                    try:
                                        conn.send("PASSED".encode("UTF-8"))
                                    except Exception as e:
                                        safe_insert(f"Error enviando RELEASE_PIECE PASSED: {e}", "red")

                                    try:
                                        parte_actual = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                        station_actual = conexion.stations()

                                        if parte_actual and parte_actual != "FAILED" and station_actual:
                                            part_id = parte_actual[0]
                                            station_id = station_actual[0]

                                            if hasattr(conexion, "duration_end_st60"):
                                                conexion.duration_end_st60(station_id, part_id, "PASS")

                                            print(
                                                f"[DURATION] Fin registrado station_id={station_id} "
                                                f"part_id={part_id} status=PASS"
                                            )

                                    except Exception as e:
                                        print(f"[DURATION WARNING] No se pudo cerrar duration: {e}")

                                    SERIAL_PADRE_GLOBAL = ""
                                    PART_NUMBER_GLOBAL = ""
                                    MEASUREMENT_KEY_GLOBAL = ""
                                    START_SCREWING_ID_GLOBAL = 0
                                    COMPONENT = ""

                                    print("[INFO] Pieza liberada localmente como PASSED.")

                                    conexionBitacora.event("END-P002", "END_PROCESS,PASSED", month, day)

                                    green_label.configure(image=image_green_full)
                                    red_label.configure(image=image_red)

                                else:
                                    if getattr(response_end_passed, "status_code", 0) in [200, 201]:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "Traceability OK\n" +
                                            "Conduit End PASS enviado con advertencia\n" +
                                            "Resultado final de pieza: PASSED\n" +
                                            "Nota: hubo una advertencia en la respuesta de Conduit, "
                                            "pero no es fallo final de pieza.\n" +
                                            "Command PASSED\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT END PASSED WARNING",
                                                request=payload_end_passed,
                                                response=response_end_passed_json
                                            ),
                                            "green"
                                        )

                                        try:
                                            conn.send("PASSED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando RELEASE_PIECE PASSED: {e}", "red")

                                        try:
                                            parte_actual = conexion.obtener_parte(SERIAL_PADRE_GLOBAL)
                                            station_actual = conexion.stations()

                                            if parte_actual and parte_actual != "FAILED" and station_actual:
                                                part_id = parte_actual[0]
                                                station_id = station_actual[0]

                                                if hasattr(conexion, "duration_end_st60"):
                                                    conexion.duration_end_st60(station_id, part_id, "PASS")

                                                print(
                                                    f"[DURATION] Fin registrado station_id={station_id} "
                                                    f"part_id={part_id} status=PASS"
                                                )

                                        except Exception as e:
                                            print(f"[DURATION WARNING] No se pudo cerrar duration: {e}")

                                        SERIAL_PADRE_GLOBAL = ""
                                        PART_NUMBER_GLOBAL = ""
                                        MEASUREMENT_KEY_GLOBAL = ""
                                        START_SCREWING_ID_GLOBAL = 0
                                        COMPONENT = ""

                                        print("[INFO] Pieza liberada localmente como PASSED con advertencia de Conduit.")

                                        conexionBitacora.event("END-P002", "END_PROCESS,PASSED,CONDUIT_WARNING", month, day)

                                        green_label.configure(image=image_green_full)
                                        red_label.configure(image=image_red)

                                    else:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "Pieza PASSED, pero Conduit End PASS no fue aceptado.\n" +
                                            "Command FAILED\n\n" +
                                            bloque_json_ui(
                                                "TRACEABILITY",
                                                request=payload_traceability,
                                                response=response_traceability_json
                                            ) +
                                            bloque_json_ui(
                                                "CONDUIT END PASS ERROR",
                                                request=payload_end_passed,
                                                response=response_end_passed_json
                                            ),
                                            "red"
                                        )

                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("END-F009", "CONDUIT_END_PASS,HTTP_FAILED", month, day)
                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)
                        except Exception as e:
                            safe_insert(
                                "Command received-> " + cadena_original + "\n" +
                                f"END_PROCESS ERROR: {e}\n" +
                                "Command FAILED\n",
                                "red"
                            )

                            print(f"[END PROCESS ERROR] {e}")

                            try:
                                conn.send("FAILED".encode("UTF-8"))
                            except Exception as send_error:
                                safe_insert(f"Error enviando: {send_error}", "red")

                            conexionBitacora.event("END-F999", f"END_PROCESS,EXCEPTION {e}", month, day)

                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)

                        finally:
                            cadena = ""
                            pieza = ""

                    case "new_model":
                        clear_table_data()
                        if len(option) == 3 and option[-1] == '1/':
                            new_models = conexion.new_model(option[1])
                            new_models = new_models[1]
                            model_name.set(new_models)
                            safe_insert("Command received-> "+cadena+"\n"+"Command NEW MODEL PASSED"+"\n")
                            try:
                                conn.send("PASSED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            conexionBitacora.event("NMP-001","Command received "+cadena,month,day)
                            conexionBitacora.event("CMD-P001","Command,PASSED",month,day)
                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)
                        else:
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            conexionBitacora.event("NMP-002","Command received "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
                        cadena = ""
                        pieza = ""

                    case "select_model":
                        clear_table_data()
                        if len(option) == 3 and option[-1] == '1/':
                            modelName = conexion.select_model(option[1])
                            if(modelName == "0"):
                                modelName = "Unregistered model"
                                model_name.set(modelName)
                                safe_insert("Command received-> "+cadena+ " Model: " +modelName+"\n"+"Command FAILED"+"\n", "red")
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                conexionBitacora.event("SMP-002","Command received "+cadena+" Model: "+modelName,month,day)
                                conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                            else:
                                modelName = modelName[1]
                                model_name.set(modelName)
                                safe_insert("Command received-> "+cadena+"\n"+"Command SELECT MODEL PASSED"+"\n")
                                try:
                                    conn.send("PASSED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                conexionBitacora.event("SMP-001","Command received "+cadena,month,day)
                                conexionBitacora.event("CMD-P001","Command,PASSED",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                        else:
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            conexionBitacora.event("SMP-002","Command received "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
                        cadena = ""
                        pieza = ""

                    case "commit":

                        cadena_original = comando_completo.strip()
                        cadena_limpia = cadena_original.rstrip(",")

                        print(f"[DEBUG COMMIT RAW] {repr(cadena_original)}")
                        logging.info(f"[DEBUG COMMIT RAW] {repr(cadena_original)}")
                        logging.info(f"[DEBUG COMMIT OPTION] len={len(option)} option={option}")

                        if len(option) >= 2 and option[-1].strip() == '1/':
                            part_name = SERIAL_PADRE_GLOBAL.strip() if SERIAL_PADRE_GLOBAL else entry_piece.get().strip()

                            if not part_name:
                                safe_insert(
                                    "Command received-> " + cadena_original + "\n" +
                                    ": The part has not been loaded" + "\n" +
                                    "Command FAILED" + "\n",
                                    "red"
                                )

                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event(
                                    "CMD-C001",
                                    "Command received " + cadena_original + ": The part has not been loaded",
                                    month,
                                    day
                                )
                                conexionBitacora.event("CMD-F001", "Command,FAILED", month, day)

                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)

                            else:
                                try:
                                    cadena_para_commit = cadena_limpia
                                    es_screwing = len(option) > 1 and str(option[1]).strip() == "Screwing"

                                    if es_screwing:
                                        cadena_para_commit = normalizar_commit_screwing_st60(cadena_limpia)

                                    print(f"[DEBUG COMMIT FINAL] {repr(cadena_para_commit)}")
                                    print(f"[DEBUG COMMIT LEN] {len(cadena_para_commit.split(','))}")

                                    print("\n========== DEBUG ANTES DE COMMIT ==========")
                                    print(f"SERIAL_PADRE_GLOBAL: {SERIAL_PADRE_GLOBAL}")
                                    print(f"entry_piece.get(): {entry_piece.get()}")
                                    print(f"part_name usado para guardar: {part_name}")
                                    print(f"cadena_para_commit: {cadena_para_commit}")
                                    print("==========================================\n")

                                    ultimo_id_antes_commit = 0
                                    if es_screwing:
                                        try:
                                            if hasattr(conexion, "obtener_ultimo_id_screwing"):
                                                ultimo_id_antes_commit = conexion.obtener_ultimo_id_screwing(part_name)

                                            print(f"[DEBUG COMMIT DB] Último ID antes del commit: {ultimo_id_antes_commit}")

                                        except Exception as e:
                                            print(f"[DEBUG COMMIT DB WARNING] No se pudo obtener último ID antes: {e}")
                                            ultimo_id_antes_commit = 0

                                    commit_options, table_data = commands.commit(cadena_para_commit, part_name)

                                    commit_screwing_failed = False
                                    screwing_insertado_en_commit = False
                                    debug_screwing = []

                                    if es_screwing:
                                        commit_screwing_failed = commit_screwing_tiene_falla(cadena_para_commit)

                                        try:
                                            ultimo_id_despues_commit = 0

                                            if hasattr(conexion, "obtener_ultimo_id_screwing"):
                                                ultimo_id_despues_commit = conexion.obtener_ultimo_id_screwing(part_name)
                                                screwing_insertado_en_commit = ultimo_id_despues_commit > ultimo_id_antes_commit

                                            debug_screwing = conexion.screwing_current_state(
                                                part_name,
                                                START_SCREWING_ID_GLOBAL
                                            )

                                            print(f"[DEBUG COMMIT DB] Último ID después del commit: {ultimo_id_despues_commit}")
                                            print(f"[DEBUG COMMIT DB] Insertado en este commit: {screwing_insertado_en_commit}")
                                            print(f"[DEBUG COMMIT DB] Mediciones guardadas para {part_name}: {len(debug_screwing)}")

                                            if not debug_screwing:
                                                print("[DEBUG COMMIT DB] commands.commit regresó:")
                                                print(f"commit_options = {commit_options}")
                                                print(f"table_data = {table_data}")

                                        except Exception as e:
                                            print(f"[DEBUG COMMIT DB ERROR] {e}")
                                            logging.error(f"[DEBUG COMMIT DB ERROR] {e}")

                                    if es_screwing:
                                        commit_procesado_ok = (commit_options == 'PASSED') or screwing_insertado_en_commit
                                    else:
                                        commit_procesado_ok = (commit_options == 'PASSED')

                                    if commit_procesado_ok:
                                        if table_data:
                                            if es_screwing:
                                                table_data = filtrar_table_data_screwing(
                                                    table_data,
                                                    cadena_para_commit
                                                )

                                            update_table_with_data(table_data)

                                        mensaje_commit = (
                                            "Command received-> " + cadena_original + "\n" +
                                            "Command COMMIT PASSED" + "\n"
                                        )

                                        if es_screwing and commit_screwing_failed:
                                            mensaje_commit += "Screwing measurement FAILED" + "\n"

                                        safe_insert(mensaje_commit)

                                        try:
                                            conn.send("PASSED".encode('UTF-8'))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("COM-001", "Command received " + cadena_original, month, day)
                                        conexionBitacora.event("CMD-P001", "Command,PASSED", month, day)

                                        if es_screwing and commit_screwing_failed:
                                            conexionBitacora.event("SCR-F001", "Screwing measurement FAILED", month, day)

                                        green_label.configure(image=image_green_full)
                                        red_label.configure(image=image_red)

                                    else:
                                        safe_insert(
                                            "Command received-> " + cadena_original + "\n" +
                                            "Command FAILED" + "\n",
                                            "red"
                                        )

                                        try:
                                            conn.send("FAILED".encode('UTF-8'))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")

                                        conexionBitacora.event("COM-002", "Command received " + cadena_original, month, day)
                                        conexionBitacora.event("CMD-F001", "Command,FAILED", month, day)

                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                                except Exception as e:
                                    safe_insert(
                                        "Command received-> " + cadena_original + "\n" +
                                        "Command FAILED\n" +
                                        f"Commit internal error: {e}\n",
                                        "red"
                                    )

                                    logging.error(f"[COMMIT INTERNAL ERROR] {e}")
                                    logging.error(f"[COMMIT RAW] {repr(cadena_original)}")
                                    logging.error(f"[COMMIT OPTION] {option}")

                                    try:
                                        conn.send("FAILED".encode('UTF-8'))
                                    except Exception as send_error:
                                        safe_insert(f"Error enviando: {send_error}", "red")

                                    conexionBitacora.event("COM-002", "Command received " + cadena_original, month, day)
                                    conexionBitacora.event("CMD-F001", "Command,FAILED", month, day)

                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)

                        else:
                            safe_insert(
                                "Command received-> " + cadena_original + "\n" +
                                "Command FAILED" + "\n" +
                                f"Invalid commit format. option={option}\n",
                                "red"
                            )

                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")

                            conexionBitacora.event("COM-002", "Command received " + cadena_original, month, day)
                            conexionBitacora.event("CMD-F001", "Command,FAILED", month, day)

                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)

                        pieza = ""
                    case "Component":
                        pieza_padre = piece_name.get()
                        entry_piece.focus_set()
                        clear_table_data()
                        if len(option) == 4 and option[-1] == '1/':
                            entry_piece.configure(state=ctk.NORMAL, textvariable=piece_name)
                            piece_name.set("")
                            safe_insert("You can scan the part.", "green")
                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)
                            try:
                                start_time = time.time()
                                while True:
                                    name_piece = entry_piece.get()
                                    time.sleep(0.05)
                                    elapsed_time = time.time() -  start_time
                                    if len(name_piece) == 0:
                                        conn.settimeout(None)
                                        if elapsed_time >= 240: 
                                            entry_piece.configure(state="readonly", textvariable=piece_name)
                                            piece_name.set("")
                                            safe_insert("Start the process again.")
                                            try:
                                                conn.send("restart".encode('UTF-8'))
                                            except Exception as e:
                                                safe_insert(f"Error enviando: {e}", "red")
                                            contador = 0
                                            break
                                        else:
                                            pass
                                    if len(name_piece) > 13:
                                        conn.settimeout(None)
                                        piece = name_piece + ", PASSED"
                                        try:
                                            conn.send(piece.encode('UTF-8'))
                                        except Exception as e:
                                            safe_insert(f"Error enviando: {e}", "red")
                                        entry_piece.configure(state="readonly", textvariable=piece_name)
                                        piece_name.set(name_piece)
                                        componente = conexion.component_store(name_piece, option[1], option[2])
                                        if componente == "FAILED":
                                            safe_insert("Error storing component in database, verify the string", "red")
                                            logging.error("Error storing component in database")
                                            break
                                        safe_insert("Command received-> "+cadena+" actuator: "+name_piece+"\n"+"Command COMPONENT PASSED"+"\n")
                                        conexionBitacora.event("SPP-001","Command received "+cadena+" actuator: "+name_piece,month,day)
                                        conexionBitacora.event("CMD-P001","Command,PASSED",month,day)
                                        green_label.configure(image=image_green_full)
                                        red_label.configure(image=image_red)
                                        pieza = name_piece
                                        entry_piece.configure(state="readonly", textvariable=piece_name)
                                        piece_name.set(pieza_padre)
                                        break
                                    elif len(name_piece) == 0 or len(name_piece) < 14:
                                        conn.settimeout(0.1)
                                        try:
                                            reset = conn.recv(1024)
                                            conn.settimeout(None)
                                            if reset:
                                                reset = reset.decode('utf-8')
                                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                                piece_name.set("")
                                                try:
                                                    conn.send("RESET".encode('UTF-8'))
                                                except Exception as e:
                                                    safe_insert(f"Error enviando: {e}", "red")
                                                safe_insert("Command received-> "+cadena+" RESET PROCESS-> Command: "+reset+"\n"+"Command COMPONENT PASSED")
                                                conexionBitacora.event("RP-002","Command received "+reset,month,day)
                                                conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                                                green_label.configure(image=image_green_full)
                                                red_label.configure(image=image_red)
                                                break
                                        except socket.timeout:
                                            pass
                                        except ConnectionResetError:
                                            safe_insert("Connection was forcibly closed by the remote host"+"\n"+"Connection error!"+"\n"+"Contact technical support!")
                                            pass
                            except TypeError as e:
                                print("Error: ", e)
                                logging.error(f"Connection was closed"+"\n"+f"Error: {str(e)}"+"\n"+"Contact technical support!")
                                safe_insert("Connection was closed"+"\n"+f"Error: {str(e)}"+"\n"+"Contact technical support!", "red")
                                cadena = ""
                        elif len(option) == 5 and option[-1] == '1/':
                            entry_piece.configure(state=ctk.NORMAL, textvariable=piece_name)
                            piece_name.set("")
                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)
                            name_piece =option[1]
                            if len(name_piece) > 13:
                                piece = name_piece + ", PASSED"
                                try:
                                    conn.send(piece.encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                piece_name.set(name_piece)
                                componente = conexion.component_store(name_piece, option[2], option[3])
                                if componente == "FAILED":
                                    safe_insert("Error storing component in database, verify the string", "red")
                                    logging.error("Error storing component in database")
                                    break
                                safe_insert("Command received-> "+cadena+" actuator: "+name_piece+"\n"+"Command COMPONENT PASSED")
                                conexionBitacora.event("SPP-001","Command received "+cadena+" actuator: "+name_piece,month,day)
                                conexionBitacora.event("CMD-P001","Command,PASSED",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                piece_name.set(pieza_padre)
                                pieza = name_piece
                            else:
                                conn.settimeout(None)
                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                piece_name.set("")
                                safe_insert("Command received-> "+cadena+" part: "+name_piece+"\n"+"Command FAILED")
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                    conn.send("verify data".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                conexionBitacora.event("SPP-002","Command received "+cadena+" part: "+name_piece,month,day)
                                conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break
                        else:
                            conn.send("FAILED".encode('UTF-8'))
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED", "red")
                            conexionBitacora.event("SPP-002","Command received "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
                            cadena = ""

                    case "laser":
                        serial = conexion.get_part_numbers('P2173404-00-C:SEYU26061A0765')
                        if serial != "PASSED":
                            conn.send(f"{serial}".encode('UTF-8'))
                            safe_insert(f"Command received-> {cadena} part: {serial}\nCommand PASSED\nPrinting...\n", "green")
                        else:
                            conn.send("do_not_print".encode('UTF-8'))
                            safe_insert(f"Command received-> {cadena} part: {serial}\nCommand PASSED\nDon't print\n", "orange")

                    case "reset":
                        for item in option:
                            cadena += str(item) + ","

                        clear_table_data()
                        # part_name = entry_piece.get()
                        if len(entry_piece.get()) == 30:
                            part_name = entry_piece.get()
                            cadena = "reset,RESET,0.0,The station was reestablished,1/"
                            # print(part_name)
                            # print(cadena)

                            duration = "PASSED" #conexion.duration(cadena,part_name)

                            if duration == "PASSED":
                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                piece_name.set("")
                                safe_insert("Command received-> "+cadena+"\n"+"Command RESET PASSED"+"\n")
                                logging.info(f"Command received-> {cadena}\n Command RESET PASSED")

                                
                                conexionBitacora.event("ENDP-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-P001","|Command,PASSED|",month,day)
                                                
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                            else:
                                safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n")
                                logging.error(f"Command received-> {cadena}\nCommand FAILED")

                                conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)

                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                        else:
                            
                            try:
                                conn.send("RESET".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                                logging.error(f"Error enviando: {e}")

                            safe_insert("Command received-> "+cadena+" RESET PROCESS-> Command: reset,1/"+"\n"+"Command RESET PASSED"+"\n")
                            logging.info(f"Command received-> {cadena} RESET PROCESS-> Command: reset,1/ \n Command RESET PASSED")

                            conexionBitacora.event("RP-002","|Command received| reset,1/",month,day)
                            conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)

                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)
                        cadena = ""

                    case _:
                        safe_insert("Command received-> "+comando_completo+"\n"+"Command FAILED"+"\n", "red")
                        try:
                            conn.send("FAILED".encode('UTF-8'))
                        except Exception as e:
                            safe_insert(f"Error enviando: {e}", "red")
                        conexionBitacora.event("COM-002","Command received "+comando_completo,month,day)
                        conexionBitacora.event("CMD-F001","Command,FAILED",month,day)
                        green_label.configure(image=image_green)
                        red_label.configure(image=image_red_full)
                        cadena = ""
                        pieza = ""
                cadena = ""
            else:
                pass
    finally:
        try:
            conn.close()
        except:
            pass
        if conn in active_connections:
            active_connections.remove(conn)

def accept_connections():
    while running:
        try:
            conn, addr = sock.accept()
            active_connections.append(conn)
            t = threading.Thread(target=worker, args=(conn, addr), daemon=True)
            client_threads[:] = [t for t in client_threads if t.is_alive()]  
            client_threads.append(t)
            t.start()
        except OSError as e:
            print(f"Error aceptando conexión: {e}")
            logging.error(f"Error aceptando conexión: {e}")
            break

def check_exit():
    if exit_event.is_set():
        root.quit()
    else:
        root.after(100, check_exit)

def application():
    if(host == server[0][1] and str(port) == str(server[0][0])):
        # Bind el evento de cierre de ventana a close_app
        root.protocol("WM_DELETE_WINDOW", safe_exit)

        # Iniciar keep-alive de BD
        keep_alive_database()
        
        threading.Thread(target=accept_connections, daemon=True).start()

        root.mainloop()

    else:
        win = ctk.CTk()
        win.geometry("750x270")
        win.title("")
        win.iconbitmap("favicon.ico")
        lbl_station = ctk.CTkLabel(master=win, 
            text=f"The IP address and port are different from the system configuration: {host}:{port}, it must be: {server[0][1]}:{server[0][0]}",
            justify="center")
        lbl_station.pack(side=ctk.LEFT, pady=10, padx=40, anchor='nw')
        win.after(3000, lambda: win.destroy())
        win.mainloop()

if __name__ == "__main__":
    application()
