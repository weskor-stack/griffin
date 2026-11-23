from urllib.parse import quote
import requests
import conexion
import unit_json

REQUEST_TIMEOUT = 30

def consultar_part_number_unit(serial):
    url_base_unit = next(
        (
            url.strip()
            for nombre, url in conexion.get_urls().items()
            if nombre.strip().upper() == "UNIT" and url and url.strip()
        ),
        "",
    )

    url_unit = url_base_unit + serial
    try:
        response_unit = requests.get(url_unit, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        return "FAILED", f"HTTP CONNECTION ERROR: {e}", url_unit
    
    if response_unit.status_code != 200:
        return "FAILED", f"API UNIT RESPONSE: {response_unit.status_code}", url_unit

    try:
        json_unit = response_unit.json()
    except Exception as e:
        return "FAILED", f"API UNIT INVALID JSON STRUCTURE: {e}", url_unit

    part_number = unit_json.extraer_part_number(json_unit)

    if part_number == None:
        return "FAILED", "Missing part number in UNIT response.", url_unit

    if part_number == "Empty data":
        return "FAILED", "Empty data", url_unit
    
    return "PASSED", part_number, url_unit

# result, part_number, url_unit = consultar_part_number_unit("P1472635-61-G:SE4A22172000000123")
# print(f"Resultado: {result}")
# print(f"part_number: {part_number}")
# print(f"url_unit: {url_unit}")