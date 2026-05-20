__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import mariadb
import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="u8ch9Xn4Ol8woLw3E2A6",
        host="127.0.0.1",
        port=3306,
        database="data_tracking"

    )
        
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

part_name = "P1895152-00-G:SHG2242791000290"

def history_file(type_station):
    # print(name_part)
    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)

    part_id = part[0][0]

    if type_station == 1:
        # print("Screwing")

        parameters_screwing = []
        parameters_name = conn.cursor()
        parameters_name.execute('''SELECT part.part_id, parameters_screwing.value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description FROM parameters_pressfit
                                    INNER JOIN part ON parameters_screwing.part_id = part.part_id
                                    WHERE part.status_id = 1 AND parameters_screwing.part_id = '''+str(part_id))
        parameters_name = parameters_name.fetchall()
        for x in parameters_name:
            parameters_screwing.append(x)

        duration = []
        duration_data = conn.cursor()
        duration_data.execute('''SELECT duration.taskresult, duration.tasktimestamp, duration.taskduration, duration.metadata FROM duration
                            INNER JOIN part ON duration.part_id = part.part_id
                            WHERE part.status_id = 1''')
        duration_data = duration_data.fetchall()
        for x in duration_data:
            duration.append(x)

        return parameters_screwing, duration
    
    elif type_station == 2:
        # print("Pressfit")

        parameters_pressfit = []
        parameters_name = conn.cursor()
        parameters_name.execute('''SELECT parameters_pressfit.part_id, parameters_pressfit.value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description FROM parameters_pressfit
                                   WHERE parameters_pressfit.part_id = '''+str(part_id))
        parameters_name = parameters_name.fetchall()
        for x in parameters_name:
            parameters_pressfit.append(x)

        duration = []
        duration_data = conn.cursor()
        duration_data.execute('''SELECT duration.taskresult, duration.tasktimestamp, duration.taskduration, duration.metadata FROM duration
                            INNER JOIN part ON duration.part_id = part.part_id
                            WHERE part.status_id = 1''')
        duration_data = duration_data.fetchall()
        for x in duration_data:
            duration.append(x)
        
        # print(parameters_pressfit)
        print(duration)

        return parameters_pressfit, duration

    elif type_station == 3:
        print("Inspection")

        parameters_inspection = []
        parameters_name = conn.cursor()
        parameters_name.execute('''SELECT part.part_id, parameters_inspection.value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description FROM parameters_pressfit
                                    INNER JOIN part ON parameters_inspection.part_id = part.part_id
                                    WHERE part.status_id = 1 AND parameters_inspection.part_id = '''+str(part_id))
        parameters_name = parameters_name.fetchall()
        for x in parameters_name:
            parameters_inspection.append(x)

        duration = []
        duration_data = conn.cursor()
        duration_data.execute('''SELECT duration.taskresult, duration.tasktimestamp, duration.taskduration, duration.metadata FROM duration
                            INNER JOIN part ON duration.part_id = part.part_id
                            WHERE part.status_id = 1''')
        duration_data = duration_data.fetchall()
        for x in duration_data:
            duration.append(x)

        return parameters_inspection, duration
    
# history_file(part_name,2)