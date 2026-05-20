#!/usr/bin/env python
"""
Descubridor de URL correcta para webservice SFIS
Autor: Asistente AI
"""

import requests
import socket
import time
from datetime import datetime
import concurrent.futures

def probar_url(url, timeout=3):
    """Prueba una URL específica"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, verify=False)
        elapsed = time.time() - start_time
        
        resultado = {
            'url': url,
            'status': response.status_code,
            'time': round(elapsed * 1000, 2),
            'content_type': response.headers.get('Content-Type', ''),
            'size': len(response.text)
        }
        
        # Verificar si es un webservice SOAP
        es_webservice = False
        contenido = response.text.lower()
        
        if response.status_code == 200:
            if any(marker in contenido for marker in ['wsdl', 'soap:', 'webservice', 'asmx']):
                es_webservice = True
                resultado['tipo'] = 'SOAP/WSDL'
            elif 'xml' in contenido:
                resultado['tipo'] = 'XML'
            else:
                resultado['tipo'] = 'HTML/Other'
        
        resultado['es_webservice'] = es_webservice
        
        # Preview del contenido
        if len(response.text) > 100:
            resultado['preview'] = response.text[:100].replace('\n', ' ')
        else:
            resultado['preview'] = response.text
        
        return resultado
        
    except requests.exceptions.Timeout:
        return {'url': url, 'error': 'Timeout', 'status': None}
    except requests.exceptions.ConnectionError:
        return {'url': url, 'error': 'Connection Error', 'status': None}
    except Exception as e:
        return {'url': url, 'error': str(e), 'status': None}

def generar_posibles_urls(base_host):
    """Genera todas las URLs posibles basadas en patrones comunes"""
    
    posibles_urls = []
    
    # Patrones comunes para webservices .NET/ASMX
    patrones = [
        # Estructura estándar ASMX
        "http://{host}/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        "http://{host}/SFISWebService/SFISTSPWebService.asmx",
        "http://{host}/SFISWebService.asmx",
        "http://{host}/WebService.asmx",
        "http://{host}/Service.asmx",
        "http://{host}/SFISTSPWebService.asmx",
        "http://{host}/TSPWebService.asmx",
        "http://{host}/SFIS_WebService.asmx",
        
        # Con puerto específico (a veces usan puerto no estándar)
        "http://{host}:8080/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        "http://{host}:8080/SFISWebService.asmx",
        "http://{host}:8000/SFISWebService.asmx",
        "http://{host}:8081/SFISWebService.asmx",
        
        # Variaciones del nombre de la carpeta
        "http://{host}/SFISWebService_TXVADB/SFISTSPWebService.asmx",
        "http://{host}/SFIS_WebService_TXVADB0QA/SFISTSPWebService.asmx",
        "http://{host}/WebServices/SFISTSPWebService.asmx",
        "http://{host}/WS/SFISTSPWebService.asmx",
        "http://{host}/webservice/SFISTSPWebService.asmx",
        
        # Nombres alternativos del servicio
        "http://{host}/SFISWebService_TXVADB0QA/WebService.asmx",
        "http://{host}/SFISWebService_TXVADB0QA/Service.asmx",
        "http://{host}/SFISWebService_TXVADB0QA/SFISService.asmx",
        
        # Root directo (poco común pero posible)
        "http://{host}/SFISTSPWebService.asmx",
        "http://{host}/",
        
        # Con parámetros WSDL
        "http://{host}/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx?wsdl",
        "http://{host}/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx?WSDL",
        "http://{host}/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx?op=WTSP_LOGINOUT",
        
        # HTTPS (por si acaso)
        "https://{host}/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        "https://{host}/SFISWebService.asmx",
    ]
    
    # También probar con y sin "www"
    hosts_variantes = [
        base_host,
        f"www.{base_host}" if not base_host.startswith('www.') else base_host[4:],
        base_host.replace('ptx-sftsp-n1', 'sftsp'),
        base_host.replace('ptx-sftsp-n1', 'sfis'),
        base_host.replace('ptx-sftsp-n1', 'sfisweb'),
    ]
    
    # Generar todas las combinaciones
    for host in hosts_variantes:
        for patron in patrones:
            url = patron.format(host=host)
            if url not in posibles_urls:
                posibles_urls.append(url)
    
    return posibles_urls

def main():
    print("="*70)
    print("DESCUBRIDOR DE URL DE WEBSERVICE SFIS")
    print("="*70)
    
    host_base = "ptx-sftsp-n1.sfis.pegatroncorp.com"
    
    print(f"\n🔍 Analizando servidor: {host_base}")
    
    # Verificar si el servidor responde
    try:
        ip = socket.gethostbyname(host_base)
        print(f"✅ Servidor encontrado: {ip}")
    except socket.gaierror:
        print(f"❌ No se puede resolver el servidor: {host_base}")
        print("\nPosibles soluciones:")
        print("1. Verifica que estés conectado a la red de la empresa")
        print("2. Verifica el nombre del servidor")
        print("3. Prueba con VPN si estás fuera de la oficina")
        return
    
    # Generar URLs posibles
    print(f"\n📋 Generando URLs posibles...")
    urls = generar_posibles_urls(host_base)
    print(f"Se probarán {len(urls)} URLs diferentes")
    
    # Probar URLs en paralelo (más rápido)
    print(f"\n⚡ Probando URLs (esto puede tomar un momento)...")
    
    webservices_encontrados = []
    respuestas_validas = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Enviar todas las pruebas
        futures = {executor.submit(probar_url, url, 5): url for url in urls}
        
        completadas = 0
        for future in concurrent.futures.as_completed(futures):
            completadas += 1
            url = futures[future]
            
            try:
                resultado = future.result()
                
                # Mostrar progreso
                print(f"\rProgreso: {completadas}/{len(urls)} URLs probadas", end="")
                
                # Guardar resultados interesantes
                if 'error' not in resultado:
                    respuestas_validas.append(resultado)
                    
                    if resultado.get('es_webservice'):
                        webservices_encontrados.append(resultado)
                        
            except Exception as e:
                pass
    
    print("\n" + "="*70)
    print("RESULTADOS")
    print("="*70)
    
    if webservices_encontrados:
        print(f"\n🎉 ¡WEBSERVICES ENCONTRADOS! ({len(webservices_encontrados)})")
        print("-"*70)
        
        # Ordenar por tipo y tiempo de respuesta
        webservices_encontrados.sort(key=lambda x: (x.get('tipo', ''), x.get('time', 9999)))
        
        for i, ws in enumerate(webservices_encontrados, 1):
            print(f"\n{i}. {ws['url']}")
            print(f"   Status: {ws['status']} | Tiempo: {ws['time']}ms | Tamaño: {ws['size']} bytes")
            print(f"   Tipo: {ws.get('tipo', 'Desconocido')}")
            print(f"   Content-Type: {ws.get('content_type', 'N/A')}")
            if 'preview' in ws:
                print(f"   Preview: {ws['preview']}")
        
        print("\n" + "="*70)
        print("RECOMENDACIÓN:")
        print("="*70)
        
        # Recomendar la mejor URL
        mejor_url = webservices_encontrados[0]['url']
        print(f"\n✨ Usa esta URL en tu código:")
        print(f"\n{mejor_url}")
        
        print(f"\n📋 Para tu archivo de configuración:")
        print(f'url = "{mejor_url}"')
        
    else:
        print(f"\n😞 No se encontraron webservices SOAP")
        
        if respuestas_validas:
            print(f"\n📄 Respuestas válidas encontradas ({len(respuestas_validas)}):")
            print("-"*70)
            
            for i, resp in enumerate(respuestas_validas[:10], 1):  # Mostrar solo 10
                print(f"\n{i}. {resp['url']}")
                print(f"   Status: {resp['status']} | Tamaño: {resp['size']} bytes")
                print(f"   Tipo: {resp.get('tipo', 'Desconocido')}")
                if 'preview' in resp:
                    print(f"   Preview: {resp['preview'][:80]}...")
        
        print("\n" + "="*70)
        print("SOLUCIONES ALTERNATIVAS:")
        print("="*70)
        
        print("\n1. 📞 Contacta al administrador del sistema SFIS y pregunta:")
        print("   • ¿Cuál es la URL exacta del webservice?")
        print("   • ¿Está el servicio SFISWebService instalado?")
        print("   • ¿En qué puerto corre el servicio?")
        
        print("\n2. 🔍 Busca manualmente en:")
        print(f"   • http://{host_base}/")
        print(f"   • http://{host_base}:8080/")
        print(f"   • http://{host_base}:8000/")
        
        print("\n3. 📁 Revisa la documentación o configuración existente")
        print("   • Busca archivos de configuración (.config, .ini, .xml)")
        print("   • Revisa documentación del sistema SFIS")
        print("   • Consulta con otros desarrolladores")
    
    print("\n" + "="*70)
    print("ARCHIVOS GUARDADOS:")
    print("="*70)
    
    # Guardar resultados en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_resultados = f"urls_encontradas_{timestamp}.txt"
    
    with open(archivo_resultados, 'w', encoding='utf-8') as f:
        f.write(f"Resultados de búsqueda de URL - {datetime.now()}\n")
        f.write(f"Servidor base: {host_base}\n")
        f.write("="*70 + "\n\n")
        
        if webservices_encontrados:
            f.write("WEBSERVICES ENCONTRADOS:\n")
            f.write("-"*70 + "\n")
            for ws in webservices_encontrados:
                f.write(f"\nURL: {ws['url']}\n")
                f.write(f"Status: {ws['status']} | Tiempo: {ws['time']}ms\n")
                f.write(f"Tipo: {ws.get('tipo', 'Desconocido')}\n")
                f.write(f"Content-Type: {ws.get('content_type')}\n")
                f.write("-"*40 + "\n")
        else:
            f.write("No se encontraron webservices\n\n")
            
            if respuestas_validas:
                f.write("RESPUESTAS VÁLIDAS:\n")
                f.write("-"*70 + "\n")
                for resp in respuestas_validas:
                    f.write(f"\nURL: {resp['url']}\n")
                    f.write(f"Status: {resp['status']} | Tamaño: {resp['size']} bytes\n")
                    f.write(f"Tipo: {resp.get('tipo', 'Desconocido')}\n")
                    f.write("-"*40 + "\n")
    
    print(f"\n📄 Resultados guardados en: {archivo_resultados}")

if __name__ == "__main__":
    # Deshabilitar warnings SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        import requests
        main()
    except ImportError:
        print("Error: Necesitas instalar requests")
        print("Ejecuta: pip install requests")
    
    input("\nPresiona Enter para salir...")