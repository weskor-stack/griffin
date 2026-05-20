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
timer = rfc3339.rfc3339(tasktimestamp, utc=True, use_system_timezone=False)+" "+last_digit[3]

####################################################################################################
def json_file():
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

    station = conexion.stations()
    type_station = station[4]

    name = conexion.pieces()
    piece_id = name[0]
    duration = conexion.duration_json(station[0], piece_id)
    name = name[1]

    station = station[2]

    divisor = name.index(":")

    flowname = "Sanmina-Automatyco-"
    metadata = duration[3] # tabla duration
    sitecode = name[divisor+2:divisor+5] #"HG2"
    taskname = station
    actorname = get_name_PC.getName()
    thingname = name

    if type_station == 1:
        screwing = conexion.screwing_data(piece_id)
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
                    "name": station+" - "+x[11]+" # "+str(indice), # Nombre de la estación más nombre del elemento a probar
                    "type": x[4],
                    "units": x[5],
                    "value": x[1],
                    "result": x[6],
                    "metadata": x[9],
                    "test_time": x[8],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "description": x[10] +" # "+str(indice),
                    "compoperator": x[7]
                }
            )
    elif type_station == 2:
        pressfit = conexion.pressfit_data(piece_id)
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
                    "name": station+" - "+x[11]+" # "+str(indice), # Nombre de la estación más nombre del elemento a probar
                    "type": x[4],
                    "units": x[5],
                    "value": x[1],
                    "result": x[6],
                    "metadata": x[9],
                    "test_time": x[8],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "description": x[10]+" # "+str(indice),
                    "compoperator": x[7]
                }
            )
            
    elif type_station == 3:
        inspections = conexion.inspection_data(piece_id)
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
                    "name": station+" - "+x[11]+" # "+str(indice), # Nombre de la estación más nombre del elemento a probar
                    "type": x[4],
                    "units": x[5],
                    "value": x[1],
                    "result": x[6],
                    "metadata": x[9],
                    "test_time": x[8],
                    "lowerlimit": x[2],
                    "upperlimit": x[3],
                    "description": x[10]+" # "+str(indice),
                    "compoperator": x[7]
                }
            )


    partnumber = name[1:divisor] #"1895152-00-G"
    taskresult = duration[0] # tabla duration
    processname = ""
    actorversion = "v1.0.0"
    flowstepname = station # Nombre de la estación
    taskduration = duration[2] # tabla duration
    actorlocation = "Sanmina Guadalajara Plant 2: Sanmina Guadalajara Plant 2"
    tasktimestamp = timer
    taskcollectionname = ""

    name2 = name.replace("-","_")
    name2 = name2.replace(":","_")

    name_file = str(tasktimestamp[0:19])
    name_file = name_file.replace("-","_")
    name_file = name_file.replace(":","_")
    name_file = name_file.replace(" ","_")

    name_file = name2+"_"+name_file+"_"+taskresult+"_"+taskname
    
    json_file = generate_json_pressfit.pressfitJson2(flowname,metadata,sitecode,taskname,actorname,thingname,parameters,partnumber,taskresult,processname,actorversion,flowstepname,taskduration,actorlocation,tasktimestamp,taskcollectionname,name_file)

    return json_file