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

def csv_file(limite):
    """Genera archivo CSV con la estructura especificada"""
    try:
        # Obtener timestamp (mismo formato que json_file)
        tasktimestamp = datetime.now(timezone.utc).astimezone()
        last_digit = str(tasktimestamp).split('-')
        timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False) + " " + last_digit[3]

        # Obtener datos básicos (mismo que json_file)
        station = conexion.stations()
        type_station = station[4]
        station_name = station[2]
        
        name = conexion.pieces()
        piece_id = name[0]
        piece_number = name[1]
        
        # Preparar datos para el CSV según estructura solicitada
        csv_data = []
        
        # FILAS 1-6: ESTRUCTURA ORIGINAL (RESPETADA)
        # Fila 1: Ver. y fecha
        fecha_actual = datetime.now().strftime("%Y/%m/%d")
        csv_data.append(["Ver.", "1.0.0"])
        
        # Fila 2: Station y piece_id
        csv_data.append([f"{station_name}", f"{piece_number}"])
        
        # Filas 3-5 vacías (3 filas vacías)
        csv_data.append([])  # Fila 3
        csv_data.append([])  # Fila 4  
        csv_data.append([])  # Fila 5
        
        # Fila 6: ReadISN y piece_id (celda C6)
        csv_data.append(["ReadISN", "0", f"{piece_number}"])
        
        # A PARTIR DE LA FILA 7: FORMATO VARIABLE/VALOR
        # Obtener todos los tests según el tipo de estación
        if type_station == 1:  # Screwing
            csv_data = get_screwing_tests_csv(piece_id, station_name, csv_data)
        elif type_station == 2:  # Pressfit
            csv_data = get_pressfit_tests_csv(piece_id, station_name, csv_data)
        elif type_station == 3:  # Inspection
            csv_data = get_inspection_tests_csv(piece_id, station_name, csv_data)
        elif type_station == 4:  # Completa
            csv_data = get_complete_tests_csv(piece_id, station_name, limite, csv_data)
        
        # Generar nombre del archivo (mismo formato que json_file)
        name = piece_number
        divisor = name.index(":")
        
        name2 = name.replace("-", "_").replace(":", "_")
        
        name_file = str(timer[0:19]).replace("-", "_").replace(":", "_").replace(" ", "_")
        name_file = f"{name2}_{name_file}_{station_name}"
        
        # Guardar archivo CSV
        result = save_csv_file(csv_data, name_file)
        return result
        
    except Exception as e:
        print(f"[ERROR] csv_file(): {e}")
        return f"FAILED: {str(e)}"

def get_screwing_tests_csv(piece_id, station_name, csv_data):
    """Obtiene tests de screwing en formato variable/valor"""
    screwing = conexion.screwing_data(piece_id)
    
    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    
    test_counter = 1
    
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"{indice}b. {station_name} Test - {x[10]} STEP {indice}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Low Limit", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["High Limit", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["Result", x[6] if len(x) > 6 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    return csv_data

def get_pressfit_tests_csv(piece_id, station_name, csv_data):
    """Obtiene tests de pressfit en formato variable/valor"""
    pressfit = conexion.pressfit_data(piece_id)
    
    indice = 0
    indice2 = 0
    indice3 = 0
    test_counter = 1
    
    for x in pressfit:
        if x[0] == 1:
            indice += 1
        if x[0] == 2:
            indice2 += 1
            indice = indice2
        if x[0] == 3:
            indice3 += 1
            indice = indice3
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"{indice}b. {station_name} Test - {x[10]} STEP {indice}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Low Limit", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["High Limit", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["Result", x[6] if len(x) > 6 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    return csv_data

def get_inspection_tests_csv(piece_id, station_name, csv_data):
    """Obtiene tests de inspection en formato variable/valor"""
    inspections = conexion.inspection_data(piece_id)
    
    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    indice5 = 0
    indice6 = 0
    test_counter = 1
    
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"{indice}b. {station_name} Test - {x[10]} STEP {indice}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Low Limit", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["High Limit", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["Result", x[6] if len(x) > 6 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    return csv_data

def get_complete_tests_csv(piece_id, station_name, limite, csv_data):
    """Obtiene todos los tests para estación completa en formato variable/valor"""
    test_counter = 1
    
    # Screwing tests
    screwing = conexion.screwing_data3(piece_id, limite)
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Screwing Test - {x[11]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Low limit", str(x[2])])
        csv_data.append(["High limit", str(x[3])])
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Result", x[6]])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Pressfit tests
    pressfit = conexion.pressfit_data3(piece_id, limite)
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Pressfit Test - {x[11]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Low limit", str(x[2])])
        csv_data.append(["High limit", str(x[3])])
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Result", x[6]])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Inspection tests
    inspections = conexion.inspection_data3(piece_id, limite)
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Inspection Test - {x[11]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Low limit", str(x[2])])
        csv_data.append(["High limit", str(x[3])])
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Result", x[6]])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Electrical tests
    electrical = conexion.electrical_data3(piece_id, limite)
    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    
    for x in electrical:
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
        
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Electrical Test - {x[11]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Low limit", str(x[2])])
        csv_data.append(["High limit", str(x[3])])
        csv_data.append(["Value", str(x[1])])
        csv_data.append(["Unit", x[5]])
        csv_data.append(["Result", x[6]])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Continuity tests
    continuity = conexion.continuity_data3(piece_id, limite)
    
    for x in continuity:
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Continuity Test - {x[0]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Low limit", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["High limit", str(x[4]) if len(x) > 4 else "N/A"])
        csv_data.append(["Value", str(x[7]) if len(x) > 7 else "N/A"])
        csv_data.append(["Unit", x[5] if len(x) > 5 else "N/A"])
        csv_data.append(["Result", x[6] if len(x) > 6 else "N/A"])
        csv_data.append(["Defect Code", x[8] if len(x) > 8 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Leak tests
    leak = conexion.leaktest_data3(piece_id, limite)
    
    for x in leak:
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Leak Test - {x[0]}"])
        test_counter += 1
        
        # Parámetros de la prueba - period= en columna A, valor en columna B
        csv_data.append(["Trial period", str(x[1]) if len(x) > 1 else "N/A"])
        csv_data.append(["Value", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["Result", x[3] if len(x) > 3 else "N/A"])
        csv_data.append(["Leak", str(x[4]) if len(x) > 4 else "N/A"])
        csv_data.append(["Low limit", str(x[6]) if len(x) > 6 else "N/A"])
        csv_data.append(["High limit", str(x[7]) if len(x) > 7 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Welding tests
    welding = conexion.welding_data3(piece_id, limite)
    
    for x in welding:
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Welding Test - {x[0]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Time", str(x[1]) if len(x) > 1 else "N/A"])
        csv_data.append(["Power", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["Collapse distance", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["Result", x[5] if len(x) > 5 else "N/A"])
        csv_data.append(["Unit", x[6] if len(x) > 6 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Temperature tests
    temperature = conexion.temperature_data3(piece_id, limite)
    
    for x in temperature:
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Temperature Test - {x[0]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Start time", str(x[1]) if len(x) > 1 else "N/A"])
        csv_data.append(["End time", str(x[2]) if len(x) > 2 else "N/A"])
        csv_data.append(["Initial temperature", str(x[3]) if len(x) > 3 else "N/A"])
        csv_data.append(["Final temperature", str(x[4]) if len(x) > 4 else "N/A"])
        csv_data.append(["Unit", x[5] if len(x) > 5 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    # Component tests
    componente = conexion.component_data(piece_id)
    
    for x in componente:
        # Título de la prueba
        csv_data.append([f"P-0{test_counter}", f"Component Test - {x[0]}"])
        test_counter += 1
        
        # Parámetros de la prueba
        csv_data.append(["Component", str(x[0]) if len(x) > 0 else "N/A"])
        csv_data.append([])  # Fila vacía entre pruebas
    
    return csv_data

def save_csv_file(csv_data, filename):
    """Guarda los datos en archivo CSV con misma estructura de directorios que JSON"""
    try:
        today = datetime.now()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")
        
        # Directorios de salida (misma estructura que generate_json_pressfit.pressfitJson3)
        file_data_bk = f"C:/AMC/RETRY/CSV/{today_year}/{today_month}/{today_day}/"
        file_data = f"C:/Users/Tesla/Documents/Traceability/{today_year}/{today_month}/{today_day}/"
        
        # Crear directorios si no existen
        os.makedirs(file_data_bk, exist_ok=True)
        os.makedirs(file_data, exist_ok=True)
        
        # Rutas completas de archivos
        filepath_bk = os.path.join(file_data_bk, f"{filename}.csv")
        filepath = os.path.join(file_data, f"{filename}.csv")
        
        # Guardar en backup
        with open(filepath_bk, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
        
        # Guardar en directorio principal
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
#     result = csv_file(4)
#     print(f"Resultado: {result}")