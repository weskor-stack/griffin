__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"


import generate_json_pressfit
import get_name_PC
from datetime import datetime, timezone 
import rfc3339
import conexion

################################## Fecha actual de la computadora ##################################

tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
last_digit = str(tasktimestamp)
last_digit = last_digit.split('-')
timer2 = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

####################################################################################################
def json_file(parte):
    print(parte)
    action = "completetask"
    tasktimestamp = datetime.now(timezone.utc).astimezone()#"2024-04-02T10:00:32Z 18:46:54"
    last_digit = str(tasktimestamp)
    last_digit = last_digit.split('-')
    timer2 = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

    indice = 0
    indice2 = 0
    indice3 = 0
    indice4 = 0
    indice5 = 0
    indice6 = 0

    parameters = []

    station = conexion.stations()

    model = conexion.model()

    task_name = model[2][0]
    
    type_station = station[4]

    name = conexion.pieces(parte)
    piece_id = name[0]
    duration = conexion.duration_json(station[0], piece_id)
    name = name[1]

    station = station[2]

    divisor = name.index(":")

    flowversion = 1
    flowstepname = "PEGATRON" #"DummyGoldenStateFlow" #model[2][1]
    flowname = "PEGATRON" #"DummyGoldenStateFlow"
    actorname = conexion.model() #get_name_PC.getName()
    actorname = actorname[0][2]
    actorversion = ""
    actorlocation = "Pegatron - MX"

    # if type_station == 1:
    #     screwing = conexion.screwing_data(piece_id)
    #     parameters = []
    #     for x in screwing:
    #         if x[0] == 1:
    #             indice +=1
    #         if x[0] == 2:
    #             indice2 +=1
    #             indice = indice2
    #         if x[0] == 3:
    #             indice3 +=1
    #             indice = indice3
    #         if x[0] == 4:
    #             indice4 +=1
    #             indice = indice4

    #         parameters.append(
    #             {
    #                 "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
    #                 "description": x[10] +" STEP "+str(indice),
    #                 "units": x[5],
    #                 "type": x[4],
    #                 "result": x[6],
    #                 "testtime": x[8],
    #                 "compoperator": x[7],
    #                 "lowerlimit": x[2],
    #                 "upperlimit": x[3],
    #                 "value": x[1],
    #                 "expectedvalue": 'null'
    #             }
    #         )
    # elif type_station == 2:
    #     pressfit = conexion.pressfit_data(piece_id)
    #     parameters = []
    #     for x in pressfit:
    #         if x[0] == 1:
    #             indice +=1
    #         if x[0] == 2:
    #             indice2 +=1
    #             indice = indice2
    #         if x[0] == 3:
    #             indice3 +=1
    #             indice = indice3

    #         parameters.append(
    #             {
    #                 "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
    #                 "description": x[10]+" STEP "+str(indice),
    #                 "units": x[5],
    #                 "type": x[4],
    #                 "result": x[6],
    #                 "testtime": x[8],
    #                 "compoperator": x[7],
    #                 "lowerlimit": x[2],
    #                 "upperlimit": x[3],
    #                 "value": x[1],
    #                 "dwelltime": x[12],
    #                 "expectedvalue": 'null'
    #             }
    #         )
            
    # elif type_station == 3:
    #     inspections = conexion.inspection_data3(piece_id)
    #     parameters = []
    #     for x in inspections:
    #         if x[0] == 1:
    #             indice +=1
    #         if x[0] == 2:
    #             indice2 +=1
    #             indice = indice2
    #         if x[0] == 3:
    #             indice3 +=1
    #             indice = indice3
    #         if x[0] == 4:
    #             indice4 +=1
    #             indice = indice4
    #         if x[0] == 5:
    #             indice5 +=1
    #             indice = indice5
    #         if x[0] == 6:
    #             indice6 +=1
    #             indice = indice6

    #         parameters.append(
    #             {
    #                 "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
    #                 "description": x[10]+" STEP "+str(indice),
    #                 "units": x[5],
    #                 "type": x[4],
    #                 "testtime": x[8],
    #                 "compoperator": x[7],
    #                 "lowerlimit": x[2],
    #                 "upperlimit": x[3],
    #                 "value": x[1],
    #                 "expectedvalue": 'null'
    #             }
    #         )

    if type_station == 4:
        print(f"La pieza es {piece_id}")
        parameters = []
        resultado = ""
        screwing = conexion.screwing_data(piece_id)
        print(f"Los datos de screwing son {screwing}")
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

            if x[6] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "name": x[10], # Nombre de la estación más nombre del elemento a probar
                    "description": x[9],
                    "result": resultado, #x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        pressfit = conexion.pressfit_data(piece_id)
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

            if x[6] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "name": x[11], # Nombre de la estación
                    "description": x[9],
                    "result": resultado, #x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        inspections = conexion.inspection_data(piece_id)
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
            
            if x[6] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "name": x[11], # Nombre de la estación
                    "description": x[9],
                    "result": resultado, #x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        electrical = conexion.electrical_data(piece_id)
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

            if x[6] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"

            parameters.append(
                {
                    "type": x[4],
                    "compoperator": x[7],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "value": x[1],
                    "name": x[11],
                    "description": x[9],
                    "result": resultado, #x[6],
                    "testtime": x[8],
                    "units": x[5]
                }
            )

        continuity = conexion.continuity_data(piece_id)
        indice = 0

        for x in continuity:

            tiempo = x[9].astimezone()
            last_digit = str(tiempo).split('-')
            timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
            indice +=1
            
            if x[6] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"

            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[2],
                    "lowerlimit": x[3],
                    "upperlimit": x[4],
                    "value": x[7],
                    "name": x[0],
                    "description": x[1],
                    "result": resultado, #x[6],
                    "testtime": timer, #x[9],
                    "units": x[5]
                }
            )
        
        leak = conexion.leaktest_data(piece_id)
        indice = 0
        
        for x in leak:
            tiempo = x[10].astimezone()
            last_digit = str(tiempo).split('-')
            timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
            indice +=1

            if x[3] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"
            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[8],
                    "lowerlimit": x[6],
                    "upperlimit": x[7],
                    "value": x[2],
                    "name": x[9],
                    "description": x[5],
                    "result": resultado, #x[3],
                    "testtime": timer, #x[9],
                    "units": x[4] #leak
                }
            )

        welding = conexion.welding_data(piece_id)
        indice = 0
        
        for x in welding:
            tiempo = x[9].astimezone()
            last_digit = str(tiempo).split('-')
            timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
            indice +=1

            if x[5] == "PASSED":
                resultado = "Passed"
            else:
                resultado = "Failed"
            
            parameters.append(
                {
                    "type": "Nummeric",
                    "compoperator": x[8],
                    "lowerlimit": "",
                    "upperlimit": "",
                    "value": x[3],
                    "name": x[0],
                    "description": x[4],
                    "result": resultado, #x[5],
                    "testtime": timer, #x[9],
                    "units": x[6]
                }
            )
            
        heatstake = conexion.heatstake_data(piece_id)
        indice = 0
        configurador = conexion.configurador()
        machine_id = configurador[0]
        for x in heatstake:
            # tiempo = x[9].astimezone()
            # last_digit = str(tiempo).split('-')
            # timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
            indice +=1
            
            parameters.extend(
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Cycle time",
                    "component_id": x[1]
                },
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Machine ID",
                    "component_id": machine_id
                },
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Laser program name + version",
                    "component_id": x[3]
                },
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Grade",
                    "component_id": x[5]
                },
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Part Number",
                    "component_id": x[2]
                }
            )

        graph = conexion.graph_data(piece_id)
        indice = 0
        for x in graph:
            # tiempo = x[9].astimezone()
            # last_digit = str(tiempo).split('-')
            # timer = rfc3339.rfc3339(tiempo, utc=True, use_system_timezone=False) + " " + last_digit[3]
            indice +=1
            
            parameters.append(
                {
                    "command": "AddNonTrackedComponent",
                    "ref_designator": "Graph",
                    "component_id": x[1]
                }
            )

        temperature = conexion.temperature_data(piece_id)
        indice = 0
        
        for x in temperature:
            indice +=1

            parameters.append(
                {
                    "name": str(indice)+'b. '+station+" Test", # Nombre de la estación más nombre del elemento a probar
                    "description": x[6]+" STEP "+str(indice),
                    "start_time": x[1],
                    "end_time": x[2],
                    "initial_temperature": x[3],
                    "final_temperature": x[4],
                    "unit" : x[5]
                }
            )

        componente = conexion.component_data(piece_id)
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
    tasktimestamp = timer2
    thingname = name[14:]
   
    # name2 = name.replace("-","_")
    # name2 = name2.replace(":","_")

    # name_file = str(tasktimestamp[0:19])
    # name_file = name_file.replace("-","_")
    # name_file = name_file.replace(":","_")
    # name_file = name_file.replace(" ","_")
    name2 = name.replace("-", "_").replace(":", "_")
    name_file = str(timer2[0:19]).replace("-", "_").replace(":", "_").replace(" ", "_")

    name_file = name2+"_"+name_file+"_"+taskresult+"_"+taskname
    
    # json_file = generate_json_pressfit.pressfitJson3(flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file)

    json_file = generate_json_pressfit.pressfitJson4(action, flowstepname, flowname,actorname, actorversion, actorlocation, parameters, partnumber, schema, sitecode, taskduration, taskname, taskresult, tasktimestamp, thingname, name_file, flowversion)
    return json_file
#############################################################################################################################################################################################################################################################


# json_file()