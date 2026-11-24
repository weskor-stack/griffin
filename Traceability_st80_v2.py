#servidor
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
import conduit_api

from conduit_api import validate_time
import urllib.parse
import unit_api
import interlocking_api


# --- VARIABLES GLOBALES PARA APIS DE TRAZABILIDAD ---
SERIAL_PADRE_GLOBAL = ""
PART_NUMBER_GLOBAL = ""

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
    global SERIAL_PADRE_GLOBAL, PART_NUMBER_GLOBAL, PART_NUMBER, COMPONENT, component_sn
    
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
                conexionBitacora.event("CDBF-001","|Command received| PLC-Disconnected",month,day)
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
                        
                        if len(option) == 2 and option[-1] == '1/':
                            entry_piece.configure(state=ctk.NORMAL, textvariable=piece_name)
                            piece_name.set("")
                            safe_insert("You can scan the part.", "green")
                            logging.info("You can scan the part.")

                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)

                            try:
                                start_time = time.time()
                                heatsink_scanned = False
                                error_detectado = False

                                while not heatsink_scanned:
                                    name_piece = entry_piece.get().strip()
                                    time.sleep(0.05)
                                    elapsed_time = time.time() - start_time

                                    if len(name_piece) == 0:
                                        if elapsed_time >= 300:
                                            entry_piece.configure(state="readonly", textvariable=piece_name)
                                            piece_name.set("")
                                            safe_insert("Timeout waiting for Parent scan.", "red")
                                            conn.send("START-AGAIN".encode('UTF-8'))
                                            error_detectado = True
                                            break
                                        continue

                                    if len(name_piece) > 27:
                                        # BLOQUEO DE CURSOR
                                        entry_piece.configure(state="disabled")

                                        conduit_status, conduit_message, response_data, detalle_conduit = conduit_api.validate_time(
                                            name_piece, station_type="ST50", detalle=None,
                                        )
                                        logging.info(f"[STATUS CONDUIT]:{conduit_status}")
                                        logging.info(f"[CONDUIT MESSAGE]:{conduit_message}")
                                        logging.info(f"[CONDUIT RESPONSE]:{response_data}")
                                                                      
                                        if conduit_status != "NO-OP":
                                            ###Meter en try
                                            pantalla_final = (f"Command received -> {comando_completo}, Command START FAILED\n\n"
                                            f"[CONDUIT REQUEST]:\n{json.dumps(detalle_conduit, indent=2, ensure_ascii=False)}\n\n"
                                            f"[CONDUIT REPONSE]:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n\n" 
                                            f"[CONDUIT MESSAGE]:{conduit_message}\n\n"
                                            f"[STATUS CONDUIT]:{conduit_status}\n\n"
                                            )

                                            entry_piece.configure(state=ctk.NORMAL)
                                            safe_insert(pantalla_final,"red")
                                            logging.error(pantalla_final)
                                            try:
                                                conn.send("FAILED".encode("UTF-8"))
                                                error_detectado = True
                                            except Exception as e:
                                                safe_insert(str(e),"red")
                                                logging.error(str(e))
                                                conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                                conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                                green_label.configure(image=image_green)
                                                red_label.configure(image=image_red_full)

                                            conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                            conexionBitacora.event("CMD-P002", "|Command,FAILED|", month, day)
                                            green_label.configure(image=image_green)
                                            red_label.configure(image=image_red_full)                               

                                            break
                                            
                                        heatsink_scanned = True
                                    else:
                                        try:
                                            conn.send("FAILED".encode("UTF-8"))
                                            error_detectado = True
                                        except Exception as e:
                                            safe_insert(str(e),"red")
                                            logging.error(str(e))
                                            conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                            conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                            green_label.configure(image=image_green)
                                            red_label.configure(image=image_red_full)

                                if error_detectado or not heatsink_scanned:
                                    break

                                pantalla_final = (f"Command received -> {comando_completo}, Command START PASSED\n\n"
                                f"[CONDUIT REQUEST]:\n{json.dumps(detalle_conduit, indent=2, ensure_ascii=False)}\n\n"
                                f"[CONDUIT REPONSE]:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n\n" 
                                f"[CONDUIT MESSAGE]:{conduit_message}\n\n"
                                f"[STATUS CONDUIT]:{conduit_status}\n\n"
                                )

                                safe_insert(pantalla_final, "green")
                                logging.info(pantalla_final)

                                try:
                                    conn.send(f"PASSED, {name_piece}".encode('UTF-8'))
                                    
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)

                                conexionBitacora.event("SPP-001", f"Serial number: {SERIAL_PADRE_GLOBAL}", month, day)
                                conexionBitacora.event("CMD-P001", "|Command,PASSED|", month, day)

                                piece_name.set(name_piece)
                                entry_piece.configure(state="readonly")
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                                break

                            except Exception as e:
                                safe_insert(f"Exception Caught: {str(e)}", "red")
                                cadena = ""
                                break

                       # BLOQUE NUEVO PARA PLC
                        elif len(option) == 3 and option[-1] == '1/':
                            name_piece = str(option[1]).strip()

                            if len(name_piece) > 27:
                                # BLOQUEO DE CURSOR
                                entry_piece.configure(state="disabled")

                                conduit_status, conduit_message, response_data, detalle_conduit = conduit_api.validate_time(
                                    name_piece, station_type="ST50", detalle=None,
                                )
                                logging.info(f"[STATUS CONDUIT]:{conduit_status}")
                                logging.info(f"[CONDUIT MESSAGE]:{conduit_message}")
                                logging.info(f"[CONDUIT RESPONSE]:{response_data}")
                                                                
                                if conduit_status != "NO-OP":
                                    ###Meter en try
                                    pantalla_final = (f"Command received -> {comando_completo}, Command START FAILED\n\n"
                                    f"[CONDUIT REQUEST]:\n{json.dumps(detalle_conduit, indent=2, ensure_ascii=False)}\n\n"
                                    f"[CONDUIT REPONSE]:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n\n" 
                                    f"[CONDUIT MESSAGE]:{conduit_message}\n\n"
                                    f"[STATUS CONDUIT]:{conduit_status}\n\n"
                                    )

                                    entry_piece.configure(state=ctk.NORMAL)
                                    safe_insert(pantalla_final,"red")
                                    logging.error(pantalla_final)
                                    try:
                                        conn.send("FAILED".encode("UTF-8"))
                                        error_detectado = True
                                    except Exception as e:
                                        safe_insert(str(e),"red")
                                        logging.error(str(e))
                                        conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                        conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)

                                    conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                    conexionBitacora.event("CMD-P002", "|Command,FAILED|", month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)                               

                                    break
                                pantalla_final = (f"Command received -> {comando_completo}, Command START PASSED\n\n"
                                f"[CONDUIT REQUEST]:\n{json.dumps(detalle_conduit, indent=2, ensure_ascii=False)}\n\n"
                                f"[CONDUIT REPONSE]:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n\n" 
                                f"[CONDUIT MESSAGE]:{conduit_message}\n\n"
                                f"[STATUS CONDUIT]:{conduit_status}\n\n"
                                )

                                safe_insert(pantalla_final, "green")
                                logging.info(pantalla_final)

                                try:
                                    conn.send(f"PASSED, {name_piece}".encode('UTF-8'))
                                    
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)

                                conexionBitacora.event("SPP-001", f"Serial number: {SERIAL_PADRE_GLOBAL}", month, day)
                                conexionBitacora.event("CMD-P001", "|Command,PASSED|", month, day)

                                piece_name.set(name_piece)
                                entry_piece.configure(state="readonly")
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                            else:
                                try:
                                    conn.send("FAILED".encode("UTF-8"))
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {name_piece}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)

                    case "reset":
                        for item in option:
                            cadena += str(item) + ","
                        clear_table_data()
                        if len(entry_piece.get()) == 30:
                            part_name = entry_piece.get()
                            cadena = "reset,RESET,0.0,The station was reestablished,1/"
                            if duration == "PASSED":
                                entry_piece.configure(state="readonly", textvariable=piece_name)
                                piece_name.set("")
                                safe_insert("Command received-> "+cadena+"\n"+"Command RESET PASSED"+"\n")
                                logging.info(f"Command received-> {cadena}\n Command RESET PASSED")
                            else:
                                safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n")
                                logging.error(f"Command received-> {cadena}\nCommand FAILED")
                                conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                        else:
                            entry_piece.configure(state="readonly", textvariable=piece_name)
                            piece_name.set("")
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
                        for item in option:
                            cadena += str(item) + ","
                        part_name = entry_piece.get()                
                        
                        if len(option) == 6 and option[-1] == '1/':
                            duration = conexion.duration(cadena, option[4])
                            cambio_status = conexion.cambio_status(option[4])

                            if duration == "PASSED":
                                try:
                                    url_data = conexion.obtener_url_api()
                                    print(url_data)

                                    url_traceability = url_data[3][0]
                                    print(f"URL Traceability: {url_traceability}")

                                    traceability_payload = traceability_json.traceability_station_80_v2(
                                        option[4]
                                    )

                                    response_traceability = requests.post(
                                        url_traceability,
                                        json=traceability_payload,
                                        headers={'Content-Type': 'application/json'},
                                        timeout=30
                                    )
                                    logging.info(f"[TRACEABILITY JSON]:\n{json.dumps(traceability_payload, indent=4, ensure_ascii=False)}")
                                    
                                    if response_traceability.status_code != 200:
                                        safe_insert(f"❌ERROR {response_traceability.status_code}]:\n{response_traceability.text}\n", "red")
                                        conn.send("FAILED, TRACEABILITY ERROR".encode('UTF-8'))
                                        cadena = ""
                                        continue
                                        
                                    json_trace = response_traceability.json()
                                    logging.info(f"[TRACEABILITY RESPONSE JSON]:\n{json.dumps(json_trace, indent=4, ensure_ascii=False)}")
                                    validador_trace = json_trace.get("success")
                                    if str(validador_trace).lower() not in ("true", "1"):
                                        msg_err_t = json_trace.get("message", "Traceability validation rejected")
                                        safe_insert(f"❌ [REJECTED 200]:\n{json.dumps(json_trace, indent=2)}\n", "red")
                                        conn.send("FAILED, TRACEABILITY REJECT".encode('UTF-8'))
                                        cadena = ""
                                        continue

                                    pantalla_end = (
                                        f"Command received-> {cadena}\nCommand END PROCESS PASSED\n"
                                        f"\nTraceability Data Dispatched & Saved Successfully"
                                        f"\n\n[TRACEABILITY]:\n{json.dumps(traceability_payload, indent=4, ensure_ascii=False)}\n\n"
                                        f"[TRACEABILITY RESPONSE]:\n{json.dumps(json_trace, indent=2)}\n\n"
                                        
                                    )

                                    safe_insert(pantalla_end, "green")

                                except Exception as err_trace:
                                    conn.send("FAILED, TRACEABILITY OFFLINE".encode('UTF-8'))
                                    logging.error(f"Error executing traceability dispatch: {err_trace}")
                                    safe_insert(f"Traceability Network Error: {str(err_trace)}", "red")
                                    conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                                    conexionBitacora.event("CMD-F002","|Command,FAILED|",month,day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    cadena = ""
                                    continue

                                try:
                                    conn.send("PASSED".encode('UTF-8'))
                                    conexionBitacora.event("ENDP-001","|Command received| "+cadena,month,day)
                                    conexionBitacora.event("CMD-F001","|Command,PASSED|",month,day)
                                    green_label.configure(image=image_green_full)
                                    red_label.configure(image=image_red)

                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                    conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                                    conexionBitacora.event("CMD-F002","|Command,FAILED|",month,day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                            else:
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n","red")
                                conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                        else:
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n","red")
                            conexionBitacora.event("ENDP-002","|Command received| "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
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
                            conexionBitacora.event("NMP-001","|Command received| "+cadena,month,day)
                            conexionBitacora.event("CMD-P001","|Command,PASSED|",month,day)
                            green_label.configure(image=image_green_full)
                            red_label.configure(image=image_red)
                        else:
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            conexionBitacora.event("NMP-002","|Command received| "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
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
                                safe_insert("Command received-> "+cadena+ " |Model:| " +modelName+"\n"+"Command FAILED"+"\n", "red")
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                conexionBitacora.event("SMP-002","|Command received| "+cadena+" |Model:| "+modelName,month,day)
                                conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
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
                                conexionBitacora.event("SMP-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-P001","|Command,PASSED|",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                        else:
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")
                            conexionBitacora.event("SMP-002","|Command received| "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
                        cadena = ""
                        pieza = ""

                    case "commit":
                        clear_table_data()
                        cadena = ""
                        for item in option:
                            cadena += str(item) + ","
                        # print(cadena)
                        if option[-1] == '1/':
                                        
                            part_name = option[-2]
                            commit_options, table_data = commands.commit(cadena, part_name)
                    
                            if(commit_options == 'PASSED'):
                                if table_data:
                                    update_table_with_data(table_data)

                                safe_insert("Command received-> "+cadena+"\n"+"Command COMMIT PASSED"+"\n")
                                try:
                                    conn.send("PASSED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")
                                
                                conexionBitacora.event("COM-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-P001","|Command,PASSED|",month,day)

                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                            else:
                                safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(f"Error enviando: {e}", "red")

                                conexionBitacora.event("COM-002","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)

                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                        else:
                            safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                            except Exception as e:
                                safe_insert(f"Error enviando: {e}", "red")

                            conexionBitacora.event("COM-002","|Command received| "+cadena,month,day)
                            conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
                            green_label.configure(image=image_green)
                            red_label.configure(image=image_red_full)
                        cadena = ""
                        pieza = ""

                    case "Component":
                        clear_table_data()

                        cadena = ""
                        for item in option:
                            cadena += str(item) + ","

                        if len(option) == 3 and option[-1] == '1/':
                            top_level = option[1].strip()
                            result, message, url_unit = unit_api.consultar_part_number_unit(top_level)
                            if result == "PASSED":
                                conexion.piece_store2(top_level, message)
                                pantalla_final = (f"Command received -> {comando_completo},\n Command COMPONENT PASSED\n\n"
                                                  f"[URL UNIT]: {url_unit}\n\n"
                                                  f"[TOP LEVEL]:\n{top_level}\n\n" 
                                                  f"[PART NUMBER]:{message}\n\n"
                                                )
                                conexionBitacora.event("COM-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,PASSED|",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)

                                try:
                                    conn.send("PASSED".encode('UTF-8'))

                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break
                                safe_insert(pantalla_final, "green")
                                logging.info(pantalla_final)
                            else:
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break
                                conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                conexionBitacora.event("CMD-P002", f"|Command,FAILED|" , month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)

                                pantalla_final = (f"Command received -> {comando_completo}\n Command COMPONENT FAILED\n\n"
                                                f"[URL UNIT]: {url_unit}\n\n"
                                                f"[TOP LEVEL]:\n{top_level}\n\n" 
                                                f"[MESSAGE]:{message}\n\n"
                                                )

                                safe_insert(pantalla_final, "red")
                                logging.info(pantalla_final)
                                    
                        elif len(option) == 4 and option[-1] == '1/':
                            top_level = option[1].strip()

                            pcb = option[2].strip()

                            result, message, url_unit = unit_api.consultar_part_number_unit(pcb)

                            if result == "PASSED":
                                conexion.component_store(pcb, message, top_level)
                                pantalla_final = (f"Command received -> {comando_completo},\n Command COMPONENT PASSED\n\n"
                                                    f"[URL UNIT]: {url_unit}\n\n"
                                                    f"[TOP LEVEL]:\n{top_level}\n\n"
                                                    f"[PCB]:\n{pcb}\n\n" 
                                                    f"[PART NUMBER PCB]:\n{message}\n\n"
                                                )
                                
                                conexionBitacora.event("COM-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,PASSED|",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)

                                try:
                                    conn.send("PASSED".encode('UTF-8'))

                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break
                                safe_insert(pantalla_final, "green")
                                logging.info(pantalla_final)
                            else:
                                try:
                                    conn.send("FAILED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break
                                conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                conexionBitacora.event("CMD-P002", f"|Command,FAILED|" , month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)

                                pantalla_final = (f"Command received -> {comando_completo}\n Command COMPONENT FAILED\n\n"
                                                f"[URL UNIT]: {url_unit}\n\n"
                                                f"[TOP LEVEL]:\n{top_level}\n\n"
                                                f"[PCB]:\n{pcb}\n\n" 
                                                f"[MESSAGE]:{message}\n\n"
                                                )

                                safe_insert(pantalla_final, "red")
                                logging.info(pantalla_final)
                        else:
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                                safe_insert("Command received-> " + cadena + "\n" + "Command FAILED", "red")
                                conexionBitacora.event("SPP-002", "|Command received| " + cadena, month, day)
                                conexionBitacora.event("CMD-F001", "|Command,FAILED|", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                cadena = ""

                            except Exception as e:
                                safe_insert(str(e),"red")
                                logging.error(str(e))
                                conexionBitacora.event("SPP-002", f"Serial number: {top_level}", month, day)
                                conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                    case "interlocking":
                        if len(option) == 3 and option[-1] == "1/":
                            safe_insert("🔗 Dispatching validation schema to Interlocking...", "blue")

                            top_level = option[1]
                            result, message, response_data, reintentos, respuesta, json_data, succes_data =interlocking_api.validate_piece_st80_v2(top_level, 5, 2)
                            if succes_data == "true":
                                try:
                                    conn.send("PASSED".encode('UTF-8'))
                                except Exception as e:
                                    safe_insert(str(e),"red")
                                    logging.error(str(e))
                                    conexionBitacora.event("INT-002", f"Serial number: {top_level}", month, day)
                                    conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    break
                                pantalla_final = (f"Command received -> {comando_completo}\n Command INTERLOCKING PASSED\n\n"
                                                f"[INTERLOCKING REQUEST]:\n {json.dumps(json_data, indent=4 )}\n\n"
                                                f"[INTERLOCKING RESPONSE]:\n {json.dumps(response_data, indent=4 )}\n\n"
                                                )
                                safe_insert(pantalla_final, "green")
                                logging.info(pantalla_final)
                                conexionBitacora.event("INT-001","|Command received| "+cadena,month,day)
                                conexionBitacora.event("CMD-F001","|Command,PASSED|",month,day)
                                green_label.configure(image=image_green_full)
                                red_label.configure(image=image_red)
                            else:
                                try:
                                    pantalla_final = (f"Command received -> {comando_completo}\n Command INTERLOCKING FAILED\n\n"
                                                    f"[INTERLOCKING REQUEST]:\n {json.dumps(json_data, indent=4 )}\n\n"
                                                    f"[INTERLOCKING RESPONSE]:\n {json.dumps(response_data, indent=4 )}\n\n"
                                                    )
                                    conn.send("FAILED".encode('UTF-8'))
                                    safe_insert(pantalla_final, "red")
                                    logging.error(pantalla_final)
                                    conexionBitacora.event("INT-002", "|Command received| " + cadena, month, day)
                                    conexionBitacora.event("CMD-F001", "|Command,FAILED|", month, day)
                                    green_label.configure(image=image_green)
                                    red_label.configure(image=image_red_full)
                                    cadena = ""

                                except Exception as e:     
                                        
                                        safe_insert(str(e),"red")
                                        logging.error(str(e))
                                        conexionBitacora.event("INT-002", f"Serial number: {top_level}", month, day)
                                        conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                        green_label.configure(image=image_green)
                                        red_label.configure(image=image_red_full)
                                        break
                                
                        else:
                            try:
                                conn.send("FAILED".encode('UTF-8'))
                                safe_insert("Command received-> " + comando_completo + "\n" + "Command FAILED", "red")
                                logging("Command received ->" + comando_completo + "\n" + "Command FAILED")
                                conexionBitacora.event("INT-002", "|Command received| " + cadena, month, day)
                                conexionBitacora.event("CMD-F001", "|Command,FAILED|", month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                cadena = ""

                            except Exception as e:
                                safe_insert(str(e),"red")
                                logging.error(str(e))
                                conexionBitacora.event("INT-002", f"Serial number: {top_level}", month, day)
                                conexionBitacora.event("CMD-P002", f"|Command,FAILED| Error:{e}" , month, day)
                                green_label.configure(image=image_green)
                                red_label.configure(image=image_red_full)
                                break

                    case "laser":
                        serial = conexion.get_part_numbers('P2173404-00-C:SEYU26061A0765')
                        if serial != "PASSED":
                            conn.send(f"{serial}".encode('UTF-8'))
                            safe_insert(f"Command received-> {cadena} part: {serial}\nCommand PASSED\nPrinting...\n", "green")
                        else:
                            conn.send("do_not_print".encode('UTF-8'))
                            safe_insert(f"Command received-> {cadena} part: {serial}\nCommand PASSED\nDon't print\n", "orange")

                    case _:
                        safe_insert("Command received-> "+cadena+"\n"+"Command FAILED"+"\n", "red")
                        try:
                            conn.send("FAILED".encode('UTF-8'))
                        except Exception as e:
                            safe_insert(f"Error enviando: {e}", "red")
                        conexionBitacora.event("COM-002","|Command received| "+cadena,month,day)
                        conexionBitacora.event("CMD-F001","|Command,FAILED|",month,day)
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
            active_connections.append(conn)  # <- Guardamos el socket
            t = threading.Thread(target=worker, args=(conn, addr), daemon=True)
            client_threads[:] = [t for t in client_threads if t.is_alive()]  # Limpieza
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
        # Tu código para mostrar ventana de error por IP/puerto
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
