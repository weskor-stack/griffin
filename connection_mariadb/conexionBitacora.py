__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

# Module Imports
import mariadb
import sys

from tkinter import  messagebox 

import datetime
import logging


# Configurar logging básico si no existe
try:
    logging.info("Inicializando módulo de conexión a BD")
except:
    logging.basicConfig(level=logging.INFO)

class DatabaseManager:
    """Gestor de conexión a BD con reconexión automática"""
    
    def __init__(self):
        self.connection = None
        self.config = {
            "user": "root",
            "password": "u8ch9Xn4Ol8woLw3E2A6",
            "host": "127.0.0.1",
            "port": 3306,
            "database": "data_tracking_griffin_bitacora",
            "connect_timeout": 10,
            "pool_name": "my_pool",
            "pool_size": 3
        }
        self._connect()
    
    def _connect(self):
        """Establece conexión inicial"""
        try:
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
            
            self.connection = mariadb.connect(**self.config)
            # Configurar auto-reconnect y timeouts más largos
            cursor = self.connection.cursor()
            cursor.execute("SET SESSION wait_timeout = 28800")  # 8 horas
            cursor.execute("SET SESSION interactive_timeout = 28800")
            cursor.execute("SET SESSION net_read_timeout = 300")
            cursor.execute("SET SESSION net_write_timeout = 300")
            cursor.close()
            
            logging.info("✅ Conexión a BD establecida correctamente")
            print("✅ Conexión a BD establecida correctamente")
            
        except mariadb.Error as e:
            logging.error(f"❌ Error conectando a BD: {e}")
            print(f"❌ Error conectando a BD: {e}")
            messagebox.showerror(
                title="Error de Conexión", 
                message="No se pudo conectar a la base de datos. Verifica que MariaDB esté ejecutándose."
            )
            sys.exit(1)
    
    def _ensure_connection(self):
        """Verifica y reconecta si es necesario"""
        try:
            # Probar si la conexión está viva
            if self.connection is None:
                logging.warning("Conexión nula, reconectando...")
                self._connect()
                return
            
            self.connection.ping(reconnect=True)
            
        except (mariadb.Error, AttributeError) as e:
            logging.warning(f"Conexión perdida: {e}. Reconectando...")
            try:
                self._connect()
            except Exception as reconnect_error:
                logging.error(f"Error al reconectar: {reconnect_error}")
                raise
    
    def get_cursor(self):
        """Obtiene un cursor válido (con reconexión automática)"""
        self._ensure_connection()
        return self.connection.cursor()
    
    def commit(self):
        """Commit con verificación de conexión"""
        self._ensure_connection()
        self.connection.commit()
    
    def close(self):
        """Cierra la conexión"""
        if self.connection:
            try:
                self.connection.close()
                logging.info("Conexión a BD cerrada")
            except:
                pass

# Instancia global del gestor
db_manager = DatabaseManager()

def get_connection():
    """Obtiene la conexión actual (con reconexión automática)"""
    db_manager._ensure_connection()
    return db_manager.connection

# Mantener compatibilidad con código existente
conn = db_manager.connection

# Connect to MariaDB Platform
# try:
#     conn = mariadb.connect(
#         user="root",
#         password="u8ch9Xn4Ol8woLw3E2A6",
#         host="127.0.0.1",
#         port=3306,
#         database="data_tracking_griffin_bitacora"

#     )    
    
# except mariadb.Error as e:
#     print(f"Error connecting to MariaDB Platform: {e}")
#     messagebox.showerror(title="Connection", message=f"Check database connection", )
#     sys.exit(1)

# # Get Cursor
# cur = conn.cursor()

def event(env_number, env_message, env_mth, env_day):
    event_registration = conn.cursor()
    sql = "INSERT INTO data_tracking_griffin_bitacora.env_event (env_number, env_message, env_mth, evn_day) VALUES (%s, %s, %s, %s)"
    val = (env_number, env_message, env_mth, env_day)
    event_registration.execute(sql,val)
    conn.commit()

# ano = datetime.datetime.today().year
# mes = datetime.datetime.today().month
# day = datetime.datetime.today().day
# fecha = [ano, mes, day]
# print(fecha)

# event("Test-001","|cmtrq,1,3,P,M51A023A22823214AJ0019,Fuerza_Pinza12:200&Nm%PASS;Corriente12:3900&A%PASS;Tiempo_Brazzing12:65&mseg%PASS,CAM_OK,1|",mes,day)