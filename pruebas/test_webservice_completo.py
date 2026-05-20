#!/usr/bin/env python
"""
TEST COMPLETO DEL WEBSERVICE SFIS
Autor: Asistente AI
Descripción: Prueba todas las operaciones del webservice SFIS
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import sys

class SFISWebServiceTester:
    def __init__(self):
        self.base_url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
        self.namespace = "http://www.pegatroncorp.com/SFISWebService/"
        
        # Configuración de prueba
        self.config = {
            'program_id': 'TSP_MXT1',
            'program_password': '8d2cH_Y/ip',
            'device': 'DEV001',
            'tsp': 'TSP0011'
        }
        
        # Archivo de resultados
        self.log_file = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, message, level="INFO"):
        """Registra mensajes en consola y archivo"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {level}: {message}"
        
        # Colores para consola
        if level == "ERROR":
            print(f"\033[91m{log_line}\033[0m")
        elif level == "SUCCESS":
            print(f"\033[92m{log_line}\033[0m")
        elif level == "WARNING":
            print(f"\033[93m{log_line}\033[0m")
        else:
            print(log_line)
        
        # Guardar en archivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def print_header(self, title):
        """Imprime un encabezado bonito"""
        print("\n" + "="*70)
        print(f" {title}")
        print("="*70)
    
    def test_connection(self):
        """Prueba conexión básica al servidor"""
        self.print_header("PRUEBA 1: CONEXIÓN BÁSICA")
        
        try:
            self.log(f"Probando conexión a: {self.base_url}")
            
            # GET básico
            response = requests.get(self.base_url, timeout=10, verify=False)
            
            if response.status_code == 200:
                self.log("✅ Servidor responde correctamente", "SUCCESS")
                
                # Verificar si es un webservice
                if 'Web Service' in response.text or 'asmx' in response.text:
                    self.log("✅ Es un webservice ASMX", "SUCCESS")
                    
                    # Guardar página para análisis
                    with open('webservice_page.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.log(f"Página guardada en: webservice_page.html")
                    
                    return True
                else:
                    self.log("⚠ La respuesta no parece un webservice ASMX", "WARNING")
                    return False
            else:
                self.log(f"❌ Error HTTP: {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.Timeout:
            self.log("❌ Timeout después de 10 segundos", "ERROR")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log(f"❌ Error de conexión: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Error inesperado: {e}", "ERROR")
            return False
    
    def test_wsdl(self):
        """Prueba obtención del WSDL"""
        self.print_header("PRUEBA 2: OBTENCIÓN DEL WSDL")
        
        try:
            wsdl_url = self.base_url + "?wsdl"
            self.log(f"Obteniendo WSDL de: {wsdl_url}")
            
            response = requests.get(wsdl_url, timeout=10, verify=False)
            
            if response.status_code == 200:
                self.log("✅ WSDL obtenido correctamente", "SUCCESS")
                
                # Guardar WSDL
                with open('wsdl_completo.xml', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.log(f"WSDL guardado en: wsdl_completo.xml")
                
                # Analizar operaciones disponibles
                self._analyze_wsdl(response.text)
                return True
            else:
                self.log(f"❌ Error obteniendo WSDL: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            return False
    
    def _analyze_wsdl(self, wsdl_content):
        """Analiza el WSDL para extraer información"""
        try:
            # Buscar operaciones
            operaciones = []
            
            # Patrones simples de búsqueda
            if 'WTSP_LOGINOUT' in wsdl_content:
                operaciones.append('WTSP_LOGINOUT')
            if 'WTSP_CHKROUTE' in wsdl_content:
                operaciones.append('WTSP_CHKROUTE')
            if 'WTSP_RESULT' in wsdl_content:
                operaciones.append('WTSP_RESULT')
            if 'GetDatabaseInformation' in wsdl_content:
                operaciones.append('GetDatabaseInformation')
            
            self.log(f"Operaciones encontradas: {', '.join(operaciones)}")
            
            # Buscar namespace
            if 'targetNamespace="' in wsdl_content:
                start = wsdl_content.find('targetNamespace="') + len('targetNamespace="')
                end = wsdl_content.find('"', start)
                namespace = wsdl_content[start:end]
                self.log(f"Namespace: {namespace}")
            
        except Exception as e:
            self.log(f"⚠ Error analizando WSDL: {e}", "WARNING")
    
    def test_wtsp_loginout(self, operator_id="TEST001"):
        """Prueba la operación WTSP_LOGINOUT"""
        self.print_header("PRUEBA 3: WTSP_LOGINOUT (LOGIN)")
        
        # Crear request SOAP
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="{self.namespace}">
      <programId>{self.config['program_id']}</programId>
      <programPassword>{self.config['program_password']}</programPassword>
      <op>{operator_id}</op>
      <password></password>
      <device>{self.config['device']}</device>
      <TSP>{self.config['tsp']}</TSP>
      <status>1</status>
    </WTSP_LOGINOUT>
  </soap:Body>
</soap:Envelope>'''
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'{self.namespace}WTSP_LOGINOUT'
        }
        
        self.log(f"Operador de prueba: {operator_id}")
        self.log(f"Program ID: {self.config['program_id']}")
        self.log(f"Device: {self.config['device']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                self.base_url,
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")
            self.log(f"Status HTTP: {response.status_code}")
            
            # Guardar request y response
            with open('loginout_request.xml', 'w', encoding='utf-8') as f:
                f.write(soap_request)
            with open('loginout_response.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            if response.status_code == 200:
                self.log("✅ Request SOAP enviado correctamente", "SUCCESS")
                
                # Analizar respuesta
                return self._analyze_loginout_response(response.text, operator_id)
            else:
                self.log(f"❌ Error HTTP: {response.status_code}", "ERROR")
                self._save_error_response(response.text, 'loginout')
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            return False
    
    def _analyze_loginout_response(self, response_text, operator_id):
        """Analiza la respuesta de WTSP_LOGINOUT"""
        try:
            # Buscar WTSP_LOGINOUTResult
            if '<WTSP_LOGINOUTResult>' in response_text:
                start = response_text.find('<WTSP_LOGINOUTResult>') + len('<WTSP_LOGINOUTResult>')
                end = response_text.find('</WTSP_LOGINOUTResult>', start)
                
                if end > start:
                    result = response_text[start:end]
                    self.log(f"Resultado: {result}")
                    
                    # Parsear parámetros
                    params = {}
                    for item in result.split(';'):
                        if '=' in item:
                            key, value = item.split('=', 1)
                            params[key.strip()] = value.strip()
                    
                    # Mostrar parámetros
                    self.log("Parámetros parseados:")
                    for key, value in params.items():
                        self.log(f"  {key}: {value}")
                    
                    # Verificar resultado
                    if 'P_RET' in params:
                        if params['P_RET'] == '1':
                            self.log("✅ LOGIN EXITOSO", "SUCCESS")
                            if 'P_NAME' in params:
                                self.log(f"Nombre del operador: {params['P_NAME']}")
                            return True
                        else:
                            error_msg = params.get('P_MSG', 'Login falló')
                            self.log(f"❌ LOGIN FALLIDO: {error_msg}", "ERROR")
                            return False
                    else:
                        self.log("⚠ P_RET no encontrado en la respuesta", "WARNING")
                        return False
            else:
                self.log("⚠ WTSP_LOGINOUTResult no encontrado", "WARNING")
                
                # Buscar fault
                if '<soap:Fault>' in response_text:
                    self._extract_soap_fault(response_text)
                
                return False
                
        except Exception as e:
            self.log(f"⚠ Error analizando respuesta: {e}", "WARNING")
            return False
    
    def test_wtsp_chkroute(self, isn="TEST_ISN_1234567890"):
        """Prueba la operación WTSP_CHKROUTE"""
        self.print_header("PRUEBA 4: WTSP_CHKROUTE (VERIFICACIÓN DE RUTA)")
        
        # Crear request SOAP
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <WTSP_CHKROUTE xmlns="{self.namespace}">
      <programId>{self.config['program_id']}</programId>
      <programPassword>{self.config['program_password']}</programPassword>
      <ISN>{isn}</ISN>
      <device>{self.config['device']}</device>
      <checkFlag>ROUTE_CHECK</checkFlag>
      <checkData>Test from Python</checkData>
      <type>1</type>
    </WTSP_CHKROUTE>
  </soap:Body>
</soap:Envelope>'''
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'{self.namespace}WTSP_CHKROUTE'
        }
        
        self.log(f"ISN de prueba: {isn}")
        
        try:
            start_time = time.time()
            response = requests.post(
                self.base_url,
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")
            self.log(f"Status HTTP: {response.status_code}")
            
            # Guardar request y response
            with open('chkroute_request.xml', 'w', encoding='utf-8') as f:
                f.write(soap_request)
            with open('chkroute_response.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            if response.status_code == 200:
                self.log("✅ Request SOAP enviado correctamente", "SUCCESS")
                
                # Analizar respuesta
                return self._analyze_chkroute_response(response.text, isn)
            else:
                self.log(f"❌ Error HTTP: {response.status_code}", "ERROR")
                self._save_error_response(response.text, 'chkroute')
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            return False
    
    def _analyze_chkroute_response(self, response_text, isn):
        """Analiza la respuesta de WTSP_CHKROUTE"""
        try:
            # Buscar WTSP_CHKROUTEResult
            if '<WTSP_CHKROUTEResult>' in response_text:
                start = response_text.find('<WTSP_CHKROUTEResult>') + len('<WTSP_CHKROUTEResult>')
                end = response_text.find('</WTSP_CHKROUTEResult>', start)
                
                if end > start:
                    result = response_text[start:end]
                    self.log(f"Resultado: {result}")
                    
                    # Parsear parámetros
                    params = {}
                    for item in result.split(';'):
                        if '=' in item:
                            key, value = item.split('=', 1)
                            params[key.strip()] = value.strip()
                    
                    # Mostrar parámetros
                    self.log("Parámetros parseados:")
                    for key, value in params.items():
                        self.log(f"  {key}: {value}")
                    
                    # Verificar resultado
                    if 'P_RET' in params:
                        if params['P_RET'] == '1':
                            self.log("✅ VERIFICACIÓN DE RUTA EXITOSA", "SUCCESS")
                            return True
                        else:
                            error_msg = params.get('P_MSG', 'Verificación falló')
                            self.log(f"❌ VERIFICACIÓN FALLIDA: {error_msg}", "ERROR")
                            return False
                    else:
                        self.log("⚠ P_RET no encontrado en la respuesta", "WARNING")
                        return False
            else:
                self.log("⚠ WTSP_CHKROUTEResult no encontrado", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"⚠ Error analizando respuesta: {e}", "WARNING")
            return False
    
    def test_wtsp_result(self, isn="TEST_ISN_1234567890"):
        """Prueba la operación WTSP_RESULT"""
        self.print_header("PRUEBA 5: WTSP_RESULT (ENVÍO DE RESULTADOS)")
        
        # Crear request SOAP con datos de prueba
        test_data = "MEASURE1=10.5;MEASURE2=20.3;STATUS=PASS"
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <WTSP_RESULT xmlns="{self.namespace}">
      <programId>{self.config['program_id']}</programId>
      <programPassword>{self.config['program_password']}</programPassword>
      <ISN>{isn}</ISN>
      <error>0</error>
      <device>{self.config['device']}</device>
      <TSP>{self.config['tsp']}</TSP>
      <data>{test_data}</data>
      <status>1</status>
      <CPKFlag>ENABLED</CPKFlag>
    </WTSP_RESULT>
  </soap:Body>
</soap:Envelope>'''
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'{self.namespace}WTSP_RESULT'
        }
        
        self.log(f"ISN de prueba: {isn}")
        self.log(f"Datos de prueba: {test_data}")
        
        try:
            start_time = time.time()
            response = requests.post(
                self.base_url,
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")
            self.log(f"Status HTTP: {response.status_code}")
            
            # Guardar request y response
            with open('result_request.xml', 'w', encoding='utf-8') as f:
                f.write(soap_request)
            with open('result_response.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            if response.status_code == 200:
                self.log("✅ Request SOAP enviado correctamente", "SUCCESS")
                
                # Analizar respuesta
                return self._analyze_result_response(response.text, isn)
            else:
                self.log(f"❌ Error HTTP: {response.status_code}", "ERROR")
                self._save_error_response(response.text, 'result')
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            return False
    
    def _analyze_result_response(self, response_text, isn):
        """Analiza la respuesta de WTSP_RESULT"""
        try:
            # Buscar WTSP_RESULTResult
            if '<WTSP_RESULTResult>' in response_text:
                start = response_text.find('<WTSP_RESULTResult>') + len('<WTSP_RESULTResult>')
                end = response_text.find('</WTSP_RESULTResult>', start)
                
                if end > start:
                    result = response_text[start:end]
                    self.log(f"Resultado: {result}")
                    
                    # Parsear parámetros
                    params = {}
                    for item in result.split(';'):
                        if '=' in item:
                            key, value = item.split('=', 1)
                            params[key.strip()] = value.strip()
                    
                    # Mostrar parámetros
                    self.log("Parámetros parseados:")
                    for key, value in params.items():
                        self.log(f"  {key}: {value}")
                    
                    # Verificar resultado
                    if 'P_RET' in params:
                        if params['P_RET'] == '1':
                            self.log("✅ ENVÍO DE RESULTADOS EXITOSO", "SUCCESS")
                            return True
                        else:
                            error_msg = params.get('P_MSG', 'Envío falló')
                            self.log(f"❌ ENVÍO FALLIDO: {error_msg}", "ERROR")
                            return False
                    else:
                        self.log("⚠ P_RET no encontrado en la respuesta", "WARNING")
                        return False
            else:
                self.log("⚠ WTSP_RESULTResult no encontrado", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"⚠ Error analizando respuesta: {e}", "WARNING")
            return False
    
    def test_get_database_info(self):
        """Prueba la operación GetDatabaseInformation"""
        self.print_header("PRUEBA 6: GetDatabaseInformation")
        
        # Crear request SOAP
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetDatabaseInformation xmlns="{self.namespace}">
    </GetDatabaseInformation>
  </soap:Body>
</soap:Envelope>'''
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'{self.namespace}GetDatabaseInformation'
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.base_url,
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")
            self.log(f"Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                self.log("✅ Request SOAP enviado correctamente", "SUCCESS")
                
                # Buscar resultado
                if '<GetDatabaseInformationResult>' in response.text:
                    start = response.text.find('<GetDatabaseInformationResult>') + len('<GetDatabaseInformationResult>')
                    end = response.text.find('</GetDatabaseInformationResult>', start)
                    
                    if end > start:
                        result = response.text[start:end]
                        self.log(f"Información de base de datos: {result}")
                        return True
                else:
                    self.log("⚠ GetDatabaseInformationResult no encontrado", "WARNING")
                    return False
            else:
                self.log(f"❌ Error HTTP: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            return False
    
    def _extract_soap_fault(self, response_text):
        """Extrae información de error SOAP"""
        # Crear request SOAP
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetDatabaseInformation xmlns="{self.namespace}">
    </GetDatabaseInformation>
  </soap:Body>
</soap:Envelope>'''
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'{self.namespace}GetDatabaseInformation'
        }
        
        try:
            response = requests.post(
                self.base_url,
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            
            if '<faultstring>' in response_text:
                start = response.text.find('<faultstring>') + len('<faultstring>')
                end = response.text.find('</faultstring>', start)
                if end > start:
                    fault = response_text[start:end]
                    self.log(f"Error SOAP: {fault}", "ERROR")
        except:
            pass
    
    def _save_error_response(self, response_text, operation):
        """Guarda respuesta de error"""
        filename = f'error_{operation}_{datetime.now().strftime("%H%M%S")}.xml'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response_text)
        self.log(f"Error guardado en: {filename}")
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("\n" + "="*70)
        print(" TEST COMPLETO DEL WEBSERVICE SFIS")
        print("="*70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {self.base_url}")
        print(f"Log file: {self.log_file}")
        print("="*70)
        
        results = {}
        
        # Ejecutar pruebas
        results['connection'] = self.test_connection()
        
        if results['connection']:
            results['wsdl'] = self.test_wsdl()
            results['loginout'] = self.test_wtsp_loginout()
            results['chkroute'] = self.test_wtsp_chkroute()
            results['result'] = self.test_wtsp_result()
            results['db_info'] = self.test_get_database_info()
        
        # Mostrar resumen
        self.print_header("RESUMEN DE PRUEBAS")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        self.log(f"Total de pruebas: {total_tests}")
        self.log(f"Pruebas exitosas: {passed_tests}")
        self.log(f"Pruebas fallidas: {total_tests - passed_tests}")
        
        print("\nDetalle:")
        for test_name, result in results.items():
            status = "✅" if result else "❌"
            self.log(f"  {status} {test_name}")
        
        print("\n" + "="*70)
        
        if passed_tests == total_tests:
            self.log("🎉 ¡TODAS LAS PRUEBAS PASARON!", "SUCCESS")
        else:
            self.log(f"⚠ {total_tests - passed_tests} prueba(s) fallaron", "WARNING")
        
        self.log(f"\nArchivos generados:")
        self.log(f"  • {self.log_file} - Log completo de pruebas")
        self.log(f"  • webservice_page.html - Página del webservice")
        self.log(f"  • wsdl_completo.xml - WSDL completo")
        self.log(f"  • *_request.xml - Requests SOAP")
        self.log(f"  • *_response.xml - Responses SOAP")
        
        print("="*70)
        
        return results


def main():
    """Función principal"""
    try:
        # Crear tester
        tester = SFISWebServiceTester()
        
        # Ejecutar todas las pruebas
        results = tester.run_all_tests()
        
        # Preguntar si quiere ver archivos generados
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Verificar dependencias
    try:
        import requests
    except ImportError:
        print("Error: Necesitas instalar requests")
        print("Ejecuta: pip install requests")
        sys.exit(1)
    
    main()