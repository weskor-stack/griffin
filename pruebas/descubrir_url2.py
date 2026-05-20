#!/usr/bin/env python
"""
Prueba directa de URLs comunes para SFIS
"""

import requests
import sys

def probar_url_simple(url):
    """Prueba una URL y muestra resultado simple"""
    try:
        print(f"\nProbando: {url}")
        response = requests.get(url, timeout=5, verify=False)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            contenido = response.text.lower()
            
            if 'wsdl' in contenido or 'soap' in contenido:
                print("  ✅ ¡ES UN WEBSERVICE SOAP!")
                print(f"  Content-Type: {response.headers.get('Content-Type')}")
                
                # Guardar esta URL
                with open('url_correcta.txt', 'w') as f:
                    f.write(url)
                print(f"  ✓ URL guardada en: url_correcta.txt")
                
                return True
            else:
                print(f"  ⚠ Responde pero no es SOAP")
                print(f"  Preview: {response.text[:100]}...")
        else:
            print(f"  ✗ Error HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("  ✗ No se puede conectar")
    except requests.exceptions.Timeout:
        print("  ✗ Timeout")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return False

def main():
    print("🔍 BUSCANDO URL CORRECTA DEL WEBSERVICE")
    print("="*60)
    
    # Las URLs MÁS PROBABLES primero
    urls_prioritarias = [
        # 1. La URL que ya tienes
        "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        
        # 2. Sin la carpeta intermedia
        "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISTSPWebService.asmx",
        
        # 3. Nombre más simple
        "http://ptx-sftsp-n1.sfis.pegatroncorp.com/WebService.asmx",
        
        # 4. Con www
        "http://www.ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        
        # 5. HTTPS por si acaso
        "https://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx",
        
        # 7. Con ?wsdl al final
        "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx?wsdl",
        
        # 8. Variación del nombre del servidor
        "http://sftsp-n1.sfis.pegatroncorp.com/SFISWebService.asmx",
        "http://sfis-web.pegatroncorp.com/WebService.asmx",
    ]
    
    print("\nProbando las URLs más probables...")
    
    for url in urls_prioritarias:
        if probar_url_simple(url):
            print(f"\n🎉 ¡URL ENCONTRADA!: {url}")
            print("\nUsa esta URL en tu archivo login_simple.py:")
            print(f"\nconfig_data = {{")
            print(f"    'url': '{url}',")
            print(f"    'program_id': 'TSP_MXT1',")
            print(f"    'program_password': '8d2cH_Y/ip',")
            print(f"    'device': 'DEV001',")
            print(f"    'tsp': 'TSP0011'")
            print(f"}}")
            return
    
    print("\n" + "="*60)
    print("❌ No se encontró la URL en las opciones comunes")
    print("\nSigue estos pasos:")
    print("1. Pregunta a tu administrador de sistemas la URL exacta")
    print("2. Busca en la documentación del proyecto")
    print("3. Revisa configuraciones anteriores")
    print("4. Prueba acceder al servidor web directamente:")
    print("   http://ptx-sftsp-n1.sfis.pegatroncorp.com/")
    print("\nLa URL típica de un webservice .NET ASMX es:")
    print("http://[servidor]/[carpeta]/[nombre].asmx")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBúsqueda cancelada")
    
    input("\nPresiona Enter para salir...")