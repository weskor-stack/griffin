import json

def extraer_part_number(json_unit):
    """Valida la respuesta de UNIT y extrae data.part_number."""

    if isinstance(json_unit, list):
        json_unit = json_unit[0] if json_unit else None

    if not isinstance(json_unit, dict):
        raise ValueError("Invalid UNIT response.")
    
    if str(json_unit.get("success")).strip().lower() not in ("true", "1"):
        raise ValueError(json_unit.get("message") or "Rejected by UNIT API.")

    datos_unit = json_unit.get("data")

    if datos_unit == {}:
        return "Empty data"

    if isinstance(datos_unit, list):
        datos_unit = datos_unit[0] if datos_unit else None
    part_number_unit = datos_unit.get("part_number") if isinstance(datos_unit, dict) else None

    if not isinstance(part_number_unit, str) or not part_number_unit.strip():
        #raise ValueError("Missing part_number in UNIT response.")
        return None
    return part_number_unit.strip()

def formatear_detalle_unit(detalle):
    """Formatea la solicitud y la respuesta para el panel de tramas."""

    if not detalle:
        return ""

    return (
        f"\n\n[UNIT REQUEST]:\n{json.dumps(detalle['request'], indent=2, ensure_ascii=False)}"
        f"\n\n[UNIT RESPONSE]:\n{json.dumps(detalle['response'], indent=2, ensure_ascii=False)}"
    )