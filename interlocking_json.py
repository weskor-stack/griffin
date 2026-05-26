import json
import conexion

def interlocking_station_20(parent_serial_number, parent_part_number, heater_part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]

    programas = conexion.select_programs()

    for x in programas:
        unit_information.append({
            "name": "Program_Name_Version",
            "value": x[2]
        })

    unit_information.append({
        "name": "Machine_ID",
        "value": machine_id
    })

    unit_information.append({
        "name": "heater_part_number",
        "value": heater_part_number
    })

    interlocking_station20 = {
        "test_steps": {
            "unit_information": unit_information
        },
        "serial": parent_serial_number,
        "product": parent_part_number,
        "station": station,
        "operator": operator,
        "process_name": process_name,
        "location": ""
    }
    # print(json.dumps(interlocking_station20, indent=4))
    return interlocking_station20

def interlocking_station_50_80(parent_serial_number, parent_part_number, component_pn):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]

    programas = conexion.select_programs()

    # Orden correcto según PDF ST50/ST80 Sec 5.1: station_id → model_id → component_partnumber
    unit_information.append({
        "name": "station_id",
        "value": machine_id
    })

    for x in programas:
        unit_information.append({
            "name": "model_id",
            "value": x[2]
        })

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

# interlocking_station_20("AABB-parent_serial_number","CCGG02-parent_part_number","ZZXX01-heater_part_number")
# interlocking_station_50_80("MODEL1-001-0000015", "2102110-00-C", "COMPONENT-1")