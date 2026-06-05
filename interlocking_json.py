import json
import conexion

def interlocking_station_20(parent_serial_number, parent_part_number, heater_part_numbers):
    unit_information = []
    configurador = conexion.configurador()
    
    # Validar que configurador tenga datos
    if not configurador or configurador == "FAILED":
        print("No se pudo obtener configuración del configurador")
        # Valores por defecto o manejo de error
        machine_id = "UNKNOWN"
        process_name = "UNKNOWN"
        operator = "UNKNOWN"
        station = "UNKNOWN"
    else:
        machine_id = configurador[0] if len(configurador) > 0 else "UNKNOWN"
        process_name = configurador[1] if len(configurador) > 1 else "UNKNOWN"
        operator = configurador[2] if len(configurador) > 2 else "UNKNOWN"
        station = configurador[3] if len(configurador) > 3 else "UNKNOWN"

    # Obtener programas
    programas = conexion.select_programs()
    if programas and programas != "FAILED":
        for x in programas:
            unit_information.append({
                "name": "Program_Name_Version",
                "value": x[2] if len(x) > 2 else "UNKNOWN"
            })

    # Agregar Machine_ID
    unit_information.append({
        "name": "Machine_ID",
        "value": machine_id
    })

    # ========== MODIFICACIÓN: AGREGAR MÚLTIPLES HEATER_PART_NUMBERS ==========
    # Verificar si heater_part_numbers es una lista o un string
    if isinstance(heater_part_numbers, list):
        # Es una lista de part numbers
        if len(heater_part_numbers) == 1:
            # Solo un part number, mantener formato original
            unit_information.append({
                "name": "heater_part_number",
                "value": heater_part_numbers[0]
            })
        else:
            # Múltiples part numbers, agregar cada uno como heater_part_number_X
            for idx, part_number in enumerate(heater_part_numbers, 1):
                # Opción 1: Nombre genérico para todos
                unit_information.append({
                    "name": "heater_part_number",
                    "value": part_number
                })
                # Opción 2: Con índice (descomentar si se prefiere)
                # unit_information.append({
                #     "name": f"heater_part_number_{idx}",
                #     "value": part_number
                # })
                
                # Opción 3: Como un array/lista (si el API lo soporta)
                # Ya está implementado como múltiples objetos
    else:
        # Es un string (un solo part number) - mantener comportamiento original
        unit_information.append({
            "name": "heater_part_number",
            "value": heater_part_numbers
        })
    
    # Log para debugging
    print(f"Interlocking: Enviando {len(heater_part_numbers) if isinstance(heater_part_numbers, list) else 1} heater_part_number(s)")

    interlocking_station20 = {
        "serial": parent_serial_number,
        "product": parent_part_number,
        "station": station,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
    }
    
    return interlocking_station20

def interlocking_station_50_80(parent_serial_number, parent_part_number, component_pn):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]
    model_id = configurador[8]

    programas = conexion.select_programs()

    unit_information.append({
        "name": "station_id",
        "value": machine_id
    })
    unit_information.append({
        "name": "model_id",
        "value": model_id
    })

    # for x in programas:
    #     unit_information.append({
    #         "name": "model_id",
    #         "value": x[2]
    #     })

    unit_information.append({
        "name": "component_partnumber",
        "value": component_pn
    })

    interlocking_st50_80 = {
        "serial": parent_serial_number,
        "product": parent_part_number,
        "station": station,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_st50_80, indent=4))
    return interlocking_st50_80

def interlocking_station_40_empty_data(shop_serial_number, shop_part_number, heatsink_pn):
    unit_information = []
    configurador = conexion.configurador()
    machine_name = configurador[0]
    client_id = configurador[6]
    id_operator = configurador[2]
    password = configurador[7]
    model_id = configurador[9]
    process_name = configurador[1]
    print_macro = configurador[10]
    location = configurador[11]
    shop_flor = configurador[12]

    programas = conexion.select_programs()

    unit_information.append({
        "name": "station_id",
        "value": machine_name
    })
    unit_information.append({
        "name": "model_id",
        "value": model_id
    })

    unit_information.append({
        "name": "heatsink_partnumber",
        "value": heatsink_pn
    })

    interlocking_station_40_empty_data = {
        "serial": shop_serial_number,
        "product": shop_part_number,
        "station": machine_name,
        "operator": id_operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_40_empty_data, indent=4))
    return interlocking_station_40_empty_data

def interlocking_station_40(serial_number, part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_name = configurador[0]
    client_id = configurador[6]
    id_operator = configurador[2]
    password = configurador[7]
    model_id = configurador[9]
    process_name = configurador[1]
    print_macro = configurador[10]
    location = configurador[11]
    shop_flor = configurador[12]

    programas = conexion.select_programs()

    unit_information.append({
        "name": "station_id",
        "value": machine_name
    })
    unit_information.append({
        "name": "program_id",
        "value": model_id
    })

    interlocking_station_40 = {
        "serial": serial_number,
        "product": part_number,
        "station": machine_name,
        "operator": id_operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_40, indent=4))
    return interlocking_station_40

def interlocking_station_100(serial_number, part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_name = configurador[0]
    id_operator = configurador[2]
    model_id = configurador[9]
    process_name = configurador[1]


    unit_information.append({
        "name": "station_id",
        "value": machine_name
    })
    unit_information.append({
        "name": "program_id",
        "value": model_id
    })

    interlocking_station_100 = {
        "serial": serial_number,
        "product": part_number,
        "station": machine_name,
        "operator": id_operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_100, indent=4))
    return interlocking_station_100

# interlocking_station_20("AABB-parent_serial_number","CCGG02-parent_part_number","ZZXX01-heater_part_number")
# interlocking_station_50_80("MODEL1-001-0000015", "2102110-00-C", "COMPONENT-1")
# interlocking_station_40_empty_data("MODEL1-001-0000015", "2102110-00-C", "HEATSINK-1")
# interlocking_station_100("P2034365-C0-B:SFY0000TEST001", "HS-2026")