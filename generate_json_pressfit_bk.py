__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import json
import os
import os.path
from datetime import date
from datetime import datetime

today = date.today()
today_year = format(today.year)
today_month = today.strftime("%m")
today_day = format(today.day)

file_data_bk = "C:/AMC/JSON/"+today_year+"/"+today_month+"/"+today_day+"/"
file_data = "C:/Users/Tesla/Documents/Traceability/"+today_year+"/"+today_month+"/"+today_day+"/"

verify_file_bk = os.path.exists(file_data_bk)
verify_file = os.path.exists(file_data)


def pressfitJson(taskname,actorname,processname,sitecode,flowname,taskcollectionname,tasktimestamp,actorversion,actorlocation,flowstepname,thingname,taskresult,partnumber,taskduration,parameters,metadata,error,ncdimensiondetails,name_file):
    data = {}

    data['thingtaskdata'] = []
    data['thingtaskdata'].append({
        'taskname':taskname,
        'actorname':actorname,
        'processname':processname,
        'sitecode':sitecode,
        'flowname':flowname,
        # 'flowversion':flowversion,
        'taskcollectionname':taskcollectionname,
        'tasktimestamp':tasktimestamp,
        'actorversion':actorversion,
        'actorlocation':actorlocation,
        # 'actorlocation':actorlocation,
        'flowstepname':flowstepname,
        'thingname':thingname,
        'taskresult':taskresult,
        'partnumber':partnumber,
        "taskduration": taskduration,
        'parameters':parameters,
        'metadata':metadata,
        'error':error,
        'ncdimensiondetails':ncdimensiondetails
    })

    # with open("example/"+name_file + '.json', 'w') as file:
    #     json.dump(data, file, indent=4)

    if file_data_bk == True:
        with open(file_data_bk+name_file+ '.json', 'w') as file:
            json.dump(data, file, indent=4)
    else:
        os.makedirs(file_data_bk)
        with open(file_data_bk+name_file+ '.json', 'w') as file:
            json.dump(data, file, indent=4)


def pressfitJson2(flowname,metadata,sitecode,taskname,actorname,thingname,parameters,partnumber,taskresult,processname,actorversion,flowstepname,taskduration,actorlocation,tasktimestamp,taskcollectionname,name_file):
    today = date.today()
    today_year = format(today.year)
    today_month = today.strftime("%m")
    today_day = format(today.day)

    file_data_bk = "C:/AMC/JSON/"+today_year+"/"+today_month+"/"+today_day+"/"
    file_data = "C:/Users/Tesla/Documents/Traceability/"+today_year+"/"+today_month+"/"+today_day+"/"

    verify_file_bk = os.path.exists(file_data_bk)
    verify_file = os.path.exists(file_data)

    data = {}
    
    data['flowname'] = flowname
    data['metadata'] = metadata
    data['sitecode'] = sitecode
    data['taskname'] = taskname
    data['actorname'] = actorname
    data['thingname'] = thingname
    data['parameters'] = parameters
    data['partnumber'] = partnumber
    data['taskresult'] = taskresult
    data['processname'] = processname
    data['actorversion'] = actorversion
    data['flowstepname'] = flowstepname
    data['taskduration'] = taskduration
    data['actorlocation'] = actorlocation
    data['tasktimestamp'] = tasktimestamp
    data['taskcollectionname'] = taskcollectionname
    # })

    if verify_file_bk == True:
        try:
            with open(file_data_bk+name_file+ '.json', 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return str(e)
    else:
        try:
            os.makedirs(file_data_bk)
            with open(file_data_bk+name_file+ '.json', 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return str(e)

    if verify_file == True:
        try:
            with open(file_data+name_file+ '.json', 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return str(e)
    else:
        try:
            os.makedirs(file_data)
            with open(file_data+name_file+ '.json', 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return str(e)
        
    return "PASSED"

def pressfitJson3(flowstepname, flowname, actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file):
    try:
        from datetime import date
        import os
        import json

        today = date.today()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")

        # LIMPIAR EL NOMBRE DEL ARCHIVO - ESTA ES LA SOLUCIÓN PRINCIPAL
        # Remover caracteres de nueva línea y otros caracteres problemáticos
        clean_name_file = name_file.replace('\n', '').replace('\r', '').replace('\t', '')
        clean_name_file = clean_name_file.replace(':', '_').replace('/', '_').replace('\\', '_')
        clean_name_file = clean_name_file.replace('?', '_').replace('*', '_').replace('"', '_')
        clean_name_file = clean_name_file.replace('<', '_').replace('>', '_').replace('|', '_')
        
        # También limpiar espacios múltiples
        clean_name_file = ' '.join(clean_name_file.split())

        file_data_bk = "C:/AMC/JSON/"+today_year+"/"+today_month+"/"+today_day+"/"
        file_data = "C:/Users/Tesla/Documents/Traceability/"+today_year+"/"+today_month+"/"+today_day+"/"

        data = {
            'flowstepname': flowstepname,
            'flowname': flowname,
            'actorname': actorname,
            'actorversion': actorversion,
            'actorlocation': actorlocation,
            'parameters': parameters,
            'partnumber': partnumber,
            'schema': schema,
            'sitecode': sitecode,
            'taskduration': taskduration,
            'taskname': taskname,
            'taskresult': taskresult,
            'tasktimestamp': tasktimestamp,
            'thingname': thingname
        }

        success_count = 0

        # Para la primera ubicación
        try:
            os.makedirs(file_data_bk, exist_ok=True)
            full_path_bk = file_data_bk + clean_name_file + '.json'
            with open(full_path_bk, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación BK: {e}")

        # Para la segunda ubicación
        try:
            os.makedirs(file_data, exist_ok=True)
            full_path = file_data + clean_name_file + '.json'
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación Main: {e}")

        return "PASSED" if success_count > 0 else "FAILED"

    except Exception as e:
        return f"FAILED - {str(e)}"
    
def pressfitJson4(action, flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file, flowversion):
    try:
        from datetime import date
        import os
        import json

        today = date.today()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")

        # LIMPIAR EL NOMBRE DEL ARCHIVO - ESTA ES LA SOLUCIÓN PRINCIPAL
        # Remover caracteres de nueva línea y otros caracteres problemáticos
        clean_name_file = name_file.replace('\n', '').replace('\r', '').replace('\t', '')
        clean_name_file = clean_name_file.replace(':', '_').replace('/', '_').replace('\\', '_')
        clean_name_file = clean_name_file.replace('?', '_').replace('*', '_').replace('"', '_')
        clean_name_file = clean_name_file.replace('<', '_').replace('>', '_').replace('|', '_')
        
        # También limpiar espacios múltiples
        clean_name_file = ' '.join(clean_name_file.split())

        file_data_bk = "C:/AMC/JSON/"+today_year+"/"+today_month+"/"+today_day+"/"
        file_data = "C:/Users/Tesla/Documents/Traceability/"+today_year+"/"+today_month+"/"+today_day+"/"

        data = {
            'action':action,
            'parameters': parameters,
            'partnumber': partnumber,
            'taskname': taskname,
            'taskresult': taskresult,
            'flowstepname': flowstepname,
            'sitecode': sitecode,
            'actorname': actorname,
            'actorversion': actorversion,
            'actorlocation': actorlocation,
            'tasktimestamp': tasktimestamp,
            'taskduration': taskduration,
            'thingname': thingname,
            'flowversion': flowversion,
            'flowname': flowname
        }

        success_count = 0

        # Para la primera ubicación
        try:
            os.makedirs(file_data_bk, exist_ok=True)
            full_path_bk = file_data_bk + clean_name_file + '.json'
            with open(full_path_bk, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación BK: {e}")

        # Para la segunda ubicación
        try:
            os.makedirs(file_data, exist_ok=True)
            full_path = file_data + clean_name_file + '.json'
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación Main: {e}")

        return "PASSED" if success_count > 0 else "FAILED"

    except Exception as e:
        return f"FAILED - {str(e)}"
    
def pressfitJson5(action, flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskname, tasktimestamp, thingname, name_file, flowversion):
    try:
        from datetime import date
        import os
        import json

        today = date.today()
        today_year = str(today.year)
        today_month = today.strftime("%m")
        today_day = today.strftime("%d")

        # LIMPIAR EL NOMBRE DEL ARCHIVO - ESTA ES LA SOLUCIÓN PRINCIPAL
        # Remover caracteres de nueva línea y otros caracteres problemáticos
        clean_name_file = name_file.replace('\n', '').replace('\r', '').replace('\t', '')
        clean_name_file = clean_name_file.replace(':', '_').replace('/', '_').replace('\\', '_')
        clean_name_file = clean_name_file.replace('?', '_').replace('*', '_').replace('"', '_')
        clean_name_file = clean_name_file.replace('<', '_').replace('>', '_').replace('|', '_')
        
        # También limpiar espacios múltiples
        clean_name_file = ' '.join(clean_name_file.split())

        file_data_bk = "C:/AMC/RETRY/JSON/"+today_year+"/"+today_month+"/"+today_day+"/"
        file_data = "C:/Users/Tesla/Documents/Traceability/"+today_year+"/"+today_month+"/"+today_day+"/"

        data = {
            'action':action,
            'parameters': parameters,
            'partnumber': partnumber,
            'taskname': taskname,
            'flowstepname': flowstepname,
            'sitecode': sitecode,
            'actorname': actorname,
            'actorversion': actorversion,
            'actorlocation': actorlocation,
            'tasktimestamp': tasktimestamp,
            'thingname': thingname,
            'flowversion': flowversion,
            'flowname': flowname
        }

        success_count = 0

        # Para la primera ubicación
        try:
            os.makedirs(file_data_bk, exist_ok=True)
            full_path_bk = file_data_bk + clean_name_file + '.json'
            with open(full_path_bk, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación BK: {e}")

        # Para la segunda ubicación
        try:
            os.makedirs(file_data, exist_ok=True)
            full_path = file_data + clean_name_file + '.json'
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            success_count += 1
        except Exception as e:
            print(f"Error en ubicación Main: {e}")

        return "PASSED" if success_count > 0 else "FAILED"

    except Exception as e:
        return f"FAILED - {str(e)}"