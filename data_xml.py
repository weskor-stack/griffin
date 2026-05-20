__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import conexion
import get_name_PC
from datetime import datetime, timezone 
import rfc3339

def xml_file():
    """Genera archivo XML estructurado por tipos de test"""
    try:
        # Obtener timestamp (mismo formato que json_file)
        tasktimestamp = datetime.now(timezone.utc).astimezone()
        last_digit = str(tasktimestamp)
        last_digit = last_digit.split('-')
        timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False) + " " + last_digit[3]

        # Obtener datos básicos (mismo que json_file)
        station = conexion.stations()
        type_station = station[4]
        station_name = station[2]
        
        name = conexion.pieces()
        piece_id = name[0]
        piece_number = name[1]
        
        duration = conexion.duration_json(station[0], piece_id)
        
        # Extraer partnumber y sitecode (mismo que json_file)
        divisor = piece_number.index(":")
        partnumber = piece_number[1:divisor]
        sitecode = piece_number[divisor+2:divisor+5]
        
        # Crear elemento raíz
        root = ET.Element("TraceabilityData")
        
        # Información general (Header)
        header = ET.SubElement(root, "Header")
        
        ET.SubElement(header, "FlowStepName").text = ""
        ET.SubElement(header, "FlowName").text = ""
        ET.SubElement(header, "ActorName").text = get_name_PC.getName()
        ET.SubElement(header, "ActorVersion").text = "1.1-130-g12b05f3"
        ET.SubElement(header, "ActorLocation").text = ""
        
        ET.SubElement(header, "Station").text = str(station_name)
        ET.SubElement(header, "PieceID").text = str(piece_id)
        ET.SubElement(header, "PieceNumber").text = str(piece_number)
        ET.SubElement(header, "PartNumber").text = str(partnumber)
        ET.SubElement(header, "Schema").text = ""
        ET.SubElement(header, "SiteCode").text = str(sitecode)
        
        ET.SubElement(header, "TaskDuration").text = str(duration[2])
        ET.SubElement(header, "TaskName").text = str(station_name)
        ET.SubElement(header, "TaskResult").text = str(duration[0])
        ET.SubElement(header, "TaskTimestamp").text = str(timer)
        ET.SubElement(header, "ThingName").text = str(piece_number)
        
        # Sección de Tests
        tests_element = ET.SubElement(root, "Tests")
        
        if type_station == 1:  # Screwing
            add_screwing_xml(tests_element, piece_id, station_name)
        elif type_station == 2:  # Pressfit
            add_pressfit_xml(tests_element, piece_id, station_name)
        elif type_station == 3:  # Inspection
            add_inspection_xml(tests_element, piece_id, station_name)
        elif type_station == 4:  # Completa
            add_complete_xml(tests_element, piece_id, station_name)
        
        # Generar nombre del archivo (mismo formato que json_file)
        name2 = str(piece_number).replace("-", "_").replace(":", "_")
        name_file = str(timer[0:19]).replace("-", "_").replace(":", "_").replace(" ", "_")
        name_file = f"{name2}_{name_file}_{duration[0]}_{station_name}"
        
        # Guardar archivo XML
        result = save_xml_file(root, name_file)
        return result
        
    except Exception as e:
        print(f"[ERROR] xml_file(): {e}")
        return f"FAILED: {str(e)}"

def add_screwing_xml(parent, piece_id, station_name):
    """Añade datos de screwing al XML"""
    screwing_element = ET.SubElement(parent, "ScrewingTests")
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
        
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(screwing_element, "Test")
        # ET.SubElement(test, "Number").text = str(indice)
        ET.SubElement(test, "Type").text = safe_str(x[4])
        ET.SubElement(test, "CompOperator").text = safe_str(x[7])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[2])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[3])
        ET.SubElement(test, "Value").text = safe_str(x[1])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[9])
        ET.SubElement(test, "Result").text = resultado
        ET.SubElement(test, "TestTime").text = safe_str(x[8])
        ET.SubElement(test, "Unit").text = safe_str(x[5])

def add_pressfit_xml(parent, piece_id, station_name):
    """Añade datos de pressfit al XML"""
    pressfit_element = ET.SubElement(parent, "PressfitTests")
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
        
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"
        
        test = ET.SubElement(pressfit_element, "Test")
        ET.SubElement(test, "Type").text = safe_str(x[4])
        ET.SubElement(test, "CompOperator").text = safe_str(x[7])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[2])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[3])
        ET.SubElement(test, "Value").text = safe_str(x[1])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[9])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(x[8])
        ET.SubElement(test, "Unit").text = safe_str(x[5])

def add_inspection_xml(parent, piece_id, station_name):
    """Añade datos de inspection al XML"""
    inspection_element = ET.SubElement(parent, "InspectionTests")
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
        
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(inspection_element, "Test")
        ET.SubElement(test, "Type").text = safe_str(x[4])
        ET.SubElement(test, "CompOperator").text = safe_str(x[7])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[2])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[3])
        ET.SubElement(test, "Value").text = safe_str(x[1])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[9])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(x[8])
        ET.SubElement(test, "Unit").text = safe_str(x[5])

def add_complete_xml(parent, piece_id, station_name):
    """Añade todos los tipos de tests al XML para estación completa"""
    # Screwing
    add_screwing_xml(parent, piece_id, station_name)
    
    # Pressfit
    add_pressfit_xml(parent, piece_id, station_name)
    
    # Inspection
    add_inspection_xml(parent, piece_id, station_name)
    
    # Electrical
    electrical_element = ET.SubElement(parent, "ElectricalTests")
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
        
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(electrical_element, "Test")
        ET.SubElement(test, "Type").text = safe_str(x[4])
        ET.SubElement(test, "CompOperator").text = safe_str(x[7])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[2])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[3])
        ET.SubElement(test, "Value").text = safe_str(x[1])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[9])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(x[8])
        ET.SubElement(test, "Unit").text = safe_str(x[5])
    
    # Continuity
    continuity_element = ET.SubElement(parent, "ContinuityTests")
    continuity = conexion.continuity_data(piece_id)

    indice = 1
    for x in continuity:
        tiempo = x[9].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
        
        if x[6] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(continuity_element, "Test")
        ET.SubElement(test, "Type").text = f"Numeric"
        ET.SubElement(test, "CompOperator").text = safe_str(x[2])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[3])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[4])
        ET.SubElement(test, "Value").text = safe_str(x[7])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[1])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(timer)
        ET.SubElement(test, "Unit").text = safe_str(x[5])
        indice += 1
    
    # Leak
    leak_element = ET.SubElement(parent, "LeakTests")
    leak = conexion.leaktest_data(piece_id)
    
    indice = 1
    for x in leak:
        tiempo = x[10].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
        
        if x[3] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(leak_element, "Test")
        ET.SubElement(test, "Test").text = safe_str(x[9])
        ET.SubElement(test, "Type").text = f"Numeric"
        ET.SubElement(test, "CompOperator").text = safe_str(x[8])
        ET.SubElement(test, "LowerLimit").text = safe_str(x[6])
        ET.SubElement(test, "UpperLimit").text = safe_str(x[7])
        ET.SubElement(test, "Value").text = safe_str(x[2])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[5])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(timer)
        ET.SubElement(test, "Unit").text = safe_str(x[4])
        indice += 1
    
    # Welding (nueva tabla)
    welding_element = ET.SubElement(parent, "WeldingTests")
    welding = conexion.welding_data(piece_id)
    
    indice = 1
    for x in welding:
        tiempo = x[9].astimezone()
        last_digit = str(tiempo).split('-')
        timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]

        if x[5] == "1":
            resultado = "Passed"
        else:
            resultado = "Failed"

        test = ET.SubElement(welding_element, "Test")
        ET.SubElement(test, "Type").text = f"Numeric"
        ET.SubElement(test, "CompOperator").text = safe_str(x[8])
        ET.SubElement(test, "LowerLimit").text = ""
        ET.SubElement(test, "UpperLimit").text = ""
        ET.SubElement(test, "Value").text = safe_str(x[3])
        ET.SubElement(test, "Name").text = f"{station_name}"
        ET.SubElement(test, "Description").text = safe_str(x[4])
        ET.SubElement(test, "Result").text = safe_str(resultado)
        ET.SubElement(test, "TestTime").text = safe_str(timer)
        ET.SubElement(test, "Unit").text = safe_str(x[6])
        indice += 1
    
    # Temperature
    temperature_element = ET.SubElement(parent, "TemperatureTests")
    temperature = conexion.temperature_data(piece_id)
    
    indice = 1
    for x in temperature:
        test = ET.SubElement(temperature_element, "Test")
        ET.SubElement(test, "Number").text = str(indice)
        ET.SubElement(test, "Name").text = f"{indice}b. {station_name} Test"
        ET.SubElement(test, "Description").text = safe_str(x[6]) + f" STEP {indice}"
        ET.SubElement(test, "StartTime").text = safe_str(x[1])
        ET.SubElement(test, "EndTime").text = safe_str(x[2])
        ET.SubElement(test, "InitialTemperature").text = safe_str(x[3])
        ET.SubElement(test, "FinalTemperature").text = safe_str(x[4])
        ET.SubElement(test, "Unit").text = safe_str(x[5])
        indice += 1
    
    # Component
    component_element = ET.SubElement(parent, "ComponentTests")
    componente = conexion.component_data(piece_id)
    
    indice = 1
    for x in componente:
        test = ET.SubElement(component_element, "Test")
        ET.SubElement(test, "Number").text = str(indice)
        ET.SubElement(test, "Name").text = f"{indice}b. {station_name} Test"
        ET.SubElement(test, "Component").text = f"{safe_str(x[0])} #{indice}"
        indice += 1

def safe_str(value):
    """Convierte cualquier valor a string de forma segura, manejando None"""
    if value is None:
        return ""
    return str(value)

def save_xml_file(root, filename):
    """Guarda los datos en archivo XML con misma estructura de directorios que JSON"""
    try:
        today = datetime.now()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")
        
        # Directorios de salida (misma estructura que generate_json_pressfit.pressfitJson3)
        file_data_bk = f"C:/AMC/XML/{today_year}/{today_month}/{today_day}/"
        file_data = f"C:/Users/Tesla/Documents/Traceability/{today_year}/{today_month}/{today_day}/"
        
        # Crear directorios si no existen
        os.makedirs(file_data_bk, exist_ok=True)
        os.makedirs(file_data, exist_ok=True)
        
        # Formatear XML
        xml_str = ET.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # Rutas completas de archivos
        filepath_bk = os.path.join(file_data_bk, f"{filename}.xml")
        filepath = os.path.join(file_data, f"{filename}.xml")
        
        # Guardar en backup
        with open(filepath_bk, 'w', encoding='utf-8') as xmlfile:
            xmlfile.write(xml_pretty)
        
        # Guardar en directorio principal
        with open(filepath, 'w', encoding='utf-8') as xmlfile:
            xmlfile.write(xml_pretty)
        
        print(f"[INFO] Archivo XML generado: {filename}.xml")
        return "PASSED"
        
    except Exception as e:
        print(f"[ERROR] save_xml_file(): {e}")
        return f"FAILED: {str(e)}"

# Función para pruebas
# if __name__ == "__main__":
#     result = xml_file()
#     print(f"Resultado: {result}")