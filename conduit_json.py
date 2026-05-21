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

# conduit_st20("P1135558-04-A:SANN26097000001")
