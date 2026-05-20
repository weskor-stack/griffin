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

def csv_file():
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
        
        duration = conexion.duration_json(station[0], piece_id)
        
        # Preparar datos para el CSV según estructura solicitada
        csv_data = []
        
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
        
        # Obtener todos los tests según el tipo de estación
        tests = []
        pruebas = []
        
        if type_station == 1:  # Screwing
            tests = get_screwing_tests(piece_id, station_name)
        elif type_station == 2:  # Pressfit
            tests = get_pressfit_tests(piece_id, station_name)
        elif type_station == 3:  # Inspection
            tests = get_inspection_tests(piece_id, station_name)
        elif type_station == 4:  # Completa
            tests, pruebas = get_complete_tests(piece_id, station_name)
        
        # Agregar tests al CSV (A7, A8, ... y C7, C8, ...)
        if type_station == 4:
            # Para type_station = 4, usar la lista pruebas en lugar de test_number
            for i, test_info in enumerate(tests):
                if i < len(pruebas):
                    # Usar el valor de pruebas[i] en lugar del número incremental
                    csv_data.append([f"P-0{pruebas[i]}", "", test_info])
                else:
                    # Fallback en caso de que no haya suficientes valores en pruebas
                    csv_data.append([f"P-0{i+1}", "", test_info])
        else:
            # Para los otros tipos de estación, mantener el comportamiento original
            test_number = 1
            for test_info in tests:
                csv_data.append([f"P-0{test_number}", "", test_info])
                test_number += 1
        
        # Generar nombre del archivo (mismo formato que json_file)
        name = piece_number
        divisor = name.index(":")
        
        name2 = name.replace("-", "_").replace(":", "_")
        
        name_file = str(timer[0:19]).replace("-", "_").replace(":", "_").replace(" ", "_")
        name_file = f"{name2}_{name_file}_{duration[0]}_{station_name}"
        
        # Guardar archivo CSV
        result = save_csv_file(csv_data, name_file)
        return result
        
    except Exception as e:
        print(f"[ERROR] csv_file(): {e}")
        return f"FAILED: {str(e)}"

def get_screwing_tests(piece_id, station_name):
    """Obtiene tests de screwing"""
    tests = []
    pruebas = []
    screwing = conexion.screwing_data(piece_id)
    
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
        
        # Formato: "TEST X: Descripción - Valor Unidad"
        test_info = f"{indice}b. {station_name} Test - {x[10]} STEP {indice}: {x[1]} {x[5]}"
        pruebas_name = f"{indice}-{x[10]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    return tests

def get_pressfit_tests(piece_id, station_name):
    """Obtiene tests de pressfit"""
    tests = []
    pruebas = []
    pressfit = conexion.pressfit_data(piece_id)
    
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
        
        test_info = f"{indice}b. {station_name} Test - {x[10]} STEP {indice}: {x[1]} {x[5]}"
        pruebas_name = f"{indice}-{x[10]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    return tests

def get_inspection_tests(piece_id, station_name):
    """Obtiene tests de inspection"""
    tests = []
    pruebas = []
    inspections = conexion.inspection_data(piece_id)
    
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
        
        test_info = f"{indice}b. {station_name} Test - {x[10]} STEP {indice}: {x[1]} {x[5]}"
        pruebas_name = f"{indice}-{x[10]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    return tests

def get_complete_tests(piece_id, station_name):
    """Obtiene todos los tests para estación completa (type_station = 4)"""
    tests = []
    pruebas = []
    
    # Screwing tests
    screwing = conexion.screwing_data(piece_id)
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
        
        test_info = f"Low limit={x[2]}, High limit={x[3]}, Value={x[1]}, Unit={x[5]}, Result={x[6]}"
        pruebas_name = f"{indice} {x[11]}-Screwing"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    # Pressfit tests
    pressfit = conexion.pressfit_data(piece_id)
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
        
        test_info = f"Low limit={x[2]}, High limit={x[3]}, Value={x[1]}, Unit={x[5]}, Result={x[6]}"
        pruebas_name = f"{indice}-{x[11]}-Pressfit"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    # Inspection tests
    inspections = conexion.inspection_data(piece_id)
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
        
        test_info = f"Low limit={x[2]}, High limit={x[3]}, Value={x[1]}, Unit={x[5]}, Result={x[6]}"
        pruebas_name = f"{indice}-{x[11]}-Inspection"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    # Electrical tests
    electrical = conexion.electrical_data(piece_id)
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
        
        test_info = f"Low limit={x[2]}, High limit={x[3]}, Value={x[1]}, Unit={x[5]}, Result={x[6]}"
        pruebas_name = f"{indice}-{x[11]}-Electrical"
        pruebas.append(pruebas_name)
        tests.append(test_info)
    
    # Continuity tests (indice empieza en 1 según data_json.py)
    continuity = conexion.continuity_data(piece_id)
    indice = 1
    
    for x in continuity:
        test_info = f"Low limit={x[3]}, High limit={x[4]}, Value={x[7]}, Unit={x[5]}, Result={x[6]}, Defect Code='{x[8]}'"
        pruebas_name = f"{indice}-{x[0]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
        indice += 1
    
    # Leak tests (indice empieza en 1 según data_json.py)
    leak = conexion.leaktest_data(piece_id)
    indice = 1
    
    for x in leak:
        test_info = f"Trial period={x[1]}, Value={x[2]}, Leak={x[4]}, Result={x[3]}, Low limit={x[6]}, High limit={x[7]}"
        pruebas_name = f"{indice}-{x[0]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
        indice += 1
    
    # Welding tests (nueva tabla, indice empieza en 1 según data_json.py)
    welding = conexion.welding_data(piece_id)
    indice = 1
    
    for x in welding:
        test_info = f"Time={x[1]}, Power={x[2]}, Collapse distance={x[3]}, Result={x[5]}, Unit={x[6]}"
        pruebas_name = f"{indice}-{x[0]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
        indice += 1
    
    # Temperature tests (indice empieza en 1 según data_json.py)
    temperature = conexion.temperature_data(piece_id)
    indice = 1
    
    for x in temperature:
        test_info = f"Start time={x[1]}, End time={x[2]}, Initial temperature={x[3]}, Final temperature={x[4]}, Unit={x[5]}"
        pruebas_name = f"{indice}-{x[0]}"
        pruebas.append(pruebas_name)
        tests.append(test_info)
        indice += 1
    
    # Component tests (indice empieza en 1 según data_json.py)
    componente = conexion.component_data(piece_id)
    indice = 1
    
    for x in componente:
        test_info = f"{indice}b. {station_name} Test - Component #{indice}: {x[0]}"
        pruebas_name = f"{indice}-Component"
        pruebas.append(pruebas_name)
        tests.append(test_info)
        indice += 1
    
    return tests, pruebas

def save_csv_file(csv_data, filename):
    """Guarda los datos en archivo CSV con misma estructura de directorios que JSON"""
    try:
        today = datetime.now()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")
        
        # Directorios de salida (misma estructura que generate_json_pressfit.pressfitJson3)
        file_data_bk = f"C:/AMC/CSV/{today_year}/{today_month}/{today_day}/"
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
#     result = csv_file()
#     print(f"Resultado: {result}")