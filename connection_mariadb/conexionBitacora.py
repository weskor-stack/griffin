# Module Imports
import mariadb
import sys

from tkinter import  messagebox 

import datetime


# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="u8ch9Xn4Ol8woLw3E2A6",
        host="127.0.0.1",
        port=3306,
        database="data_tracking_bitacora"

    )    
    
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    messagebox.showerror(title="Connection", message=f"Check database connection", )
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

def event(env_number, env_message, env_mth, env_day):
    event_registration = conn.cursor()
    sql = "INSERT INTO env_event (env_number, env_message, env_mth, evn_day) VALUES (%s, %s, %s, %s)"
    val = (env_number, env_message, env_mth, env_day)
    event_registration.execute(sql,val)
    conn.commit()

# ano = datetime.datetime.today().year
# mes = datetime.datetime.today().month
# day = datetime.datetime.today().day
# fecha = [ano, mes, day]
# print(fecha)

# event("Test-001","|cmtrq,1,3,P,M51A023A22823214AJ0019,Fuerza_Pinza12:200&Nm%PASS;Corriente12:3900&A%PASS;Tiempo_Brazzing12:65&mseg%PASS,CAM_OK,1|",mes,day)