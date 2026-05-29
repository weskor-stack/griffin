import json
import conexion
import rfc3339

def evaluar_codigo_defecto(val_plc, low_lim, high_lim, plc_defect_code, test_name, atributos_db):
    if low_lim in (None, "") or high_lim in (None, ""):
        return plc_defect_code
        
    try:
        val = float(val_plc)
        low = float(low_lim)
        high = float(high_lim)
        
        if not (low <= val <= high):
            for attr in atributos_db:
                if attr[0] == test_name: 
                    return attr[6] if len(attr) > 6 else plc_defect_code
            return plc_defect_code
            
    except ValueError:
        pass 
        
    return plc_defect_code

def traceability_station_20(serial_number,parent_serial_number, parent_part_number, heater_serial_number, plc_value, plc_defect_code):
    
    config = conexion.configurador()
    if not config or config == "FAILED":
        return "Error: No se encontró configuración."
        
    machine_id = config[0]         
    process_name = config[1]       
    operator = config[2]           
    program_name = config[4]       

    part = conexion.obtener_parte(serial_number)
    if not part or part == "FAILED":
        return f"Error: No se encontró la pieza {serial_number}"
        
    part_id = part[0]
    start_time = part[3]
    last_digit = str(start_time).split('-')
    timer = rfc3339.rfc3339(start_time, utc=True, use_system_timezone=False) + " " + last_digit[-1]       

    station_info = conexion.stations()
    if not station_info:
        return "Error: No hay estaciones activas."
        
    station_id = station_info[0]
    type_station = station_info[4]

    duration = conexion.duration_json(station_id, part_id)
    status_general = duration[0] if duration else ""
    end_time = duration[1] if duration else ""

    atributos_db = conexion.atributos()
    test_steps_array = []

    def agregar_steps(data_list, name_idx, desc_idx, low_idx, high_idx, unit_idx, status_idx, val_source, defect_code_idx):
        for x in data_list:
            low = x[low_idx] if low_idx is not None else ""
            high = x[high_idx] if high_idx is not None else ""
            val = x[val_source] if val_source is not None else ""
            test_name = x[name_idx]
            
            defect_code_value = x[defect_code_idx] if defect_code_idx is not None else ""
            
            # codigo_defecto = evaluar_codigo_defecto(val, low, high, plc_defect_code, test_name, atributos_db)

            test_steps_array.append({
                "name": test_name,                           
                "description": x[desc_idx] if desc_idx is not None else test_name, 
                "comparator": "GELE",
                "lowLimit": low,
                "highLimit": high,
                "units": x[unit_idx] if unit_idx is not None else "",
                "status": x[status_idx] if status_idx is not None else "PASSED",
                "value": val,
                "defect_code": defect_code_value
            })

    if type_station == 1 or type_station == 4: 
        agregar_steps(conexion.screwing_data(part_id), 11, 11, 2, 3, 5, 6, 1, 9)
        
    if type_station == 2 or type_station == 4: 
        agregar_steps(conexion.pressfit_data(part_id), 11, 11, 2, 3, 5, 6, 1, 9)
        
    if type_station == 3 or type_station == 4: 
        agregar_steps(conexion.inspection_data3(part_id), 11, 11, 2, 3, 5, 6, 1, 9)
        
    if type_station == 4: 
        agregar_steps(conexion.electrical_data(part_id), 11, 11, 2, 3, 5, 6, 1, 9)
        agregar_steps(conexion.continuity_data(part_id), 0, 0, 3, 4, 5, 6, 7, 8)
        agregar_steps(conexion.leaktest_data(part_id), 0, 0, None, None, 4, 3, 2, 5)
        agregar_steps(conexion.welding_data(part_id), 0, 0, None, None, 6, 5, 2, 7)
        agregar_steps(conexion.temperature_data(part_id), 0, 0, 9, 10, 5, None, 4, 8)

    estructura_json = {
        "serial": parent_serial_number,
        "product": parent_part_number, 
        "station": machine_id,
        "operator": operator,
        "password": "",
        "start_time": str(timer) if timer else "",
        "end_time": str(end_time) if end_time else "",
        "type": "PRODUCTION",
        "process_name": process_name,
        "status": status_general,
        "commands": [],
        "test_steps": {
            machine_id: test_steps_array
        }
    }

    if program_name and str(program_name).strip() != "":
        estructura_json["commands"].append({
            "command": "ReplaceNontrackedComponent",
            "ref_designator": str(process_name)+"_Program_Name_Version",
            "component_id": program_name
        })

    estructura_json["commands"].append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}__Machine_ID",
        "component_id": machine_id
    })

    estructura_json["commands"].append({
        "command": "ReplaceTrackedComponent",
        "ref_designator": f"{process_name}_heater_serial_number",
        "workstation": "COMP",
        "component_id": heater_serial_number
    })

    return estructura_json

# if __name__ == "__main__":
#     resultado_json = traceability_station_20(
#         serial_number="P1517040-01-G:REV01:SANN26097000001",
#         parent_serial_number="P1135558-04-A:SANN26097000001",
#         parent_part_number="LFTM1135558-04-A",           
#         heater_serial_number="P2034365-C0-B:SFY0000TEST001", 
#         plc_value="2.33",                                      
#         plc_defect_code="PLC_DEFAULT_001"
#     )
    
#     if isinstance(resultado_json, dict):
#         print(json.dumps(resultado_json, indent=4))
#     else:
#         print(f"\nError:\n{resultado_json}")