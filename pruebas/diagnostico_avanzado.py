#!/usr/bin/env python
"""
DIAGNÓSTICO AVANZADO - Encontrar qué campo causa el error ParseInt32
"""

import requests
import re

def analizar_error_detallado():
    print("🔍 DIAGNÓSTICO AVANZADO - ERROR ParseInt32")
    print("="*70)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    print(f"\n📌 Stack trace del error:")
    print("at SFIS_LOGINOUT.TSP_LOGINOUT.LOGINOUT_Portal()")
    print("at System.Number.ParseInt32(String s)")
    print("\n💡 Esto significa que en el método LOGINOUT_Portal()")
    print("   se está intentando convertir un string a número (ParseInt32)")
    print("   pero el string no tiene formato numérico válido")
    
    print("\n" + "="*70)
    print("¿QUÉ CAMPOS PODRÍAN SER NUMÉRICOS?")
    print("="*70)
    
    print("\nSegún el WSDL, los campos son:")
    print("1. programId: string")
    print("2. programPassword: string")
    print("3. op: string (operador)")
    print("4. password: string")
    print("5. device: string")
    print("6. TSP: string ← ¿DEBERÍA SER NÚMERO?")
    print("7. status: int ← YA ES NÚMERO")
    
    print("\n⚠ El campo 'TSP' tiene valor 'TSP0011'")
    print("  Si el sistema espera un número, 'TSP0011' fallará en ParseInt32")
    
    # Leer WSDL para verificar tipos
    print("\n" + "="*70)
    print("VERIFICANDO WSDL PARA TIPOS DE DATOS")
    print("="*70)
    
    try:
        wsdl_response = requests.get(url + "?wsdl", timeout=10, verify=False)
        if wsdl_response.status_code == 200:
            wsdl_content = wsdl_response.text
            
            # Buscar definición de WTSP_LOGINOUT
            if 'WTSP_LOGINOUT' in wsdl_content:
                start = wsdl_content.find('name="WTSP_LOGINOUT"')
                end = wsdl_content.find('</s:complexType>', start)
                
                if end > start:
                    section = wsdl_content[start:end]
                    print("\nDefinición de WTSP_LOGINOUT en WSDL:")
                    print("-"*40)
                    
                    # Extraer cada campo
                    lines = section.split('\n')
                    for line in lines:
                        if 'name=' in line and 'type=' in line:
                            # Limpiar y mostrar
                            clean_line = line.strip().replace('s:', '')
                            print(f"  {clean_line}")
    except:
        pass
    
    print("\n" + "="*70)
    print("PRUEBA 1: ¿EL CAMPO 'TSP' DEBE SER NUMÉRICO?")
    print("="*70)
    
    config_base = {
        'program_id': 'TSP_MXT1',
        'program_password': '8d2cH_Y/ip',
        'device': 'DEV001',
        'tsp': '0011',  # Probando solo número
        'op': '001'
    }
    
    # Probar diferentes valores para TSP
    valores_tsp = [
        ("0011", "Solo número (sin TSP)"),
        ("1", "Número simple"),
        ("11", "Dos dígitos"),
        ("TSP0011", "Original con TSP"),
        ("", "Vacío"),
        ("TSP", "Solo texto"),
    ]
    
    for tsp_val, desc in valores_tsp:
        print(f"\n🔍 Probando TSP='{tsp_val}' ({desc})")
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{config_base['program_id']}</programId>
      <programPassword>{config_base['program_password']}</programPassword>
      <op>{config_base['op']}</op>
      <password></password>
      <device>{config_base['device']}</device>
      <TSP>{tsp_val}</TSP>
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
                            print(f"   ✅ ¡ÉXITO! TSP debe ser: '{tsp_val}'")
                            print(f"   Resultado: {result}")
                            return {'tsp': tsp_val, 'result': result}
                        elif 'Input string was not' in result:
                            print(f"   ❌ Mismo error ParseInt32")
                        else:
                            print(f"   ❌ Otro error: {result[:100]}")
                else:
                    print(f"   ⚠ Respuesta inesperada")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("PRUEBA 2: ¿EL CAMPO 'device' DEBE SER NUMÉRICO?")
    print("="*70)
    
    # Probando device como número
    valores_device = [
        ("001", "DEV001 como número"),
        ("1", "Solo 1"),
        ("DEV001", "Original"),
        ("", "Vacío"),
    ]
    
    for device_val, desc in valores_device:
        print(f"\n🔍 Probando device='{device_val}' ({desc})")
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{config_base['program_id']}</programId>
      <programPassword>{config_base['program_password']}</programPassword>
      <op>{config_base['op']}</op>
      <password></password>
      <device>{device_val}</device>
      <TSP>0011</TSP>
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
                            print(f"   ✅ ¡ÉXITO! Device debe ser: '{device_val}'")
                            return {'device': device_val, 'tsp': '0011', 'result': result}
                        elif 'Input string was not' in result:
                            print(f"   ❌ Mismo error ParseInt32")
                        else:
                            print(f"   ❌ Otro error: {result[:100]}")
                else:
                    print(f"   ⚠ Respuesta inesperada")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("PRUEBA 3: ¿LOS DATOS DE CONFIGURACIÓN SON INCORRECTOS?")
    print("="*70)
    
    print("\n💡 Posibilidad: TODOS los datos de configuración son incorrectos")
    print("   Necesitas los valores REALES de tu sistema SFIS")
    
    print("\n📋 Pregunta a tu administrador:")
    print("1. ¿Cuál es el programId REAL?")
    print("2. ¿Cuál es el programPassword REAL?")
    print("3. ¿El TSP es numérico o alfanumérico?")
    print("4. ¿El device es numérico o alfanumérico?")
    print("5. ¿Cuál es mi ID de operador REAL?")
    
    return None

def probar_con_datos_reales():
    """Prueba con datos que deberían ser reales"""
    print("\n" + "="*70)
    print("PRUEBA CON DATOS COMUNES EN SISTEMAS SFIS")
    print("="*70)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    # Combinaciones comunes en sistemas de fábrica
    combinaciones = [
        {
            'desc': 'Configuración típica 1',
            'programId': 'SFIS',
            'programPassword': 'sfis123',
            'op': '001',
            'device': '001',
            'tsp': '001',
            'status': '1'
        },
        {
            'desc': 'Configuración típica 2',
            'programId': 'MES',
            'programPassword': 'mes123',
            'op': '1001',
            'device': '001',
            'tsp': '001',
            'status': '1'
        },
        {
            'desc': 'Configuración con valores mínimos',
            'programId': '1',
            'programPassword': '1',
            'op': '1',
            'device': '1',
            'tsp': '1',
            'status': '1'
        },
    ]
    
    for combo in combinaciones:
        print(f"\n🔍 {combo['desc']}")
        
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <WTSP_LOGINOUT xmlns="http://www.pegatroncorp.com/SFISWebService/">
      <programId>{combo['programId']}</programId>
      <programPassword>{combo['programPassword']}</programPassword>
      <op>{combo['op']}</op>
      <password></password>
      <device>{combo['device']}</device>
      <TSP>{combo['tsp']}</TSP>
      <status>{combo['status']}</status>
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
                            print(f"   ✅ ¡FUNCIONA CON ESTOS DATOS!")
                            print(f"   Usa esta configuración:")
                            for key, value in combo.items():
                                if key != 'desc':
                                    print(f"   {key}: {value}")
                            return combo
                        else:
                            print(f"   ❌ Error: {result[:100]}")
                else:
                    print(f"   ⚠ Respuesta inesperada")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def generar_script_consultar_admin():
    """Genera un script para consultar al administrador"""
    script = '''#!/usr/bin/env python
"""
Script para mostrar al administrador qué información necesitas
"""

print("="*70)
print("INFORMACIÓN REQUERIDA PARA CONFIGURAR EL WEBSERVICE SFIS")
print("="*70)

print("\n📋 NECESITO ESTOS DATOS EXACTOS:")
print("\n1. DATOS DE CONFIGURACIÓN DEL WEBSERVICE:")
print("   • programId: ¿Cuál es el ID del programa?")
print("   • programPassword: ¿Cuál es la contraseña?")
print("   • device: ¿Cuál es el código del dispositivo? (¿numérico o texto?)")
print("   • TSP: ¿Cuál es el código TSP? (¿numérico o texto?)")

print("\n2. MI INFORMACIÓN PERSONAL:")
print("   • Mi ID de operador: ¿Cuál es mi número/código de operador?")
print("   • ¿Es numérico (001) o alfanumérico (OP001)?")

print("\n3. URL EXACTA:")
print("   • ¿Esta URL es correcta?")
print("   http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx")

print("\n" + "="*70)
print("INSTRUCCIONES PARA EL ADMINISTRADOR:")
print("="*70)

print("\n1. Verifique en la base de datos SFIS la tabla de configuración")
print("2. Busque los parámetros para 'WebService' o 'TSP'")
print("3. Consulte mi usuario en el sistema de operadores")
print("4. Verifique que el webservice esté activo y accesible")

print("\n" + "="*70)
input("Presiona Enter para mostrar esta información al administrador...")
'''

    with open('consultar_administrador.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script generado: consultar_administrador.py")
    print("  Ejecútalo y muéstraselo a tu administrador")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS DEL ERROR ParseInt32")
    print("="*70)
    
    print("\n🚨 PROBLEMA DETECTADO:")
    print("El método LOGINOUT_Portal() está intentando convertir")
    print("un string a número (ParseInt32) pero falla porque")
    print("el string no tiene formato numérico válido.")
    
    resultado = analizar_error_detallado()
    
    if not resultado:
        print("\n" + "="*70)
        print("NO SE ENCONTRÓ SOLUCIÓN AUTOMÁTICA")
        print("="*70)
        
        # Probar con datos comunes
        datos_reales = probar_con_datos_reales()
        
        if not datos_reales:
            print("\n❌ NINGUNA COMBINACIÓN FUNCIONÓ")
            print("\n📋 CONCLUSIÓN FINAL:")
            print("1. Los datos de configuración que tienes son INCORRECTOS")
            print("2. Necesitas los datos REALES de tu sistema SFIS")
            print("3. Debes consultar con el administrador del sistema")
            
            # Generar script para administrador
            generar_script_consultar_admin()
    
    print("\n" + "="*70)
    print("PASOS A SEGUIR:")
    print("="*70)
    print("\n1. Ejecuta: python consultar_administrador.py")
    print("2. Muestra la información a tu administrador")
    print("3. Pídele los datos EXACTOS de configuración")
    print("4. Con los datos correctos, volver a probar")
    
    input("\nPresiona Enter para salir...")