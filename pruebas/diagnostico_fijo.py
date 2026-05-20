"""
Diagnóstico específico para el webservice SFIS con datos fijos

Fecha: 2026
"""

import requests
import socket
import time
import sys
import os
from datetime import datetime
from xml.etree import ElementTree as ET
import json

class DiagnosticoWebserviceFijo:
    def __init__(self):
        # Datos fijos según especificas
        self.config = {
            'url': 'http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx',
            'program_id': 'TSP_MXT1',
            'device': 'DEV001',
            'program_password': '8d2cH_Y/ip',
            'tsp': 'TSP001'
        }
        
        self.operator_id = 'TEST001'  # Operador de prueba
        self.resultados = []
        self.archivo_log = f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, mensaje, nivel="INFO"):
        """Registra un mensaje en consola y archivo"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        linea = f"[{timestamp}] {nivel}: {mensaje}"
        
        # Mostrar en consola con colores
        if nivel == "ERROR":
            print(f"\033[91m{linea}\033[0m")  # Rojo
        elif nivel == "SUCCESS":
            print(f"\033[92m{linea}\033[0m")   # Verde
        elif nivel == "WARNING":
            print(f"\033[93m{linea}\033[0m")   # Amarillo
        else:
            print(linea)
        
        # Guardar en lista de resultados
        self.resultados.append({
            'timestamp': timestamp,
            'nivel': nivel,
            'mensaje': mensaje
        })
        
        # Guardar en archivo
        with open(self.archivo_log, 'a', encoding='utf-8') as f:
            f.write(linea + '\n')
    
    def crear_soap_login(self):
        """Crea el XML SOAP para login (igual que tu código)"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
  <soap:Body>
    <WTSP_LOGINOUT>
      <programId>{self.config['program_id']}</programId>
      <programPassword>{self.config['program_password']}</programPassword>
      <op>{self.operator_id}</op>
      <password></password>
      <device>{self.config['device']}</device>
      <TSP>{self.config['tsp']}</TSP>
      <status>1</status>
    </WTSP_LOGINOUT>
  </soap:Body>
</soap:Envelope>'''
    
    def crear_soap_chkroute(self, isn="TEST_ISN_1234567890"):
        """Crea el XML SOAP para WTSP_CHKROUTE"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_CHKROUTE>
      <programId>{self.config['program_id']}</programId>
      <programPassword>{self.config['program_password']}</programPassword>
      <ISN>{isn}</ISN>
      <device>{self.config['device']}</device>
      <checkFlag>ROUTE_CHECK</checkFlag>
      <checkData>Diagnostic Test</checkData>
      <type>1</type>
    </WTSP_CHKROUTE>
  </soap:Body>
</soap:Envelope>'''
    
    def test_resolucion_dns(self):
        """Prueba resolución DNS del hostname"""
        self.log("="*70)
        self.log("PRUEBA 1: RESOLUCIÓN DNS")
        self.log("="*70)
        
        try:
            # Extraer hostname de la URL
            url_parts = self.config['url'].split('//')[1].split('/')
            hostname = url_parts[0]
            
            self.log(f"Hostname a resolver: {hostname}")
            
            inicio = time.time()
            ip_address = socket.gethostbyname(hostname)
            fin = time.time()
            
            tiempo_respuesta = round((fin - inicio) * 1000, 2)
            
            self.log(f"✓ Resuelto a IP: {ip_address}", "SUCCESS")
            self.log(f"Tiempo de respuesta: {tiempo_respuesta} ms")
            
            return ip_address
            
        except socket.gaierror as e:
            self.log(f"✗ Error de resolución DNS: {e}", "ERROR")
            return None
        except Exception as e:
            self.log(f"✗ Error inesperado: {e}", "ERROR")
            return None
    
    def test_conectividad_tcp(self, ip_address):
        """Prueba conectividad TCP al puerto 80"""
        self.log("")
        self.log("PRUEBA 2: CONECTIVIDAD TCP (Puerto 80)")
        self.log("="*70)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 segundos de timeout
            
            inicio = time.time()
            resultado = sock.connect_ex((ip_address, 80))
            fin = time.time()
            
            sock.close()
            
            tiempo_conexion = round((fin - inicio) * 1000, 2)
            
            if resultado == 0:
                self.log(f"✓ Puerto 80 accesible", "SUCCESS")
                self.log(f"Tiempo de conexión: {tiempo_conexion} ms")
                return True
            else:
                self.log(f"✗ Puerto 80 no accesible (código error: {resultado})", "ERROR")
                return False
                
        except socket.timeout:
            self.log("✗ Timeout después de 5 segundos", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Error de conexión: {e}", "ERROR")
            return False
    
    def test_http_basico(self):
        """Prueba HTTP GET básico"""
        self.log("")
        self.log("PRUEBA 3: HTTP GET BÁSICO")
        self.log("="*70)
        
        try:
            self.log(f"URL: {self.config['url']}")
            
            headers = {
                'User-Agent': 'SFIS-Diagnostic-Tool/1.0',
                'Accept': 'text/xml, application/soap+xml, */*'
            }
            
            inicio = time.time()
            response = requests.get(self.config['url'], headers=headers, timeout=10)
            fin = time.time()
            
            tiempo_respuesta = round((fin - inicio) * 1000, 2)
            
            self.log(f"Status HTTP: {response.status_code}")
            self.log(f"Tiempo de respuesta: {tiempo_respuesta} ms")
            
            if response.status_code == 200:
                self.log("✓ Servidor respondió correctamente", "SUCCESS")
                
                # Analizar headers
                self.log("Headers recibidos:")
                for header, value in response.headers.items():
                    if header.lower() in ['server', 'content-type', 'content-length']:
                        self.log(f"  {header}: {value}")
                
                # Verificar tipo de contenido
                content_type = response.headers.get('Content-Type', '').lower()
                if 'xml' in content_type or 'soap' in content_type:
                    self.log("✓ Contenido XML/SOAP detectado", "SUCCESS")
                else:
                    self.log("⚠ Tipo de contenido no es XML/SOAP", "WARNING")
                
                # Verificar si es WSDL/SOAP
                contenido = response.text.lower()
                if 'wsdl' in contenido or 'soap' in contenido:
                    self.log("✓ WSDL/SOAP detectado en contenido", "SUCCESS")
                    
                    # Guardar WSDL para análisis
                    with open('wsdl_dump.xml', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.log("WSDL guardado en: wsdl_dump.xml")
                else:
                    self.log("⚠ No se detectó WSDL/SOAP en contenido", "WARNING")
                
                # Mostrar preview del contenido
                preview = response.text[:300].replace('\n', ' ').strip()
                self.log(f"Preview (300 chars): {preview}")
                
                return response
            else:
                self.log(f"✗ Error HTTP: {response.status_code}", "ERROR")
                if response.text:
                    self.log(f"Contenido del error: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            self.log("✗ Timeout después de 10 segundos", "ERROR")
            return None
        except requests.exceptions.ConnectionError as e:
            self.log(f"✗ Error de conexión: {e}", "ERROR")
            return None
        except Exception as e:
            self.log(f"✗ Error inesperado: {e}", "ERROR")
            return None
    
    def test_soap_login(self):
        """Prueba el servicio SOAP WTSP_LOGINOUT"""
        self.log("")
        self.log("PRUEBA 4: SERVICIO SOAP WTSP_LOGINOUT")
        self.log("="*70)
        
        try:
            # Crear request SOAP
            soap_request = self.crear_soap_login()
            
            self.log(f"Operador de prueba: {self.operator_id}")
            self.log(f"Program ID: {self.config['program_id']}")
            self.log(f"Device: {self.config['device']}")
            self.log(f"TSP: {self.config['tsp']}")
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"WTSP_LOGINOUT"',
                'User-Agent': 'SFIS-Diagnostic-Tool/1.0'
            }
            
            self.log("Enviando request SOAP...")
            
            inicio = time.time()
            response = requests.post(
                self.config['url'],
                data=soap_request,
                headers=headers,
                timeout=15
            )
            fin = time.time()
            
            tiempo_respuesta = round((fin - inicio) * 1000, 2)
            
            self.log(f"Status HTTP: {response.status_code}")
            self.log(f"Tiempo de respuesta: {tiempo_respuesta} ms")
            
            if response.status_code == 200:
                self.log("✓ Servicio SOAP respondió", "SUCCESS")
                
                # Analizar respuesta SOAP
                self.analizar_respuesta_soap(response.text, "WTSP_LOGINOUT")
                return True
            else:
                self.log(f"✗ Error HTTP: {response.status_code}", "ERROR")
                self.log(f"Respuesta: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            self.log("✗ Timeout después de 15 segundos", "ERROR")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log(f"✗ Error de conexión: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Error inesperado: {e}", "ERROR")
            return False
    
    def test_soap_chkroute(self):
        """Prueba el servicio SOAP WTSP_CHKROUTE"""
        self.log("")
        self.log("PRUEBA 5: SERVICIO SOAP WTSP_CHKROUTE")
        self.log("="*70)
        
        try:
            # Crear request SOAP con ISN de prueba
            isn_prueba = "TEST_ISN_" + datetime.now().strftime("%Y%m%d%H%M%S")
            soap_request = self.crear_soap_chkroute(isn_prueba)
            
            self.log(f"ISN de prueba: {isn_prueba}")
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"WTSP_CHKROUTE"',
                'User-Agent': 'SFIS-Diagnostic-Tool/1.0'
            }
            
            self.log("Enviando request SOAP...")
            
            inicio = time.time()
            response = requests.post(
                self.config['url'],
                data=soap_request,
                headers=headers,
                timeout=15
            )
            fin = time.time()
            
            tiempo_respuesta = round((fin - inicio) * 1000, 2)
            
            self.log(f"Status HTTP: {response.status_code}")
            self.log(f"Tiempo de respuesta: {tiempo_respuesta} ms")
            
            if response.status_code == 200:
                self.log("✓ Servicio WTSP_CHKROUTE respondió", "SUCCESS")
                
                # Analizar respuesta SOAP
                self.analizar_respuesta_soap(response.text, "WTSP_CHKROUTE")
                return True
            else:
                self.log(f"✗ Error HTTP: {response.status_code}", "ERROR")
                self.log(f"Respuesta: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error: {e}", "ERROR")
            return False
    
    def analizar_respuesta_soap(self, respuesta_xml, operacion):
        """Analiza la respuesta SOAP"""
        self.log("")
        self.log(f"ANÁLISIS RESPUESTA {operacion}:")
        
        # Guardar respuesta completa
        archivo_respuesta = f"respuesta_{operacion.lower()}.xml"
        with open(archivo_respuesta, 'w', encoding='utf-8') as f:
            f.write(respuesta_xml)
        self.log(f"Respuesta guardada en: {archivo_respuesta}")
        
        # Buscar P_RET en varios formatos
        p_ret_patterns = [
            ('<P_RET>', '</P_RET>'),
            ('<tsp:P_RET>', '</tsp:P_RET>'),
            ('P_RET=', ';'),
            ('P_RET=', '\n'),
            ('"P_RET":"', '"'),
            ("'P_RET':'", "'")
        ]
        
        for inicio_tag, fin_tag in p_ret_patterns:
            if inicio_tag in respuesta_xml:
                try:
                    start = respuesta_xml.find(inicio_tag) + len(inicio_tag)
                    end = respuesta_xml.find(fin_tag, start)
                    if end > start:
                        p_ret_valor = respuesta_xml[start:end]
                        self.log(f"P_RET encontrado: {p_ret_valor}")
                        
                        if p_ret_valor == '1':
                            self.log("✓ P_RET=1 (ÉXITO)", "SUCCESS")
                        elif p_ret_valor == '0':
                            self.log("⚠ P_RET=0 (FALLO LÓGICO)", "WARNING")
                        else:
                            self.log(f"⚠ P_RET={p_ret_valor} (VALOR DESCONOCIDO)", "WARNING")
                        break
                except:
                    pass
        
        # Buscar P_MSG (mensaje)
        p_msg_patterns = [
            ('<P_MSG>', '</P_MSG>'),
            ('<tsp:P_MSG>', '</tsp:P_MSG>'),
            ('P_MSG=', ';'),
            ('P_MSG=', '\n'),
            ('"P_MSG":"', '"'),
            ("'P_MSG':'", "'")
        ]
        
        for inicio_tag, fin_tag in p_msg_patterns:
            if inicio_tag in respuesta_xml:
                try:
                    start = respuesta_xml.find(inicio_tag) + len(inicio_tag)
                    end = respuesta_xml.find(fin_tag, start)
                    if end > start:
                        p_msg_valor = respuesta_xml[start:end]
                        # Limpiar CDATA si existe
                        if '<![CDATA[' in p_msg_valor and ']]>' in p_msg_valor:
                            cdata_start = p_msg_valor.find('<![CDATA[') + len('<![CDATA[')
                            cdata_end = p_msg_valor.find(']]>', cdata_start)
                            if cdata_end > cdata_start:
                                p_msg_valor = p_msg_valor[cdata_start:cdata_end]
                        
                        self.log(f"Mensaje (P_MSG): {p_msg_valor}")
                        break
                except:
                    pass
        
        # Verificar si es fault SOAP
        if 'faultstring' in respuesta_xml.lower():
            fault_start = respuesta_xml.lower().find('faultstring')
            fault_end = respuesta_xml.find('</', fault_start)
            if fault_end > fault_start:
                fault_msg = respuesta_xml[fault_start:fault_end+10]
                self.log(f"✗ Error SOAP detectado: {fault_msg}", "ERROR")
        
        # Mostrar preview
        if len(respuesta_xml) > 500:
            self.log(f"Preview respuesta (500 chars): {respuesta_xml[:500]}...")
        else:
            self.log(f"Respuesta completa: {respuesta_xml}")
    
    def test_alternativas_url(self):
        """Prueba URLs alternativas"""
        self.log("")
        self.log("PRUEBA 6: URLs ALTERNATIVAS")
        self.log("="*70)
        
        base_url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService"
        
        alternativas = [
            base_url + ".asmx",
            base_url + ".asmx?wsdl",
            base_url + ".asmx?WSDL",
            base_url + ".asmx?singleWsdl",
            base_url + ".asmx?op=WTSP_LOGINOUT",
            "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/",
            "http://ptx-sftsp-n1.sfis.pegatroncorp.com/",
        ]
        
        for i, url in enumerate(alternativas, 1):
            try:
                self.log(f"\n{i}. Probando: {url}")
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.log(f"   Status: {response.status_code} ✓", "SUCCESS")
                    
                    # Verificar contenido
                    content_lower = response.text.lower()
                    if 'wsdl' in content_lower or 'soap' in content_lower:
                        self.log("   ✓ Contiene WSDL/SOAP", "SUCCESS")
                    elif 'xml' in content_lower:
                        self.log("   ✓ Contiene XML", "SUCCESS")
                    else:
                        self.log("   ⚠ No parece ser servicio web", "WARNING")
                else:
                    self.log(f"   Status: {response.status_code} ✗", "ERROR")
                    
            except requests.exceptions.ConnectionError:
                self.log("   ✗ No se puede conectar", "ERROR")
            except Exception as e:
                self.log(f"   ✗ Error: {e}", "ERROR")
    
    def test_configuracion_sistema(self):
        """Verifica configuración del sistema"""
        self.log("")
        self.log("PRUEBA 7: CONFIGURACIÓN DEL SISTEMA")
        self.log("="*70)
        
        # Verificar proxy
        proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
        proxy_encontrado = False
        
        for var in proxy_vars:
            if var in os.environ:
                self.log(f"Proxy configurado ({var}): {os.environ[var]}", "WARNING")
                proxy_encontrado = True
        
        if not proxy_encontrado:
            self.log("✓ Sin proxy configurado", "SUCCESS")
        
        # Verificar conectividad a internet
        try:
            test = requests.get("http://www.google.com", timeout=5)
            self.log("✓ Conectividad a internet: OK", "SUCCESS")
        except:
            self.log("✗ Sin conectividad a internet", "ERROR")
        
        # Información del sistema
        self.log(f"Sistema operativo: {sys.platform}")
        self.log(f"Python version: {sys.version.split()[0]}")
        self.log(f"Requests version: {requests.__version__}")
    
    def generar_reporte_final(self):
        """Genera reporte final con conclusiones"""
        self.log("")
        self.log("="*70)
        self.log("REPORTE FINAL")
        self.log("="*70)
        
        # Contar resultados
        total_pruebas = len([r for r in self.resultados if 'PRUEBA' in r['mensaje']])
        exitos = len([r for r in self.resultados if r['nivel'] == 'SUCCESS'])
        errores = len([r for r in self.resultados if r['nivel'] == 'ERROR'])
        
        self.log(f"Pruebas realizadas: {total_pruebas}")
        self.log(f"Éxitos: {exitos}")
        self.log(f"Errores: {errores}")
        
        self.log("")
        self.log("DATOS DE CONFIGURACIÓN USADOS:")
        for key, value in self.config.items():
            self.log(f"  {key}: {value}")
        
        self.log("")
        self.log("CONCLUSIONES Y RECOMENDACIONES:")
        self.log("-"*50)
        
        # Verificar el estado general
        if errores > 0:
            # Buscar el primer error crítico
            errores_criticos = [r for r in self.resultados if r['nivel'] == 'ERROR' and any(
                keyword in r['mensaje'] for keyword in ['DNS', 'conectar', 'puerto', 'timeout']
            )]
            
            if errores_criticos:
                self.log("❌ PROBLEMA DE CONECTIVIDAD DE RED", "ERROR")
                self.log("   Posibles causas:")
                self.log("   1. El servidor no existe o está apagado")
                self.log("   2. Firewall bloqueando el puerto 80")
                self.log("   3. Necesitas VPN para acceder a la red interna")
                self.log("   4. Nombre del servidor incorrecto")
                self.log("")
                self.log("   Acciones recomendadas:")
                self.log("   1. Abre la URL en un navegador web")
                self.log("   2. Verifica con el comando: ping ptx-sftsp-n1.sfis.pegatroncorp.com")
                self.log("   3. Contacta al administrador de red")
            else:
                self.log("⚠ PROBLEMA EN EL SERVICIO WEB", "WARNING")
                self.log("   El servidor responde pero el servicio tiene problemas")
                self.log("   Posibles causas:")
                self.log("   1. Credenciales incorrectas")
                self.log("   2. Servicio SOAP mal configurado")
                self.log("   3. Parámetros inválidos")
                self.log("")
                self.log("   Verifica:")
                self.log("   1. Los datos de program_id, program_password")
                self.log("   2. Que el operador exista en el sistema")
                self.log("   3. Los logs del servidor SFIS")
        else:
            self.log("✅ TODAS LAS PRUEBAS PASARON", "SUCCESS")
            self.log("   El webservice está funcionando correctamente")
            self.log("   El problema podría estar en:")
            self.log("   1. El código de tu aplicación")
            self.log("   2. La configuración en la base de datos")
            self.log("   3. Manejo de excepciones en tu código")
        
        self.log("")
        self.log(f"Log completo guardado en: {self.archivo_log}")
        self.log("="*70)
        
        # También guardar reporte en JSON
        reporte_json = {
            'fecha': datetime.now().isoformat(),
            'configuracion': self.config,
            'resultados': self.resultados,
            'resumen': {
                'total_pruebas': total_pruebas,
                'exitos': exitos,
                'errores': errores
            }
        }
        
        with open('reporte_diagnostico.json', 'w', encoding='utf-8') as f:
            json.dump(reporte_json, f, indent=2, ensure_ascii=False)
        
        self.log(f"Reporte JSON guardado en: reporte_diagnostico.json")
    
    def ejecutar_diagnostico_completo(self):
        """Ejecuta todas las pruebas"""
        print("\n" + "="*70)
        print("DIAGNÓSTICO WEBSERVICE SFIS - DATOS FIJOS")
        print("="*70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {self.config['url']}")
        print("="*70)
        
        # Limpiar archivo de log anterior
        if os.path.exists(self.archivo_log):
            os.remove(self.archivo_log)
        
        # Ejecutar pruebas en orden
        ip = self.test_resolucion_dns()
        
        if ip:
            self.test_conectividad_tcp(ip)
        
        http_response = self.test_http_basico()
        
        if http_response:
            self.test_soap_login()
            self.test_soap_chkroute()
        
        self.test_alternativas_url()
        self.test_configuracion_sistema()
        
        # Generar reporte final
        self.generar_reporte_final()

def main():
    """Función principal - ejecuta el diagnóstico completo"""
    try:
        diagnostico = DiagnosticoWebserviceFijo()
        diagnostico.ejecutar_diagnostico_completo()
        
        # Preguntar si quiere ver el log
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrumpido por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Verificar que requests esté instalado
    try:
        import requests
    except ImportError:
        print("Error: La biblioteca 'requests' no está instalada.")
        print("Instálala con: pip install requests")
        sys.exit(1)
    
    main()