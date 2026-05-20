#!/usr/bin/env python
"""
Diagnóstico detallado para webservice SFIS cuando el ping funciona
Fecha: 2026
"""
from zeep import Client
from zeep.transports import Transport
import requests
import socket
import time
import sys
import os
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
import urllib3
import logging.config

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DiagnosticoWebserviceDetallado:
    def __init__(self):
        # Configuración exacta como la usas
        self.config = {
            'url': 'http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx',
            'program_id': 'TSP_MXT1',
            'device': 'DEV001', 
            'program_password': '8d2cH_Y/ip',
            'tsp': 'TSP0011'
        }
        
        self.resultados = []
        self.archivo_log = f"webservice_diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log(self, mensaje, nivel="INFO", mostrar=True):
        """Registra mensaje con timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        linea = f"[{timestamp}] {nivel}: {mensaje}"
        
        if mostrar:
            if nivel == "ERROR":
                print(f"\033[91m{linea}\033[0m")
            elif nivel == "SUCCESS":
                print(f"\033[92m{linea}\033[0m")
            elif nivel == "WARNING":
                print(f"\033[93m{linea}\033[0m")
            else:
                print(linea)
        
        self.resultados.append(linea)
        
        with open(self.archivo_log, 'a', encoding='utf-8') as f:
            f.write(linea + '\n')
    
    def test_ping_detallado(self):
        """Prueba de ping más detallada"""
        print("\n" + "="*80)
        print("1. PRUEBA DE PING DETALLADA")
        print("="*80)
        
        hostname = "ptx-sftsp-n1.sfis.pegatroncorp.com"
        
        try:
            # Comando ping con más intentos
            self.log(f"Ejecutando ping a {hostname}...")
            
            # Usar subprocess para mejor control
            resultado = subprocess.run(
                ['ping', '-n', '10', hostname],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if resultado.returncode == 0:
                self.log("✓ Ping exitoso", "SUCCESS")
                
                # Extraer información del ping
                lineas = resultado.stdout.split('\n')
                for linea in lineas:
                    if 'ms' in linea and '=' in linea:
                        self.log(f"  Estadísticas: {linea.strip()}")
                    elif 'TTL=' in linea:
                        self.log(f"  Respuesta: {linea.strip()}")
            else:
                self.log(f"✗ Ping falló (código: {resultado.returncode})", "ERROR")
                self.log(f"  Salida: {resultado.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            self.log("✗ Timeout en ping", "ERROR")
        except Exception as e:
            self.log(f"✗ Error en ping: {e}", "ERROR")
    
    def test_traceroute(self):
        """Prueba traceroute (tracert) en Windows"""
        print("\n" + "="*80)
        print("2. TRACEROUTE (TRA CERT) AL SERVIDOR")
        print("="*80)
        
        hostname = "ptx-sftsp-n1.sfis.pegatroncorp.com"
        
        try:
            self.log(f"Ejecutando tracert a {hostname}...")
            
            # Ejecutar tracert
            resultado = subprocess.run(
                ['tracert', '-h', '15', hostname],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                self.log("✓ Tracert completado", "SUCCESS")
                
                # Mostrar solo primeros 10 saltos para no saturar
                lineas = resultado.stdout.split('\n')
                self.log("Primeros 10 saltos:")
                for i, linea in enumerate(lineas[:15]):
                    if linea.strip():
                        self.log(f"  {linea.strip()}")
            else:
                self.log(f"✗ Tracert falló", "WARNING")
                self.log(f"  Última línea: {resultado.stdout.strip().split('\n')[-1]}")
                
        except subprocess.TimeoutExpired:
            self.log("⚠ Tracert timeout (puede ser normal en redes corporativas)", "WARNING")
        except Exception as e:
            self.log(f"✗ Error en tracert: {e}", "ERROR")
    
    def test_puerto_80_detallado(self):
        """Prueba detallada del puerto 80"""
        print("\n" + "="*80)
        print("3. PRUEBA DETALLADA PUERTO 80")
        print("="*80)
        
        hostname = "ptx-sftsp-n1.sfis.pegatroncorp.com"
        
        try:
            # Primero obtener IP
            ip = socket.gethostbyname(hostname)
            self.log(f"IP del servidor: {ip}")
            
            # Probar con telnet (simulado)
            self.log("\nProbando conexión TCP al puerto 80...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            inicio = time.time()
            resultado = sock.connect_ex((ip, 80))
            fin = time.time()
            
            sock.close()
            
            tiempo = round((fin - inicio) * 1000, 2)
            
            if resultado == 0:
                self.log(f"✓ Puerto 80 ACCESIBLE", "SUCCESS")
                self.log(f"  Tiempo de conexión: {tiempo} ms")
                return True
            else:
                self.log(f"✗ Puerto 80 NO ACCESIBLE (código error: {resultado})", "ERROR")
                
                # Probar con PowerShell
                self.log("\nProbando con PowerShell...")
                try:
                    ps_command = f'Test-NetConnection -ComputerName {hostname} -Port 80 -InformationLevel Detailed'
                    resultado_ps = subprocess.run(
                        ['powershell', '-Command', ps_command],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if resultado_ps.stdout:
                        self.log(f"  PowerShell output: {resultado_ps.stdout[:300]}")
                except:
                    pass
                    
                return False
                
        except socket.gaierror:
            self.log("✗ No se puede resolver el hostname", "ERROR")
            return False
        except socket.timeout:
            self.log("✗ Timeout en conexión al puerto", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Error: {e}", "ERROR")
            return False
    
    def test_http_headers(self):
        """Prueba diferentes métodos HTTP"""
        print("\n" + "="*80)
        print("4. PRUEBAS HTTP CON DIFERENTES MÉTODOS")
        print("="*80)
        
        url = self.config['url']
        
        # Probar HEAD primero (más rápido)
        self.log(f"\n1. Probando HEAD request a: {url}")
        try:
            inicio = time.time()
            response = requests.head(url, timeout=10, verify=False, allow_redirects=True)
            fin = time.time()
            
            tiempo = round((fin - inicio) * 1000, 2)
            
            self.log(f"  Status: {response.status_code}")
            self.log(f"  Tiempo: {tiempo} ms")
            
            # Mostrar headers importantes
            headers_interesantes = ['Server', 'Content-Type', 'Content-Length', 'Date']
            for header in headers_interesantes:
                if header in response.headers:
                    self.log(f"  {header}: {response.headers[header]}")
            
            return response.status_code == 200
            
        except Exception as e:
            self.log(f"✗ Error HEAD: {e}", "ERROR")
            return False
    
    def test_get_detallado(self):
        """Prueba GET detallada"""
        print("\n" + "="*80)
        print("5. PRUEBA GET DETALLADA")
        print("="*80)
        
        url = self.config['url']
        
        self.log(f"URL: {url}")
        
        try:
            # Configurar sesión
            session = requests.Session()
            
            # Añadir headers típicos de navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            self.log("Enviando GET request...")
            
            inicio = time.time()
            response = session.get(url, headers=headers, timeout=15, verify=False)
            fin = time.time()
            
            tiempo = round((fin - inicio) * 1000, 2)
            
            self.log(f"Status: {response.status_code}")
            self.log(f"Tiempo total: {tiempo} ms")
            self.log(f"Tamaño respuesta: {len(response.text)} bytes")
            
            if response.status_code == 200:
                self.log("✓ GET exitoso", "SUCCESS")
                
                # Analizar respuesta
                self.analizar_respuesta_http(response)
                return True
                
            elif response.status_code == 404:
                self.log("✗ Error 404 - Página no encontrada", "ERROR")
                self.log("  Esto significa que el servidor web está funcionando")
                self.log("  pero la ruta específica del webservice no existe")
                self.log(f"  URL probada: {url}")
                
                # Guardar respuesta para análisis
                with open('respuesta_404.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.log("  Respuesta guardada en: respuesta_404.html")
                
                return False
                
            elif response.status_code in [401, 403]:
                self.log(f"✗ Error {response.status_code} - Acceso denegado", "ERROR")
                self.log("  El servidor requiere autenticación")
                return False
                
            else:
                self.log(f"✗ Error HTTP: {response.status_code}", "ERROR")
                self.log(f"  Respuesta: {response.text[:200]}")
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
        
    
    def analizar_respuesta_http(self, response):
        """Analiza la respuesta HTTP"""
        self.log("\nAnálisis de respuesta HTTP:")
        
        # Mostrar todos los headers
        self.log("Headers recibidos:")
        for header, valor in response.headers.items():
            self.log(f"  {header}: {valor}")
        
        # Verificar si es SOAP/WSDL
        contenido = response.text
        
        # Buscar indicadores SOAP
        indicadores = {
            'wsdl:definitions': 'WSDL Service',
            '<soap:': 'SOAP Envelope',
            '<?xml': 'XML Document',
            'Web Service': 'Web Service Page',
            'Service Description': 'Service Description'
        }
        
        encontrados = []
        for indicador, descripcion in indicadores.items():
            if indicador.lower() in contenido.lower():
                encontrados.append(descripcion)
        
        if encontrados:
            self.log(f"✓ Indicadores encontrados: {', '.join(encontrados)}", "SUCCESS")
        else:
            self.log("⚠ No se encontraron indicadores SOAP/WSDL", "WARNING")
        
        # Guardar contenido para análisis
        with open('contenido_webservice.txt', 'w', encoding='utf-8') as f:
            f.write(contenido)
        self.log(f"✓ Contenido guardado en: contenido_webservice.txt")
        
        # Mostrar preview
        if len(contenido) > 500:
            preview = contenido[:500].replace('\n', ' ').strip()
            self.log(f"Preview (500 chars): {preview}...")
        else:
            self.log(f"Contenido completo: {contenido}")
    
    def test_urls_alternativas(self):
        """Prueba URLs alternativas"""
        print("\n" + "="*80)
        print("6. URLs ALTERNATIVAS")
        print("="*80)
        
        base_url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com"
        servicio_base = f"{base_url}/SFISWebService_TXVADB0QA"
        
        urls_a_probar = [
            # URL original
            self.config['url'],
            
            # Variaciones del webservice
            f"{servicio_base}/SFISTSPWebService.asmx?wsdl",
            f"{servicio_base}/SFISTSPWebService.asmx?WSDL",
            f"{servicio_base}/SFISTSPWebService.asmx?op=WTSP_LOGINOUT",
            f"{servicio_base}/SFISTSPWebService.asmx?singleWsdl",
            
            # Directorios padres
            f"{servicio_base}/",
            f"{servicio_base}/SFISTSPWebService.asmx",
            
            # Root del servidor
            f"{base_url}/",
            
            # Posibles otros nombres
            f"{servicio_base}/WebService.asmx",
            f"{servicio_base}/Service.asmx",
            f"{servicio_base}/SFISWebService.asmx",
        ]
        
        self.log(f"Base URL: {base_url}")
        self.log(f"Servicio base: {servicio_base}")
        
        for i, url in enumerate(urls_a_probar, 1):
            self.log(f"\n{i}. Probando: {url}")
            
            try:
                # GET rápido
                response = requests.get(url, timeout=5, verify=False)
                
                if response.status_code == 200:
                    self.log(f"  ✓ Status: 200 (OK)", "SUCCESS")
                    
                    # Verificar contenido
                    if any(marker in response.text.lower() for marker in ['wsdl', 'soap', 'xml']):
                        self.log(f"  ✓ Contiene WSDL/SOAP/XML", "SUCCESS")
                    else:
                        self.log(f"  ⚠ No contiene WSDL/SOAP", "WARNING")
                        
                elif response.status_code == 404:
                    self.log(f"  ✗ Status: 404 (Not Found)", "ERROR")
                elif response.status_code in [401, 403]:
                    self.log(f"  ⚠ Status: {response.status_code} (Auth required)", "WARNING")
                else:
                    self.log(f"  ⚠ Status: {response.status_code}", "WARNING")
                    
            except requests.exceptions.ConnectionError:
                self.log(f"  ✗ No se puede conectar", "ERROR")
            except requests.exceptions.Timeout:
                self.log(f"  ✗ Timeout", "ERROR")
            except Exception as e:
                self.log(f"  ✗ Error: {e}", "ERROR")
    
    def test_soap_exacto(self):
        """Prueba SOAP exactamente como tu código"""
        print("\n" + "="*80)
        print("7. PRUEBA SOAP EXACTA (COMO TU CÓDIGO)")
        print("="*80)
        
        # Crear EXACTAMENTE el mismo SOAP que tu código
        soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Body>
            <WTSP_LOGINOUT>
            <programId>{self.config['program_id']}</programId>
            <programPassword>{self.config['program_password']}</programPassword>
            <op>TEST001</op>
            <password></password>
            <device>{self.config['device']}</device>
            <TSP>{self.config['tsp']}</TSP>
            <status>1</status>
            </WTSP_LOGINOUT>
        </soap:Body>
        </soap:Envelope>'''
        
        self.log("Request SOAP que se enviará:")
        self.log(soap_request)
        
        try:
            # Headers EXACTOS como tu código
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"WTSP_LOGINOUT"'
            }
            
            self.log(f"\nEnviando a: {self.config['url']}")
            self.log(f"Headers: {headers}")
            
            inicio = time.time()
            response = requests.post(
                self.config['url'],
                data=soap_request,
                headers=headers,
                timeout=20,
                verify=False
            )
            fin = time.time()
            
            tiempo = round((fin - inicio) * 1000, 2)
            
            self.log(f"\nResultado:")
            self.log(f"Status: {response.status_code}")
            self.log(f"Tiempo: {tiempo} ms")
            
            # Guardar request y response
            with open('soap_request.xml', 'w', encoding='utf-8') as f:
                f.write(soap_request)
            
            with open('soap_response.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.log(f"Request guardado en: soap_request.xml")
            self.log(f"Response guardado en: soap_response.xml")
            
            if response.status_code == 200:
                self.log("✓ Servicio SOAP respondió", "SUCCESS")
                
                # Analizar respuesta
                self.analizar_respuesta_soap_detallada(response.text)
                return True
            else:
                self.log(f"✗ Error HTTP: {response.status_code}", "ERROR")
                
                # Mostrar error detallado
                if response.text:
                    self.log(f"Respuesta del error: {response.text[:500]}")
                    
                    # Guardar error
                    with open('soap_error.xml', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.log(f"Error guardado en: soap_error.xml")
                    
                return False
                
        except requests.exceptions.Timeout:
            self.log("✗ Timeout después de 20 segundos", "ERROR")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log(f"✗ Error de conexión: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Error inesperado: {e}", "ERROR")
            return False
    
    def analizar_respuesta_soap_detallada(self, respuesta):
        """Análisis detallado de respuesta SOAP"""
        self.log("\nAnálisis detallado de respuesta SOAP:")
        
        # Convertir a minúsculas para búsqueda
        resp_lower = respuesta.lower()
        
        # Buscar fault SOAP
        if 'faultstring' in resp_lower:
            self.log("✗ Error SOAP Fault encontrado", "ERROR")
            
            # Extraer mensaje de fault
            fault_start = resp_lower.find('faultstring')
            fault_text = respuesta[fault_start:fault_start+500]
            self.log(f"  Fault: {fault_text[:200]}...")
        
        # Buscar P_RET en diferentes formatos
        patrones_p_ret = [
            ('<p_ret>', '</p_ret>'),
            ('<tsp:p_ret>', '</tsp:p_ret>'),
            ('p_ret=', ';'),
            ('"p_ret":"', '"'),
            ("'p_ret':'", "'")
        ]
        
        p_ret_encontrado = False
        for inicio, fin in patrones_p_ret:
            if inicio in resp_lower:
                try:
                    start_idx = resp_lower.find(inicio) + len(inicio)
                    end_idx = resp_lower.find(fin, start_idx)
                    if end_idx > start_idx:
                        p_ret_valor = respuesta[start_idx:end_idx]
                        self.log(f"P_RET encontrado: {p_ret_valor}")
                        
                        if '1' in p_ret_valor:
                            self.log("  ✓ P_RET=1 (ÉXITO)", "SUCCESS")
                        elif '0' in p_ret_valor:
                            self.log("  ⚠ P_RET=0 (FALLO LÓGICO)", "WARNING")
                        
                        p_ret_encontrado = True
                        break
                except:
                    pass
        
        if not p_ret_encontrado:
            self.log("⚠ P_RET no encontrado en respuesta", "WARNING")
        
        # Mostrar preview de respuesta
        if len(respuesta) > 1000:
            self.log(f"\nPreview respuesta (1000 chars):")
            self.log(respuesta[:1000] + "...")
        else:
            self.log(f"\nRespuesta completa:")
            self.log(respuesta)
    
    def generar_reporte_final(self):
        """Genera reporte final con soluciones"""
        print("\n" + "="*80)
        print("REPORTE FINAL Y SOLUCIONES")
        print("="*80)
        
        # Resumen de pruebas
        self.log("\nRESUMEN DE PRUEBAS:")
        
        # Buscar errores críticos
        errores = [r for r in self.resultados if '✗' in r or 'ERROR' in r]
        exitos = [r for r in self.resultados if '✓' in r or 'SUCCESS' in r]
        
        self.log(f"Total pruebas: {len(self.resultados)}")
        self.log(f"Errores encontrados: {len(errores)}")
        self.log(f"Éxitos: {len(exitos)}")
        
        if errores:
            self.log("\nPRINCIPALES ERRORES ENCONTRADOS:", "ERROR")
            for error in errores[:5]:  # Mostrar solo primeros 5
                self.log(f"  • {error}")

        # Análisis de situación
        self.log("\n" + "-"*80)
        self.log("ANÁLISIS DE SITUACIÓN:")
        
        # Verificar patrones comunes
        mensajes = " ".join(self.resultados)
        
        if "404" in mensajes:
            self.log("❌ PROBLEMA: Error 404 - Ruta no encontrada", "ERROR")
            self.log("   El servidor web funciona pero la URL del webservice no existe")
            self.log("")
            self.log("   SOLUCIONES POSIBLES:")
            self.log("   1. Verificar la URL exacta del webservice")
            self.log("   2. Consultar con el administrador del sistema SFIS")
            self.log("   3. Verificar si el webservice está instalado")
            self.log("   4. Probar URLs alternativas (ver logs)")
            
        elif "No se puede conectar" in mensajes or "ConnectionError" in mensajes:
            self.log("❌ PROBLEMA: Error de conexión al puerto 80", "ERROR")
            self.log("   El servidor responde a ping pero el puerto 80 está bloqueado")
            self.log("")
            self.log("   SOLUCIONES POSIBLES:")
            self.log("   1. Verificar firewall de Windows")
            self.log("   2. Verificar firewall corporativo")
            self.log("   3. Contactar a soporte de red")
            self.log("   4. Probar desde otra computadora")
            
        elif "Timeout" in mensajes:
            self.log("⚠ PROBLEMA: Timeout en conexión", "WARNING")
            self.log("   El servidor responde pero hay problemas de latencia")
            self.log("")
            self.log("   SOLUCIONES POSIBLES:")
            self.log("   1. Aumentar timeout en tu código a 30 segundos")
            self.log("   2. Verificar congestión de red")
            self.log("   3. Probar en horas de menor tráfico")
            
        elif "401" in mensajes or "403" in mensajes:
            self.log("⚠ PROBLEMA: Autenticación requerida", "WARNING")
            self.log("   El servidor requiere credenciales")
            self.log("")
            self.log("   SOLUCIONES POSIBLES:")
            self.log("   1. Verificar si necesita autenticación NTLM/Kerberos")
            self.log("   2. Contactar al administrador para permisos")
            self.log("   3. Configurar autenticación en requests")
            
        elif "P_RET=0" in mensajes:
            self.log("⚠ PROBLEMA: Error lógico del webservice", "WARNING")
            self.log("   El servicio responde pero rechaza la operación")
            self.log("")
            self.log("   SOLUCIONES POSIBLES:")
            self.log("   1. Verificar credenciales (program_id, program_password)")
            self.log("   2. Verificar que el operador exista en SFIS")
            self.log("   3. Consultar logs del servidor SFIS")
            
        else:
            self.log("✅ TODAS LAS PRUEBAS PASARON", "SUCCESS")
            self.log("   El webservice está funcionando correctamente")
            self.log("")
            self.log("   El problema podría estar en:")
            self.log("   1. Tu código de Python")
            self.log("   2. Manejo de excepciones")
            self.log("   3. Procesamiento de respuestas")
        
        # Información de archivos generados
        self.log("\n" + "-"*80)
        self.log("ARCHIVOS GENERADOS:")
        archivos = [
            self.archivo_log,
            'contenido_webservice.txt',
            'soap_request.xml',
            'soap_response.xml',
            'respuesta_404.html'
        ]
        
        for archivo in archivos:
            if os.path.exists(archivo):
                tamano = os.path.getsize(archivo)
                self.log(f"  ✓ {archivo} ({tamano} bytes)")
        
        self.log(f"\nLog completo en: {self.archivo_log}")
        print("="*80)
    
    # 1. Configurar logging para ver el XML
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {
                'format': '%(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    })

    def configurar_logging():
        """Configura el sistema de logging"""
        
        # Crear directorio logs si no existe
        os.makedirs("logs", exist_ok=True)
        
        # Nombre del archivo de log con fecha
        log_filename = f"logs/server_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Obtener logger root
        logger = logging.getLogger()
        
        # Limpiar handlers existentes
        logger.handlers.clear()
        
        # Configurar nivel
        logger.setLevel(logging.DEBUG)
        
        # Crear formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Handler 1: Archivo diario (DEBUG y superior)
        file_handler_daily = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler_daily.setLevel(logging.DEBUG)
        file_handler_daily.setFormatter(formatter)
        logger.addHandler(file_handler_daily)
        
        # Handler 2: Archivo general (INFO y superior)
        file_handler_general = logging.FileHandler("logs/server.log", encoding='utf-8')
        file_handler_general.setLevel(logging.INFO)
        file_handler_general.setFormatter(formatter)
        logger.addHandler(file_handler_general)
        
        # Handler 3: Consola (INFO y superior)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Reducir verbosidad de algunas librerías
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("flet").setLevel(logging.WARNING)
        
        # Forzar escritura inicial
        logger.info("=" * 70)
        logger.info("🔄 LOGGING CONFIGURADO - INICIO DE APLICACIÓN")
        logger.info(f"📁 Archivo diario: {log_filename}")
        logger.info(f"📁 Archivo general: logs/server.log")
        logger.info("=" * 70)
        
        # Forzar flush
        for handler in logger.handlers:
            handler.flush()
        
        return logger

    logger = configurar_logging()

    def ejecutar_todas_pruebas(self):
        """Ejecuta todas las pruebas"""
        print("\n" + "="*80)
        print("DIAGNÓSTICO COMPLETO WEBSERVICE SFIS")
        print("="*80)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Servidor: ptx-sftsp-n1.sfis.pegatroncorp.com")
        print(f"URL: {self.config['url']}")
        print("="*80)
        
        # Limpiar archivos anteriores
        for archivo in ['contenido_webservice.txt', 'soap_request.xml', 
                       'soap_response.xml', 'respuesta_404.html', 'soap_error.xml']:
            if os.path.exists(archivo):
                os.remove(archivo)
        
        # Ejecutar pruebas en orden
        self.test_ping_detallado()
        self.test_traceroute()
        
        if self.test_puerto_80_detallado():
            self.test_http_headers()
            self.test_get_detallado()
            self.test_urls_alternativas()
            self.test_soap_exacto()
        
        self.generar_reporte_final()

        # 2. Crear el cliente
        wsdl_url = 'http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx'
        client = Client(wsdl_url)

        # 3. Llamar a una función (ejemplo: 'GetData')
        # Al ejecutar esto, se imprimirá el XML crudo en la consola
        try:
            response = client.service.GetData(param1='valor')
            print("Respuesta:", response)
            logging.info(f"[LOGIN] Respuesta:\n {response}")
        except Exception as e:
            print(e)
            logging.error(f"[LOGIN] Error:\n {e}")
        
        print(f"\nDiagnóstico completado. Revisa el archivo: {self.archivo_log}")
        

def main():
    """Función principal"""
    try:
        diagnostico = DiagnosticoWebserviceDetallado()
        diagnostico.ejecutar_todas_pruebas()
        
        # Mantener ventana abierta
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrumpido por el usuario")
    except Exception as e:
        print(f"\nError crítico: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import requests
    except ImportError:
        print("Error: Instala requests con: pip install requests")
        sys.exit(1)
    
    main()