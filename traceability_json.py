from html import parser
import json
import conexion
import rfc3339
import leer_shop_order
from dateutil import parser

def traceability_station_10(serial_number):
    unit_information = []
    configurador = conexion.configurador()
    pruebas = conexion.type_test()
    heatstake_data = conexion.heatstake_info(serial_number)
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]

    programas = conexion.select_programs()

    station_activo = conexion.stations()
    name = conexion.pieces(serial_number)
    piece_id = name[0]
    duration = conexion.duration_json(station_activo[0], piece_id)
    obtener_parte = conexion.obtener_parte(serial_number)

    last_digit = str(obtener_parte[3])
    last_digit = last_digit.split('-')
    timer_start = rfc3339.rfc3339(obtener_parte[3], utc=True, use_system_timezone=False)+" "+last_digit[2]

    last_digit2 = str(duration[4])
    last_digit2 = last_digit2.split('-')
    timer_end = rfc3339.rfc3339(duration[4], utc=True, use_system_timezone=False)+" "+last_digit2[2]

    # part_number, serial_number_shop_order, process_name_shop_order = leer_shop_order.leer_archivo_generado()

    # "start_time": "2026-04-24T17:10:51Z 24 17:10:51",
    # "end_time":   "2026-04-24T23:11:50Z 06:00",


    for z in heatstake_data:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": "Cycle time",
            "component_id": z[1]
        })

    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Machine ID",
        "component_id": machine_id
    })

    for x in programas:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": "Laser program name + version",
            "component_id": x[2]
        })

    for y in heatstake_data:
        divisor = y[2].index(":")
        partnumber = y[2][1:divisor]
        unit_information.extend([
            {
            "command": "AddNonTrackedComponent",
            "ref_designator": "Grade",
            "component_id": y[5]
            },
            {
            "command": "AddNonTrackedComponent",
            "ref_designator": "Part Number",
            "component_id": partnumber
            }
        ])
    
    traceability_station10_send = {
        "commands": unit_information,
        "serial": serial_number,
        "test_id": pruebas[0][1],
        "station": station,
        "operator": operator,
        "password": "",
        "start_time": timer_start.split()[0],
        "end_time": timer_end.split()[0],
        "type": "PRODUCTION",
        "process_name": process_name, #process_name_shop_order,
        "status": duration[0]
    }
    # print(json.dumps(traceability_station10_send, indent=4))
    return traceability_station10_send

def traceability_station_20(serial_number):
    unit_information = []
    configurador = conexion.configurador()
    pruebas = conexion.type_test()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]
    product = configurador[4]

    station_activo = conexion.stations()
    name = conexion.pieces(serial_number)
    piece_id = name[0]
    duration = conexion.duration_json(station_activo[0], piece_id)
    obtener_parte = conexion.obtener_parte(serial_number)

    graph_image = conexion.obtener_image(serial_number)

    last_digit = str(obtener_parte[3])
    last_digit = last_digit.split('-')
    timer_start = rfc3339.rfc3339(obtener_parte[3], utc=True, use_system_timezone=False)+" "+last_digit[2]

    last_digit2 = str(duration[4])
    last_digit2 = last_digit2.split('-')
    timer_end = rfc3339.rfc3339(duration[4], utc=True, use_system_timezone=False)+" "+last_digit2[2]

    programas = conexion.select_programs()

    pressfit = conexion.pressfit_data(piece_id)
    inspections = conexion.inspection_data3(piece_id)

    divisor = serial_number.index(":")
    partnumber = serial_number[1:divisor]

    results_inspection = []
    pin_height = []

    for x in pressfit:
        if x[0] == 1 or x[0] == 2:
            results_inspection.append({
                "name": x[11],
                "lowLimit": x[2],
                "highLimit": x[3],
                "units": x[5],
                "status": x[6],
                "value": x[1]
            })
        else:
            pin_height.append({
                "name": x[9],
                "lowLimit": x[2],
                "highLimit": x[3],
                "units": x[5],
                "status": x[6],
                "value": x[1]
            })
    
    for x in inspections:
        pin_height.append({
            "name": x[9],
            "lowLimit": x[2],
            "highLimit": x[3],
            "units": x[5],
            "status": x[6],
            "value": x[1]
        })
        
    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "CycleTime",
        "component_id": duration[2]
    })

    for x in programas:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": "Inspection program name + version",
            "component_id": x[2]
        })
    
    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Machine ID",
        "component_id": machine_id
    })

    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Part Number",
        "component_id": partnumber
    })

    for x in graph_image:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": "Data Sampling "+str(x[1]),
            "component_id": x[2]
        })

    componente = conexion.component_data(piece_id)
        
    for x in componente:
        unit_information.append({
            "command": "ReplaceTrackedComponent",
            "ref_designator": x[1],
            "component_id": x[0]
         })

    traceability_station20_send = {
        "test_steps": {
            "RESULTS INSPECTION": results_inspection,
            "PIN HEIGHT": pin_height
        },
        "commands": unit_information,
        "serial": serial_number,
        "test_id": pruebas[0][1],
        "station": station,
        "operator": operator,
        "password": "",
        "start_time": timer_start.split()[0],
        "end_time": timer_end.split()[0],
        "type": "PRODUCTION",
        "process_name": process_name,
        "status": duration[0]
    }
    # print(json.dumps(traceability_station20_send, indent=4))
    return traceability_station20_send

def traceability_station_30(serial_number):
    unit_information = []
    configurador = conexion.configurador()
    pruebas = conexion.type_test()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]
    product = configurador[4]

    station_activo = conexion.stations()
    name = conexion.pieces(serial_number)
    piece_id = name[0]
    duration = conexion.duration_json(station_activo[0], piece_id)
    obtener_parte = conexion.obtener_parte(serial_number)

    graph_image = conexion.obtener_image(serial_number)

    last_digit = str(obtener_parte[3])
    last_digit = last_digit.split('-')
    timer_start = rfc3339.rfc3339(obtener_parte[3], utc=True, use_system_timezone=False)+" "+last_digit[2]

    last_digit2 = str(duration[4])
    last_digit2 = last_digit2.split('-')
    timer_end = rfc3339.rfc3339(duration[4], utc=True, use_system_timezone=False)+" "+last_digit2[2]

    programas = conexion.select_programs()

    pressfit = conexion.pressfit_data(piece_id)
    inspections = conexion.inspection_data3(piece_id)

    heatstake_data = conexion.heatstake_info(serial_number)

    divisor = serial_number.index(":")
    partnumber = serial_number[1:divisor]

    results_inspection = []
    pin_height = []

    for x in pressfit:
        if x[0] == 1:
            results_inspection.append({
                "name": x[11],
                "lowLimit": x[2],
                "highLimit": x[3],
                "units": x[5],
                "status": x[6],
                "value": x[1]
            })
    
    for x in inspections:
        pin_height.append({
            "name": x[9],
            "lowLimit": x[2],
            "highLimit": x[3],
            "units": x[5],
            "status": x[6],
            "value": x[1]
        })
    
    # unit_information.append({
    #     "command": "AddNonTrackedComponent",
    #     "ref_designator": "CycleTime",
    #     "component_id": duration[2]
    # })

    for y in heatstake_data:
        unit_information.extend([
            {
            "command": "AddNonTrackedComponent",
            "ref_designator": "CycleTime",
            "component_id": y[1]
            },
            {
            "command": "AddNonTrackedComponent",
            "ref_designator": y[6],
            "component_id": y[4]
            }
        ])
    start_dt = parser.isoparse(timer_start.split()[0])
    end_dt = parser.isoparse(timer_end.split()[0])
    diferencia = end_dt - start_dt
    
    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Work time",
        "component_id": str(diferencia.total_seconds()) + " seconds"
    })

    for x in programas:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": "Inspection program name + version",
            "component_id": x[2]
        })
    
    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Machine ID",
        "component_id": machine_id
    })

    unit_information.append({
        "command": "AddNonTrackedComponent",
        "ref_designator": "Part Number",
        "component_id": partnumber
    })

    for x in graph_image:
        unit_information.append({
            "command": "AddNonTrackedComponent",
            "ref_designator": x[2],
            "component_id": x[1]
        })

    componente = conexion.component_data(piece_id)
        
    for x in componente:
        unit_information.append({
            "command": "ReplaceTrackedComponent",
            "ref_designator": x[1],
            "component_id": x[0]
         })

    traceability_station30_send = {
        "test_steps": {
            "RESULTS INSPECTION": results_inspection,
            "PIN HEIGHT": pin_height
        },
        "commands": unit_information,
        "serial": serial_number,
        "test_id": pruebas[0][1],
        "station": station,
        "operator": operator,
        "password": "",
        "start_time": timer_start.split()[0],
        "end_time": timer_end.split()[0],
        "type": "PRODUCTION",
        "process_name": process_name,
        "status": duration[0]
    }
    # print(json.dumps(traceability_station30_send, indent=4))
    return traceability_station30_send

# traceability_station_10("P2173404-00-C:SEYU26061A0765")
# traceability_station_20("P2173404-00-C:SEYU26061A0765")
# traceability_station_30("P2173404-00-C:SEYU26061A0765")