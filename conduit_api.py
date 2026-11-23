# conduit_api.py
"""Módulo para manejar las llamadas a la API de CONDUIT en ST50 y ST80."""
import logging
import time

import requests

import conexion
import conduit_json


MAX_RETRIES = 5
RETRY_DELAY = 2
REQUEST_TIMEOUT = 15


def get_conduit_url():
    """Obtiene la URL de CONDUIT usando get_urls() de conexion.py."""
    try:
        urls = conexion.get_urls()
        for name, url in urls.items():
            if name.strip().upper() == "CONDUIT" and url and url.strip():
                return url.strip()

        logging.warning("No se encontró URL para CONDUIT en la base de datos")
    except Exception as exc:
        logging.error("Error obteniendo URL de CONDUIT: %s", exc)
    return None


def call_conduit_api_with_retry(
    serial_number, station_type, max_retries=None,
    retry_delay=None, *, include_request=False
):
    """Devuelve los seis valores habituales y añade el JSON del POST si se solicita."""
    request_extra = (None,) if include_request else ()
    station_type = str(station_type).strip().upper()
    if station_type not in ("ST50", "ST80"):
        message = f"Estación no soportada para CONDUIT: {station_type}. Usa ST50 o ST80."
        return False, message, None, None, 0, 0, *request_extra

    max_retries = MAX_RETRIES if max_retries is None else max_retries
    retry_delay = RETRY_DELAY if retry_delay is None else retry_delay
    if max_retries < 1 or retry_delay < 0:
        return False, "Configuración de reintentos inválida.", None, None, 0, 0, *request_extra

    conduit_url = get_conduit_url()
    if not conduit_url:
        message = "No se ha configurado la URL de CONDUIT en la base de datos."
        logging.error(message)
        return False, message, None, None, 0, 0, *request_extra

    for attempt in range(1, max_retries + 1):
        response_data = None
        status_code = None
        response_time_ms = 0
        logging.info(
            "Intento %s/%s para API CONDUIT (pieza: %s, estación: %s)",
            attempt, max_retries, serial_number, station_type,
        )

        try:
            if station_type == "ST50":
                json_data = conduit_json.conduit_st50_v2(serial_number)
            else:
                json_data = conduit_json.conduit_st80_v2(serial_number)
            if not isinstance(json_data, dict) or not json_data:
                raise ValueError("El generador de CONDUIT no devolvió un diccionario con datos.")

            if include_request:
                request_extra = (json_data,)

            start_time = time.perf_counter()
            response = requests.post(
                conduit_url,
                json=json_data,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
            response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            status_code = response.status_code
            logging.info("API CONDUIT respondió HTTP %s en %s ms", status_code, response_time_ms)

            try:
                response_data = response.json()
            except ValueError:
                response_data = {"message": response.text, "raw_response": True}
                last_error = f"CONDUIT devolvió HTTP {status_code} sin un JSON válido."
            else:
                if not 200 <= status_code < 300:
                    last_error = f"CONDUIT devolvió HTTP {status_code}."
                elif isinstance(response_data, dict) and (
                    str(response_data.get("status", "")).strip().lower() in ("error", "failed", "fail")
                    or response_data.get("valid") is False
                    or response_data.get("success") is False
                ):
                    last_error = response_data.get("message") or "CONDUIT rechazó la operación."
                else:
                    return (
                        True, "API call successful", response_data, status_code,
                        attempt, response_time_ms, *request_extra, json_data,
                    )

        except requests.exceptions.Timeout as exc:
            last_error = (
                f"Timeout en la llamada a API CONDUIT (intento {attempt}): "
                f"{type(exc).__name__}: {exc}"
            )
        except requests.exceptions.ConnectionError as exc:
            last_error = (
                f"Error de conexión con API CONDUIT (intento {attempt}): "
                f"{type(exc).__name__}: {exc}"
            )
        except Exception as exc:
            last_error = f"Error en API CONDUIT (intento {attempt}): {exc}"

        logging.warning("%s", last_error)
        if attempt < max_retries:
            time.sleep(retry_delay)

    message = f"Todos los {max_retries} intentos fallaron. Último error: {last_error}"
    return False, message, response_data, status_code, attempt, response_time_ms, *request_extra, json_data


def send_conduit_data(
    serial_number, station_type, max_retries=None,
    retry_delay=None, *, include_request=False
):
    """Devuelve cinco valores al servidor, con el JSON de solicitud opcional al final."""
    success, message, response_data, _, attempts, response_time_ms, *request_extra, json_data = call_conduit_api_with_retry(
        serial_number=serial_number,
        station_type=station_type,
        
        max_retries=max_retries,
        retry_delay=retry_delay,
        include_request=include_request,
    )
    if success:
        logging.info("CONDUIT PASSED para %s (estación: %s, intentos: %s)", serial_number, station_type, attempts)
    else:
        logging.error("CONDUIT FAILED para %s (estación: %s): %s", serial_number, station_type, message)
    return success, message, response_data, attempts, response_time_ms, *request_extra, json_data


def validate_time(serial_number, station_type, *, detalle=None):
    """Devuelve el status y el message y, si se solicita, llena detalle para pantalla."""
    success, message, response_data, _, _, *request_extra, json_data = send_conduit_data(
        serial_number,
        station_type,
        max_retries=1,
        include_request=detalle is not None,
    )
    if detalle is not None:
        detalle["part_number"] = None
        for clave, contenido in (("request", request_extra[0]), ("response", response_data)):
            if isinstance(contenido, dict):
                source = contenido.get("source")
                if isinstance(source, dict) and "password" in source:
                    contenido = {**contenido, "source": {**source}}
            detalle[clave] = contenido

    if not success:
        if isinstance(response_data, dict) and "message" in response_data and not response_data.get("raw_response"):
            message = response_data["message"]
        return "ERROR", message

    try:
        transaction, = response_data["transaction_responses"]
        command_response, = [
            command for command in transaction["command_responses"]
            if command["command"]["name"] == "RejectIfTimeExpired"
        ]
        result = command_response["results"][0]
        dt_status = result["status"]
        if not isinstance(dt_status, str) or not dt_status.strip():
            raise ValueError("Invalid RejectIfTimeExpired status")
    except (KeyError, IndexError, TypeError, ValueError):
        return "ERROR", "Missing or invalid RejectIfTimeExpired result."

    if detalle is not None and dt_status == "NO-OP":
        try:
            detalle["part_number"] = transaction["scanned_unit"]["unit"]["part_number"]
        except (KeyError, IndexError, TypeError):
            pass

    return dt_status, result.get("message", ""), response_data, json_data

validate_dispensing_time = validate_time