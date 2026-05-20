#!/usr/bin/env python
"""
Diagnóstico específico del error de formato
"""

import requests
import re

def analizar_error():
    print("🔍 DIAGNÓSTICO DEL ERROR DE FORMATO")
    print("="*60)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    print(f"\nError recibido:")
    print("0 [LOGINOUT_Portal]-ErrorMsg:Input string was not in a correct format.")
    print("\n📌 Este error ocurre cuando:")
    print("1. Un campo numérico recibe texto vacío o inválido")
    print("2. El formato del número no es correcto")
    print("3. Hay caracteres invisibles en los datos")
    
    print("\n" + "="*60)
    print("PROBANDO DIFERENTES VALORES PARA 'status'")
    print("="*60)
    
    # Configuración base
    config = {
        'program_id': 'TSP_MXT1',
        'program_password': '8d2cH_Y/ip',
        'device': 'DEV001',
        'tsp': 'TSP0011'
    }
    
    # Diferentes valores para status
    valores_status = [
        ("1", "Enter (login)"),
        ("0", "Exit (logout)"),
        ("2", "Status 2 (¿otro valor?)"),
        (" 1", "Con espacio al inicio"),
        ("1 ", "Con espacio al final"),
        ("\n1", "Con nueva línea"),
        ("\t1", "Con tabulación"),
        ("01", "Con cero a la izquierda"),
    ]
    
    for status_val, descripcion in valores_status:
        print(f"\n🔍 Probando status='{repr(status_val)}' ({descripcion})")
        
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
      <status>{status_val}</status>
    </WTSP_LOGINOUT>
  </soap:Body>
</soap:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.pegatroncorp.com/SFISWebService/WTSP_LOGINOUT'
        }
        
        try:
            response = requests.post(url, data=soap_request, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                # Buscar resultado
                if '<WTSP_LOGINOUTResult>' in response.text:
                    start = response.text.find('<WTSP_LOGINOUTResult>') + len('<WTSP_LOGINOUTResult>')
                    end = response.text.find('</WTSP_LOGINOUTResult>', start)
                    
                    if end > start:
                        result = response.text[start:end]
                        
                        if 'P_RET=1' in result:
                            print(f"   ✅ ¡ÉXITO! Con status={status_val}")
                            print(f"   Resultado: {result}")
                            return status_val, result
                        elif 'Input string was not' in result:
                            print(f"   ❌ Mismo error de formato")
                        else:
                            print(f"   ⚠ Otro error: {result[:100]}")
                else:
                    print(f"   ⚠ Respuesta inesperada")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("PRUEBA CON OPERADORES DIFERENTES")
    print("="*60)
    
    # Probar con diferentes operadores
    operadores = [
        ("001", "Operador numérico"),
        ("OP001", "Operador alfanumérico"),
        ("TEST_OP", "Con guión bajo"),
        ("OPERATOR-01", "Con guión"),
        ("  OP001", "Con espacios"),
        ("", "Vacío"),
    ]
    
    for operador, desc in operadores:
        print(f"\n🔍 Probando operador='{operador}' ({desc})")
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{config['program_id']}</programId>
      <programPassword>{config['program_password']}</programPassword>
      <op>{operador}</op>
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
            response = requests.post(url, data=soap_request, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                if '<WTSP_LOGINOUTResult>' in response.text:
                    start = response.text.find('<WTSP_LOGINOUTResult>') + len('<WTSP_LOGINOUTResult>')
                    end = response.text.find('</WTSP_LOGINOUTResult>', start)
                    
                    if end > start:
                        result = response.text[start:end]
                        
                        if 'P_RET=1' in result:
                            print(f"   ✅ ¡ÉXITO! Con operador={operador}")
                            return "1", result
                        else:
                            print(f"   ❌ Error: {result[:100]}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None, None

def probar_valores_manuales():
    """Prueba con valores manuales"""
    print("\n" + "="*60)
    print("PRUEBA CON VALORES ESPECÍFICOS")
    print("="*60)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    # Posibles combinaciones
    pruebas = [
        {
            'desc': 'Valores básicos',
            'programId': 'TSP_MXT1',
            'programPassword': '8d2cH_Y/ip',
            'op': '001',
            'password': '',
            'device': 'DEV001',
            'tsp': 'TSP0011',
            'status': '1'
        },
        {
            'desc': 'Sin password',
            'programId': 'TSP_MXT1',
            'programPassword': '8d2cH_Y/ip',
            'op': '001',
            'password': None,  # Probando sin elemento
            'device': 'DEV001',
            'tsp': 'TSP0011',
            'status': '1'
        },
        {
            'desc': 'Status como número sin comillas',
            'programId': 'TSP_MXT1',
            'programPassword': '8d2cH_Y/ip',
            'op': '001',
            'password': '',
            'device': 'DEV001',
            'tsp': 'TSP0011',
            'status': 1  # Sin comillas
        }
    ]
    
    for prueba in pruebas:
        print(f"\n🔍 {prueba['desc']}")
        
        # Construir XML
        password_element = f"<password>{prueba['password']}</password>" if prueba['password'] is not None else ""
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{prueba['programId']}</programId>
      <programPassword>{prueba['programPassword']}</programPassword>
      <op>{prueba['op']}</op>
      {password_element}
      <device>{prueba['device']}</device>
      <TSP>{prueba['tsp']}</TSP>
      <status>{prueba['status']}</status>
    </WTSP_LOGINOUT>
  </soap:Body>
</soap:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.pegatroncorp.com/SFISWebService/WTSP_LOGINOUT'
        }
        
        try:
            response = requests.post(url, data=soap_request, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                if '<WTSP_LOGINOUTResult>' in response.text:
                    start = response.text.find('<WTSP_LOGINOUTResult>') + len('<WTSP_LOGINOUTResult>')
                    end = response.text.find('</WTSP_LOGINOUTResult>', start)
                    
                    if end > start:
                        result = response.text[start:end]
                        print(f"   Resultado: {result}")
                        
                        if 'P_RET=1' in result:
                            print(f"   ✅ ¡ÉXITO!")
                        else:
                            print(f"   ❌ Error")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DIAGNÓSTICO DEL ERROR 'Input string was not in a correct format'")
    print("="*60)
    
    # Analizar el error
    status_correcto, resultado = analizar_error()
    
    if status_correcto:
        print(f"\n🎉 SOLUCIÓN ENCONTRADA!")
        print(f"Usa status = '{status_correcto}'")
        print(f"\nResultado obtenido: {resultado}")
    else:
        print(f"\n⚠ No se encontró solución automática")
        print(f"\n📋 Prueba manualmente:")
        print(f"1. Verifica el valor de 'status' - debe ser un número válido")
        print(f"2. Asegúrate que no haya espacios extra")
        print(f"3. Prueba con diferentes operadores (001, 002, etc.)")
        print(f"4. Contacta al administrador para saber los valores correctos")
        
        # Probar valores manuales
        probar_valores_manuales()
    
    input("\nPresiona Enter para salir...")