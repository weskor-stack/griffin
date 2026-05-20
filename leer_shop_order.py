"""
Script para leer el archivo generado por consulta_api.py
Autor: Asistente de programación
Fecha: 2026
Descripción: Lee el archivo shop_order_*_enabled.txt generado y extrae la información
a partir de la línea 4 (después del encabezado).
"""

import os
import glob
from datetime import datetime
from typing import List, Dict, Optional

def leer_archivo_generado(ruta_archivo: str = None, shop_order: str = None):
    """
    Lee el archivo generado y extrae los datos a partir de la línea 4
    
    Args:
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        dict: Diccionario con la información del archivo
    """
    
    # Determinar qué archivo leer
    if ruta_archivo:
        # Si se proporciona ruta directa
        if not os.path.exists(ruta_archivo):
            print(f"❌ Error: No se encontró el archivo {ruta_archivo}")
            return None
        archivo_a_leer = ruta_archivo
    elif shop_order:
        # Si se proporciona shop_order, buscar el archivo correspondiente
        nombre_archivo = f"shop_order_{shop_order}_enabled.txt"
        if os.path.exists(nombre_archivo):
            archivo_a_leer = nombre_archivo
        else:
            print(f"❌ Error: No se encontró el archivo {nombre_archivo}")
            return None
    else:
        # Si no se especifica nada, buscar el archivo más reciente
        archivos = glob.glob("shop_order_*_enabled.txt")
        if not archivos:
            print("❌ Error: No se encontró ningún archivo shop_order_*_enabled.txt")
            return None
        
        # Ordenar por fecha de modificación (el más reciente primero)
        archivos.sort(key=os.path.getmtime, reverse=True)
        archivo_a_leer = archivos[0]
        # print(f"📁 Usando el archivo más reciente: {archivo_a_leer}")
    
    try:
        # print(f"\n📖 Leyendo archivo: {archivo_a_leer}")
        # print("=" * 60)
        
        # Leer todo el contenido del archivo
        with open(archivo_a_leer, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
        
        # Verificar que el archivo tenga al menos 4 líneas
        if len(lineas) < 4:
            # print(f"⚠️ El archivo solo tiene {len(lineas)} líneas. No hay datos a partir de la línea 4.")
            return None
        
        # Extraer información de las primeras líneas
        total_registros = lineas[0].strip() if len(lineas) > 0 else "No disponible"
        linea_vacia = lineas[1].strip() if len(lineas) > 1 else "No disponible"
        encabezados = lineas[2].strip() if len(lineas) > 2 else "No disponible"
        
        # Extraer datos a partir de la línea 4 (índice 3)
        datos_linea4 = []
        for i in range(3, len(lineas)):
            if lineas[i].strip():  # Si la línea no está vacía
                datos_linea4.append(lineas[i].strip())
        
        # Procesar los datos estructurados
        registros = []
        for linea in datos_linea4:
            if '|' in linea:
                partes = linea.split('|')
                if len(partes) >= 3:
                    registro = {
                        'part_number': partes[0],
                        'serial_number': partes[1],
                        'process_name': partes[2]
                    }
                    registros.append(registro)
        
        # Crear diccionario con toda la información
        resultado = {
            'archivo': archivo_a_leer,
            'total_registros_segun_archivo': total_registros,
            'encabezados': encabezados,
            'cantidad_registros_encontrados': len(registros),
            'linea_4_en_adelante': datos_linea4,
            'registros_estructurados': registros,
            'primer_registro': registros[0] if registros else None,
            'ultimo_registro': registros[-1] if registros else None
        }
        
        # Mostrar información
        # print(f"\n📊 INFORMACIÓN DEL ARCHIVO:")
        # print(f"   📄 Archivo: {archivo_a_leer}")
        # print(f"   📅 Fecha modificación: {datetime.fromtimestamp(os.path.getmtime(archivo_a_leer)).strftime('%Y-%m-%d %H:%M:%S')}")
        # print(f"   📏 Tamaño: {os.path.getsize(archivo_a_leer)} bytes")
        # print(f"\n📋 CONTENIDO DEL ARCHIVO:")
        # print(f"   Línea 1: {total_registros}")
        # print(f"   Línea 2: {linea_vacia if linea_vacia else '(vacía)'}")
        # print(f"   Línea 3: {encabezados}")
        # print(f"\n📊 DATOS A PARTIR DE LA LÍNEA 4:")
        # print(f"   Total de registros encontrados: {len(registros)}")
        
        part_number = ""
        serial_number = ""
        process_name = ""

        if registros:
            # print(f"\n📝 PRIMEROS 5 REGISTROS (línea 4 en adelante):")
            for i, registro in enumerate(registros[:1], 1):
                part_number = registro['part_number']
                serial_number = registro['serial_number']
                process_name = registro['process_name']

                # print(f"   Registro {i}:")
                # print(f"      Part Number: {registro['part_number']}")
                # print(f"      Serial Number: {registro['serial_number']}")
                # print(f"      Process Name: {registro['process_name']}")
                # print(f"      Línea completa: {datos_linea4[i-1]}")
            
            # if len(registros) > 5:
            #     print(f"\n   ... y {len(registros) - 5} registros más")
            
            # Mostrar últimos registros
            # if len(registros) > 5:
            #     print(f"\n📝 ÚLTIMOS 3 REGISTROS:")
            #     for i, registro in enumerate(registros[-3:], len(registros)-2):
            #         print(f"   Registro {i}: {registro['serial_number']}")
        
        return part_number, serial_number, process_name
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None


def extraer_registros_desde_linea4(ruta_archivo: str = None, shop_order: str = None) -> Optional[List[Dict]]:
    """
    Función específica para extraer SOLO los registros desde la línea 4
    
    Args:
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        list: Lista de diccionarios con los registros (part_number, serial_number, process_name)
    """
    resultado = leer_archivo_generado(ruta_archivo, shop_order)
    if resultado:
        return resultado['registros_estructurados']
    return None


def buscar_por_serial_number(serial_number: str, ruta_archivo: str = None, shop_order: str = None) -> Optional[Dict]:
    """
    Busca un registro específico por serial_number
    
    Args:
        serial_number (str): Serial number a buscar
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        dict: Registro encontrado o None si no existe
    """
    registros = extraer_registros_desde_linea4(ruta_archivo, shop_order)
    
    if registros:
        for registro in registros:
            if registro['serial_number'] == serial_number:
                print(f"\n✅ Registro encontrado:")
                print(f"   Part Number: {registro['part_number']}")
                print(f"   Serial Number: {registro['serial_number']}")
                print(f"   Process Name: {registro['process_name']}")
                return registro
        print(f"\n❌ No se encontró el serial_number: {serial_number}")
    return None


def contar_registros_por_process(process_name: str, ruta_archivo: str = None, shop_order: str = None) -> int:
    """
    Cuenta cuántos registros tienen un process_name específico
    
    Args:
        process_name (str): Nombre del proceso a buscar
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        int: Cantidad de registros encontrados
    """
    registros = extraer_registros_desde_linea4(ruta_archivo, shop_order)
    
    if registros:
        contador = sum(1 for registro in registros if registro['process_name'] == process_name)
        print(f"\n📊 Proceso '{process_name}': {contador} registro(s)")
        return contador
    return 0


def listar_todos_serial_numbers(ruta_archivo: str = None, shop_order: str = None) -> List[str]:
    """
    Lista todos los serial_numbers del archivo
    
    Args:
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        list: Lista de serial_numbers
    """
    registros = extraer_registros_desde_linea4(ruta_archivo, shop_order)
    
    if registros:
        serials = [registro['serial_number'] for registro in registros]
        print(f"\n📋 Total de serial_numbers: {len(serials)}")
        print(f"   Primer serial: {serials[0] if serials else 'N/A'}")
        print(f"   Último serial: {serials[-1] if serials else 'N/A'}")
        return serials
    return []


def generar_resumen_archivo(ruta_archivo: str = None, shop_order: str = None) -> Dict:
    """
    Genera un resumen completo del archivo
    
    Args:
        ruta_archivo (str): Ruta directa al archivo (opcional)
        shop_order (str): Nombre del shop_order para buscar el archivo (opcional)
    
    Returns:
        dict: Diccionario con el resumen del archivo
    """
    resultado = leer_archivo_generado(ruta_archivo, shop_order)
    
    if resultado:
        registros = resultado['registros_estructurados']
        
        # Contar procesos únicos
        procesos = {}
        for registro in registros:
            process = registro['process_name']
            procesos[process] = procesos.get(process, 0) + 1
        
        # Contar part_numbers únicos
        part_numbers = {}
        for registro in registros:
            part = registro['part_number']
            part_numbers[part] = part_numbers.get(part, 0) + 1
        
        resumen = {
            'archivo': resultado['archivo'],
            'total_registros': len(registros),
            'procesos_encontrados': procesos,
            'part_numbers_encontrados': part_numbers,
            'primer_serial': registros[0]['serial_number'] if registros else None,
            'ultimo_serial': registros[-1]['serial_number'] if registros else None
        }
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL ARCHIVO")
        print("=" * 60)
        print(f"📄 Archivo: {resumen['archivo']}")
        print(f"📊 Total registros: {resumen['total_registros']}")
        print(f"\n📋 Procesos encontrados:")
        for process, cantidad in resumen['procesos_encontrados'].items():
            print(f"   • {process}: {cantidad} registro(s)")
        print(f"\n🔧 Part Numbers encontrados:")
        for part, cantidad in resumen['part_numbers_encontrados'].items():
            print(f"   • {part}: {cantidad} registro(s)")
        print(f"\n🔢 Serial Numbers:")
        print(f"   • Primero: {resumen['primer_serial']}")
        print(f"   • Último: {resumen['ultimo_serial']}")
        print("=" * 60)
        
        return resumen
    
    return None


# ==================== MENÚ PRINCIPAL ====================

def menu_lector():
    """
    Menú interactivo para el lector de archivos
    """
    while True:
        print("\n" + "=" * 60)
        print("📖 SISTEMA LECTOR DE ARCHIVOS GENERADOS")
        print("=" * 60)
        print("1. Leer archivo más reciente")
        print("2. Leer archivo por Shop Order")
        print("3. Leer archivo por ruta específica")
        print("4. Buscar por Serial Number")
        print("5. Contar registros por Process Name")
        print("6. Listar todos los Serial Numbers")
        print("7. Generar resumen completo")
        print("8. Salir")
        print("-" * 40)
        
        opcion = input("\n➤ Seleccione una opción (1-8): ").strip()
        
        if opcion == "1":
            # Leer archivo más reciente
            print("\n" + "=" * 60)
            leer_archivo_generado()
            
        elif opcion == "2":
            # Leer por Shop Order
            shop_order = input("\nIngrese el Shop Order: ").strip()
            if shop_order:
                leer_archivo_generado(shop_order=shop_order)
            else:
                print("❌ No ingresó un Shop Order")
                
        elif opcion == "3":
            # Leer por ruta específica
            ruta = input("\nIngrese la ruta del archivo: ").strip()
            if ruta:
                leer_archivo_generado(ruta_archivo=ruta)
            else:
                print("❌ No ingresó una ruta")
                
        elif opcion == "4":
            # Buscar por Serial Number
            serial = input("\nIngrese el Serial Number a buscar: ").strip()
            if serial:
                buscar_por_serial_number(serial)
            else:
                print("❌ No ingresó un Serial Number")
                
        elif opcion == "5":
            # Contar por Process Name
            process = input("\nIngrese el Process Name: ").strip()
            if process:
                contar_registros_por_process(process)
            else:
                print("❌ No ingresó un Process Name")
                
        elif opcion == "6":
            # Listar todos los Serial Numbers
            listar_todos_serial_numbers()
            
        elif opcion == "7":
            # Generar resumen completo
            generar_resumen_archivo()
            
        elif opcion == "8":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida")
        
        input("\n\nPresione Enter para continuar...")


# ==================== EJECUCIÓN PRINCIPAL ====================

# if __name__ == "__main__":
#     # print("=" * 60)
#     # print("📖 SISTEMA LECTOR DE ARCHIVOS GENERADOS")
#     # print("=" * 60)
#     # print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     # print("=" * 60)
    
#     # Mostrar archivos disponibles
#     archivos = glob.glob("shop_order_*_enabled.txt")
#     if archivos:
#         # print("\n📁 Archivos disponibles:")
#         for archivo in archivos:
#             tamaño = os.path.getsize(archivo)
#             fecha = datetime.fromtimestamp(os.path.getmtime(archivo)).strftime('%Y-%m-%d %H:%M:%S')
#             # print(f"   • {archivo} ({tamaño} bytes) - {fecha}")
#     else:
#         print("\n⚠️ No se encontraron archivos shop_order_*_enabled.txt")
#         print("   Ejecute primero consulta_api.py para generar un archivo")
    
#     # Ejecutar menú interactivo
#     # menu_lector()
#     datos = leer_archivo_generado()
#     print(datos)