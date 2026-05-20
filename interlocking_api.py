# interlocking_api.py
"""
Módulo para manejar las llamadas a la API de INTERLOCKING
"""
import requests
import json
import logging
import traceback
import time
import conexion  # Solo para obtener URLs de la BD

# Configuración de reintentos
MAX_RETRIES = 5  # Máximo número de reintentos
RETRY_DELAY = 2  # Segundos entre reintentos

def get_interlocking_url():
    """
    Obtiene la URL de INTERLOCKING desde la base de datos
    utilizando la función get_urls() de conexion.py
    """
    try:
        urls = conexion.get_urls()
        for name, url in urls.items():
            if 'INTERLOCKING' in name.upper():
                logging.info(f"URL de INTERLOCKING encontrada: {name} -> {url}")
                return url
        
        logging.warning("No se encontró URL para INTERLOCKING en la base de datos")
        return None
        
    except Exception as e:
        logging.error(f"Error obteniendo URL de INTERLOCKING: {e}")
        return None

def call_interlocking_api_with_retry(serial_number=None, is_station_10=False, max_retries=None, retry_delay=None):
    """
    Llama a la API de INTERLOCKING con reintentos automáticos
    
    Args:
        serial_number (str, optional): Número de serie para estaciones normales
        is_station_10 (bool): Si es True, usa estructura para estación 10
        max_retries (int, optional): Máximo número de reintentos
        retry_delay (int, optional): Segundos entre reintentos
    
    Returns:
        tuple: (success, message, response_data, status_code, attempts, response_time_ms)
    """
    max_retries = max_retries if max_retries is not None else MAX_RETRIES
    retry_delay = retry_delay if retry_delay is not None else RETRY_DELAY
    
    # Obtener la URL de INTERLOCKING
    interlocking_url = get_interlocking_url()
    
    if not interlocking_url:
        error_msg = "No se ha configurado la URL de INTERLOCKING en la base de datos"
        logging.error(error_msg)
        return False, error_msg, None, None, 0, 0
    
    attempts = 0
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        attempts = attempt
        logging.info(f"Intento {attempt}/{max_retries} para API INTERLOCKING" + 
                    (f" (pieza: {serial_number})" if serial_number else " (Station 10)"))
        
        try:
            import interlocking_json
            
            # Obtener el JSON según el tipo de llamada
            if is_station_10:
                json_data = interlocking_json.interlocking_station_10()
                logging.info(f"JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                call_description = "Station 10"
            else:
                json_data = interlocking_json.interlocking_station(serial_number)
                logging.info(f"JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                call_description = f"pieza: {serial_number}"
            
            # Validar que el JSON no sea un string de error
            if isinstance(json_data, str) and "Error" in json_data:
                logging.error(f"Error generando JSON para {call_description}: {json_data}")
                last_error = json_data
                if attempt < max_retries:
                    logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                    time.sleep(retry_delay)
                continue
            
            logging.debug(f"Datos enviados (intento {attempt}): {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            
            # Medir tiempo de respuesta
            start_time = time.time()
            
            # Realizar la llamada POST a la API
            response = requests.post(
                interlocking_url,
                json=json_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
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
            logging.info(f"API INTERLOCKING respondió con código {response.status_code} (intento {attempt}) - Tiempo respuesta: {response_time_ms} ms")
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
                    logging.info(f"✅ API INTERLOCKING exitosa en intento {attempt} para {call_description} - Tiempo: {response_time_ms} ms")
                    return True, "API call successful", response_data, response.status_code, attempts, response_time_ms
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
            response_time_ms = 15000  # Timeout de 15 segundos
            error_msg = f"Timeout en llamada API INTERLOCKING (intento {attempt}) - Tiempo: {response_time_ms} ms"
            logging.error(error_msg)
            last_error = error_msg
            if attempt < max_retries:
                logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                time.sleep(retry_delay)
            continue
            
        except requests.exceptions.ConnectionError:
            response_time_ms = 0
            error_msg = f"Error de conexión con API INTERLOCKING (intento {attempt})"
            logging.error(error_msg)
            last_error = error_msg
            if attempt < max_retries:
                logging.info(f"Esperando {retry_delay} segundos antes del reintento {attempt + 1}...")
                time.sleep(retry_delay)
            continue
            
        except Exception as e:
            response_time_ms = 0
            error_msg = f"Error inesperado en API INTERLOCKING (intento {attempt}): {str(e)}"
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

def validate_piece(serial_number, max_retries=None, retry_delay=None):
    """
    Valida una pieza con la API de INTERLOCKING usando estructura genérica
    (Para estaciones que NO son la ST10)
    
    Args:
        serial_number (str): Número de serie a validar
        max_retries (int, optional): Máximo número de reintentos
        retry_delay (int, optional): Segundos entre reintentos
    
    Returns:
        tuple: (is_valid, message, attempts, response_time_ms)
    """
    success, message, response_data, status_code, attempts, response_time_ms = call_interlocking_api_with_retry(
        serial_number=serial_number,
        is_station_10=False,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    if success:
        logging.info(f"✓ INTERLOCKING validation PASSED for {serial_number} (intentos: {attempts}, tiempo: {response_time_ms} ms)")
        return True, message, response_data, attempts, response_time_ms
    else:
        logging.error(f"✗ INTERLOCKING validation FAILED for {serial_number} después de {attempts} intentos: {message} (tiempo último intento: {response_time_ms} ms)")
        return False, message, response_data, attempts, response_time_ms

def validate_station_10(max_retries=None, retry_delay=None):
    """
    Valida la estación 10 con la API de INTERLOCKING usando estructura específica
    (Para la estación ST10 - Laser)
    
    Returns:
        tuple: (is_valid, message, attempts, response_time_ms)
    """
    success, message, response_data, status_code, attempts, response_time_ms = call_interlocking_api_with_retry(
        serial_number=None,
        is_station_10=True,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    if success:
        logging.info(f"✓ INTERLOCKING Station 10 validation PASSED (intentos: {attempts}, tiempo: {response_time_ms} ms)\nresponse_data:{response_data}")
        return True, message, response_data, attempts, response_time_ms
    else:
        logging.error(f"✗ INTERLOCKING Station 10 validation FAILED después de {attempts} intentos: {message} (tiempo último intento: {response_time_ms} ms)")
        return False, message, response_data, attempts, response_time_ms