import json
import conexion
import rfc3339
from datetime import datetime, timezone

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

def interlocking_station_20(serial_number, parent_serial_number, parent_part_number, heater_serial_number, plc_value, plc_defect_code):
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

    def agregar_steps(data_list, name_idx, desc_idx, low_idx, high_idx, unit_idx, status_idx, val_source):
        for x in data_list:
            low = x[low_idx] if low_idx is not None else ""
            high = x[high_idx] if high_idx is not None else ""
            val = x[val_source] if isinstance(val_source, int) else val_source
            test_name = x[name_idx]
            
            codigo_defecto = evaluar_codigo_defecto(val, low, high, plc_defect_code, test_name, atributos_db)

            test_steps_array.append({
                "name": test_name,                                           
                "description": test_name, 
                "comparator": "GELE",
                "lowLimit": low,
                "highLimit": high,
                "units": x[unit_idx] if unit_idx is not None else "",
                "status": x[status_idx] if status_idx is not None else "PASSED",
                "value": val,
                "defect_code": codigo_defecto
            })

    if type_station == 1 or type_station == 4: 
        agregar_steps(conexion.screwing_data(part_id), 11, 11, 2, 3, 5, 6, plc_value)
        
    if type_station == 2 or type_station == 4: 
        agregar_steps(conexion.pressfit_data(part_id), 11, 11, 2, 3, 5, 6, plc_value)
        
    if type_station == 3 or type_station == 4: 
        agregar_steps(conexion.inspection_data(part_id), 11, 11, 2, 3, 5, 6, plc_value)
        
    if type_station == 4: 
        agregar_steps(conexion.electrical_data(part_id), 11, 11, 2, 3, 5, 6, plc_value)
        agregar_steps(conexion.continuity_data(part_id), 0, 0, 3, 4, 5, 6, 7)
        agregar_steps(conexion.leaktest_data(part_id), 0, 0, None, None, 4, 3, 2)
        agregar_steps(conexion.welding_data(part_id), 0, 0, None, None, 6, 5, 2)
        agregar_steps(conexion.temperature_data(part_id), 0, 0, 9, 10, 5, None, 4)

    estructura_json = {
        "serial": parent_serial_number,
        "product": parent_part_number, 
        "station": machine_id,
        "operator": operator,
        "start_time": str(timer) if timer else "",
        "end_time": str(end_time) if end_time else "",
        "process_name": process_name,
        "status": status_general,
        "test_steps": {
            "STEPS LIST": test_steps_array
        },
        "commands": []
    }

    estructura_json["commands"].append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Station ID",
        "component_id": machine_id
    })

    program_id = str(program_name).strip() if program_name else "default_program"
    estructura_json["commands"].append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Program ID",
        "component_id": program_id
    })

    estructura_json["commands"].append({
        "command": "ReplaceTrackedComponent",
        "ref_designator": f"{process_name}_component",
        "component_id": heater_serial_number
    })

    return estructura_json

def traceability_station_50_80(task_duration, serial_padre, part_number_padre, component_serial, component_part_number, defect_code_default):
    config_local = conexion.configuradorst50_80()
    
    if config_local and config_local != "FAILED" and len(config_local) >= 6:
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        component_name_db = str(config_local[4]).strip()
        program_version = str(config_local[5]).strip()
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        component_name_db = "component"
        program_version = "default_program"

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list): all_test_rows.extend(sr)
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list): all_test_rows.extend(pr)
        except Exception: pass
        
        try:
            ir = conexion.inspection_data(part_id)
            if ir and isinstance(ir, list): all_test_rows.extend(ir)
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list): all_test_rows.extend(er)
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            val_medido = str(row[1]) if row[1] is not None else "0.0"
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[11]) if row[11] is not None else "Measurement"
            desc_step = str(row[10]) if row[10] is not None else "Description"
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            step_defect = defect_code_default if defect_code_default else "PLC_DEFAULT_001"
        else:
            step_defect = "NONE"

        steps_list.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "GELE",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "units": unidad,
            "status": status_step,
            "value": val_medido,
            "defect_code": step_defect
        })

    program_version = str(program_version).strip() if program_version else "default_program"

    payload = {
        "serial": serial_padre,
        "product": part_number_padre,
        "station": machine_id,
        "operator": operator_id,
        "start_time": now_utc,
        "end_time": now_utc,
        "process_name": process_name,
        "status": global_status,
        "test_steps": {
            "STEPS LIST": steps_list
        },
        "commands": [
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Station ID",
                "component_id": machine_id
            },
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Program ID",
                "component_id": program_version   
            },
            {
                "command": "ReplaceTrackedComponent",
                "ref_designator": f"{process_name}_{component_name_db}",
                "component_id": component_part_number
            }
        ]
    }

    return payload

# if __name__ == "__main__":
#     resultado_json = traceability_station_50_80(
#         serial_number = "P2173404-00-C:SEYU26061A0765",
#         parent_serial_number="P1106394-71-P:SE4A25079000001",
#         parent_part_number="1231284792783",           
#         heater_serial_number="P2170207-00-E:SE4A26127000245", 
#         plc_value="2.33",                                      
#         plc_defect_code="PLC_DEFAULT_001"
#     )
    
#     if isinstance(resultado_json, dict):
#         print(json.dumps(resultado_json, indent=4))
#     else:
#         print(f"\nError:\n{resultado_json}")