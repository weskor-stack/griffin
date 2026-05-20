import requests
import json
import os
import glob
from datetime import datetime

def eliminar_todos_archivos_shop_order(directorio=""):
    """
    Elimina TODOS los archivos que coincidan con el patrón 'shop_order_*_enabled.txt'
    
    Args:
        directorio (str): Directorio donde buscar los archivos (opcional)
    
    Returns:
        int: Cantidad de archivos eliminados
    """
    # Construir el patrón de búsqueda
    if directorio:
        patron = os.path.join(directorio, "shop_order_*_enabled.txt")
    else:
        patron = "shop_order_*_enabled.txt"
    
    # Buscar todos los archivos que coincidan con el patrón
    archivos_encontrados = glob.glob(patron)
    
    if archivos_encontrados:
        print(f"\n🗑️ Eliminando archivos anteriores de shop_order...")
        for archivo in archivos_encontrados:
            try:
                os.remove(archivo)
                print(f"   ✓ Eliminado: {os.path.basename(archivo)}")
            except Exception as e:
                print(f"   ❌ Error al eliminar {archivo}: {e}")
        print(f"   Total eliminados: {len(archivos_encontrados)}")
        return len(archivos_encontrados)
    else:
        print(f"\n✓ No se encontraron archivos previos de shop_order para eliminar")
        return 0

def consultar_api_y_guardar(api_url, shop_order,directorio_destino=""):
    """
    Consulta una API, extrae part_number, serial_number y process_name,
    ordena los datos por serial_number de forma ascendente,
    y guarda los resultados en un archivo de texto.
    El nombre del archivo se genera dinámicamente usando el shop_order.
    Antes de crear el nuevo archivo, elimina TODOS los archivos shop_order_*_enabled.txt existentes.
    
    Args:
        api_url (str): URL de la API a consultar
        directorio_destino (str): Directorio donde guardar el archivo (opcional)
    
    Returns:
        tuple: (success, nombre_archivo, cantidad_registros)
    """
    url_concatenada = f"{api_url}{shop_order}"
    try:
        # 1. Consultar la API
        # print(f"📡 Consultando API: {url_concatenada}")
        response = requests.get(url_concatenada, timeout=30)
        response.raise_for_status()
        
        # 2. Parsear la respuesta JSON
        datos_api = response.json()
        
        # 3. Verificar que la respuesta tenga la estructura esperada
        if not datos_api.get('success', False):
            # print(f"❌ Error en la respuesta de la API: {datos_api.get('message', 'Error desconocido')}")
            return False, None, 0
        
        # 4. Verificar que hay datos
        if not datos_api.get('data') or len(datos_api['data']) == 0:
            # print("⚠️ No hay datos en la respuesta de la API")
            return False, None, 0
        
        # 5. Extraer el shop_order del primer elemento
        shop_order = datos_api['data'][0].get('shop_order', '')
        if not shop_order:
            # print("❌ No se encontró shop_order en la respuesta de la API")
            return False, None, 0
        
        # print(f"🏷️ Shop_order identificado: {shop_order}")
        
        # 6. Generar el nombre del archivo
        nombre_archivo = f"shop_order_{shop_order}_enabled.txt"
        
        # 7. Construir la ruta completa si se especificó un directorio
        if directorio_destino:
            # Asegurar que el directorio existe
            os.makedirs(directorio_destino, exist_ok=True)
            ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        else:
            ruta_completa = nombre_archivo
        
        # 8. Extraer y procesar los datos PRIMERO
        # print(f"\n📊 Procesando datos de la API...")
        datos_extraidos = []
        for item in datos_api.get('data', []):
            registro = {
                'part_number': item.get('part_number', ''),
                'serial_number': item.get('serial_number', ''),
                'process_name': item.get('process_name', '')
            }
            datos_extraidos.append(registro)
        
        # 9. ORDENAR LOS DATOS POR SERIAL_NUMBER DE FORMA ASCENDENTE
        # print(f"🔄 Ordenando datos por serial_number (ascendente)...")
        datos_extraidos.sort(key=lambda x: x['serial_number'])
        # print(f"✓ Datos ordenados correctamente")
        
        # 10. Contar registros
        total_registros = len(datos_extraidos)
        # print(f"📊 Se extrajeron {total_registros} registros")
        
        # 11. AHORA SÍ, eliminar TODOS los archivos existentes
        # print(f"\n🔍 Buscando archivos anteriores para eliminar...")
        
        # Construir el patrón de búsqueda
        if directorio_destino:
            patron = os.path.join(directorio_destino, "shop_order_*_enabled.txt")
        else:
            patron = "shop_order_*_enabled.txt"
        
        # Buscar todos los archivos que coincidan con el patrón
        archivos_encontrados = glob.glob(patron)
        
        if archivos_encontrados:
            # print(f"🗑️ Eliminando {len(archivos_encontrados)} archivo(s) anterior(es)...")
            for archivo in archivos_encontrados:
                try:
                    os.remove(archivo)
                    # print(f"   ✓ Eliminado: {os.path.basename(archivo)}")
                except Exception as e:
                    print(f"   ❌ Error al eliminar {archivo}: {e}")
        else:
            # print(f"✓ No se encontraron archivos previos de shop_order para eliminar")
            pass
        
        # 12. Crear el nuevo archivo
        # print(f"\n📝 Creando nuevo archivo: {nombre_archivo}")
        with open(ruta_completa, 'w', encoding='utf-8') as archivo:
            # Primera línea: cantidad de datos extraídos
            archivo.write(f"Total de registros extraídos: {total_registros}\n")
            
            # Segunda línea: vacía
            archivo.write("\n")
            
            # Tercera línea: encabezados
            archivo.write("part_number|serial_number|process_name\n")
            
            # Cuarta línea en adelante: datos (ya ordenados)
            for registro in datos_extraidos:
                linea = f"{registro['part_number']}|{registro['serial_number']}|{registro['process_name']}\n"
                archivo.write(linea)
        
        # Verificar que el archivo se creó correctamente
        if os.path.exists(ruta_completa):
            tamaño = os.path.getsize(ruta_completa)
            # print(f"\n✅ Nuevo archivo creado exitosamente!")
            # print(f"   📄 Nombre: {nombre_archivo}")
            # print(f"   📁 Ubicación: {os.path.dirname(ruta_completa) or '.'}")
            # print(f"   📏 Tamaño: {tamaño} bytes")
            # print(f"   📊 Registros: {total_registros}")
            
            # Mostrar las primeras líneas del archivo
            # print(f"\n📄 Vista previa del archivo:")
            # with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            #     lineas = archivo.readlines()
            #     for i, linea in enumerate(lineas[:5], 1):
            #         print(f"   Línea {i}: {linea.rstrip()}")
            #     if len(lineas) > 5:
            #         print(f"   ... y {len(lineas) - 5} líneas más")
        else:
            # print(f"\n❌ Error: No se pudo crear el archivo")
            return False, None, 0
        
        # Mostrar resumen del ordenamiento
        # if total_registros > 0:
        #     print(f"\n📋 Resumen del ordenamiento:")
        #     print(f"   Primer serial_number (menor): {datos_extraidos[0]['serial_number']}")
        #     if total_registros > 1:
        #         print(f"   Último serial_number (mayor): {datos_extraidos[-1]['serial_number']}")
        
        return True, nombre_archivo, total_registros
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout al consultar la API (30 segundos)")
        return False, None, 0
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión - No se pudo conectar al servidor")
        return False, None, 0
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consultar la API: {e}")
        return False, None, 0
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear la respuesta JSON: {e}")
        return False, None, 0
    except PermissionError as e:
        print(f"❌ Error de permisos al eliminar/crear el archivo: {e}")
        return False, None, 0
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, None, 0


def prueba_con_json_local(archivo_json):
    """
    Función de prueba que procesa el JSON desde un archivo local
    y genera el archivo con el shop_order correspondiente.
    Los datos se ordenan por serial_number de forma ascendente.
    Antes de crear el nuevo archivo, elimina TODOS los archivos shop_order_*_enabled.txt existentes.
    
    Args:
        archivo_json (str): Ruta al archivo JSON de ejemplo
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        print(f"📂 Leyendo archivo JSON: {archivo_json}")
        
        # Leer el JSON desde el archivo
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos_api = json.load(f)
        
        # Verificar estructura
        if not datos_api.get('data') or len(datos_api['data']) == 0:
            print("⚠️ No hay datos en el JSON")
            return False
        
        # Extraer shop_order
        shop_order = datos_api['data'][0].get('shop_order', '')
        if not shop_order:
            print("❌ No se encontró shop_order en el JSON")
            return False
        
        print(f"🏷️ Shop_order identificado: {shop_order}")
        
        # Generar nombre del archivo
        nombre_archivo = f"shop_order_{shop_order}_enabled.txt"
        
        # Extraer y procesar datos PRIMERO
        print(f"\n📊 Procesando datos del JSON...")
        datos_extraidos = []
        for item in datos_api.get('data', []):
            registro = {
                'part_number': item.get('part_number', ''),
                'serial_number': item.get('serial_number', ''),
                'process_name': item.get('process_name', '')
            }
            datos_extraidos.append(registro)
        
        # ORDENAR LOS DATOS POR SERIAL_NUMBER DE FORMA ASCENDENTE
        print(f"🔄 Ordenando datos por serial_number (ascendente)...")
        datos_extraidos.sort(key=lambda x: x['serial_number'])
        print(f"✓ Datos ordenados correctamente")
        
        total_registros = len(datos_extraidos)
        print(f"📊 Se extrajeron {total_registros} registros")
        
        # AHORA SÍ, eliminar TODOS los archivos existentes
        print(f"\n🔍 Buscando archivos anteriores para eliminar...")
        patron = "shop_order_*_enabled.txt"
        archivos_encontrados = glob.glob(patron)
        
        if archivos_encontrados:
            print(f"🗑️ Eliminando {len(archivos_encontrados)} archivo(s) anterior(es)...")
            for archivo in archivos_encontrados:
                try:
                    os.remove(archivo)
                    print(f"   ✓ Eliminado: {archivo}")
                except Exception as e:
                    print(f"   ❌ Error al eliminar {archivo}: {e}")
        else:
            print(f"✓ No se encontraron archivos previos de shop_order para eliminar")
        
        # Crear nuevo archivo
        print(f"\n📝 Creando nuevo archivo: {nombre_archivo}")
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Total de registros extraídos: {total_registros}\n")
            archivo.write("\n")
            archivo.write("part_number|serial_number|process_name\n")
            
            for registro in datos_extraidos:
                linea = f"{registro['part_number']}|{registro['serial_number']}|{registro['process_name']}\n"
                archivo.write(linea)
        
        # Verificar que el archivo se creó correctamente
        if os.path.exists(nombre_archivo):
            tamaño = os.path.getsize(nombre_archivo)
            print(f"\n✅ Nuevo archivo creado exitosamente!")
            print(f"   📄 Nombre: {nombre_archivo}")
            print(f"   📏 Tamaño: {tamaño} bytes")
            print(f"   📊 Registros: {total_registros}")
            print(f"   🏷️ Shop_order: {shop_order}")
            
            # Mostrar las primeras líneas del archivo generado
            print("\n📄 Contenido del archivo generado:")
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                lineas = archivo.readlines()
                for i, linea in enumerate(lineas[:10], 1):
                    print(f"   Línea {i}: {linea.rstrip()}")
                if len(lineas) > 10:
                    print(f"   ... y {len(lineas) - 10} líneas más")
        else:
            print(f"\n❌ Error: No se pudo crear el archivo")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {archivo_json}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear el JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def listar_archivos_existentes(directorio=""):
    """
    Lista todos los archivos shop_order_*_enabled.txt existentes
    
    Args:
        directorio (str): Directorio donde buscar los archivos (opcional)
    
    Returns:
        list: Lista de archivos encontrados
    """
    if directorio:
        patron = os.path.join(directorio, "shop_order_*_enabled.txt")
    else:
        patron = "shop_order_*_enabled.txt"
    
    archivos = glob.glob(patron)
    
    if archivos:
        # print(f"\n📁 Archivos shop_order encontrados:")
        for archivo in archivos:
            tamaño = os.path.getsize(archivo)
            # print(f"   - {os.path.basename(archivo)} ({tamaño} bytes)")
    else:
        print(f"\n✓ No hay archivos shop_order existentes")
    
    return archivos

# ==================== CONFIGURACIÓN PRINCIPAL ====================

# if __name__ == "__main__":
    # print("=" * 60)
    # print("🚀 SISTEMA DE EXTRACCIÓN DE DATOS DE API")
    # print("📊 CON ORDENAMIENTO ASCENDENTE POR SERIAL_NUMBER")
    # print("🗑️  ELIMINA TODOS LOS SHOP_ORDER ANTERIORES")
    # print("=" * 60)
    # print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # print("=" * 60)
    
    # Mostrar archivos existentes antes de comenzar
    # print("\n📋 Archivos existentes ANTES de la ejecución:")
    # listar_archivos_existentes()
    
    
    # ===== USO CON API REAL =====
    # print("-" * 40)
    
    # Ejemplo de uso con API real
    # URL_API = "http://localhost:8000/custom-api/p2480dc1/units/in-locations/by-pn-so?shortstation=FLPA&shoporderno="
    # SOP_ORDER = "SO0012"
    # print(f"📝 URL a consultar: {URL_API}{SOP_ORDER}")
    # print("\nEjecutando consulta a API real...")
    
    # Descomentar la siguiente línea para ejecutar con la API real
    #exito, nombre, cantidad = consultar_api_y_guardar(URL_API, SOP_ORDER)
    
    # if exito:
    #     print(f"\n✅ Proceso completado exitosamente!")
    #     print(f"   📄 Archivo generado: {nombre}")
    #     print(f"   📊 Registros procesados: {cantidad}")
    #     print("\n📋 Archivos existentes DESPUÉS de la ejecución:")
    #     # listar_archivos_existentes()
    # else:
    #     print(f"\n❌ Error en el proceso de consulta a la API")
    #     print("   (Esto es normal si el servidor no está ejecutándose)")
    
    # print("\n" + "=" * 60)
    # print("✅ FIN DEL PROCESO")
    # print("=" * 60)