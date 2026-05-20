# Module Imports
import mariadb
import sys

from tkinter import  messagebox 


# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="u8ch9Xn4Ol8woLw3E2A6",
        host="127.0.0.1",
        port=3306,
        database="data_tracking"

    )

    mycursor = conn.cursor()
    mycursor.execute("SELECT status_name FROM status")
    myresult = mycursor.fetchall()
    # for x in myresult:
    #     print(x[0])
    
    
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    messagebox.showerror(title="Connection", message=f"Check database connection", )
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

def server_connection():
    server =[]
    host = conn.cursor()
    host.execute("SELECT server_port, server_ip_address FROM server")
    host = host.fetchall()
    for x in host:
        server.append(x)
        # print(x)

    # print(server)
    return server

def new_model(model):
    project = []
    models = []
    project_name = conn.cursor()
    project_name.execute("SELECT project_id, pro_key, pro_name FROM project where status_id = 1")
    project_name = project_name.fetchall()
    for x in project_name:
        project.append(x)

    status_model = conn.cursor()
    sql_status = "UPDATE model SET status_id = %s WHERE status_id = %s"
    val_status = (2,1)
    status_model.execute(sql_status,val_status)
    conn.commit()

    model_name = conn.cursor()
    sql = "INSERT INTO model (name, project_id, status_id) VALUES (%s, %s, %s)"
    val = (model,project[0][0],1)
    model_name.execute(sql,val)
    conn.commit()

    select_new_model = conn.cursor()
    select_new_model.execute("SELECT model_id, name, project_id FROM model where status_id = 1 and project_id = "+str(project[0][0]))
    select_new_model = select_new_model.fetchall()
    for x in select_new_model:
        models.append(x)

    return models[0]    

def model():
    project = []
    models = []
    stations = []
    project_name = conn.cursor()
    project_name.execute("SELECT project_id, pro_key, pro_name FROM project where status_id = 1")
    project_name = project_name.fetchall()
    for x in project_name:
        project.append(x)
    
    model_name = conn.cursor()
    model_name.execute("SELECT model_id, name, project_id FROM model where status_id = 1 and project_id = "+str(project[0][0]))
    model_name = model_name.fetchall()
    for x in model_name:
        models.append(x)

    if len(models) == 0:
        # print(search_models)
        new_model("Model-T1")

    model_name = conn.cursor()
    model_name.execute("SELECT model_id, name, project_id FROM model where status_id = 1 and project_id = "+str(project[0][0]))
    model_name = model_name.fetchall()
    for x in model_name:
        models.append(x)
    
    station_name = conn.cursor()
    station_name.execute("SELECT station_name FROM station where status_id = 1")
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)
    
    # print(project)
    return project[0],models[0],stations[0]

def piece_store(numPiece):
    project = []
    models = []
    project_name = conn.cursor()
    project_name.execute("SELECT project_id, pro_key, pro_name FROM project where status_id = 1")
    project_name = project_name.fetchall()
    for x in project_name:
        project.append(x)

    model_name = conn.cursor()
    model_name.execute("SELECT model_id, name FROM model where status_id = 1 and project_id = "+str(project[0][0]))
    model_name = model_name.fetchall()
    for x in model_name:
        models.append(x)

    status_piece = conn.cursor()
    sql_status = "UPDATE part SET status_id = %s WHERE status_id = %s"
    val_status = (2,1)
    status_piece.execute(sql_status,val_status)
    conn.commit()

    piece = conn.cursor()
    sql = "INSERT INTO part (part_number, model_id, status_id) VALUES (%s, %s, %s)"
    val = (numPiece,models[0][0],1)
    piece.execute(sql,val)
    conn.commit()

def select_model(model):
    search_models = []
    search_model = conn.cursor()
    search_model.execute("SELECT model_id, name, project_id FROM model where name = '"+model+"'")
    search_model = search_model.fetchall()
    for x in search_model:
        search_models.append(x)
    
    if len(search_models) == 0:
        # print(search_models)
        return "0"
    else:
        project = []
        models = []
        project_name = conn.cursor()
        project_name.execute("SELECT project_id, pro_key, pro_name FROM project where status_id = 1")
        project_name = project_name.fetchall()
        for x in project_name:
            project.append(x)

        status_model = conn.cursor()
        sql_status = "UPDATE model SET status_id = %s WHERE status_id = %s"
        val_status = (2,1)
        status_model.execute(sql_status,val_status)
        conn.commit()

        select_models = conn.cursor()
        sql_status = "UPDATE model SET status_id = %s WHERE status_id = %s AND name = %s"
        val_status = (1,2,model)
        select_models.execute(sql_status,val_status)
        conn.commit()

        model_name = conn.cursor()
        model_name.execute("SELECT model_id, name, project_id FROM model where status_id = 1 and project_id = "+str(project[0][0]))
        model_name = model_name.fetchall()
        for x in model_name:
            models.append(x)
        
        return models[0]

def stations():
    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)
    return stations[0]

def parameters_pressfit(element,name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    measurement = []
    pressfit_measurement = element[0]
    measurement_key = conn.cursor()
    measurement_key.execute("SELECT pressfit_measurement_id, name FROM `data_tracking`.`pressfit_measurement` WHERE pressfit_measurement.`key` = '"+pressfit_measurement+"'")
    measurement_key = measurement_key.fetchall()
    for x in measurement_key:
        measurement.append(x)
    
    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)

    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE part_number ='"+name_piece+"' AND status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)

    value = element[1]
    low_limit = element[2]
    high_limit = element[3]
    data_type = element[4]
    units = element[5]
    result = element[6]
    compoperator = evaluation.evaluation(element[1:4])
    test_time = timer
    metadata = element[7]
    description = stations[0][2] + " " + measurement[0][1] +" Test"
    pressfit_measurement_id = measurement[0][0]
    station_id = stations[0][0]
    part_id = part[0][0]

    parameter_pressfit = conn.cursor()
    sql = '''INSERT INTO parameters_pressfit (value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, pressfit_measurement_id, station_id, part_id)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    val = (value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, pressfit_measurement_id, station_id, part_id)
    parameter_pressfit.execute(sql,val)
    conn.commit()

def parameters_screwing(element,name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    measurement = []
    screwing_measurement = element[0]
    measurement_key = conn.cursor()
    measurement_key.execute("SELECT screwing_measurement_id, name FROM `data_tracking`.`screwing_measurement` WHERE screwing_measurement.`key` = '"+screwing_measurement+"'")
    measurement_key = measurement_key.fetchall()
    for x in measurement_key:
        measurement.append(x)
    
    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)

    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE part_number ='"+name_piece+"' AND status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)

    value = element[1]
    low_limit = element[2]
    high_limit = element[3]
    data_type = element[4]
    units = element[5]
    result = element[6]
    compoperator = evaluation.evaluation(element[1:4])
    test_time = timer
    metadata = element[7]
    description = stations[0][2] + " " + measurement[0][1] +" Test"
    screwing_measurement_id = measurement[0][0]
    station_id = stations[0][0]
    part_id = part[0][0]

    parameter_screwing = conn.cursor()
    sql = '''INSERT INTO parameters_screwing (value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, screwing_measurement_id, station_id, part_id)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    val = (value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, screwing_measurement_id, station_id, part_id)
    parameter_screwing.execute(sql,val)
    conn.commit()

def parameters_inspection_vs(element,name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    measurement = []
    inspection_measurement = element[0]
    measurement_key = conn.cursor()
    measurement_key.execute("SELECT inspection_measurement_id, name FROM `data_tracking`.`inspection_measurement` WHERE inspection_measurement.`key` = '"+inspection_measurement+"'")
    measurement_key = measurement_key.fetchall()
    for x in measurement_key:
        measurement.append(x)
    
    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)

    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE part_number ='"+name_piece+"' AND status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)
    
    if len(part) == 0:
        # print(search_models)
        return "FAILED"

    value = element[1]
    low_limit = element[2]
    high_limit = element[3]
    data_type = element[4]
    units = element[5]
    result = element[6]
    compoperator = evaluation.evaluation(element[1:4])
    test_time = timer
    metadata = element[7]
    description = stations[0][2] + " " + measurement[0][1] +" VS - Test"
    inspection_measurement_id = measurement[0][0]
    station_id = stations[0][0]
    part_id = part[0][0]
    type_inspection_id = 1

    parameter_inspection = conn.cursor()
    sql = '''INSERT INTO parameters_inspection (value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, inspection_measurement_id, station_id, part_id, type_inspection_id)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    val = (value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, inspection_measurement_id, station_id, part_id, type_inspection_id)
    parameter_inspection.execute(sql,val)
    conn.commit()

def parameters_inspection_xt(element,name_piece):
    import evaluation
    from datetime import datetime, timezone 
    import rfc3339

    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    measurement = []
    inspection_measurement = element[0]
    measurement_key = conn.cursor()
    measurement_key.execute("SELECT inspection_measurement_id, name FROM `data_tracking`.`inspection_measurement` WHERE inspection_measurement.`key` = '"+inspection_measurement+"'")
    measurement_key = measurement_key.fetchall()
    for x in measurement_key:
        measurement.append(x)
    
    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)

    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE part_number ='"+name_piece+"' AND status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)
    
    if len(part) == 0:
        # print(search_models)
        return "FAILED"

    value = element[1]
    low_limit = element[2]
    high_limit = element[3]
    data_type = element[4]
    units = element[5]
    result = element[6]
    compoperator = evaluation.evaluation(element[1:4])
    test_time = timer
    metadata = element[7]
    description = stations[0][2] + " " + measurement[0][1] +" XT - Test"
    inspection_measurement_id = measurement[0][0]
    station_id = stations[0][0]
    part_id = part[0][0]
    type_inspection_id = 2

    parameter_inspection = conn.cursor()
    sql = '''INSERT INTO parameters_inspection (value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, inspection_measurement_id, station_id, part_id, type_inspection_id)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    val = (value, low_limit, high_limit, data_type, units, result, compoperator, test_time, metadata, description, inspection_measurement_id, station_id, part_id, type_inspection_id)
    parameter_inspection.execute(sql,val)
    conn.commit()

def duration(element,name_piece):
    element = element.split(',')
    
    from datetime import datetime, timezone 
    import rfc3339

    task_timestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(task_timestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(task_timestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    stations = []
    station_name = conn.cursor()
    station_name.execute('''SELECT station_id, station_key, station_name, status_id, type_station.ts_id, type_station.ts_name AS 'Name' FROM station 
                            inner JOIN data_tracking.type_station ON type_station.ts_id = station.ts_id
                            WHERE status_id=1''')
    station_name = station_name.fetchall()
    for x in station_name:
        stations.append(x)

    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE part_number ='"+name_piece+"' AND status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)
    
    if len(part) == 0:
        print("vacio")
        return "FAILED"

    station_id = stations[0][0]
    part_id = part[0][0]
    taskresult = element[1]
    tasktimestamp = timer
    taskduration = element[2]
    metadata = element[3]

    durations = conn.cursor()
    sql = '''INSERT INTO duration (station_id, part_id, taskresult, tasktimestamp, taskduration, metadata)
             VALUES (%s, %s, %s, %s, %s, %s)'''
    val = (station_id, part_id, taskresult, tasktimestamp, taskduration, metadata)
    durations.execute(sql,val)
    conn.commit()

    return "PASSED"
#################################################### Consultas para el archivo JSON ##############################################
def pieces():
    part = []
    part_name = conn.cursor()
    part_name.execute("SELECT part_id, part_number, model_id FROM part WHERE status_id=1")
    part_name = part_name.fetchall()
    for x in part_name:
        part.append(x)
    
    return part[0]

def duration_json(station_id, part_id):
    duration_data = []
    durationJson = conn.cursor()
    durationJson.execute("SELECT taskresult, tasktimestamp, taskduration, metadata FROM duration WHERE station_id ='"+str(station_id)+"' AND part_id = '"+str(part_id)+"'")
    durationJson = durationJson.fetchall()
    for x in durationJson:
        duration_data.append(x)
    return duration_data[0]

def inspection_data(part_id):
    inspection = []
    inspectionJson = conn.cursor()
    inspectionJson.execute('''SELECT parameters_inspection.inspection_measurement_id, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, inspection_measurement.name FROM parameters_inspection 
                           inner JOIN data_tracking.inspection_measurement ON inspection_measurement.inspection_measurement_id = parameters_inspection.inspection_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY inspection_measurement_id ASC")
    inspectionJson =inspectionJson.fetchall()
    for x in inspectionJson:
        inspection.append(x)
        
    return inspection

def screwing_data(part_id):
    screwing = []
    screwingJson = conn.cursor()
    screwingJson.execute('''SELECT parameters_screwing.screwing_measurement_id, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, screwing_measurement.name FROM parameters_screwing 
                           inner JOIN data_tracking.screwing_measurement ON screwing_measurement.screwing_measurement_id = parameters_screwing.screwing_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY screwing_measurement_id ASC")
    screwingJson =screwingJson.fetchall()
    for x in screwingJson:
        screwing.append(x)
        
    return screwing

def pressfit_data(part_id):
    pressfit = []
    pressfitJson = conn.cursor()
    pressfitJson.execute('''SELECT parameters_pressfit.pressfit_measurement_id, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, pressfit_measurement.name FROM parameters_pressfit 
                           inner JOIN data_tracking.pressfit_measurement ON pressfit_measurement.pressfit_measurement_id = parameters_pressfit.pressfit_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY pressfit_measurement_id ASC")
    pressfitJson =pressfitJson.fetchall()
    for x in pressfitJson:
        pressfit.append(x)
        
    return pressfit
############################################# View Table ###########################################################

def inspection_data2(part_id):
    inspection = []
    inspectionJson = conn.cursor()
    inspectionJson.execute('''SELECT inspection_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_inspection.inspection_measurement_id FROM parameters_inspection 
                           inner JOIN data_tracking.inspection_measurement ON inspection_measurement.inspection_measurement_id = parameters_inspection.inspection_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_inspection_id DESC LIMIT 6")
    inspectionJson =inspectionJson.fetchall()
    for x in inspectionJson:
        inspection.append(x)
        
    return inspection

def screwing_data2(part_id):
    screwing = []
    screwingJson = conn.cursor()
    screwingJson.execute('''SELECT screwing_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_screwing.screwing_measurement_id FROM parameters_screwing 
                           inner JOIN data_tracking.screwing_measurement ON screwing_measurement.screwing_measurement_id = parameters_screwing.screwing_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_screwing_id DESC LIMIT 6")
    screwingJson =screwingJson.fetchall()
    for x in screwingJson:
        screwing.append(x)
        
    return screwing

def pressfit_data2(part_id):
    pressfit = []
    pressfitJson = conn.cursor()
    pressfitJson.execute('''SELECT pressfit_measurement.name, value, low_limit, high_limit, data_type, unit, result, compoperator, test_time, metadata, description, parameters_pressfit.pressfit_measurement_id FROM parameters_pressfit 
                           inner JOIN data_tracking.pressfit_measurement ON pressfit_measurement.pressfit_measurement_id = parameters_pressfit.pressfit_measurement_id
                           WHERE part_id = '''+"'"+str(part_id)+"' ORDER BY parameters_pressfit_id DESC LIMIT 6")
    pressfitJson =pressfitJson.fetchall()
    for x in pressfitJson:
        pressfit.append(x)
        
    return pressfit