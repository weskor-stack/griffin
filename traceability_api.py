# traceability_api.py
"""
Módulo para manejar las llamadas a la API de TRACEABILITY
"""
import requests
import json
import logging
import traceback
import time
import conexion  # Solo para obtener URLs de la BD

# Configuración de reintentos
MAX_RETRIES = 5  # Máximo número de reintentos
RETRY_DELAY = 5  # Segundos entre reintentos

def get_traceability_url():
    """
    Obtiene la URL de TRACEABILITY desde la base de datos
    utilizando la función get_urls() de conexion.py
    """
    try:
        urls = conexion.get_urls()
        for name, url in urls.items():
            if 'TRACEABILITY' in name.upper():
                logging.info(f"URL de TRACEABILITY encontrada: {name} -> {url}")
                return url
        
        logging.warning("No se encontró URL para TRACEABILITY en la base de datos")
        logging.debug(f"URLs disponibles: {list(urls.keys())}")
        return None
        
    except Exception as e:
        logging.error(f"Error obteniendo URL de TRACEABILITY: {e}")
        return None

def call_traceability_api_with_retry(serial_number, station_type, max_retries=None, retry_delay=None):
    """
    Llama a la API de TRACEABILITY con reintentos automáticos
    
    Args:
        serial_number (str): Número de serie de la pieza
        station_type (str): Tipo de estación ('ST10', 'ST20', 'ST30', etc.)
        max_retries (int, optional): Máximo número de reintentos
        retry_delay (int, optional): Segundos entre reintentos
    
    Returns:
        tuple: (success, message, response_data, status_code, attempts, response_time_ms)
    """
    max_retries = max_retries if max_retries is not None else MAX_RETRIES
    retry_delay = retry_delay if retry_delay is not None else RETRY_DELAY
    
    # Obtener la URL de TRACEABILITY
    traceability_url = get_traceability_url()
    
    if not traceability_url:
        error_msg = "No se ha configurado la URL de TRACEABILITY en la base de datos"
        logging.error(error_msg)
        return False, error_msg, None, None, 0, 0
    
    attempts = 0
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        attempts = attempt
        logging.info(f"Intento {attempt}/{max_retries} para API TRACEABILITY (pieza: {serial_number}, estación: {station_type})")
        
        try:
            import traceability_json
            
            # Obtener el JSON según el tipo de estación
            if station_type == "ST10":
                json_data = traceability_json.traceability_station_10(serial_number)
                logging.info(f"JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                call_description = f"Station 10 - {serial_number}"
            elif station_type == "ST20":
                json_data = traceability_json.traceability_station_20(serial_number)
                logging.info(f"JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                call_description = f"Station 20 - {serial_number}"
            elif station_type == "ST30":
                json_data = traceability_json.traceability_station_30(serial_number)
                logging.info(f"JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                call_description = f"Station 30 - {serial_number}"
            else:
                # Por defecto usar estructura de ST20 (genérica)
                logging.warning(f"Estación {station_type} no reconocida, usando estructura ST20")
                json_data = traceability_json.traceability_station_20(serial_number)
                call_description = f"Station {station_type} (default ST20) - {serial_number}"
            
            # Validar que el JSON no sea un string de error
            if isinstance(json_data, str) and ("Error" in json_data or "error" in json_data.lower()):
                logging.error(f"Error generando JSON para {call_description}: {json_data}")
                last_error = json_data
                if attempt < max_retries:
                    logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                    time.sleep(retry_delay)
                continue
            
            logging.debug(f"Datos enviados (intento {attempt}): {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")  # Truncado para no saturar
            
            # Medir tiempo de respuesta
            start_time = time.time()
            
            # Realizar la llamada POST a la API
            response = requests.post(
                traceability_url,
                json=json_data,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Timeout de 30 segundos (puede ser más largo por los datos)
            )
            
            # Calcular tiempo de respuesta en milisegundos
            end_time = time.time()
            response_time_ms = round((end_time - start_time) * 1000, 2)
            
            # Intentar parsear la respuesta como JSON
            response_data = None
            try:
                response_data = response.json()
            except:
                response_data = {"message": response.text, "raw_response": True}
            
            # Logging con tiempo de respuesta
            logging.info(f"API TRACEABILITY respondió con código {response.status_code} (intento {attempt}) - Tiempo respuesta: {response_time_ms} ms")
            logging.debug(f"Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False) if response_data else 'No data'}")
            
            # Evaluar si la respuesta fue exitosa (códigos 200-599)
            if 200 <= response.status_code < 600:
                is_valid = True
                if isinstance(response_data, dict):
                    if response_data.get('status') == 'error':
                        is_valid = False
                    elif response_data.get('valid') is False:
                        is_valid = False
                    elif response_data.get('success') is False:
                        is_valid = False
                
                if is_valid:
                    logging.info(f"✅ API TRACEABILITY exitosa en intento {attempt} para {call_description} - Tiempo: {response_time_ms} ms")
                    return True, {json.dumps(response_data, indent=2, ensure_ascii=False) if response_data else 'No data'}, response_data, response.status_code, attempts, response_time_ms
                else:
                    error_msg = "API returned invalid status"
                    logging.warning(f"{error_msg} para {call_description} - Tiempo: {response_time_ms} ms")
                    last_error = error_msg
                    if attempt < max_retries:
                        logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                        time.sleep(retry_delay)
                    continue
            else:
                error_msg = f"API respondió con código {response.status_code}: {response.text}"
                logging.error(f"{error_msg} - Tiempo: {response_time_ms} ms")
                last_error = error_msg
                if attempt < max_retries:
                    logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                    time.sleep(retry_delay)
                continue
                
        except requests.exceptions.Timeout:
            response_time_ms = 30000  # Timeout de 30 segundos
            error_msg = f"Timeout en llamada API TRACEABILITY (intento {attempt}) - Tiempo: {response_time_ms} ms"
            logging.error(error_msg)
            last_error = error_msg
            if attempt < max_retries:
                logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                time.sleep(retry_delay)
            continue
            
        except requests.exceptions.ConnectionError:
            response_time_ms = 0
            error_msg = f"Error de conexión con API TRACEABILITY (intento {attempt})"
            logging.error(error_msg)
            last_error = error_msg
            if attempt < max_retries:
                logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                time.sleep(retry_delay)
            continue
            
        except Exception as e:
            response_time_ms = 0
            error_msg = f"Error inesperado en API TRACEABILITY (intento {attempt}): {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            last_error = error_msg
            if attempt < max_retries:
                logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                time.sleep(retry_delay)
            continue
    
    final_error = f"Todos los {max_retries} intentos fallaron. Último error: {last_error}"
    logging.error(final_error)
    return False, final_error, None, None, attempts, 0

def send_traceability_data(serial_number, station_type, max_retries=None, retry_delay=None):
    """
    Envía datos a la API de TRACEABILITY
    
    Args:
        serial_number (str): Número de serie de la pieza
        station_type (str): Tipo de estación ('ST10', 'ST20', 'ST30')
        max_retries (int, optional): Máximo número de reintentos
        retry_delay (int, optional): Segundos entre reintentos
    
    Returns:
        tuple: (is_valid, message, attempts, response_time_ms)
    """
    success, message, response_data, status_code, attempts, response_time_ms = call_traceability_api_with_retry(
        serial_number=serial_number,
        station_type=station_type,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    if success:
        logging.info(f"✓ TRACEABILITY data sent successfully for {serial_number} (estación: {station_type}, intentos: {attempts}, tiempo: {response_time_ms} ms)")
        return True, message, attempts, response_time_ms
    else:
        logging.error(f"✗ TRACEABILITY data send FAILED for {serial_number} después de {attempts} intentos: {message}")
        return False, message, attempts, response_time_ms