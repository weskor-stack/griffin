#!/usr/bin/env python
"""
PRUEBA RÁPIDA DEL WEBSERVICE
"""

import requests
import time

def test_rapido():
    print("⚡ PRUEBA RÁPIDA WEBSERVICE SFIS")
    print("="*50)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    # Configuración
    config = {
        'program_id': 'TSP_MXT1',
        'program_password': '8d2cH_Y/ip',
        'device': 'DEV001',
        'tsp': 'TSP0011'
    }
    
    print(f"\n1. Probando conexión...")
    try:
        response = requests.get(url, timeout=5, verify=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Servidor responde")
        else:
            print("   ❌ Error de conexión")
            return
    except:
        print("   ❌ No se puede conectar")
        return
    
    print(f"\n2. Probando WTSP_LOGINOUT...")
    
    # Request SOAP
    soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{config['program_id']}</programId>
      <programPassword>{config['program_password']}</programPassword>
      <op>TEST001</op>
      <password></password>
      <device>{config['device']}</device>
      <TSP>{config['tsp']}</TSP>
      <status>1</status>
    </WTSP_LOGINOUT>
  </soap:Body>
</soap:Envelope>'''
    
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://www.pegatroncorp.com/SFISWebService/WTSP_LOGINOUT'
    }
    
    try:
        start = time.time()
        response = requests.post(url, data=soap_request, headers=headers, timeout=10, verify=False)
        elapsed = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Tiempo: {elapsed:.2f}s")
        
        if response.status_code == 200:
            if 'Server did not recognize' not in response.text:
                print("   ✅ ¡FUNCIONA!")
                
                # Buscar resultado
                if '<WTSP_LOGINOUTResult>' in response.text:
                    start_idx = response.text.find('<WTSP_LOGINOUTResult>') + len('<WTSP_LOGINOUTResult>')
                    end_idx = response.text.find('</WTSP_LOGINOUTResult>', start_idx)
                    if end_idx > start_idx:
                        result = response.text[start_idx:end_idx]
                        print(f"\n   Resultado: {result}")
                        
                        # Parsear
                        params = {}
                        for item in result.split(';'):
                            if '=' in item:
                                key, val = item.split('=', 1)
                                params[key] = val
                        
                        if 'P_RET' in params:
                            if params['P_RET'] == '1':
                                print(f"   ✅ Login exitoso")
                                if 'P_NAME' in params:
                                    print(f"   Operador: {params['P_NAME']}")
                            else:
                                print(f"   ❌ Login fallido: {params.get('P_MSG', 'Sin mensaje')}")
                return True
            else:
                print("   ❌ Error SOAPAction")
        else:
            print("   ❌ Error HTTP")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    if test_rapido():
        print("\n" + "="*50)
        print("✅ Webservice funcionando correctamente")
        print("\nReemplaza tu login_simple.py con la versión corregida")
    else:
        print("\n" + "="*50)
        print("❌ Hay problemas con el webservice")
        print("\nVerifica:")
        print("1. La URL es correcta")
        print("2. Las credenciales son correctas")
        print("3. El namespace en el XML")
    
    input("\nPresiona Enter para salir...")