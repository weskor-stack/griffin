"""
Script para procesar registros del archivo shop_order
Autor: Asistente de programación
Fecha: 2026
Descripción: Toma el primer registro (línea 4) del archivo shop_order_*_enabled.txt
y lo mueve a un archivo llamado registros_procesados.txt, recorriendo los registros restantes
y actualizando el contador de registros extraídos.
"""

import os
import glob
import shutil
import re
from datetime import datetime
from typing import Tuple, Optional, List

def procesar_primer_registro(shop_order: str = None, ruta_archivo: str = None) -> Tuple[bool, str]:
    """
    Toma el primer registro (línea 4) del archivo shop_order y lo mueve a registros_procesados.txt
    Actualiza el contador de "Total de registros extraídos" en la primera línea.
    
    Args:
        shop_order (str): Nombre del shop_order (opcional)
        ruta_archivo (str): Ruta directa al archivo (opcional)
    
    Returns:
        tuple: (success, mensaje)
    """
    
    # Determinar qué archivo procesar
    if ruta_archivo:
        if not os.path.exists(ruta_archivo):
            return False, f"❌ Error: No se encontró el archivo {ruta_archivo}"
        archivo_origen = ruta_archivo
    elif shop_order:
        nombre_archivo = f"shop_order_{shop_order}_enabled.txt"
        if os.path.exists(nombre_archivo):
            archivo_origen = nombre_archivo
        else:
            return False, f"❌ Error: No se encontró el archivo {nombre_archivo}"
    else:
        # Buscar el archivo más reciente
        archivos = glob.glob("shop_order_*_enabled.txt")
        if not archivos:
            return False, "❌ Error: No se encontró ningún archivo shop_order_*_enabled.txt"
        archivos.sort(key=os.path.getmtime, reverse=True)
        archivo_origen = archivos[0]
    
    try:
        # print(f"\n📖 Procesando archivo: {archivo_origen}")
        # print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # print("=" * 60)
        
        # Leer el archivo completo
        with open(archivo_origen, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
        
        # Verificar que hay al menos 4 líneas (para tener datos)
        if len(lineas) < 4:
            return False, f"⚠️ El archivo solo tiene {len(lineas)} líneas. No hay registros para procesar."
        
        # Obtener la primera línea (Total de registros extraídos)
        primera_linea = lineas[0].strip()
        
        # Extraer el número actual de registros
        import re
        match = re.search(r'(\d+)', primera_linea)
        if not match:
            return False, f"⚠️ No se pudo extraer el número de registros de: {primera_linea}"
        
        total_registros_actual = int(match.group(1))
        # print(f"\n📊 Total de registros actual: {total_registros_actual}")
        
        # Obtener las primeras 3 líneas (encabezado)
        encabezado = lineas[:3]
        
        # Obtener los registros (desde línea 4 en adelante)
        registros = lineas[3:]
        
        # Verificar que hay al menos un registro
        if not registros or not registros[0].strip():
            return False, "⚠️ No hay registros para procesar en el archivo."
        
        # Tomar el primer registro (línea 4 original)
        primer_registro = registros[0].strip()
        
        # Los registros restantes (desde el segundo registro en adelante)
        registros_restantes = registros[1:] if len(registros) > 1 else []
        
        # Calcular nuevo total de registros
        nuevo_total_registros = total_registros_actual - 1
        
        # print(f"\n📋 PRIMER REGISTRO (será movido):")
        # print(f"   {primer_registro}")
        # print(f"\n📊 Actualizando contador:")
        # print(f"   Total anterior: {total_registros_actual}")
        # print(f"   Nuevo total: {nuevo_total_registros}")
        
        # Actualizar la primera línea con el nuevo contador
        nueva_primera_linea = f"Total de registros extraídos: {nuevo_total_registros}\n"
        
        # Crear/actualizar el archivo registros_procesados.txt
        archivo_procesados = "registros_procesados.txt"
        
        # Verificar si el archivo ya existe
        if os.path.exists(archivo_procesados):
            # Si existe, agregar el nuevo registro al final
            with open(archivo_procesados, 'a', encoding='utf-8') as proc:
                # Agregar timestamp y el registro
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                proc.write(f"[{timestamp}] {primer_registro}\n")
            print(f"\n✅ Registro agregado a {archivo_procesados} (modo append)")
        else:
            # Si no existe, crear nuevo archivo con encabezado
            with open(archivo_procesados, 'w', encoding='utf-8') as proc:
                proc.write("=" * 80 + "\n")
                proc.write("REGISTROS PROCESADOS\n")
                # proc.write(f"Archivo de origen: {archivo_origen}\n")
                proc.write(f"Fecha de creación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                proc.write("=" * 80 + "\n\n")
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                proc.write(f"[{timestamp}] {primer_registro}\n")
            # print(f"\n✅ Nuevo archivo creado: {archivo_procesados}")
        
        # Reconstruir el archivo original con el contador actualizado
        with open(archivo_origen, 'w', encoding='utf-8') as archivo:
            # Escribir la primera línea actualizada
            archivo.write(nueva_primera_linea)
            
            # Escribir la segunda línea (vacía) - mantener igual
            archivo.write(encabezado[1] if len(encabezado) > 1 else "\n")
            
            # Escribir la tercera línea (encabezados)
            archivo.write(encabezado[2] if len(encabezado) > 2 else "part_number|serial_number|process_name\n")
            
            # Escribir los registros restantes
            if registros_restantes:
                archivo.writelines(registros_restantes)
                # print(f"\n📝 Archivo original actualizado:")
                # print(f"   Registros restantes: {len(registros_restantes)}")
                # print(f"   Nuevo total registros: {nuevo_total_registros}")
            else:
                # print(f"\n📝 Archivo original actualizado:")
                # print(f"   No quedan registros en el archivo original")
                # print(f"   Nuevo total registros: {nuevo_total_registros}")
                pass
        
        # Mostrar resumen
        # print(f"\n📊 RESUMEN:")
        # print(f"   • Registro movido: {primer_registro[:50]}...")
        # print(f"   • Archivo origen: {archivo_origen}")
        # print(f"   • Registros restantes: {len(registros_restantes)}")
        # print(f"   • Nuevo total registros: {nuevo_total_registros}")
        # print(f"   • Archivo destino: {archivo_procesados}")
        
        return True, f"✅ Expected value: Record processed successfully . There are {len(registros_restantes)} remaining (Total: {nuevo_total_registros})."
        
    except Exception as e:
        return False, f"❌ Error processing the file: {e}"


def verificar_archivos():
    """
    Verifica el estado de los archivos y muestra información
    """
    # print("\n" + "=" * 60)
    # print("📁 VERIFICACIÓN DE ARCHIVOS")
    # print("=" * 60)
    
    # Verificar archivos shop_order
    archivos_shop = glob.glob("shop_order_*_enabled.txt")
    if archivos_shop:
        # print(f"\n📄 Archivos shop_order encontrados:")
        for archivo in archivos_shop:
            tamaño = os.path.getsize(archivo)
            fecha = datetime.fromtimestamp(os.path.getmtime(archivo)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Leer el archivo para mostrar información
            with open(archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                if lineas:
                    # Extraer total de registros de la primera línea
                    primera_linea = lineas[0].strip()
                    match = re.search(r'(\d+)', primera_linea)
                    total_registros = int(match.group(1)) if match else 0
                    
                    # Contar registros reales (líneas después de la línea 3)
                    registros_reales = max(0, len(lineas) - 3)
                    
                    # print(f"   • {archivo}")
                    # print(f"     - Tamaño: {tamaño} bytes")
                    # print(f"     - Fecha: {fecha}")
                    # print(f"     - Total según línea 1: {total_registros}")
                    # print(f"     - Registros reales: {registros_reales}")
                    if total_registros != registros_reales:
                        print(f"     - ⚠️ Diferencia detectada!")
                    if registros_reales == 0:
                        print("EMPTY_DATA")
                        return "EMPTY_DATA"
                    
                    return registros_reales
    else:
        print(f"\n⚠️ No se encontraron archivos shop_order_*_enabled.txt")
        return "EMPTY_FILE"
    
    # Verificar archivo de registros procesados
    archivo_proc = "registros_procesados.txt"
    if os.path.exists(archivo_proc):
        tamaño = os.path.getsize(archivo_proc)
        fecha = datetime.fromtimestamp(os.path.getmtime(archivo_proc)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Contar registros procesados
        with open(archivo_proc, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            registros_procesados = sum(1 for linea in lineas if linea.startswith('['))
        
        print(f"\n📋 Archivo registros_procesados.txt:")
        print(f"   • Tamaño: {tamaño} bytes")
        print(f"   • Fecha: {fecha}")
        print(f"   • Registros procesados: {registros_procesados}")
    else:
        print(f"\n📋 Archivo registros_procesados.txt: No existe aún")
    
    print("=" * 60)


def procesar_todos_los_registros():
    """
    Procesa todos los registros del archivo hasta que quede vacío
    """
    print("\n" + "=" * 60)
    print("🔄 PROCESANDO TODOS LOS REGISTROS")
    print("=" * 60)
    
    contador = 0
    while True:
        resultado, mensaje = procesar_primer_registro()
        contador += 1
        
        if not resultado:
            print(f"\n{mensaje}")
            break
        
        print(f"\n✅ Registro {contador} procesado")
        
        # Verificar si quedan registros
        archivos = glob.glob("shop_order_*_enabled.txt")
        if archivos:
            with open(archivos[0], 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                if len(lineas) <= 3:
                    print(f"\n📊 No quedan más registros por procesar")
                    break
        
        # Preguntar si continuar
        if contador < 10:  # Si son pocos, continuar automáticamente
            continuar = input("\n¿Desea procesar el siguiente registro? (s/n): ").strip().lower()
            if continuar != 's':
                break
    
    print(f"\n📊 Total de registros procesados en esta sesión: {contador}")


def mostrar_registros_procesados():
    """
    Muestra el contenido del archivo registros_procesados.txt
    """
    archivo_proc = "registros_procesados.txt"
    
    if not os.path.exists(archivo_proc):
        print(f"\n⚠️ El archivo {archivo_proc} no existe aún")
        return
    
    print("\n" + "=" * 60)
    print("📋 REGISTROS PROCESADOS")
    print("=" * 60)
    
    with open(archivo_proc, 'r', encoding='utf-8') as f:
        contenido = f.read()
        print(contenido)
    
    print("=" * 60)


def reiniciar_contador(shop_order: str = None, nuevo_total: int = None):
    """
    Función para reiniciar o corregir manualmente el contador
    
    Args:
        shop_order (str): Nombre del shop_order (opcional)
        nuevo_total (int): Nuevo total de registros (opcional)
    
    Returns:
        bool: True si se actualizó correctamente
    """
    if shop_order:
        archivo = f"shop_order_{shop_order}_enabled.txt"
    else:
        archivos = glob.glob("shop_order_*_enabled.txt")
        if not archivos:
            print("❌ No se encontró archivo")
            return False
        archivo = archivos[0]
    
    if not os.path.exists(archivo):
        print(f"❌ No existe el archivo {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    # Contar registros reales
    registros_reales = max(0, len(lineas) - 3)
    
    if nuevo_total is None:
        nuevo_total = registros_reales
    
    # Actualizar primera línea
    nueva_primera_linea = f"Total de registros extraídos: {nuevo_total}\n"
    lineas[0] = nueva_primera_linea
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.writelines(lineas)
    
    print(f"✅ Contador actualizado: {nuevo_total}")
    return True


# def menu_principal():
#     """
#     Menú interactivo para el procesamiento de registros
#     """
#     while True:
#         print("\n" + "=" * 60)
#         print("🔄 SISTEMA DE PROCESAMIENTO DE REGISTROS")
#         print("=" * 60)
#         print("1. Procesar primer registro")
#         print("2. Procesar todos los registros")
#         print("3. Verificar estado de archivos")
#         print("4. Ver registros procesados")
#         print("5. Reiniciar contador manualmente")
#         print("6. Salir")
#         print("-" * 40)
        
#         opcion = input("\n➤ Seleccione una opción (1-6): ").strip()
        
#         if opcion == "1":
#             # Procesar primer registro
#             resultado, mensaje = procesar_primer_registro()
#             print(f"\n{mensaje}")
            
#         elif opcion == "2":
#             # Procesar todos los registros
#             confirmar = input("\n⚠️ Esto procesará TODOS los registros. ¿Desea continuar? (s/n): ").strip().lower()
#             if confirmar == 's':
#                 procesar_todos_los_registros()
            
#         elif opcion == "3":
#             # Verificar archivos
#             verificar_archivos()
            
#         elif opcion == "4":
#             # Ver registros procesados
#             mostrar_registros_procesados()
            
#         elif opcion == "5":
#             # Reiniciar contador
#             confirmar = input("\n⚠️ ¿Desea reiniciar el contador según los registros reales? (s/n): ").strip().lower()
#             if confirmar == 's':
#                 reiniciar_contador()
            
#         elif opcion == "6":
#             print("\n👋 ¡Hasta luego!")
#             break
#         else:
#             print("\n❌ Opción no válida")
        
#         input("\n\nPresione Enter para continuar...")


# ==================== FUNCIONES ADICIONALES ÚTILES ====================

def obtener_primer_registro_sin_mover(shop_order: str = None) -> Optional[str]:
    """
    Obtiene el primer registro sin moverlo (solo lectura)
    
    Args:
        shop_order (str): Nombre del shop_order (opcional)
    
    Returns:
        str: Primer registro o None si no hay
    """
    if shop_order:
        archivo = f"shop_order_{shop_order}_enabled.txt"
    else:
        archivos = glob.glob("shop_order_*_enabled.txt")
        if not archivos:
            return None
        archivos.sort(key=os.path.getmtime, reverse=True)
        archivo = archivos[0]
    
    if not os.path.exists(archivo):
        return None
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    if len(lineas) >= 4:
        return lineas[3].strip()
    return None


def contar_registros_pendientes(shop_order: str = None) -> int:
    """
    Cuenta cuántos registros quedan por procesar
    
    Args:
        shop_order (str): Nombre del shop_order (opcional)
    
    Returns:
        int: Número de registros pendientes
    """
    if shop_order:
        archivo = f"shop_order_{shop_order}_enabled.txt"
    else:
        archivos = glob.glob("shop_order_*_enabled.txt")
        if not archivos:
            return 0
        archivos.sort(key=os.path.getmtime, reverse=True)
        archivo = archivos[0]
    
    if not os.path.exists(archivo):
        return 0
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    # Intentar obtener el total de la primera línea
    if lineas:
        match = re.search(r'(\d+)', lineas[0])
        if match:
            return int(match.group(1))
    
    return max(0, len(lineas) - 3)


# ==================== EJECUCIÓN PRINCIPAL ====================

# if __name__ == "__main__":    
    # Mostrar estado inicial
    # verificar_archivos()
    
    # Ejecutar menú
    # menu_principal()
    # resultado, mensaje = procesar_primer_registro()
    # print(f"\n{mensaje}")
    # procesar_primer_registro()