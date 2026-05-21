import json
import requests
import conexion

def generar_json_expiration(parent_serial_number):
    datos_bd = conexion.obtener_datos_expiration()
    
    if not datos_bd:
        return "Error: No se pudieron obtener los datos de la base de datos."
        
    estructura_json = {
        "version": "1.0",
        "keep_alive": False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": datos_bd["workStation_ID"],
                "type": "Location"
            },
            "client_id": datos_bd["Client_id"],
            "employee": datos_bd["operator_id"],
            "password": ""
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": parent_serial_number 
                },
                "commands": [
                    {
                        "name": "RejectIfTimeExpired",
                        "workstation": datos_bd["dispensing_process_name_1"],
                        "defect_code": datos_bd["time_defect_code_1"],
                        "minute_duration": datos_bd["minute_duration_1"],
                        "move_to_loc": datos_bd["move_to_loc_1"]
                    }
                ]
            }
        ]
    }
    return estructura_json

def enviar_datos_api(payload, url_destino):
    """
    Función encargada exclusivamente de manejar la petición POST.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        respuesta = requests.post(url_destino, json=payload, headers=headers, timeout=10)
        respuesta.raise_for_status() 
        
        print(f"✅ ¡Éxito! La API respondió con código HTTP: {respuesta.status_code}")
        # print(f"Respuesta del servidor: {respuesta.text}") # Descomentar para ver la respuesta de la API
        return True
        
    except requests.exceptions.Timeout:
        print("⏳ Error: La API tardó demasiado en responder (Timeout).")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Error: No se pudo conectar al servidor. Revisa la URL o tu conexión.")
        return False
    except requests.exceptions.HTTPError as err:
        print(f"❌ Error HTTP de la API: {err}")
        print(f"Detalle del servidor: {respuesta.text}")
        return False
    except Exception as e:
        print(f"⚠️ Error inesperado al enviar: {e}")
        return False

if __name__ == "__main__":
    
    SIMULACION = True 
    URL_API = ""
    serial_api = "SN-123456789"  

    print("--- 1. Generando Payload ---")
    payload_json = generar_json_expiration(serial_api)
    
    if isinstance(payload_json, str) and payload_json.startswith("Error"):
        print(f"\nSe detuvo el proceso:\n{payload_json}")
    else:
        if SIMULACION:
            print("Los datos NO se enviaron. Este es el payload generado:\n")
            print(json.dumps(payload_json, indent=4))
        else:
            print(f"\n[ MODO SIMULACIÓN: DESACTIVADO ]")
            print(f"Enviando POST a: {URL_API} ...\n")
            enviar_datos_api(payload_json, URL_API)