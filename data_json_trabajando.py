__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"


import generate_json_pressfit
import get_name_PC
from datetime import datetime, timezone 
import rfc3339
import conexion_trabajando

################################## Fecha actual de la computadora ##################################

tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
last_digit = str(tasktimestamp)
last_digit = last_digit.split('-')
timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

####################################################################################################
def json_file():
    
    action = "completetask"
    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    indice5 = 0
    indice6 = 0

    parameters = []

    station = conexion_trabajando.stations()

    model = conexion_trabajando.model()

    task_name = model[2][0]
    
    type_station = station[4]

    name = conexion_trabajando.pieces()
    piece_id = name[0]
    duration = conexion_trabajando.duration_json(station[0], piece_id)
    name = name[1]

    station = station[2]

    divisor = name.index(":")

    flowversion = 1
    flowstepname = "PEGATRON" #"DummyGoldenStateFlow" #model[2][1]
    flowname = "PEGATRON" #"DummyGoldenStateFlow"
    actorname = get_name_PC.getName()
    actorversion = "1.1-130-g12b05f3"
    actorlocation = "PEGATRON"

    if type_station == 1:
        screwing = conexion_trabajando.screwing_data(piece_id)
        parameters = []
        for x in screwing:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3
            if x[0] == 4:
                indice4 +=1
                indice = indice4

            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10] +" STEP "+str(indice),
                    "units": x[5],
                    "type": x[4],
                    "result": x[6],
                    "testtime": x[8],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "expectedvalue": 'null'
                }
            )
    elif type_station == 2:
        pressfit = conexion_trabajando.pressfit_data(piece_id)
        parameters = []
        for x in pressfit:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3

            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10]+" STEP "+str(indice),
                    "units": x[5],
                    "type": x[4],
                    "result": x[6],
                    "testtime": x[8],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "dwelltime": x[12],
                    "expectedvalue": 'null'
                }
            )
            
    elif type_station == 3:
        inspections = conexion_trabajando.inspection_data(piece_id)
        parameters = []
        for x in inspections:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3
            if x[0] == 4:
                indice4 +=1
                indice = indice4
            if x[0] == 5:
                indice5 +=1
                indice = indice5
            if x[0] == 6:
                indice6 +=1
                indice = indice6

            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10]+" STEP "+str(indice),
                    "units": x[5],
                    "type": x[4],
                    "testtime": x[8],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "expectedvalue": 'null'
                }
            )

    elif type_station == 4:
        parameters = []
        screwing = conexion_trabajando.screwing_data(piece_id)
        for x in screwing:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3
            if x[0] == 4:
                indice4 +=1
                indice = indice4

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "value": x[1],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10] +" STEP "+str(indice),
                    "result": x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        pressfit = conexion_trabajando.pressfit_data(piece_id)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        indice5 = 0
        indice6 = 0
        for x in pressfit:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "value": x[1],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10] +" STEP "+str(indice),
                    "result": x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        inspections = conexion_trabajando.inspection_data(piece_id)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        indice5 = 0
        indice6 = 0
        for x in inspections:
            if x[0] == 1:
                indice +=1
            if x[0] == 2:
                indice2 +=1
                indice = indice2
            if x[0] == 3:
                indice3 +=1
                indice = indice3
            if x[0] == 4:
                indice4 +=1
                indice = indice4
            if x[0] == 5:
                indice5 +=1
                indice = indice5
            if x[0] == 6:
                indice6 +=1
                indice = indice6

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "value": x[1],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10] +" STEP "+str(indice),
                    "result": x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        electrical = conexion_trabajando.electrical_data(piece_id)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        
        for x in electrical:
            if x[0] == 1:
                indice += 1
            if x[0] == 2:
                indice2 += 1
                indice = indice2
            if x[0] == 3:
                indice3 += 1
                indice = indice3
            if x[0] == 4:
                indice4 += 1
                indice = indice4

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "value": x[1],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[10] +" STEP "+str(indice),
                    "result": x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        continuity = conexion_trabajando.continuity_data(piece_id)
        indice = 0

        for x in continuity:
            indice +=1
            
            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[2],
                    "value": x[7],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[1] +" STEP "+str(indice),
                    "result": x[6],
                    "testtime": x[9],
                    "units": x[5]
                }
            )
        
        leak = conexion_trabajando.leaktest_data(piece_id)
        indice = 0
        
        for x in leak:
            indice +=1

            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[8],
                    "value": x[2],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[5] +" STEP "+str(indice),
                    "result": x[3],
                    "testtime": x[9],
                    "leak": x[4] #units
                }
            )

        welding = conexion_trabajando.welding_data(piece_id)
        indice = 0
        
        for x in welding:
            indice +=1

            parameters.append(
                {
                    "type": "Nummeric",
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[4]+" STEP "+str(indice),
                    "welding_time": x[1],
                    "welding_power": x[2],
                    "collapse_distance": x[3],
                    "result": x[5],
                    "unit" : x[6]
                }
            )

        temperature = conexion_trabajando.temperature_data(piece_id)
        indice = 0
        
        for x in temperature:
            indice +=1

            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[9],
                    "lowerlimit":[10],
                    "upperlimit":[11],
                    "value": x[12],
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[6] +" STEP "+str(indice),
                    "result": x[13],
                    "testtime": x[9],
                    "units": x[5]
                }
            )

        componente = conexion_trabajando.component_data(piece_id)
        indice = 1
        
        for x in componente:
            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "key_part": x[0]
                }
            )
            indice += 1

    
    partnumber = name[1:divisor] #"1895152-00-G"
    schema = ""
    sitecode = name[divisor+2:divisor+5] #"HG2"
    taskduration = duration[2] # tabla duration
    taskname = task_name
    taskresult = duration[0] # tabla duration
    tasktimestamp = timer
    thingname = name
   
    name2 = name.replace("-","_")
    name2 = name2.replace(":","_")

    name_file = str(tasktimestamp[0:19])
    name_file = name_file.replace("-","_")
    name_file = name_file.replace(":","_")
    name_file = name_file.replace(" ","_")

    name_file = name2+"_"+name_file+"_"+taskresult+"_"+taskname
    
    # json_file = generate_json_pressfit.pressfitJson3(flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file)

    json_file = generate_json_pressfit.pressfitJson4(action, flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file, flowversion)
    return json_file
#############################################################################################################################################################################################################################################################
def json_file2(limite):
    action = "completetask"
    tasktimestamp = datetime.now(timezone.utc).astimezone()
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    indice5 = 0
    indice6 = 0

    parameters = []

    station = conexion_trabajando.stations()
    model = conexion_trabajando.model()
    task_name = model[2][0]
    type_station = station[4]
    name = conexion_trabajando.pieces()
    piece_id = name[0]
    name = name[1]
    station = station[2]
    divisor = name.index(":")

    flowversion = 1
    flowstepname = "PEGATRON"
    flowname = "PEGATRON"
    actorname = get_name_PC.getName()
    actorversion = "1.1-130-g12b05f3"
    actorlocation = "PEGATRON"

    if type_station == 4:
        parameters = []
        
        # Screwing data - CORREGIDO
        screwing = conexion_trabajando.screwing_data3(piece_id, limite)
        for x in screwing:
            if x[0] == 1:
                indice += 1
            elif x[0] == 2:
                indice2 += 1
                indice = indice2
            elif x[0] == 3:
                indice3 += 1
                indice = indice3
            elif x[0] == 4:
                indice4 += 1
                indice = indice4

            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[10] +" STEP "+str(indice),
                "units": x[5],
                "type": x[4],
                "result": x[6],
                "testtime": x[8],
                "compoperator": x[7],
                "lowerlimit": x[2],
                "upperlimit": x[3],
                "value": x[1]
            })
        
        # Pressfit data - CORREGIDO
        pressfit = conexion_trabajando.pressfit_data3(piece_id, limite)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        indice5 = 0
        indice6 = 0
        for x in pressfit:
            if x[0] == 1:
                indice += 1
            elif x[0] == 2:
                indice2 += 1
                indice = indice2
            elif x[0] == 3:
                indice3 += 1
                indice = indice3

            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[10]+" STEP "+str(indice),
                "units": x[5],
                "type": x[4],
                "result": x[6],
                "testtime": x[8],
                "compoperator": x[7],
                "lowerlimit": x[2],
                "upperlimit": x[3],
                "value": x[1],
                "dwelltime": x[12]
            })

        # Inspections data - CORREGIDO
        inspections = conexion_trabajando.inspection_data3(piece_id, limite)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        indice5 = 0
        indice6 = 0
        for x in inspections:
            if x[0] == 1:
                indice += 1
            elif x[0] == 2:
                indice2 += 1
                indice = indice2
            elif x[0] == 3:
                indice3 += 1
                indice = indice3
            elif x[0] == 4:
                indice4 += 1
                indice = indice4
            elif x[0] == 5:
                indice5 += 1
                indice = indice5
            elif x[0] == 6:
                indice6 += 1
                indice = indice6

            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[10]+" STEP "+str(indice),
                "units": x[5],
                "type": x[4],
                "testtime": x[8],
                "compoperator": x[7],
                "lowerlimit": x[2],
                "upperlimit": x[3],
                "value": x[1]
            })

        # Electrical data - CORREGIDO
        electrical = conexion_trabajando.electrical_data3(piece_id, limite)
        indice = 0
        indice2 = 0
        indice3 = 0
        indice4 = 0
        
        for x in electrical:
            if x[0] == 1:
                indice += 1
            elif x[0] == 2:
                indice2 += 1
                indice = indice2
            elif x[0] == 3:
                indice3 += 1
                indice = indice3
            elif x[0] == 4:
                indice4 += 1
                indice = indice4

            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[10]+" STEP "+str(indice),
                "units": x[5],
                "type": x[4],
                "testtime": x[8],
                "compoperator": x[7],
                "lowerlimit": x[2],
                "upperlimit": x[3],
                "value": x[1],
                "result": x[6]
            })

        # Continuity data - CORREGIDO
        continuity = conexion_trabajando.continuity_data3(piece_id, limite)
        indice = 0

        for x in continuity:
            indice += 1
            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[1]+" STEP "+str(indice),
                "units": x[5],
                "compoperator": x[2],
                "lowerlimit": x[3],
                "upperlimit": x[4],
                "value": x[7],
                "result": x[6],
                "defect_code": x[8]
            })
            
        # Leak data - CORREGIDO
        leak = conexion_trabajando.leaktest_data3(piece_id, limite)
        indice = 0
        
        for x in leak:
            indice += 1
            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[5]+" STEP "+str(indice),
                "leak": x[4],
                "lowerlimit": x[6],
                "upperlimit": x[7],
                "trial_period": x[1],
                "value": x[2],
                "result": x[3]
            })

        # Welding data - CORREGIDO
        welding = conexion_trabajando.welding_data3(piece_id, limite)
        indice = 0
        
        for x in welding:
            indice += 1
            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[4]+" STEP "+str(indice),
                "welding_time": x[1],
                "welding_power": x[2],
                "collapse_distance": x[3],
                "result": x[5],
                "unit" : x[6]
            })

        # Temperature data - CORREGIDO
        temperature = conexion_trabajando.temperature_data3(piece_id, limite)
        indice = 0
        
        for x in temperature:
            indice += 1
            parameters.append({
                "name": str(indice)+'b. '+station+" Test",
                "description": x[6]+" STEP "+str(indice),
                "start_time": x[1],
                "end_time": x[2],
                "initial_temperature": x[3],
                "final_temperature": x[4],
                "unit" : x[5]
            })

        componente = conexion_trabajando.component_data(piece_id)
        indice = 1
        
        for x in componente:
            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "key_part": x[0]
                }
            )
            indice += 1
    partnumber = name[1:divisor]
    schema = ""
    sitecode = name[divisor+2:divisor+5]
    taskname = task_name
    tasktimestamp = timer
    thingname = name
   
    name2 = name.replace("-","_")
    name2 = name2.replace(":","_")

    name_file = str(tasktimestamp[0:19])
    name_file = name_file.replace("-","_")
    name_file = name_file.replace(":","_")
    name_file = name_file.replace(" ","_")

    name_file = name2+"_"+name_file+"_"+taskname
    
    json_file = generate_json_pressfit.pressfitJson5(
        action, flowstepname, flowname, actorname, 
        actorversion, actorlocation, parameters, partnumber, 
        schema, sitecode, taskname, tasktimestamp, thingname, 
        name_file, flowversion
    )
    return json_file

# json_file()