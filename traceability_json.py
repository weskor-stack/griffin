import json
import conexion
import rfc3339
from datetime import datetime, timezone
import pendulum
from history_csv import traceability_manager
from zoneinfo import ZoneInfo

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

def traceability_station_50_80(task_duration, serial_padre, part_number_padre, component_serial, component_part_number, defect_code_default=""):
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
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            test_source = str(row[-1]).strip().lower() if isinstance(row[-1], str) and row[-1] in ['screwing', 'pressfit', 'inspection', 'electrical'] else ""
            
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            
            if test_source == 'inspection':
                name_step = str(row[7]).strip() if row[7] is not None else "Inspection_Step"
            else:
                name_step = str(row[11]).strip() if row[11] is not None else "Measurement"
                
            desc_step = name_step
            
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'SCREWING',
                'pressfit': 'PRESSFIT', 
                'inspection': 'INSPECTION',  
                'electrical': 'ELECTRICAL'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.upper())
            
            if attr_name.lower() in atributos_map:
                defect_code_low = atributos_map[attr_name.lower()]['defect_code_low']
                defect_code_high = atributos_map[attr_name.lower()]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low if defect_code_low else defect_code_default
            elif val_medido > lim_sup:
                step_defect = defect_code_high if defect_code_high else defect_code_default
            else:
                step_defect = defect_code_high if defect_code_high else (defect_code_low if defect_code_low else defect_code_default)
        else:
            step_defect = ""

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
                "component_id": component_serial 
            }
        ]
    }

    return payload

def traceability_station_40(bandera, serial_padre, part_number_padre, component_serial, component_part_number, defect_code_default):
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
    
    part_row = conexion.pieces(serial_padre)
    station = conexion.stations()
    piece_id = part_row[0]
    duration = conexion.duration_json(station[0], piece_id)
    start_duration = part_row[3]
    end_duration = duration[4]
    all_test_rows = []

    atributos = conexion.select_attributes_st50_80()
    
    atributos_map = {}
    for attr in atributos:
        nombre_atributo = attr[1].lower()  
        atributos_map[nombre_atributo] = {
            'defect_code_low': attr[5],   
            'defect_code_high': attr[6],  
            'name': attr[1],
            'unit': attr[2],
            'lower_limit': attr[3],
            'upper_limit': attr[4]
        }
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data4(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASS"

    for row in all_test_rows:
        try:
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[11]) if row[11] is not None else "Measurement"
            desc_step = str(row[11]) if row[11] is not None else "Description"
            test_source = str(row[12]) if len(row) > 12 else ""
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'screwing',
                'pressfit': 'pressfit', 
                'inspection': 'inspection',  
                'electrical': 'electrical'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.lower())
            
            if attr_name in atributos_map:
                defect_code_low = atributos_map[attr_name]['defect_code_low']
                defect_code_high = atributos_map[attr_name]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low
            elif val_medido > lim_sup:
                step_defect = defect_code_high
            else:
                step_defect = defect_code_default
        else:
            step_defect = ""

        steps_list.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "N/A",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "units": unidad,
            "status": status_step,
            "value": val_medido,
            "defect_code": step_defect
        })

    program_version = configurador[4]

    if bandera == 1:
        payload = {
            "serial": part_number_padre,
            "product": component_serial,
            "station": machine_name,
            "operator": id_operator,
            "start_time": str(start_duration),
            "end_time": str(end_duration),
            "process_name": process_name,
            "status": global_status,
            "test_steps": {
                "STEPS LIST": steps_list
            },
            "commands": [
                {
                    "command": "ReplaceNontrackedComponent",
                    "ref_designator": f"{process_name}_Station ID",
                    "component_id": machine_name
                },
                {
                    "command": "ReplaceNontrackedComponent",
                    "ref_designator": f"{process_name}_Program ID",
                    "component_id": program_version 
                },
                {
                    "command": "ReplaceTrackedComponent",
                    "ref_designator": f"{process_name}_Heatsink",
                    "component_id": serial_padre
                }
            ]
        }
    else:
        payload = {
            "serial": component_serial,
            "product": part_number_padre,
            "station": machine_name,
            "operator": id_operator,
            "start_time": str(start_duration),
            "end_time": str(end_duration),
            "process_name": process_name,
            "status": global_status,
            "test_steps": {
                "STEPS LIST": steps_list
            },
            "commands": [
                {
                    "command": "ReplaceNontrackedComponent",
                    "ref_designator": f"{process_name}_Station ID",
                    "component_id": machine_name
                },
                {
                    "command": "ReplaceNontrackedComponent",
                    "ref_designator": f"{process_name}_Program ID",
                    "component_id": program_version   
                }
            ]
        }

    return payload

def traceability_station_100(serial_padre, part_number_padre, defect_code_default):
    configurador = conexion.configurador()
    machine_name = configurador[0]
    id_operator = configurador[2]
    model_id = configurador[9]
    process_name = configurador[1]
    
    part_row = conexion.pieces(serial_padre)
    station = conexion.stations()
    piece_id = part_row[0]
    duration = conexion.duration_json(station[0], piece_id)
    start_duration = part_row[3]
    end_duration = duration[4]

    weight = conexion.weight_data(piece_id)
    weight_value = weight[0][0]
    all_test_rows = []

    atributos = conexion.select_attributes_st50_80()
    
    atributos_map = {}
    for attr in atributos:
        nombre_atributo = attr[1].lower()  
        atributos_map[nombre_atributo] = {
            'defect_code_low': attr[5],   
            'defect_code_high': attr[6],  
            'name': attr[1],
            'unit': attr[2],
            'lower_limit': attr[3],
            'upper_limit': attr[4]
        }
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    list_step = []
    global_status = "PASS"

    for row in all_test_rows:
        try:
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[9]) if row[9] is not None else "Measurement"
            desc_step = str(row[9]) if row[9] is not None else "Description"
            test_source = str(row[12]) if len(row) > 12 else ""
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'screwing',
                'pressfit': 'pressfit', 
                'inspection': 'inspection',  
                'electrical': 'electrical'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.lower())
            
            if attr_name in atributos_map:
                defect_code_low = atributos_map[attr_name]['defect_code_low']
                defect_code_high = atributos_map[attr_name]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low
            elif val_medido > lim_sup:
                step_defect = defect_code_high
            else:
                step_defect = defect_code_default
        else:
            step_defect = ""

        steps_list.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "N/A",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "units": unidad,
            "status": status_step,
            "value": val_medido,
            "defect_code": step_defect
        })

        list_step.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "N/A",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "status": status_step,
            "value": val_medido
        })
    # =============================================
    # 🆕 GUARDAR TRAZABILIDAD EN CSV
    # =============================================
    try:
        # Formatear fechas para el CSV
        start_time_formatted = pendulum.parse(str(start_duration)).format("YYYY-MM-DD HH:mm:ss")
        end_time_formatted = pendulum.parse(str(end_duration)).format("YYYY-MM-DD HH:mm:ss")
        
        # Guardar trazabilidad con TODOS los pasos
        traceability_manager.save_traceability(
            sn=serial_padre,
            overall_result=global_status,
            steps_list=list_step,
            start_time=start_time_formatted,
            end_time=end_time_formatted
        )
    except Exception as e:
        print(f"⚠️ Error al guardar trazabilidad: {e}")
        import traceback
        traceback.print_exc()

    program_version = configurador[4]

    payload = {
        "serial": serial_padre,
        "product": part_number_padre,
        "station": machine_name,
        "operator": id_operator,
        "start_time": pendulum.parse(str(start_duration)).format("MM/DD/YYYY hh:mm:ss A"),
        "end_time": pendulum.parse(str(end_duration)).format("MM/DD/YYYY hh:mm:ss A"),
        "process_name": process_name,
        "status": global_status,
        "test_steps": {
            "STEPS LIST": steps_list
        },
        "commands": [
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Station ID",
                "component_id": machine_name
            },
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Model ID",
                "component_id": model_id 
            },
            {
                "command": "ReplaceTrackedComponent",
                "ref_designator": f"{process_name}_Weight",
                "component_id": weight_value
            }
        ]
    }
    

    return payload

def traceability_component_station_80(serial_padre, defect_code_default=""):
    config_local = conexion.configuradorst80()
    partes = conexion.obtener_parte2(serial_padre)
    
    componente = conexion.component_data(partes[0])
    parte = conexion.obtener_parte2(serial_padre)

    if config_local and config_local != "FAILED":
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        component_name_db = str(config_local[4]).strip()
        program_version = str(config_local[2]).strip()
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        component_name_db = "component"
        program_version = "default_program"

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%d/%m/%Y %I:%M:%S %p")
    fecha = str(parte[3])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %I:%M:%S %p")
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            test_source = str(row[-1]).strip().lower() if isinstance(row[-1], str) and row[-1] in ['screwing', 'pressfit', 'inspection', 'electrical'] else ""
            
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[9]) if row[9] is not None else "Measurement"
            desc_step = str(row[9]) if row[9] is not None else "Description"
            
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'SCREWING',
                'pressfit': 'PRESSFIT', 
                'inspection': 'INSPECTION',  
                'electrical': 'ELECTRICAL'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.upper())
            
            if attr_name.lower() in atributos_map:
                defect_code_low = atributos_map[attr_name.lower()]['defect_code_low']
                defect_code_high = atributos_map[attr_name.lower()]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low if defect_code_low else defect_code_default
            elif val_medido > lim_sup:
                step_defect = defect_code_high if defect_code_high else defect_code_default
            else:
                step_defect = defect_code_high if defect_code_high else (defect_code_low if defect_code_low else defect_code_default)
        else:
            step_defect = ""

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
        "product": parte[4],
        "station": machine_id,
        "operator": operator_id,
        "start_time": fecha_formateada,
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
                "ref_designator": f"{process_name}_Drip Case",
                "component_id": componente[0][0]
            }
        ]
    }

    return payload

def traceability_station_80(serial_padre, defect_code_default=""):
    config_local = conexion.configuradorst80()
    parte = conexion.obtener_parte2(serial_padre)
    
    if config_local and config_local != "FAILED":
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        component_name_db = str(config_local[4]).strip()
        program_version = str(config_local[2]).strip()
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        component_name_db = "component"
        program_version = "default_program"

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%d/%m/%Y %I:%M:%S %p")
    fecha = str(parte[3])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y/%m/%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %I:%M:%S %p")
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            test_source = str(row[-1]).strip().lower() if isinstance(row[-1], str) and row[-1] in ['screwing', 'pressfit', 'inspection', 'electrical'] else ""
            
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[9]) if row[9] is not None else "Measurement"
            desc_step = str(row[9]) if row[9] is not None else "Description"
            
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'SCREWING',
                'pressfit': 'PRESSFIT', 
                'inspection': 'INSPECTION',  
                'electrical': 'ELECTRICAL'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.upper())
            
            if attr_name.lower() in atributos_map:
                defect_code_low = atributos_map[attr_name.lower()]['defect_code_low']
                defect_code_high = atributos_map[attr_name.lower()]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low if defect_code_low else defect_code_default
            elif val_medido > lim_sup:
                step_defect = defect_code_high if defect_code_high else defect_code_default
            else:
                step_defect = defect_code_high if defect_code_high else (defect_code_low if defect_code_low else defect_code_default)
        else:
            step_defect = ""

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
        "product": parte[4],
        "station": machine_id,
        "operator": operator_id,
        "start_time": fecha_formateada,
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
            }
        ]
    }

    return payload

#ST60
def traceability_st60(
    serial_padre,
    part_number_padre,
    measurement_key,
    all_screwing_attempts,
    atributos_map,
    now_utc,
    machine_id,
    intento_actual=None,
    operator_id="",
    process_name="",
    password=""
):

    machine_name_payload = str(machine_id or "").strip() or "ST60 PCBA SCREWING"
    operator_payload = str(operator_id or "").strip()
    process_name_payload = str(process_name or "").strip()
    password_payload = str(password or "").strip()

    status_general = "PASS"
    step_list_dinamico = []

    catalogo_inspecciones = {
        1: "Torque",
        2: "Angles",
        3: "Rundown Angle",
        4: "Position Y"
    }

    def texto(valor):
        return str(valor or "").strip()

    def numero(valor, default=0.0):
        try:
            if valor in [None, ""]:
                return default
            return float(valor)
        except Exception:
            return default

    def entero(valor, default=1):
        try:
            if valor in [None, ""]:
                return default
            return int(float(str(valor).strip()))
        except Exception:
            return default

    def status_plc(valor):
        valor = texto(valor).upper()

        if valor in ["PASS", "PASSED", "OK"]:
            return "PASS"

        if valor in ["FAIL", "FAILED", "NOK"]:
            return "FAIL"

        return "FAIL"

    def normalizar_nombre(valor):
        nombre = texto(valor).lower()
        nombre = nombre.replace("_", " ").replace("-", " ")
        nombre = " ".join(nombre.split())

        alias = {
            "t": "torque",
            "torque": "torque",

            "a": "angles",
            "angle": "angles",
            "angles": "angles",
            "angulo": "angles",
            "ángulo": "angles",

            "px": "rundown angle",
            "position x": "rundown angle",
            "positionx": "rundown angle",
            "rda": "rundown angle",
            "ra": "rundown angle",
            "rundown": "rundown angle",
            "rundown angle": "rundown angle",
            "rundownangle": "rundown angle",

            "py": "position y",
            "position y": "position y",
            "positiony": "position y",
        }

        return alias.get(nombre, nombre)

    def es_comentario_generico(valor):
        valor = normalizar_nombre(valor)
        return valor in [
            "",
            "none",
            "null",
            "n/a",
            "na",
            "comentario",
            "comment",
            "comments"
        ]

    def preparar_atributos():
        mapa = {}

        try:
            for key, config in (atributos_map or {}).items():
                candidatos = [key]

                if isinstance(config, dict):
                    candidatos.append(config.get("name", ""))

                for candidato in candidatos:
                    key_norm = normalizar_nombre(candidato)

                    if not key_norm:
                        continue

                    mapa[key_norm] = config
                    mapa[key_norm.replace(" ", "_")] = config
                    mapa[key_norm.replace(" ", "")] = config

        except Exception as e:
            print(f"[TRACEABILITY WARNING] No se pudo preparar atributos ST60: {e}")

        return mapa

    atributos_norm = preparar_atributos()

    def buscar_atributo(*candidatos):
        for candidato in candidatos:
            key_norm = normalizar_nombre(candidato)

            posibles_keys = [
                key_norm,
                key_norm.replace(" ", "_"),
                key_norm.replace(" ", "")
            ]

            for key in posibles_keys:
                if key in atributos_norm:
                    return atributos_norm[key]

        return {}

    def obtener_defect_code(config_atributo, valor, low, high):
        if not isinstance(config_atributo, dict):
            return ""

        defect_code_low = texto(
            config_atributo.get("defect_code_low")
            or config_atributo.get("defect_code")
            or config_atributo.get("low_defect_code")
            or config_atributo.get("defect_code_bajo")
        )

        defect_code_high = texto(
            config_atributo.get("defect_code_high")
            or config_atributo.get("high_defect_code")
            or config_atributo.get("defect_code_alto")
        )

        if valor < low:
            return defect_code_low

        if valor > high:
            return defect_code_high

        return defect_code_low if defect_code_low else defect_code_high

    test_step_actual = entero(intento_actual, 1)

    for row in all_screwing_attempts or []:
        try:
            val_medido = numero(row[1])
            lim_inf_plc = numero(row[2])
            lim_sup_plc = numero(row[3])
            unidad = texto(row[5] if len(row) > 5 else "")
            status_raw = status_plc(row[6] if len(row) > 6 else "FAIL")
            plc_step_name = texto(row[10] if len(row) > 10 else "")

            measurement_key_db = ""
            measurement_type = ""

            if len(row) >= 18:
                measurement_key_db = texto(row[-2])
                measurement_type = texto(row[-1])

            elif len(row) >= 12:
                measurement_type = texto(row[11])

            # if not measurement_type:
            #     id_inspeccion = entero(row[0] if len(row) > 0 else 1, 1)
            #     measurement_type = catalogo_inspecciones.get(id_inspeccion, "Torque")

            # if normalizar_nombre(measurement_key_db) == "rundown angle":
            #     measurement_type = "Rundown Angle"

            # if normalizar_nombre(measurement_type) == "rundown angle":
            #     measurement_type = "Rundown Angle"

            if es_comentario_generico(plc_step_name):
                nombre_step = measurement_type
            # elif normalizar_nombre(measurement_type) == "rundown angle":
            #     nombre_step = measurement_type
            else:
                nombre_step = plc_step_name

            fuera_de_limite = val_medido < lim_inf_plc or val_medido > lim_sup_plc

            if status_raw == "FAIL" or fuera_de_limite:
                status_step = "FAIL"
                status_general = "FAIL"

                config_atributo = buscar_atributo(
            measurement_type,
            nombre_step,
            measurement_key_db,
            "screwing"
        )

                defect_code = obtener_defect_code(
                    config_atributo,
                    val_medido,
                    lim_inf_plc,
                    lim_sup_plc
                )

                if not defect_code:
                    print(
                        "[TRACEABILITY WARNING] Sin defect_code ST60: "
                        f"name={nombre_step}, key={measurement_key_db}, "
                        f"type={measurement_type}, value={val_medido}, "
                        f"low={lim_inf_plc}, high={lim_sup_plc}"
                    )

            else:
                status_step = "PASS"
                defect_code = ""

            step_list_dinamico.append({
                "name": nombre_step,
                "description": nombre_step,
                "comparator": "GELE",
                "lowLimit": lim_inf_plc,
                "highLimit": lim_sup_plc,
                "units": unidad,
                "status": status_step,
                "value": val_medido,
                "test_step": test_step_actual,
                "defect_code": defect_code
            })

        except Exception as e:
            print(f"[TRACEABILITY ERROR] Fila Screwing inválida: {e}")
            continue

    if not step_list_dinamico:
        status_general = "FAIL"

        step_list_dinamico.append({
            "name": "NO DATA",
            "description": "NO DATA",
            "comparator": "GELE",
            "lowLimit": 0.0,
            "highLimit": 0.0,
            "units": "",
            "status": "FAIL",
            "value": 0.0,
            "test_step": test_step_actual,
            "defect_code": ""
        })

    payload = {
        "serial": serial_padre,
        "product": part_number_padre,
        "station": machine_name_payload,
        "operator": operator_payload,
        "password": password_payload,
        "start_time": now_utc,
        "end_time": now_utc,
        "measkey": measurement_key,
        "process_name": process_name_payload,
        "status": status_general,
        "test_steps": {
            f"{machine_name_payload} LIST": step_list_dinamico
        }
    }

    return payload
