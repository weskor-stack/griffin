__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

# Module Imports
from datetime import datetime
import mariadb
import sys
from tkinter import  messagebox 
# import history_xlsx

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="u8ch9Xn4Ol8woLw3E2A6",
        host="127.0.0.1",
        port=3306,
        database="data_tracking_qwert")

except mariadb.Error as e:
    # print(f"Error connecting to MariaDB Platform: {e}")
    messagebox.showerror(title="Connection", message=f"Check database connection", )
    sys.exit(1)

# Get Cursor
# cur = conn.cursor()
def obtener_datos_fila_unica():
    try:
        cursor = conn.cursor()
        # Aquí pedimos explícitamente los 6 datos:
        cursor.execute("SELECT machine_id, process_name, operator, station, product, shop_order FROM configurador LIMIT 1")
        return cursor.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        return None
    
# def insert_simple(machine, process, operator, station):

#URLs
def get_station():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT station 
            FROM configurador 
            ORDER BY configurador_id DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None
    except mariadb.Error as e:
        print(f"Error en get_station: {e}")
        return None
    
def get_connection():
    return mariadb.connect(
        user="root",
        password="u8ch9Xn4Ol8woLw3E2A6",
        host="127.0.0.1",
        port=3306,
        database="data_tracking_qwert"
    )

def select_api_configs():
    """
    Lee de url_data. 
    Columnas: [0]url_data_id [1]tc_id [2]name [3]url_data [4]user_id [5]create_registration
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url_data_id, tc_id, name, url_data FROM url_data ORDER BY url_data_id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    print(f"Registros DB: {rows}")  # debug — quítalo cuando funcione
    return rows

def update_api_by_name(nombre, url):
    """Actualiza la URL de un registro por su nombre."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE url_data SET url_data = ? WHERE name = ?",
        (url, nombre)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
# def insert_attribute(name, unit, upper, lower, value, create_registration):
#     cursor = conn.cursor()

#     sql = """
#         INSERT INTO configurador
#         (machine_id, process_name, operator, station, create_registration)
#         VALUES (?, ?, ?, ?, ?)
#     """
#     cursor.execute(sql, (machine, process, operator, station, datetime.now()))
#     conn.commit()
#     cursor.close()

def select_distinct(column):
    cursor = conn.cursor()

    query = f"""SELECT DISTINCT {column} FROM configurador
    WHERE  {column} IS NOT NULL AND {column} != ''"""
    cursor.execute(query)
    data = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return data

    query = f"""SELECT DISTINCT {column} FROM configurador""" 

def insert_configurador(machine, process, operator, station, product, shop_order):
    """Actualiza la fila del usuario 9999 con TODOS los campos"""
    try:
        cursor = conn.cursor()
        # 1. Intentamos actualizar la fila existente
        query_update = """
            UPDATE configurador 
            SET machine_id = ?, process_name = ?, operator = ?, station = ?, product = ?, shop_order = ?
            WHERE user_id = 9999
        """
        cursor.execute(query_update, (machine, process, operator, station, product, shop_order))
        
        # 2. Si no existe (rowcount == 0), la creamos
        if cursor.rowcount == 0:
            query_insert = """
                INSERT INTO configurador (user_id, machine_id, process_name, operator, station, product, shop_order)
                VALUES (9999, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_insert, (machine, process, operator, station, product, shop_order))
            
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar: {e}")
        raise e
    
def select_configurador():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT configurador_id, machine_id, process_name, operator, station
        FROM configurador
        ORDER BY configurador_id DESC
        LIMIT 1
    """)

    data = cursor.fetchone()
    cursor.close()
    return data

def obtener_url_api():
    """Busca la URL en la tabla url_data"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT url_data FROM url_data LIMIT 1")
        res = cursor.fetchone()
        cursor.close()
        return res[0] if res else None
    except:
        return None
    
def insert_attribute(name, unit, upper, lower, value, create_registration):
    cursor = conn.cursor()
    sql = """
        INSERT INTO attribute 
        (name, unit, upper_limit, lower_limit, value_expected, create_registration)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(sql, (name, unit, upper, lower, value, create_registration))
    conn.commit()

    attribute_id = cursor.lastrowid
    cursor.close()

    return attribute_id

def insert_program(name, description, create_registration):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO programs (name, description, create_registration) VALUES (%s, %s, %s)",
        (name, description, create_registration)
    )
    conn.commit()
    program_id = cursor.lastrowid
    cursor.close()
    return program_id

def update_program(program_id, name, description):
    cursor = conn.cursor()
    sql = """
        UPDATE programs
        SET name = ?, description = ?
        WHERE programs_id = ?
    """
    cursor.execute(sql, (name, description, program_id))
    conn.commit()
    cursor.close()  

def delete_program(program_id):
    cursor = conn.cursor()
    sql = "DELETE FROM programs WHERE programs_id = ?"
    cursor.execute(sql, (program_id,))
    conn.commit()
    cursor.close()

def select_programs():
    cursor = conn.cursor()
    cursor.execute("SELECT programs_id, name, description FROM programs")
    data = cursor.fetchall()
    cursor.close()
    return data

#ATTRIBUTES

def select_attributes():
    cursor = conn.cursor()
    cursor.execute("SELECT attribute_id, name, unit, upper_limit, lower_limit, value_expected, user_id, time, create_registration FROM attribute")
    data = cursor.fetchall()
    cursor.close()
    return data

def insert_attribute(name, unit, upper_limit, lower_limit, value_expected, time, create_registration):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attribute (name, unit, upper_limit, lower_limit, value_expected, time, create_registration) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, unit, upper_limit, lower_limit, value_expected, time, create_registration)
    )
    conn.commit()
    attribute_id = cursor.lastrowid
    cursor.close()
    return attribute_id

def update_attribute(attribute_id, name, unit, upper_limit, lower_limit,time, value_expected):
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE attribute SET name=%s, unit=%s, upper_limit=%s, lower_limit=%s, time=%s, value_expected=%s WHERE attribute_id=%s",
        (name, unit, upper_limit, lower_limit, time, value_expected, attribute_id)
    )

    conn.commit()
    cursor.close()
def delete_attribute(attribute_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attribute WHERE attribute_id=%s", (attribute_id,))
    conn.commit()
    cursor.close()
    

def select_type_test():
    cursor = conn.cursor()
    cursor.execute("SELECT test_type_id, name, status_id FROM test_type")
    data = cursor.fetchall()
    cursor.close()
    return data

def insert_type_test(name, status_id, user_id, create_registration):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_type (name, status_id, user_id, create_registration) VALUES (%s, %s, %s, %s)",
        (name, status_id, user_id, create_registration)
    )
    conn.commit()
    test_type_id = cursor.lastrowid
    cursor.close()
    return test_type_id

def update_type_test(test_type_id, name, status_id):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE test_type SET name=%s, status_id=%s WHERE test_type_id=%s",
        (name, status_id, test_type_id)
    )
    conn.commit()
    cursor.close()
    
def server_connection():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT server_port, server_ip_address FROM server")
            servers = cursor.fetchall()
        return servers
    except Exception as e:
        # print(f"[ERROR] server_connection(): {e}")
        return []
    
def new_model(model):
    project = []
    models = []

    with conn.cursor() as cur:
        cur.execute("SELECT project_id, pro_key, pro_name FROM project WHERE status_id = 1")
        project = cur.fetchall()
    
    if not project:
        raise ValueError("No active project found")

    with conn.cursor() as cur:
        cur.execute("UPDATE model SET status_id = %s WHERE status_id = %s", (2, 1))
        conn.commit()

        cur.execute("INSERT INTO model (name, project_id, status_id) VALUES (%s, %s, %s)", (model, project[0][0], 1))
        conn.commit()

        cur.execute("SELECT model_id, name, project_id FROM model WHERE status_id = 1 AND project_id = %s", (project[0][0],))
        models = cur.fetchall()

    if not models:
        raise ValueError("No models found after insertion")
    return models[0]  

def model():
    try:
        cursor_proj = conn.cursor()
        cursor_proj.execute("SELECT project_id, pro_key, pro_name FROM project WHERE status_id = 1")
        project = cursor_proj.fetchone()
        cursor_proj.close()

        if not project:
            # print("No hay proyecto activo.")
            return None, None, None
        
        project_id = project[0]
        cursor_model = conn.cursor()
        cursor_model.execute(
            "SELECT model_id, name, project_id FROM model WHERE status_id = 1 AND project_id = ?",
            (project_id,)
        )
        model = cursor_model.fetchone()
        cursor_model.close()

        if not model:
            new_model("Model-T1")  
            cursor_model2 = conn.cursor()
            cursor_model2.execute(
                "SELECT model_id, name, project_id FROM model WHERE status_id = 1 AND project_id = ?",
                (project_id,)
            )
            model = cursor_model2.fetchone()
            cursor_model2.close()

        if not model:
            # print("No se pudo obtener o crear un modelo.")
            return project, None, None

        cursor_station = conn.cursor()
        cursor_station.execute("SELECT station_name FROM station WHERE status_id = 1")
        station = cursor_station.fetchone()
        cursor_station.close()

        if not station:
            # print("No hay estaciones activas.")
            return project, model, None

        return project, model, station

    except mariadb.Error as e:
        return None, None, None
    
def piece_store(numPiece):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT project_id, pro_key, pro_name FROM project WHERE status_id = 1 LIMIT 1")
        project = cursor.fetchone()
        cursor.close()

        if not project:
            return "FAILED"

        cursor = conn.cursor()
        cursor.execute("SELECT model_id, name FROM model WHERE status_id = 1 AND project_id = ?", (project[0],))
        model = cursor.fetchone()
        cursor.close()

        if not model:
            return "FAILED"

        # Desactivar piezas anteriores
        # cursor = conn.cursor()
        # cursor.execute("UPDATE part SET status_id = ? WHERE status_id = ?", (2, 1))
        # conn.commit()
        # cursor.close()

        # Insertar nueva pieza
        cursor = conn.cursor()
        cursor.execute("INSERT INTO part (part_number, model_id, status_id) VALUES (?, ?, ?)", (numPiece, model[0], 3))
        conn.commit()
        cursor.close()

        # Exportar a archivo
        # history_xlsx.history_file_xlsx([numPiece, model[1]])

        return "PASSED"

    except mariadb.Error as e:
        # print(f"[DB ERROR] {e}")
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] {e}")
        return "FAILED"

def select_model(model):
    with conn.cursor() as cur:
        cur.execute("SELECT model_id, name, project_id FROM model WHERE name = %s", (model,))
        search_models = cur.fetchall()

        if not search_models:
            return "0"

        cur.execute("SELECT project_id FROM project WHERE status_id = 1")
        project = cur.fetchone()
        if not project:
            return "0"

        cur.execute("UPDATE model SET status_id = %s WHERE status_id = %s", (2, 1))
        conn.commit()

        cur.execute("UPDATE model SET status_id = %s WHERE status_id = %s AND name = %s", (1, 2, model))
        conn.commit()

       
        cur.execute("SELECT model_id, name, project_id FROM model WHERE status_id = 1 AND project_id = %s", (project[0],))
        models = cur.fetchall()

        if not models:
            return "0"
        
        return models[0]

def stations():
    with conn.cursor() as cur:
        cur.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS Name 
                       FROM station 
                       INNER JOIN data_tracking_qwert.type_station ON type_station.ts_id = station.ts_id
                       WHERE status_id = 1''')
        result = cur.fetchone()  #
    return result

def parameters_pressfit(element, name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    tasktimestamp = datetime.now(timezone.utc).astimezone()
    last_digit = str(tasktimestamp).split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False) + " " + last_digit[3]

    with conn.cursor() as cur:
        cur.execute(
            "SELECT pressfit_measurement_id, name FROM data_tracking_qwert.pressfit_measurement WHERE `key` = %s",
            (element[0],)
        )
        measurement = cur.fetchone()
        if not measurement:
            return "Measurement key not found"

        cur.execute('''
            SELECT station_id, station_key, station_name 
            FROM station
            INNER JOIN data_tracking_qwert.type_station ON type_station.ts_id = station.ts_id
            WHERE status_id = 1
            LIMIT 1
        ''')
        station = cur.fetchone()
        if not station:
            return "No active station found"

        cur.execute(
            "SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(name_piece,)
        )
        part = cur.fetchone()
        if not part:
            return "FAILED"

        value = element[1]
        low_limit = element[2]
        high_limit = element[3]
        if value == "" and low_limit == "" and high_limit == "":
            return "GENERAL_ERROR"
        data_type = element[4]
        units = element[5]
        result = element[6]
        compoperator = evaluation.evaluation(element[1:4])
        test_time = timer
        metadata = element[7]
        description = f"{station[2]} {measurement[1]} Test"
        dwell_time = element[8]

        sql = '''
            INSERT INTO parameters_pressfit
            (value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, dwell_time, pressfit_measurement_id, station_id, part_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        vals = (value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, dwell_time, measurement[0], station[0], part[0])

        try:
            cur.execute(sql, vals)
            conn.commit()
        except Exception as e:
            print("Error inserting pressfit parameter:", e)
            return "FAILED"

    # num_piece = ["", "", value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, dwell_time]
    # history_xlsx.history_file_xlsx(num_piece)
    return "PASSED"

def parameters_screwing(element, name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    try:
        # Timestamp actual
        now = datetime.now(timezone.utc).astimezone()
        test_time = rfc3339.rfc3339(now, utc=True, use_system_timezone=False)

        cursor = conn.cursor()
        cursor.execute("""
            SELECT screwing_measurement_id, name 
            FROM screwing_measurement 
            WHERE screwing_measurement.key = ?
        """, (element[0],))
        measurement = cursor.fetchone()
        cursor.close()

        if not measurement:
            raise ValueError("Measurement no encontrado para key: " + element[0])

        cursor = conn.cursor()
        cursor.execute("""
            SELECT station_id, station_key, station_name 
            FROM station 
            WHERE status_id = 1
        """)
        station = cursor.fetchone()
        cursor.close()

        if not station:
            raise ValueError("No hay estaciones activas")

        cursor = conn.cursor()
        cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(name_piece,))
        part = cursor.fetchone()
        cursor.close()

        if not part:
            # raise ValueError("Parte no encontrada: " + name_piece)
            return "FAILED"
        value, low_limit, high_limit, data_type, units, result, metadata = element[1:8]
        compoperator = evaluation.evaluation(element[1:4])
        description = f"{measurement[1]}_{element[8]}"
        screwing_measurement_id = measurement[0]
        station_id = station[0]
        part_id = part[0]
        cursor = conn.cursor()
        sql = '''
            INSERT INTO parameters_screwing (
                value, low_limit, high_limit, data_type, unit, result, 
                compoperator, test_time, metadata, description, 
                screwing_measurement_id, station_id, part_id
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        val = (
            value, low_limit, high_limit, data_type, units, result,
            compoperator, test_time, metadata, description,
            screwing_measurement_id, station_id, part_id
        )
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()

    except mariadb.Error as e:
        print(f"[DB ERROR] {e}")
        return f"[DB ERROR] {e}"
    except Exception as e:
        print(f"[GENERAL_ERROR] {e}")
        return "GENERAL_ERROR"

    # num_piece = ["","",value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, ""]
    # history_xlsx.history_file_xlsx(num_piece)

def parameters_inspection_vs(element, name_piece):
    import evaluation
    from datetime import datetime, timezone
    import rfc3339

    try:
        # Timestamp formateado correctamente
        now = datetime.now(timezone.utc).astimezone()
        test_time = rfc3339.rfc3339(now, utc=True, use_system_timezone=False)

        # Obtener measurement
        cursor = conn.cursor()
        cursor.execute("""
            SELECT inspection_measurement_id, name 
            FROM inspection_measurement 
            WHERE inspection_measurement.key = ?
        """, (element[0],))
        measurement = cursor.fetchone()
        cursor.close()

        if not measurement:
            # print("Measurement no encontrado:", element[0])
            return "FAILED"

        # Obtener station
        cursor = conn.cursor()
        cursor.execute("""
            SELECT station_id, station_key, station_name 
            FROM station 
            INNER JOIN type_station ON type_station.ts_id = station.ts_id
            WHERE status_id = 1
        """)
        station = cursor.fetchone()
        cursor.close()

        if not station:
            # print("No se encontró una estación activa")
            return "FAILED"

        # Obtener part
        cursor = conn.cursor()
        cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(name_piece,))
        part = cursor.fetchone()
        cursor.close()

        if not part:
            # print("Parte no encontrada:", name_piece)
            return "FAILED"

        # Preparar datos
        value, low_limit, high_limit, data_type, units, result, metadata = element[1:8]
        compoperator = evaluation.evaluation(element[1:4])
        description = f"{station[2]} {measurement[1]} VS - Test"
        inspection_measurement_id = measurement[0]
        station_id = station[0]
        part_id = part[0]
        type_inspection_id = 1

        # Insertar en DB
        cursor = conn.cursor()
        sql = '''
            INSERT INTO parameters_inspection (
                value, low_limit, high_limit, data_type, unit, result, 
                compoperator, test_time, metadata, description, 
                inspection_measurement_id, station_id, part_id, type_inspection_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        val = (
            value, low_limit, high_limit, data_type, units, result,
            compoperator, test_time, metadata, description,
            inspection_measurement_id, station_id, part_id, type_inspection_id
        )
        cursor.execute(sql, val)
        conn.commit()

        # num_piece = ["","",value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, ""]
        # history_xlsx.history_file_xlsx(num_piece)
        
        cursor.close()
        return "PASSED"

    except mariadb.Error as e:
        print("[DB ERROR]", e)
        return "FAILED"
    except Exception as e:
        print("[GENERAL ERROR]", e)
        return "GENERAL_ERROR"

    

def parameters_inspection_xt(element, name_piece):
    import evaluation
    from datetime import datetime, timezone
    import rfc3339

    try:
        # Generar timestamp en formato RFC 3339 (sin manipulaciones innecesarias)
        now = datetime.now(timezone.utc).astimezone()
        test_time = rfc3339.rfc3339(now, utc=True, use_system_timezone=False)

        # Obtener measurement
        cursor = conn.cursor()
        cursor.execute("""
            SELECT inspection_measurement_id, name 
            FROM data_tracking_qwert.inspection_measurement 
            WHERE inspection_measurement.key = ?
        """, (element[0],))
        measurement = cursor.fetchone()
        cursor.close()

        if not measurement:
            # print(f"[WARNING] Measurement no encontrado: {element[0]}")
            return "FAILED"

        # Obtener station
        cursor = conn.cursor()
        cursor.execute("""
            SELECT station_id, station_key, station_name 
            FROM station 
            INNER JOIN data_tracking_qwert.type_station ON type_station.ts_id = station.ts_id
            WHERE status_id = 1
        """)
        station = cursor.fetchone()
        cursor.close()

        if not station:
            # print("[WARNING] No se encontró estación activa.")
            return "FAILED"

        # Obtener part
        cursor = conn.cursor()
        cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(name_piece,))
        part = cursor.fetchone()
        cursor.close()

        if not part:
            # print(f"[WARNING] Parte no encontrada: {name_piece}")
            return "FAILED"

        # Descomponer datos del elemento
        value, low_limit, high_limit, data_type, units, result, metadata = element[1:8]
        # value = element[1]
        # low_limit = element[2]
        # high_limit = element[3]
        if value == "" and low_limit == "" and high_limit == "":
            return "GENERAL_ERROR"
        compoperator = evaluation.evaluation(element[1:4])
        description = f"{station[2]} {measurement[1]} XT - Test"
        inspection_measurement_id = measurement[0]
        station_id = station[0]
        part_id = part[0]
        type_inspection_id = 2  # XT

        # Insertar en la base de datos
        cursor = conn.cursor()
        sql = '''
            INSERT INTO parameters_inspection (
                value, low_limit, high_limit, data_type, unit, result,
                compoperator, test_time, metadata, description,
                inspection_measurement_id, station_id, part_id, type_inspection_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        val = (
            value, low_limit, high_limit, data_type, units, result,
            compoperator, test_time, metadata, description,
            inspection_measurement_id, station_id, part_id, type_inspection_id
        )
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        # num_piece = ["","",value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, ""]
        # history_xlsx.history_file_xlsx(num_piece)
        return "PASSED"

    except mariadb.Error as e:
        print(f"[DB ERROR] {e}")
        return "FAILED"
    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
        return "GENERAL_ERROR"


def parameters_electrical(element, name_piece):
    import evaluation
    from datetime import datetime, timezone
    import rfc3339

    try:
        # Obtener timestamp en formato RFC3339 (sin manipular strings)
        now = datetime.now(timezone.utc).astimezone()
        test_time = rfc3339.rfc3339(now, utc=True, use_system_timezone=False)

        # Obtener measurement_id y name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT electrical_measurement_id, name 
            FROM data_tracking_qwert.electrical_measurement 
            WHERE electrical_measurement.key = ?
        """, (element[0],))
        measurement = cursor.fetchone()
        cursor.close()

        if not measurement:
            # print(f"[WARNING] No se encontró medición: {element[0]}")
            return "FAILED"

        # Obtener primera estación activa
        cursor = conn.cursor()
        cursor.execute("""
            SELECT station_id, station_name 
            FROM station 
            INNER JOIN data_tracking_qwert.type_station ON type_station.ts_id = station.ts_id
            WHERE station.status_id = 1
            LIMIT 1
        """)
        station = cursor.fetchone()
        cursor.close()

        if not station:
            # print("[WARNING] No hay estaciones activas")
            return "FAILED"

        # Obtener parte
        cursor = conn.cursor()
        cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(name_piece,))
        part = cursor.fetchone()
        cursor.close()

        if not part:
            # print(f"[WARNING] Parte no encontrada: {name_piece}")
            return "FAILED"

        # Extraer y preparar datos
        value, low_limit, high_limit, data_type, units, result, metadata = element[1:8]
        compoperator = evaluation.evaluation(element[1:4])
        description = f"{measurement[1]}"

        # Insertar en tabla
        cursor = conn.cursor()
        sql = '''
            INSERT INTO parameters_electrical (
                value, low_limit, high_limit, data_type, unit, result,
                compoperator, test_time, metadata, description,
                electrical_measurement_id, station_id, part_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        val = (
            value, low_limit, high_limit, data_type, units, result,
            compoperator, test_time, metadata, description,
            measurement[0], station[0], part[0]
        )
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        # num_piece = ["","",value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, ""]
        # history_xlsx.history_file_xlsx(num_piece)
        return "PASSED"

    except mariadb.Error as e:
        # print(f"[DB ERROR] {e}")
        return "FAILED"

    except Exception as e:
        # print(f"[ERROR] {e}")
        return "GENERAL_ERROR"

def duration(element, name_piece):
    import rfc3339
    from datetime import datetime, timezone

    try:
        # Parsear entrada
        element = element.split(',')
        taskresult = element[1]
        taskduration = element[2]
        metadata = element[3]

        # Generar timestamp RFC3339
        task_timestamp = datetime.now(timezone.utc).astimezone()
        last_digit = str(task_timestamp).split('-')[3]
        tasktimestamp = rfc3339.rfc3339(task_timestamp, utc=True, use_system_timezone=False) + " " + last_digit

        # Obtener estación activa
        with conn.cursor() as cursor:
            cursor.execute('''SELECT station_id FROM station 
                              INNER JOIN data_tracking_qwert.type_station ON type_station.ts_id = station.ts_id
                              WHERE status_id = 1 LIMIT 1''')
            station = cursor.fetchone()
            if not station:
                # print("[ERROR] No hay estación activa")
                return "FAILED"
            station_id = station[0]

        # Obtener parte activa
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC", (name_piece,))
            part = cursor.fetchone()
            if not part:
                # print("[ERROR] Pieza no encontrada")
                return "FAILED"
            part_id = part[0]

        # Insertar duración
        with conn.cursor() as cursor:
            sql = '''INSERT INTO duration (station_id, part_id, taskresult, tasktimestamp, taskduration, metadata)
                     VALUES (?, ?, ?, ?, ?, ?)'''
            val = (station_id, part_id, taskresult, tasktimestamp, taskduration, metadata)
            cursor.execute(sql, val)
            conn.commit()

        # Desactivar piezas anteriores
        cursor = conn.cursor()
        cursor.execute("UPDATE part SET status_id = ? WHERE status_id = ? AND part_number = ?", (2, 3, name_piece))
        conn.commit()
        cursor.close()

        # Eliminar pieza de la tabla serial_number
        cursor = conn.cursor()
        cursor.execute("DELETE FROM serial_number WHERE data = ?", (name_piece,))
        conn.commit()
        cursor.close()

        # Registrar en historial
        # num_piece = [""] * 13 + [taskresult, tasktimestamp, taskduration, metadata]
        # history_xlsx.history_file_xlsx(num_piece)

        return "PASSED"

    except Exception as e:
        # print(f"[ERROR] {e}")
        return "FAILED"

#################################################### Consultas para el archivo JSON ##############################################
def pieces(parte):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 2 AND part_number = %s ORDER BY part_id DESC LIMIT 1",(parte,))
            part = cursor.fetchone()
            if not part:
                return None  # O podrías lanzar una excepción si prefieres

            return part

    except Exception as e:
        # print(f"[ERROR] pieces(): {e}")
        return None


def duration_json(station_id, part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT taskresult, tasktimestamp, taskduration, metadata, create_registration FROM duration WHERE station_id = %s AND part_id = %s ORDER BY duration_id DESC LIMIT 1",
                (station_id, part_id)
            )
            result = cursor.fetchone()
            return result if result else None

    except Exception as e:
        # print(f"[ERROR] duration_json(): {e}")
        return None

def inspection_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT *
                FROM (
                    SELECT 
                        parameters_inspection.inspection_measurement_id, 
                        value, 
                        low_limit, 
                        high_limit, 
                        data_type, 
                        unit, 
                        result, 
                        compoperator, 
                        test_time, 
                        metadata, 
                        description, 
                        inspection_measurement.name,
                        parameters_inspection.type_inspection_id,
                        parameters_inspection.parameters_inspection_id,
                        ROW_NUMBER() OVER (
                            PARTITION BY parameters_inspection.type_inspection_id
                            ORDER BY test_time DESC
                        ) AS rn
                    FROM parameters_inspection 
                    INNER JOIN data_tracking_qwert.inspection_measurement 
                        ON inspection_measurement.inspection_measurement_id = parameters_inspection.inspection_measurement_id
                    WHERE part_id = %s
                ) t
                WHERE 
                    (type_inspection_id = 1 AND rn <= 3)
                OR (type_inspection_id <> 1 AND rn <= 4)
                ORDER BY parameters_inspection_id DESC;
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] inspection_data(): {e}")
        return []

def screwing_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_screwing.screwing_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    screwing_measurement.name 
                FROM parameters_screwing 
                INNER JOIN data_tracking_qwert.screwing_measurement 
                    ON screwing_measurement.screwing_measurement_id = parameters_screwing.screwing_measurement_id
                WHERE part_id = %s
                ORDER BY parameters_screwing_id ASC
                
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] screwing_data(): {e}")
        return []

def pressfit_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_pressfit.pressfit_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    pressfit_measurement.name, 
                    dwell_time 
                FROM parameters_pressfit 
                INNER JOIN data_tracking_qwert.pressfit_measurement 
                    ON pressfit_measurement.pressfit_measurement_id = parameters_pressfit.pressfit_measurement_id
                WHERE part_id = %s
                ORDER BY parameters_pressfit_id ASC
                
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] pressfit_data(): {e}")
        return []

def electrical_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_electrical.electrical_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    electrical_measurement.name 
                FROM parameters_electrical
                INNER JOIN data_tracking_qwert.electrical_measurement 
                    ON electrical_measurement.electrical_measurement_id = parameters_electrical.electrical_measurement_id
                WHERE part_id = %s
                ORDER BY parameters_electrical_id DESC
                LIMIT 4
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def continuity_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    description, 
                    compoperator, 
                    low_limit,
                    high_limit, 
                    unit_measurement, 
                    status, 
                    value, 
                    defect_code,
                    create_registration
                FROM parameters_continuity
                WHERE part_id = %s
                ORDER BY parameters_continuity_id DESC
                LIMIT 1
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def leaktest_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    trial_period, 
                    value, 
                    result,
                    unit, 
                    description, extra1, extra2, compoperator, test,
                    create_registration
                FROM parameters_leaktest
                WHERE part_id = %s
                ORDER BY parameters_leaktest_id DESC
                LIMIT 2
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def welding_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    welding_time, 
                    welding_power, 
                    collapse_distance,
                    description,
                    result,
                    unit, 
                    extra1,
                    compoperator,
                    create_registration
                FROM parameters_welding
                WHERE part_id = %s
                ORDER BY parameters_welding_id DESC
                LIMIT 1
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def heatstake_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    part_id, 
                    cicle_time, 
                    serial_number, 
                    program_name,
                    times_tamp,
                    grade,
                    description,
                    create_registration
                FROM heatstake
                WHERE part_id = %s
                ORDER BY heatstake_id ASC
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def graph_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    part_id, 
                    data_image, 
                    description,
                    create_registration
                FROM graph_image
                WHERE part_id = %s
                ORDER BY graph_image_id ASC
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def temperature_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    start_time, 
                    end_time, 
                    initial_temperature,
                    final_temperature, 
                    unit,
                    description, extra1, extra2
                FROM parameters_temperature
                WHERE part_id = %s
                ORDER BY parameters_temperature_id DESC
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def component_data(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    component_name,
                    description
                FROM component
                WHERE part_id = %s
                ORDER BY component_id ASC
            ''', (part_id,))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
############################################# Archivos por prueba ##################################################

def screwing_data3(part_id, limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_screwing.screwing_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    screwing_measurement.name 
                FROM parameters_screwing 
                INNER JOIN data_tracking_qwert.screwing_measurement 
                    ON screwing_measurement.screwing_measurement_id = parameters_screwing.screwing_measurement_id
                WHERE part_id = %s
                ORDER BY screwing_measurement_id DESC
                LIMIT %s
            ''', (part_id,limite))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] screwing_data(): {e}")
        return []
    
def pressfit_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_pressfit.pressfit_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    pressfit_measurement.name, 
                    dwell_time 
                FROM parameters_pressfit 
                INNER JOIN data_tracking_qwert.pressfit_measurement 
                    ON pressfit_measurement.pressfit_measurement_id = parameters_pressfit.pressfit_measurement_id
                WHERE part_id = %s
                ORDER BY pressfit_measurement_id DESC
                LIMIT %s
            ''', (part_id,limite))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] pressfit_data(): {e}")
        return []

def inspection_data3(part_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_inspection.inspection_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    inspection_measurement.name 
                FROM parameters_inspection 
                INNER JOIN data_tracking_qwert.inspection_measurement 
                    ON inspection_measurement.inspection_measurement_id = parameters_inspection.inspection_measurement_id
                WHERE part_id = %s
                ORDER BY parameters_inspection_id ASC
            ''', (part_id,))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] inspection_data(): {e}")
        return []
    
def electrical_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    parameters_electrical.electrical_measurement_id, 
                    value, 
                    low_limit, 
                    high_limit, 
                    data_type, 
                    unit, 
                    result, 
                    compoperator, 
                    test_time, 
                    metadata, 
                    description, 
                    electrical_measurement.name 
                FROM parameters_electrical
                INNER JOIN data_tracking_qwert.electrical_measurement 
                    ON electrical_measurement.electrical_measurement_id = parameters_electrical.electrical_measurement_id
                WHERE part_id = %s
                ORDER BY electrical_measurement_id DESC
                LIMIT %s
            ''', (part_id,limite))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def continuity_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    description, 
                    compoperator, 
                    low_limit,
                    high_limit, 
                    unit_measurement, 
                    status, 
                    value, 
                    defect_code
                FROM parameters_continuity
                WHERE part_id = %s
                ORDER BY parameters_continuity_id DESC
                LIMIT %s
            ''', (part_id,limite))
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def leaktest_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    trial_period, 
                    value, 
                    result,
                    unit, 
                    description, extra1, extra2
                FROM parameters_leaktest
                WHERE part_id = %s
                ORDER BY parameters_leaktest_id DESC
                LIMIT %s
            ''', (part_id,limite))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def welding_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    welding_time, 
                    welding_power, 
                    collapse_distance,
                    description,
                    result,
                    unit, extra1
                FROM parameters_welding
                WHERE part_id = %s
                ORDER BY parameters_welding_id DESC
                LIMIT %s
            ''', (part_id,limite))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def welding_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    welding_time, 
                    welding_power, 
                    collapse_distance,
                    description,
                    result,
                    unit, extra1
                FROM parameters_welding
                WHERE part_id = %s
                ORDER BY parameters_welding_id DESC
                LIMIT %s
            ''', (part_id,limite))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []
    
def temperature_data3(part_id,limite):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    measurement_name, 
                    start_time, 
                    end_time, 
                    initial_temperature,
                    final_temperature, 
                    unit,
                    description, extra1, extra2
                FROM parameters_temperature
                WHERE part_id = %s
                ORDER BY parameters_temperature_id DESC
                LIMIT %s
            ''', (part_id,limite))
            # print(cursor.fetchall())
            return cursor.fetchall()
    except Exception as e:
        # print(f"[ERROR] electrical_data(): {e}")
        return []

####################################################################################################################
    
############################################# View Table ###########################################################

def inspection_data2(part_id):
    inspection = []
    try:
        inspectionJson = conn.cursor()
        inspectionJson.execute('''SELECT inspection_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_inspection.inspection_measurement_id FROM parameters_inspection 
                            inner JOIN data_tracking_qwert.inspection_measurement ON inspection_measurement.inspection_measurement_id = parameters_inspection.inspection_measurement_id
                            WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_inspection_id DESC LIMIT 4")
        results =inspectionJson.fetchall()
        for x in results:
            inspection.append(x)

        # print(inspection) 
        return inspection
    except mariadb.Error as e:
        # print(f"Error en pressfit_data2: {e}")
        return []

    finally:
        inspectionJson.close()

def screwing_data2(part_id):
    screwing = []
    try:
        screwingJson = conn.cursor()
        screwingJson.execute('''SELECT screwing_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_screwing.screwing_measurement_id FROM parameters_screwing 
                            inner JOIN data_tracking_qwert.screwing_measurement ON screwing_measurement.screwing_measurement_id = parameters_screwing.screwing_measurement_id
                            WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_screwing_id DESC LIMIT 4")
        results =screwingJson.fetchall()
        for x in results:
            screwing.append(x)
            
        return screwing
    except mariadb.Error as e:
        # print(f"Error en pressfit_data2: {e}")
        return []

    finally:
        screwingJson.close()

def pressfit_data2(part_id):
    pressfit = []
    try:
        pressfitJson = conn.cursor()
        pressfitJson.execute('''SELECT pressfit_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_pressfit.pressfit_measurement_id FROM parameters_pressfit 
                            inner JOIN data_tracking_qwert.pressfit_measurement ON pressfit_measurement.pressfit_measurement_id = parameters_pressfit.pressfit_measurement_id
                            WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_pressfit_id DESC LIMIT 4")
        results =pressfitJson.fetchall()
        for x in results:
            pressfit.append(x)
                
        return pressfit
    
    except mariadb.Error as e:
        # print(f"Error en pressfit_data2: {e}")
        return []

    finally:
        pressfitJson.close()
    
def electrical_data2(part_id):
    electrical = []
    try:
        electricalJson = conn.cursor()
        electricalJson.execute('''SELECT electrical_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_electrical.electrical_measurement_id FROM parameters_electrical 
                            inner JOIN data_tracking_qwert.electrical_measurement ON electrical_measurement.electrical_measurement_id = parameters_electrical.electrical_measurement_id
                            WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_electrical_id DESC LIMIT 7")
        results =electricalJson.fetchall()
        for x in results:
            electrical.append(x)
            
        return electrical
    except mariadb.Error as e:
        # print(f"Error en pressfit_data2: {e}")
        return []

    finally:
        electricalJson.close()

########################################################## REGISTRO DE COMPONENTES ####################################################
def component_store(component_name,descripcion,parte):
    try:
        # --- Obtener part activo ---
        cursor = conn.cursor()
        cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC LIMIT 1",(parte,))
        part = cursor.fetchone()
        cursor.close()

        if not part:
            # print("[ERROR] No se encontró una pieza activa.")
            return "FAILED"

        part_id = part[0]

        # --- Insertar componente ---
        cursor = conn.cursor()
        sql = """
            INSERT INTO component (part_id, component_name, description)
            VALUES (?, ?, ?)
        """
        cursor.execute(sql, (part_id, component_name, descripcion))
        conn.commit()
        cursor.close()

        return "PASSED"

    except mariadb.Error as e:
        # print(f"[DB ERROR] component_store(): {e}")
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] component_store(): {e}")
        return "FAILED"

def parameters_continuity(element):
    import evaluation

    print(element)
    
    # Preparar evaluación
    evaluacion = [element[7], element[3], element[4]]
    compoperator = evaluation.evaluation(evaluacion)
    
    try:
        # Obtener estación activa
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT station_id 
                FROM station 
                INNER JOIN data_tracking_qwert.type_station 
                    ON type_station.ts_id = station.ts_id
                WHERE station.status_id = 1
                LIMIT 1
            ''')
            station = cursor.fetchone()
        
        if not station:
            # print("[ERROR] No hay estaciones activas.")
            return "FAILED"
        
        station_id = station[0]

        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[9],))
            part = cursor.fetchone()
        
        if not part:
            # print("[ERROR] No se encontró una pieza activa.")
            return "FAILED"
        
        part_id = part[0]

        # Insertar datos en parameters_continuity
        sql = '''
            INSERT INTO parameters_continuity (
                measurement_name, description, compoperator,
                low_limit, high_limit, unit_measurement,
                status, value, defect_code,
                station_id, part_id, status_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        val = (
            element[1],  # measurement_name
            element[2],  # description
            compoperator,
            float(element[3]) if element[3] else 0.0,  # low_limit
            float(element[4]) if element[4] else 0.0,  # high_limit
            element[5],  # unit_measurement
            element[6],  # status
            float(element[7]) if element[7] else 0.0,  # value
            element[8],  # defect_code
            # element[9],  # user_id
            station_id,
            part_id,
            1  # status_status_id
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        # print("[ÉXITO] Datos insertados correctamente en parameters_continuity")
        return "PASSED"
        
    except mariadb.Error as e:
        # print(f"[DB ERROR] parameters_continuity(): {e}")
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_continuity(): {e}")
        return "FAILED"

def parameters_leak(element):
    import evaluation
    
    # Preparar evaluación
    evaluacion = [element[3], element[7], element[8]]
    compoperator = evaluation.evaluation(evaluacion)
    test = element[9]
    
    try:
        # Obtener estación activa
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT station_id 
                FROM station 
                INNER JOIN data_tracking_qwert.type_station 
                    ON type_station.ts_id = station.ts_id
                WHERE station.status_id = 1
                LIMIT 1
            ''')
            station = cursor.fetchone()
        
        if not station:
            # print("[ERROR] No hay estaciones activas.")
            return "FAILED"
        
        station_id = station[0]

        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[10],))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]
        
        # Insertar datos en parameters_continuity
        sql = '''
            INSERT INTO parameters_leaktest (
                measurement_name, trial_period, value,
                result, unit, description,
                extra1, extra2, compoperator, test, station_id, part_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        val = (
            element[1],  # measurement_name
            element[2],  # trial_period
            element[3],  # value
            element[4],  # result
            element[5],  # unit
            element[6],  # description
            element[7],  # extra1
            element[8],  # extra2
            compoperator,#compoperator 
            test,        #test
            station_id,
            part_id
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        print("[ÉXITO] Datos insertados correctamente en parameters_leak")
        return "PASSED"
        
    except mariadb.Error as e:
        print(f"[DB ERROR] parameters_leak(): {e}")
        # NO cierres la conexión aquí
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_leak(): {e}")
        return "FAILED"

def parameters_temperature(element):
        
    try:
        # Obtener estación activa
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT station_id 
                FROM station 
                INNER JOIN data_tracking_qwert.type_station 
                    ON type_station.ts_id = station.ts_id
                WHERE station.status_id = 1
                LIMIT 1
            ''')
            station = cursor.fetchone()
        
        if not station:
            # print("[ERROR] No hay estaciones activas.")
            return "FAILED"
        
        station_id = station[0]

        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[10],))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]
        
        # Insertar datos en parameters_continuity
        sql = '''
            INSERT INTO parameters_temperature (
                measurement_name, start_time, end_time,
                initial_temperature, final_temperature, unit,
                description,
                extra1, extra2, station_id, part_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        val = (
            element[1],  # measurement_name
            element[2],  # start_time
            element[3],  # end_time
            element[4],  # initial_temperature
            element[5],  # final_temperature
            element[6],  # unit
            element[7],  # description
            element[8],  # extra1
            element[9],  # extra2
            station_id,
            part_id
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        # print("[ÉXITO] Datos insertados correctamente en parameters_temperature")
        return "PASSED"
        
    except mariadb.Error as e:
        # print(f"[DB ERROR] parameters_temperature(): {e}")
        # NO cierres la conexión aquí
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_temperature(): {e}")
        return "FAILED"
    
def parameters_welding(element):
        
    try:
        # Obtener estación activa
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT station_id 
                FROM station 
                INNER JOIN data_tracking_qwert.type_station 
                    ON type_station.ts_id = station.ts_id
                WHERE station.status_id = 1
                LIMIT 1
            ''')
            station = cursor.fetchone()
        
        if not station:
            # print("[ERROR] No hay estaciones activas.")
            return "FAILED"
        
        station_id = station[0]

        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[8],))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]
        
        # Insertar datos en parameters_continuity
        sql = '''
            INSERT INTO parameters_welding (
                measurement_name, welding_time, welding_power,
                collapse_distance, description, result, unit, station_id, part_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        val = (
            element[1],  # measurement_name
            element[2],  # welding_time
            element[3],  # welding_power
            element[4],  # collapse_distance
            element[7],  # description
            element[6],  # result
            element[5],  # unit
            station_id,
            part_id
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        # print("[ÉXITO] Datos insertados correctamente en parameters_welding")
        return "PASSED"
        
    except mariadb.Error as e:
        # print(f"[DB ERROR] parameters_welding(): {e}")
        # NO cierres la conexión aquí
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_welding(): {e}")
        return "FAILED"

def parameters_heatstake(element):
        
    try:
        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[4],))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]
        
        # Insertar datos en parameters_continuity
        sql = '''
            INSERT INTO heatstake (
                cicle_time, serial_number,
                program_name, times_tamp, grade, description, part_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        val = (
            element[3],  # cicle_time
            element[4],  # serial_number
            element[5],  # program_name
            element[6],  # times_tamp
            element[7],  # grade
            element[8],  # description
            part_id
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        # print("[ÉXITO] Datos insertados correctamente en parameters_welding")
        return "PASSED"
        
    except mariadb.Error as e:
        # print(f"[DB ERROR] parameters_heatstake(): {e}")
        # NO cierres la conexión aquí
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_heatstake(): {e}")
        return "FAILED"

def parameters_graph(element):
    print(element)
    try:
        # Obtener part activo
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 3 AND part_number = %s ORDER BY part_id DESC",(element[2],))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]
        
        # Insertar datos en parameters_continuity
        if element[0] =="" and element[1] =="":
            # print("[ERROR] No se proporcionó data_image.")
            return "GENERAL_ERROR"
        sql = '''
            INSERT INTO graph_image (
                part_id, data_image, description
            ) VALUES (?, ?, ?)
        '''
        
        val = (
            part_id,
            element[0],  # data_image
            element[1],  # description
        )
        
        # print(f"Valores a insertar: {val}")
        
        with conn.cursor() as cursor:
            cursor.execute(sql, val)
            conn.commit()
        
        # print("[ÉXITO] Datos insertados correctamente en parameters_welding")
        return "PASSED"
        
    except mariadb.Error as e:
        # print(f"[DB ERROR] parameters_heatstake(): {e}")
        # NO cierres la conexión aquí
        return "FAILED"
    except Exception as e:
        # print(f"[ERROR] parameters_heatstake(): {e}")
        return "FAILED"

############################################### CONFIGURADOR ####################################################


def get_configurator_data():
    """Obtiene los datos de configuración actuales"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT configurator_id, url, program_id, device, 
                       program_password, tsp
                FROM configurator 
                LIMIT 1
            """)
            config = cursor.fetchone()
            return config
    except Exception as e:
        print(f"[ERROR] get_configurator_data(): {e}")
        return None

def update_configurator(url, program_id, device, program_password, tsp):
    """Actualiza o inserta datos en la tabla configurator"""
    try:
        with conn.cursor() as cursor:
            # Verificar si existe un registro
            cursor.execute("SELECT COUNT(*) FROM configurator")
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Actualizar registro existente
                sql = """
                    UPDATE configurator 
                    SET url = ?, program_id = ?, device = ?, 
                        program_password = ?, tsp = ?
                    WHERE configurator_id = 1
                """
            else:
                # Insertar nuevo registro
                sql = """
                    INSERT INTO configurator 
                    (url, program_id, device, program_password, tsp)
                    VALUES (?, ?, ?, ?, ?)
                """
            
            cursor.execute(sql, (url, program_id, device, program_password, tsp))
            conn.commit()
            return True
    except Exception as e:
        print(f"[ERROR] update_configurator(): {e}")
        return False

def update_export_status(file_type, status):
    """Actualiza el estado de exportación para CSV, JSON o XML"""
    try:
        # Mapeo de tipos de archivo a key
        file_key_map = {
            'CSV': 'CSV_EXPORT',
            'JSON': 'JSON_EXPORT', 
            'XML': 'XML_EXPORT'
        }
        
        file_key = file_key_map.get(file_type.upper())
        if not file_key:
            print(f"[ERROR] Tipo de archivo no válido: {file_type}")
            return False
        
        # status: 1 = enabled, 2 = disabled
        with conn.cursor() as cursor:
            # Verificar si existe el registro por key
            cursor.execute(
                "SELECT export_file_id FROM export_file WHERE `key` = ?", 
                (file_key,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar registro existente
                sql = """
                    UPDATE export_file 
                    SET status_id = ?, name = ?
                    WHERE export_file_id = ?
                """
                cursor.execute(sql, (status, file_type, existing[0]))
            else:
                # Insertar nuevo registro
                sql = """
                    INSERT INTO export_file (`key`, name, status_id) 
                    VALUES (?, ?, ?)
                """
                cursor.execute(sql, (file_key, file_type, status))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"[ERROR] update_export_status(): {e}")
        return False

def get_export_status():
    """Obtiene el estado actual de los checkboxes CSV, JSON, XML - versión alternativa"""
    try:
        with conn.cursor() as cursor:
            # Obtener todos los registros
            cursor.execute("SELECT name, status_id FROM export_file")
            all_rows = cursor.fetchall()
            print(f"[DEBUG] Todas las filas en export_file: {all_rows}")
            
            # Filtrar y normalizar
            status_dict = {'CSV': 2, 'JSON': 2, 'XML': 2}
            
            for name, status in all_rows:
                if name:
                    name_upper = name.upper().strip()
                    if name_upper == 'CSV':
                        status_dict['CSV'] = status
                    elif name_upper == 'JSON':
                        status_dict['JSON'] = status
                    elif name_upper == 'XML':
                        status_dict['XML'] = status
            
            print(f"[DEBUG] Estado final: {status_dict}")
            return status_dict
            
    except Exception as e:
        print(f"[ERROR] get_export_status(): {e}")
        return {'CSV': 2, 'JSON': 2, 'XML': 2}

def get_enabled_export_formats():
    """Obtiene los formatos de exportación habilitados (status_id = 1)"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name 
                FROM export_file 
                WHERE status_id = 1 
                AND `key` IN ('CSV_EXPORT', 'JSON_EXPORT', 'XML_EXPORT')
                ORDER BY FIELD(name, 'CSV', 'JSON', 'XML')
            """)
            
            results = cursor.fetchall()
            return [result[0].upper() for result in results]
    except Exception as e:
        print(f"[ERROR] get_enabled_export_formats(): {e}")
        return []

def initialize_export_file_table():
    """Inicializa la tabla export_file con los tipos de archivo si no existen"""
    try:
        with conn.cursor() as cursor:
            # Verificar si ya existen los registros
            cursor.execute("""
                SELECT COUNT(*) FROM export_file 
                WHERE `key` IN ('CSV_EXPORT', 'JSON_EXPORT', 'XML_EXPORT')
            """)
            count = cursor.fetchone()[0]
            
            if count < 3:
                # Insertar los tipos faltantes
                file_types = [
                    ('CSV_EXPORT', 'CSV', 2),  # disabled por defecto
                    ('JSON_EXPORT', 'JSON', 2),  # disabled por defecto
                    ('XML_EXPORT', 'XML', 2)  # disabled por defecto
                ]
                
                for file_key, name, status in file_types:
                    cursor.execute("""
                        INSERT IGNORE INTO export_file (`key`, name, status_id)
                        VALUES (?, ?, ?)
                    """, (file_key, name, status))
                
                conn.commit()
                print("[INFO] Tabla export_file inicializada")
                return True
        return False
    except Exception as e:
        print(f"[ERROR] initialize_export_file_table(): {e}")
        return False

#################################################################################################################
################################################ EXPORT FILE ####################################################

# Añade estas funciones al archivo conexion.py

def get_data_for_export():
    """Obtiene datos de ejemplo para exportación"""
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Ejemplo: Obtener datos de partes recientes
            cursor.execute("""
                SELECT 
                    p.part_id,
                    p.part_number,
                    p.model_id,
                    m.name as model_name,
                    p.status_id,
                    DATE(p.created_at) as created_date
                FROM part p
                LEFT JOIN model m ON p.model_id = m.model_id
                ORDER BY p.part_id DESC
                LIMIT 100
            """)
            
            return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] get_data_for_export(): {e}")
        return []

def export_all_enabled_formats():
    """Exporta datos a todos los formatos habilitados"""
    try:
        # Obtener formatos habilitados
        enabled_formats = get_enabled_export_formats()
        
        if not enabled_formats:
            print("[INFO] No hay formatos de exportación habilitados")
            return False
        
        # Obtener datos para exportar
        data = get_data_for_export()
        
        if not data:
            print("[INFO] No hay datos para exportar")
            return False
        
        results = []
        for file_type in enabled_formats:
            success = export_data_to_format(file_type, data)
            results.append((file_type, success))
        
        # Retornar resultados
        return all(success for _, success in results)
        
    except Exception as e:
        print(f"[ERROR] export_all_enabled_formats(): {e}")
        return False

def export_data_to_format(file_type, data):
    """Exporta datos al formato especificado"""
    try:
        formats = {
            'CSV': export_to_csv,
            'JSON': export_to_json,
            'XML': export_to_xml
        }
        
        if file_type in formats:
            return formats[file_type](data)
        else:
            print(f"[ERROR] Formato no soportado: {file_type}")
            return False
    except Exception as e:
        print(f"[ERROR] export_data_to_format(): {e}")
        return False

def export_to_csv(data):
    """Exporta datos a CSV"""
    try:
        import csv
        import os
        from datetime import datetime
        
        # Crear directorio de exportación si no existe
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(export_dir, f"export_{timestamp}.csv")
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if data and len(data) > 0:
                # Asumiendo que data es una lista de diccionarios
                if isinstance(data[0], dict):
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    # Si es lista de tuplas
                    writer = csv.writer(csvfile)
                    writer.writerows(data)
        
        print(f"[INFO] Datos exportados a {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] export_to_csv(): {e}")
        return False

def export_to_json(data):
    """Exporta datos a JSON"""
    try:
        import json
        import os
        from datetime import datetime
        
        # Crear directorio de exportación si no existe
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(export_dir, f"export_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Datos exportados a {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] export_to_json(): {e}")
        return False

def export_to_xml(data):
    """Exporta datos a XML"""
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        import os
        from datetime import datetime
        
        # Crear directorio de exportación si no existe
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(export_dir, f"export_{timestamp}.xml")
        
        # Crear elemento raíz
        root = ET.Element("export_data")
        
        if data and len(data) > 0:
            # Asumiendo que data es una lista de diccionarios
            for item in data:
                record = ET.SubElement(root, "record")
                for key, value in item.items():
                    field = ET.SubElement(record, str(key))
                    field.text = str(value) if value is not None else ""
        
        # Formatear XML
        xml_str = ET.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        with open(filename, 'w', encoding='utf-8') as xmlfile:
            xmlfile.write(xml_pretty)
        
        print(f"[INFO] Datos exportados a {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] export_to_xml(): {e}")
        return False

################################################################# Números de series ###########################################################################

def get_part_numbers(numero):
    
    # Obtener part_id
    cursor = conn.cursor()
    cursor.execute("SELECT serial_number_id, data FROM serial_number WHERE status_serial_number_id = 2 AND data = %s",(numero,))
    part = cursor.fetchone()
    cursor.close()

    if not part:
        cur = conn.cursor()
        sql = '''
            INSERT INTO serial_number
            (data, status_serial_number_id)
            VALUES (%s, %s)
        '''
        vals = (numero, 2)

        try:
            cur.execute(sql, vals)
            conn.commit()
        except Exception as e:
            print("Error inserting pressfit parameter:", e)
            return "FAILED"
        
        return numero
    
    return "PASSED"

def return_part_serial_number (numero):
    cursor = conn.cursor()
    sql = "DELETE FROM serial_number WHERE data = ?"
    cursor.execute(sql, (numero,))
    conn.commit()
    cursor.close()
    
################################################################# Configurador ###########################################################################

def configurador():
    
    # Obtener configuración actual
    cursor = conn.cursor()
    cursor.execute("SELECT machine_id, process_name, operator, station, product, shop_order FROM configurador")
    configurador = cursor.fetchone()
    cursor.close()

    if not configurador:
        print("[ERROR] No se encontró configuración activa.")
        
        return "FAILED"
    
    return configurador


################################################################# Atributos ###########################################################################

def atributos():
    # Obtener atributos actuales
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, unit, upper_limit, lower_limit, value_expected, time FROM attribute")
            
            results = cursor.fetchall()
            # print([result for result in results])
            return [result for result in results]
            # return [result[0].upper() for result in results]
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return []
    
################################################################# URLs ###########################################################################

def get_urls():
    """Obtener todas las URLs de la tabla url_data - Estructura actualizada"""    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT
                    name,
                    url_data
                FROM url_data 
                WHERE tc_id = 1
                ORDER BY url_data_id ASC
            ''')
            urls = cursor.fetchall()
            
            # Convertir a diccionario para fácil acceso
            url_dict = {}
            for name, url in urls:
                url_dict[name] = url
            # print(url_dict['SHOP ORDER'])
            return url_dict
            
    except Exception as e:
        print(f"Error obteniendo URLs: {e}")
        return {}

################################################################# Type Test ###########################################################################

def type_test():
    # Obtener atributos actuales
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT test_type_id, name FROM test_type WHERE status_id = 1")
            
            results = cursor.fetchall()
            # print([result for result in results])
            # return [result for result in results]
            # return [result[0].upper() for result in results]
            return results
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return []

################################################################# Heatstake ###########################################################################

def heatstake_info(serial_number):
    # Obtener atributos actuales
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 2 AND part_number = %s ORDER BY part_id DESC LIMIT 1",(serial_number,))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]

        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, cicle_time, serial_number, program_name, times_tamp, grade, description FROM heatstake WHERE part_id = %s",(part_id,))
            
            results = cursor.fetchall()
            # print([result for result in results])
            # return [result for result in results]
            # return [result[0].upper() for result in results]
            return results
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return []

################################################################# Obtener Parte ###########################################################################

def obtener_parte(serial_number):
     # Obtener part_id
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id, create_registration FROM part WHERE part_number = %s ORDER BY part_id DESC LIMIT 1",(serial_number,))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        
        return part
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return []
    
################################################################# Obtener graph ###########################################################################

def obtener_image(serial_number):
    # Obtener part_id
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id = 2 AND part_number = %s ORDER BY part_id DESC LIMIT 1",(serial_number,))
            part = cursor.fetchone()
        
        if not part:
            return "FAILED"
        
        part_id = part[0]

        with conn.cursor() as cursor:
            cursor.execute("SELECT part_id, data_image, description FROM graph_image WHERE part_id = %s",(part_id,))
            
            results = cursor.fetchall()
            return results
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return []
#################################################################################################################

################################################################# Obtener contadores de seriales ###########################################################################
def seriales_procesados():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(DISTINCT part_id) FROM part WHERE status_id = 2")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return 0
    
def seriales_pendientes():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(DISTINCT part_id) FROM part WHERE status_id = 3")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return 0

def unidades_falladas():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(DISTINCT part_id) FROM duration WHERE taskresult = 'FAILED'")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return 0
    
def multiplo_series():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT CASE WHEN COUNT(DISTINCT part_id) % 100 = 0 AND COUNT(DISTINCT part_id) > 0 THEN 'multiplo' ELSE 'no_multiplo' END AS tipo_conteo FROM part;")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print("[ERROR] No se encontraron atributos.")
        return 0
############################################################################################################################################################
# name = "P1895152-00-G:SHG2242791000290"
# parameters_pressfit(['F', '50', '10', '100', 'Numeric', 'N', 'PASSED', 'Comentarios', 'dwell_time'],name)
# parameters_electrical(['Ct', '50', '10', '100', 'Numeric', 'N', 'OK', 'Comentarios'],name)
# temperatura = "commit,Temp,start (timestamp),salida al proceso (timestamp),temp_inicial,temp_final,unit,descripcion,extra1,extra2,1/" 
# parametros = ['commit','Welding','welding_time','welding_power','100','mm','PASSED','description','1/']
# parameters_temperature(parametros)

# temperature_data(18)
# parameters_welding(parametros)
# welding_data(1)
# atributos()
# get_urls()