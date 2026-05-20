#!/usr/bin/env python
"""
ÚLTIMO INTENTO - Prueba TODAS las combinaciones posibles
"""

import requests
import itertools

def ultimo_intento():
    print("🔄 ÚLTIMO INTENTO - TODAS LAS COMBINACIONES POSIBLES")
    print("="*70)
    
    url = "http://ptx-sftsp-n1.sfis.pegatroncorp.com/SFISWebService_TXVADB0QA/SFISTSPWebService.asmx"
    
    # Valores posibles para cada campo (basado en sistemas SFIS típicos)
    valores = {
        'programId': ['TSP_MXT1', 'SFIS', 'MES', 'TSP', '1', '001', 'TSP001'],
        'programPassword': ['8d2cH_Y/ip', 'password', '123456', 'sfis123', 'mes123', '1'],
        'op': ['001', '002', '010', '100', '1', '2', '10', '1001'],
        'device': ['DEV001', '001', '1', 'STATION01', '01'],
        'tsp': ['TSP0011', '0011', '11', '1', '001', 'TSP001'],
        'status': ['1', '0']
    }
    
    print(f"\n📊 Combinaciones a probar:")
    total = 1
    for key, vals in valores.items():
        print(f"  {key}: {len(vals)} valores")
        total *= len(vals)
    
    print(f"  TOTAL: {total:,} combinaciones (¡demasiadas!)")
    
    print(f"\n🔍 Probando combinaciones MÁS PROBABLES primero...")
    
    # Combinaciones más probables
    combinaciones_probables = [
        # Común en Pegatron/SFIS
        {
            'programId': 'TSP_MXT1',
            'programPassword': '8d2cH_Y/ip',
            'op': '001',
            'device': '001',
            'tsp': '0011',
            'status': '1'
        },
        {
            'programId': 'TSP',
            'programPassword': 'TSP',
            'op': '001',
            'device': '001',
            'tsp': '001',
            'status': '1'
        },
        # Valores mínimos
        {
            'programId': '1',
            'programPassword': '1',
            'op': '1',
            'device': '1',
            'tsp': '1',
            'status': '1'
        },
        # Sin prefijos
        {
            'programId': 'MXT1',
            'programPassword': '8d2cH_Y/ip',
            'op': '001',
            'device': 'DEV001',
            'tsp': '0011',
            'status': '1'
        },
    ]
    
    for i, combo in enumerate(combinaciones_probables, 1):
        print(f"\n{i}. Probando combinación:")
        for key, value in combo.items():
            print(f"   {key}: {value}")
        
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
                            print(f"   ✅ ¡¡¡ÉXITO TOTAL!!!")
                            print(f"   🔥 USAR ESTA CONFIGURACIÓN")
                            
                            # Guardar solución
                            with open('SOLUCION_FINAL_ENCONTRADA.txt', 'w') as f:
                                f.write("# ¡SOLUCIÓN ENCONTRADA!\n")
                                f.write("# ====================\n\n")
                                f.write(f"URL: {url}\n\n")
                                f.write("CONFIGURACIÓN QUE FUNCIONA:\n")
                                for key, value in combo.items():
                                    f.write(f"{key} = '{value}'\n")
                                f.write(f"\nResultado: {result}\n")
                            
                            print(f"\n✓ Configuración guardada en: SOLUCION_FINAL_ENCONTRADA.txt")
                            return True
                        else:
                            if 'Input string was not' in result:
                                print(f"   ❌ Mismo error ParseInt32")
                            else:
                                print(f"   ❌ Otro error: {result[:80]}")
                else:
                    print(f"   ⚠ Respuesta inesperada")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "="*70)
    print("❌ NINGUNA COMBINACIÓN FUNCIONÓ")
    print("="*70)
    
    print(f"\n🚨 CONCLUSIÓN DEFINITIVA:")
    print(f"Los datos de configuración que tienes NO SON CORRECTOS")
    print(f"Necesitas obtener los datos REALES de tu sistema")
    
    print(f"\n📞 CONTACTA A:")
    print(f"1. Administrador del sistema SFIS")
    print(f"2. Supervisor de tu área")
    print(f"3. Departamento de TI/Systems")
    
    print(f"\n📋 PREGUNTA ESPECÍFICAMENTE:")
    print(f"• '¿Cuáles son los parámetros del webservice TSP_LOGINOUT?'")
    print(f"• 'Necesito programId, programPassword, device, TSP'")
    print(f"• '¿Cuál es mi ID de operador en el sistema?'")
    
    return False

if __name__ == "__main__":
    if ultimo_intento():
        print("\n" + "="*70)
        print("🎉 ¡PROBLEMA RESUELTO!")
        print("="*70)
        print("\nUsa la configuración encontrada en tu aplicación")
    else:
        print("\n" + "="*70)
        print("⚠ NECESITAS AYUDA DEL ADMINISTRADOR")
        print("="*70)
        print("\nEjecuta: python consultar_administrador.py")
        print("y muestra el resultado a tu administrador")
    
    input("\nPresiona Enter para salir...")
    