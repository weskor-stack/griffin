__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import os
import csv
from datetime import datetime
import conexion
import get_name_PC
from datetime import datetime, timezone 
import rfc3339

# Encabezados para columnas C a K (las columnas A y B se dejan vacías en el encabezado)
ENCABEZADOS = [
    "data type",
    "compoperator",
    "lowerlimit",
    "upperlimit",
    "value",
    "result",
    "testtime",
    "units",
    "duration"
]

def csv_file():
    """Genera archivo CSV con el formato exacto del ejemplo"""
    try:
        # Obtener timestamp con formato RFC3339 + offset (ej. "2026-03-07T17:49:43Z 06:00")
        tasktimestamp = datetime.now(timezone.utc).astimezone()
        last_digit = str(tasktimestamp).split('-')
        timer2 = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False) + " " + last_digit[3]

        # Obtener datos básicos
        station = conexion.stations()
        type_station = station[4]
        station_name = station[2]
        
        name = conexion.pieces()
        piece_id = name[0]
        piece_number = name[1]
        
        # Fecha/hora para testtime (mismo timer para todas las pruebas)
        current_time = timer2
        
        # Preparar datos para el CSV
        csv_data = []
        
        # FILAS 1-6: ESTRUCTURA DEL EJEMPLO
        csv_data.append(["Ver.", "1.0.0"])                                      # Fila 1
        csv_data.append([station_name, piece_number])                           # Fila 2
        csv_data.append([])                                                     # Fila 3
        csv_data.append([])                                                     # Fila 4
        csv_data.append([])                                                     # Fila 5
        csv_data.append(["ReadISN", "0", piece_number])                         # Fila 6
        
        # FILA 7: ENCABEZADOS (comenzando en columna C)
        csv_data.append(["", ""] + ENCABEZADOS)
        
        # Obtener todas las filas de datos según el tipo de estación
        filas_datos = []
        if type_station == 1:  # Screwing
            filas_datos = get_screwing_rows(piece_id, station_name, current_time)
        elif type_station == 2:  # Pressfit
            filas_datos = get_pressfit_rows(piece_id, station_name, current_time)
        elif type_station == 3:  # Inspection
            filas_datos = get_inspection_rows(piece_id, station_name, current_time)
        elif type_station == 4:  # Completa
            filas_datos = get_complete_rows(piece_id, station_name, current_time)
        
        # Agregar filas de datos (cada fila ya tiene 11 columnas: A, B, y C-K)
        csv_data.extend(filas_datos)
        
        name = conexion.pieces()
        piece_id = name[0]
        duration = conexion.duration_json(station[0], piece_id)
        
        taskresult = duration[0] # tabla duration

        # Generar nombre del archivo (igual que antes)
        name = piece_number
        divisor = name.index(":")
        name2 = name.replace("-", "_").replace(":", "_")
        name_file = str(timer2[0:19]).replace("-", "_").replace(":", "_").replace(" ", "_")
        name_file = f"{name2}_{name_file}_{taskresult}_{station_name}"
        
        result = save_csv_file(csv_data, name_file)
        return result
        
    except Exception as e:
        print(f"[ERROR] csv_file(): {e}")
        return f"FAILED: {str(e)}"

def get_screwing_rows(piece_id, station_name, current_time):
    """Devuelve lista de filas (11 columnas) para pruebas de screwing"""
    screwing = conexion.screwing_data(piece_id)
    filas = []
    
    
    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    
    for x in screwing:
        if x[0] == 1:
            indice += 1
        if x[0] == 2:
            indice2 += 1
            indice = indice2
        if x[0] == 3:
            indice3 += 1
            indice = indice3
        if x[0] == 4:
            indice4 += 1
            indice = indice4
        
        # Construir fila de 11 elementos: [A, B, C, D, E, F, G, H, I, J, K]
        fila = [
            "Screwing",                          # A: type
            "",                                   # B: vacío
            "Numeric",                            # C: data type (fijo)
            "",                                   # D: compoperator
            str(x[2]) if len(x) > 2 else "",      # E: lowerlimit
            str(x[3]) if len(x) > 3 else "",      # F: upperlimit
            str(x[1]) if len(x) > 1 else "",      # G: value
            f"Step {indice} - {x[10] if len(x) > 10 else ''}",  # H: description
            x[6] if len(x) > 6 else "",           # I: result
            current_time,                          # J: testtime
            x[5] if len(x) > 5 else ""             # K: units
        ]
        filas.append(fila)
    
    return filas

def get_pressfit_rows(piece_id, station_name, current_time):
    """Devuelve lista de filas para pruebas de pressfit"""
    pressfit = conexion.pressfit_data(piece_id)
    filas = []
    
    indice = 0
    indice2 = 0
    indice3 = 0
    
    for x in pressfit:
        if x[0] == 1:
            indice += 1
        if x[0] == 2:
            indice2 += 1
            indice = indice2
        if x[0] == 3:
            indice3 += 1
            indice = indice3
        
        fila = [
            "Pressfit",
            "",
            "Numeric",
            "",
            str(x[2]) if len(x) > 2 else "",
            str(x[3]) if len(x) > 3 else "",
            str(x[1]) if len(x) > 1 else "",
            f"Step {indice} - {x[10] if len(x) > 10 else ''}",
            x[6] if len(x) > 6 else "",
            current_time,
            x[5] if len(x) > 5 else ""
        ]
        filas.append(fila)
    
    return filas

def get_inspection_rows(piece_id, station_name, current_time):
    """Devuelve lista de filas para pruebas de inspection"""
    inspections = conexion.inspection_data(piece_id)
    filas = []
    
    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    indice5 = 0
    indice6 = 0
    
    for x in inspections:
        if x[0] == 1:
            indice += 1
        if x[0] == 2:
            indice2 += 1
            indice = indice2
        if x[0] == 3:
            indice3 += 1
            indice = indice3
        if x[0] == 4:
            indice4 += 1
            indice = indice4
        if x[0] == 5:
            indice5 += 1
            indice = indice5
        if x[0] == 6:
            indice6 += 1
            indice = indice6
        
        fila = [
            "Inspection",
            "",
            "Numeric",
            "",
            str(x[2]) if len(x) > 2 else "",
            str(x[3]) if len(x) > 3 else "",
            str(x[1]) if len(x) > 1 else "",
            f"Step {indice} - {x[10] if len(x) > 10 else ''}",
            x[6] if len(x) > 6 else "",
            current_time,
            x[5] if len(x) > 5 else ""
        ]
        filas.append(fila)
    
    return filas

def get_complete_rows(piece_id, station_name, current_time):
    """Devuelve lista de filas para estación completa (todos los tipos de prueba)"""
    filas = []
    resultado = ""
    
    # Screwing tests (data3)
    screwing = conexion.screwing_data(piece_id)
    for x in screwing:

        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        fila = [
            x[11],
            "",
            str(x[4]),
            str(x[7]),
            str(x[2]),
            str(x[3]),
            str(x[1]),
            # str(x[9]),
            resultado,
            str(x[8]),
            str(x[5]),
            "" 
        ]
        filas.append(fila)
    
    # Pressfit tests (data3)
    pressfit = conexion.pressfit_data(piece_id)
    for x in pressfit:
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"
        fila = [
            x[11],
            "",
            str(x[4]),
            str(x[7]),
            str(x[2]),
            str(x[3]),
            str(x[1]),
            # str(x[9]),
            resultado,
            str(x[8]),
            str(x[5]),
            ""
        ]
        filas.append(fila)
    
    # Inspection tests (data3)
    inspections = conexion.inspection_data(piece_id)
    for x in inspections:
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        low_limit = str(x[2])
        hig_limit = str(x[3])

        if low_limit == '0.0':
            low_limit = ""
        
        if hig_limit == '0.0':
            hig_limit = ""
        
        fila = [
            x[11],
            "",
            str(x[4]),
            str(x[7]),
            low_limit,
            hig_limit,
            str(x[1]),
            # str(x[9]),
            resultado,
            str(x[8]),
            str(x[5]),
            ""
        ]
        filas.append(fila)
    
    # Electrical tests (data3)
    electrical = conexion.electrical_data(piece_id)
    for x in electrical:
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"
        fila = [
            x[11],
            "",
            str(x[4]),
            str(x[7]),
            str(x[2]),
            str(x[3]),
            str(x[1]),
            # str(x[9]),
            resultado,
            str(x[8]),
            str(x[5]),
            ""
        ]
        filas.append(fila)
    
    # Continuity tests (data3)
    continuity = conexion.continuity_data(piece_id)
    for x in continuity:

        tiempo = x[9].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]

        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"
        fila = [
            str(x[0]),
            "",
            "Numeric",
            str(x[2]),
            str(x[3]),
            str(x[4]),
            str(x[7]),
            # str(x[1]),
            resultado,
            timer,
            str(x[5]),
            ""
        ]
        filas.append(fila)
    
    # Leak tests (data3)
    leak = conexion.leaktest_data(piece_id)
    for x in leak:
        tiempo = x[10].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]

        if x[3] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

    
        fila = [
            str(x[9]),
            "",
            str(x[1]),
            str(x[8]),
            str(x[6]),
            str(x[7]),
            str(x[2]),
            # str(x[5]),
            resultado,
            timer,
            str(x[4]),
            ""
        ]
        filas.append(fila)
    
    # Welding tests (data3)
    welding = conexion.welding_data(piece_id)
    for x in welding:
        tiempo = x[9].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]

        if x[5] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        fila = [
            str(x[0]),
            "",
            "Numeric",
            str(x[8]),
            "-",
            "-",
            str(x[3]),
            str(x[4]),
            resultado,
            timer,
            str(x[6]),
            ""
        ]
        filas.append(fila)
    
    # Temperature tests (data3)
    temperature = conexion.temperature_data(piece_id)
    for x in temperature:
        fila = [
            "Temperature",
            "",
            "Numeric",
            "",
            "",  # lowerlimit
            "",  # upperlimit
            f"Initial: {x[3]}, Final: {x[4]}" if len(x) > 4 else str(x[3]),
            f"Start: {x[1]}, End: {x[2]}",
            "",  # result no disponible
            current_time,
            x[5] if len(x) > 5 else ""
        ]
        filas.append(fila)
    
    # Component tests
    componente = conexion.component_data(piece_id)
    for x in componente:
        fila = [
            "Component",
            "",
            "Numeric",
            "",
            "",  # lowerlimit
            "",  # upperlimit
            x[0] if len(x) > 0 else "",   # nombre del componente como value
            "Componente instalado",
            "",  # result
            current_time,
            ""
        ]
        filas.append(fila)

    station = conexion.stations()
    duration = conexion.duration_json(station[0], piece_id)
    taskduration = duration[2]
    fila=[
        "Taskduration",
        "",
        "-",
        "-",
        "-",
        "-",
        "-",
        # "-",
        "-",
        "-",
        "-",
        taskduration
    ]
    filas.append(fila)

    return filas

def save_csv_file(csv_data, filename):
    """Guarda los datos en archivo CSV con misma estructura de directorios que JSON"""
    try:
        today = datetime.now()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")
        
        file_data_bk = f"C:/AMC/CSV/{today_year}/{today_month}/{today_day}/"
        file_data = f"C:/Users/Tesla/Documents/Traceability/{today_year}/{today_month}/{today_day}/"
        
        os.makedirs(file_data_bk, exist_ok=True)
        os.makedirs(file_data, exist_ok=True)
        
        filepath_bk = os.path.join(file_data_bk, f"{filename}.csv")
        filepath = os.path.join(file_data, f"{filename}.csv")
        
        with open(filepath_bk, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
        
        print(f"[INFO] Archivo CSV generado: {filename}.csv")
        return "PASSED"
        
    except Exception as e:
        print(f"[ERROR] save_csv_file(): {e}")
        return f"FAILED: {str(e)}"

# Función para pruebas
# if __name__ == "__main__":
#     result = csv_file()
#     print(f"Resultado: {result}")