#!/usr/bin/env python
"""
Prueba rápida de conexión al webservice SFIS
"""

import requests
import socket

# Configuración fija
CONFIG = {
    'url': 'http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx',
    'program_id': 'TSP_MXT1',
    'device': 'DEV001',
    'program_password': '8d2cH_Y/ip',
    'tsp': 'TSP0011'
}

def prueba_conexion_rapida():
    """Prueba de conexión en 30 segundos"""
    print("🔍 PRUEBA RÁPIDA DE CONEXIÓN")
    print("=" * 50)
    
    url = CONFIG['url']
    print(f"URL: {url}")
    
    # 1. Extraer hostname
    try:
        hostname = url.split('//')[1].split('/')[0]
        print(f"\n1. Resolviendo DNS: {hostname}")
        ip = socket.gethostbyname(hostname)
        print(f"   ✅ IP: {ip}")
    except:
        print("   ❌ No se puede resolver DNS")
        return False
    
    # 2. Probar puerto 80
    print(f"\n2. Probando puerto 80 en {ip}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        resultado = sock.connect_ex((ip, 80))
        sock.close()
        if resultado == 0:
            print("   ✅ Puerto 80 accesible")
        else:
            print(f"   ❌ Puerto 80 bloqueado (error: {resultado})")
            return False
    except:
        print("   ❌ Error al conectar al puerto")
        return False
    
    # 3. HTTP GET básico
    print(f"\n3. HTTP GET básico")
    try:
        response = requests.get(url, timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        
        # Verificar si es SOAP
        if 'soap' in response.text.lower() or 'wsdl' in response.text.lower():
            print("   ✅ Es un servicio SOAP/WSDL")
        else:
            print("   ⚠ No parece SOAP/WSDL")
            
        return True
        
    except requests.exceptions.Timeout:
        print("   ❌ Timeout después de 5 segundos")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    if prueba_conexion_rapida():
        print("\n" + "=" * 50)
        print("✅ Servicio accesible")
        print("\nSi tu aplicación no funciona, verifica:")
        print("1. Los datos de configuración")
        print("2. Las credenciales del operador")
        print("3. El formato del XML SOAP")
    else:
        print("\n" + "=" * 50)
        print("❌ No se puede conectar al servicio")
        print("\nPosibles causas:")
        print("1. Servidor no disponible")
        print("2. Firewall bloqueando")
        print("3. Necesitas VPN")
        print("4. URL incorrecta")
    
    input("\nPresiona Enter para salir...")