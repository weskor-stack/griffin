import json
import conexion

def conduit_st20(parent_serial_number):
    configurador     = conexion.configurador()
    expiration_times = conexion.get_expiration_time()

    workstation_id = configurador[3]          # station  → worStation_ID
    operator_id    = configurador[2]          # operator → Operator_ID
    client_id      = configurador[6]          # cliente → cliente_ID

    commands = []
    for row in expiration_times:
        commands.append({
            "name":            "RejectIfTimeExpired",
            "workstation":     row[0],   # process_name
            "defect_code":     row[1],   # defect_code
            "minute_duration": row[2],   # minute_duration
            "move_to_loc":     row[3]    # move_loc
        })

    conduit_json = {
        "version":      "1.0",
        "keep_alive":   False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": workstation_id,
                "type":    "Location"
            },
            "client_id": client_id,
            "employee":  operator_id,
            "password":  ""
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": parent_serial_number
                },
                "commands": commands
            }
        ]
    }
    # print(json.dumps(conduit_json, indent=4))
    return conduit_json

def conduit_st40(serial_number):
    configurador     = conexion.configurador()

    workstation_id = configurador[3]          # station  → worStation_ID
    operator_id    = configurador[2]          # operator → Operator_ID
    client_id      = configurador[6]          # cliente → cliente_ID
    location       = configurador[11]
    sf_id          = configurador[12]
    password       = configurador[7]
    print_macro    = configurador[10] 

    commands = []

    commands.append({
        "command": print_macro
    })
    
    conduit_json = {
        "version":      "1.0",
        "keep_alive":   False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": location,
                "type":    "location"
            },
            "client_id": sf_id,
            "employee":  operator_id,
            "password":  password
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": serial_number
                },
                "commands": commands
            }
        ]
    }
    # print(json.dumps(conduit_json, indent=4))
    return conduit_json

def conduit_st60(
    process_name,
    client_id,
    operator_id,
    parent_serial_number,
    program_version,
    machine_id,
    status="PASS"
):
    """
    Payload Conduit End ST60.

    Incluye:
    - ReplaceNontrackedComponent Program_Name_Version
    - ReplaceNontrackedComponent Machine_ID
    - End

    Esta función SOLO arma el JSON. No hace POST.
    """

    status = str(status or "PASS").strip().upper()

    if status in ["PASSED", "PASS", "OK"]:
        status = "PASS"
    else:
        status = "FAIL"

    return {
        "version": "1.0",
        "keep_alive": False,
        "refresh_unit": True,
        "status": status,
        "source": {
            "workstation": {
                "station": process_name,
                "type": "Process"
            },
            "client_id": client_id,
            "employee": operator_id,
            "password": ""
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": parent_serial_number
                },
                "commands": [
                    {
                        "name": "ReplaceNontrackedComponent",
                        "ref_designator": f"{process_name}_Program_Name_Version",
                        "component_id": program_version
                    },
                    {
                        "name": "ReplaceNontrackedComponent",
                        "ref_designator": f"{process_name}_Machine_ID",
                        "component_id": machine_id
                    },
                    {
                        "name": "End"
                    }
                ]
            }
        ]
    }

def conduit_st60_v2(serial_number, conduit_status):
    configurador     = conexion.configurador_st60()

    process_name    = configurador[2]          # process_name
    client_id       = configurador[3]          # client_id
    operator_id     = configurador[4]          # operator_id

    commands = []

    if conduit_status == 1:
        commands.append({
            "name": "AddMeasurementKey"
        })
    
    conduit_json = {
        "version":      "1.0",
        "keep_alive":   False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": process_name,
                "type":    "Process"
            },
            "client_id": client_id,
            "employee":  operator_id,
            "password":  ""
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": serial_number
                },
                "commands": commands
            }
        ]
    }
    # print(json.dumps(conduit_json, indent=4))
    return conduit_json

def conduit_st60_v3(serial_number, conduit_status, defect_code):
    configurador     = conexion.configurador_st60()

    process_name    = configurador[2]          # process_name
    client_id       = configurador[3]          # client_id
    operator_id     = configurador[4]          # operator_id
    program_version = configurador[0]          # program_version
    machine_id      = configurador[1]          # machine_id

    commands = []

    if conduit_status == 1:
        commands.append({
            "name": "AddMeasurementKey"
        })
    elif conduit_status == 2:
        commands.append({
            "name": "RecordDefect",
            "defect_code": defect_code
        })
    elif conduit_status == 3:
        commands.append({
            "name": "RepairAllDefects"
        })
    elif conduit_status == 4:
        commands.extend([{
            "name": "ReplaceNontrackedComponent",
            "ref_designator": process_name + "_Program_Name_Version",
            "component_id": program_version
        },
        {
            "name": "ReplaceNontrackedComponent",
            "ref_designator": process_name + "_Machine_ID",
            "component_id": machine_id
        },
        {
            "name": "End"
        }])
    
    conduit_json = {
        "version":      "1.0",
        "keep_alive":   False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": process_name,
                "type":    "Process"
            },
            "client_id": client_id,
            "employee":  operator_id,
            "password":  ""
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": serial_number
                },
                "commands": commands
            }
        ]
    }
    # print(json.dumps(conduit_json, indent=4))
    return conduit_json

# conduit_st60_v2("P1135558-04-A:SANN26097000001",2,"DEFECTO-PRUEBA")
