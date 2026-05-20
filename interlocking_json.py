import json
import conexion
import leer_shop_order

def interlocking_station_10():
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]
    product = configurador[4]

    part_number, serial_number, process_name_shop_order = leer_shop_order.leer_archivo_generado()

    programas = conexion.select_programs()

    unit_information.append({
        "name": "Machine ID",
        "value": machine_id
    })
    
    for x in programas:
        unit_information.append({
            "name": "Laser program number + version",
            "value": x[2]
        })
    interlocking_station10 = {
        "test_steps": {
            "unit_information": unit_information
        },
        "serial": serial_number,
        "product": part_number,
        "station": station,
        "operator": operator,
        "process_name": process_name, #process_name_shop_order,
        "location": ""
    }
    # print(json.dumps(interlocking_station10, indent=4))
    return interlocking_station10

def interlocking_station(serial_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    station = configurador[3]
    product = configurador[4]

    atributos = conexion.atributos()
    
    programas = conexion.select_programs()

    unit_information.append({
        "name": "Machine ID",
        "value": machine_id
    })
    
    try:
        for x in programas:
            unit_information.append({
                "name": "Perfilometer program number + version",
                "value": x[2]
            })
    except Exception as e:
        print(f"Error no hay programas cargados: {e}")
        return "Error no hay programas cargados:"

    try:
        for y in atributos:
            if y[3] != "" and y[2] != "" and y[5] != "" and y[4] != "":
                unit_information.extend([
                    {
                        "name": y[0]+" Lower limit",
                        "value": y[3]
                    },
                    {
                        "name": y[0]+" Upper limit",
                        "value": y[2]
                    },
                    {
                        "name": y[0]+" Expected value",
                        "value": y[4]
                    },
                    {
                        "name": y[0]+" Time",
                        "value": y[5]
                    }
                ])
            elif y[3] == "" and y[2] == "" and y[5] != "" and y[4] == "":
                unit_information.append({
                    "name": y[0],
                    "value": y[5]
                })
            elif y[3] != "" and y[2] != "" and y[5] == "" and y[4] != "":
                unit_information.extend([
                    {
                        "name": y[0]+" Lower limit",
                        "value": y[3]
                    },
                    {
                        "name": y[0]+" Upper limit",
                        "value": y[2]
                    },
                    {
                        "name": y[0],
                        "value": y[4]
                    }
                ])
            elif y[3] == "" and y[2] == "" and y[5] == "" and y[4] != "":
                unit_information.append(                    {
                        "name": y[0],
                        "value": y[4]
                    }
                )
            elif y[3] != "" and y[2] == "" and y[5] == "" and y[4] == "":
                unit_information.append(                    {
                        "name": y[0]+" Lower limit",
                        "value": y[3]
                    }
                )
            elif y[3] == "" and y[2] != "" and y[5] == "" and y[4] == "":
                unit_information.append(                    {
                        "name": y[0]+" Upper limit",
                        "value": y[2]
                    }
                )
            elif y[1] == '':
                if y[0] == "Force":
                    unit_information.append(                    
                        {
                            "name": y[0]+" limits",
                            "value": y[3]
                        }
                    )
                elif y[0]=="Pin":
                    unit_information.append(                    
                        {
                            "name": y[0]+" height limits",
                            "value": y[3]
                        }
                    )
                elif y[0] == "Speed":
                    unit_information.append(                    
                        {
                            "name": y[0]+" limits",
                            "value": y[3]
                        }
                    )
                elif y[0] == "Power":
                    unit_information.append(                    
                        {
                            "name": y[0]+" limits",
                            "value": y[3]
                        }
                    )
                elif y[0] == "Time":
                    unit_information.append(                    
                        {
                            "name": y[0],
                            "value": y[3]
                        }
                    )
                else:
                    unit_information.extend([
                        {
                            "name": y[0]+" limits",
                            "value": y[3]
                        },
                        {
                            "name": y[0]+" height limits",
                            "value": y[2]
                        },
                        {
                            "name": y[0]+" Upper limit",
                            "value": y[2]
                        }
                    ])

    except Exception as e:
        print(f"Error no hay atributos cargados: {e}")
        return "Error no hay atributos cargados:"


    interlocking_station = {
        "test_steps": {
            "unit_information": unit_information
        },
        "serial": serial_number,
        "product": product,
        "station": station,
        "operator": operator,
        "process_name": process_name,
        "location": ""
    }
    # print(json.dumps(interlocking_station, indent=4))
    return interlocking_station

# interlocking_station("P2170207-00-E:SE4A2612000000")
# interlocking_station_10()