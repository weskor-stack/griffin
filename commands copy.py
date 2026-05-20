__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

# maria DB
import conexion


cadenas = "commit,Pressfit,F,50,10,100,Numeric,N,PASSED,Comentarios,dwell_time,D,500,498,502,Numeric,mm,PASSED,Comentarios,dwell_time,S,100,95,110,Numeric,mm/s,PASSED,Comentarios,dwell_time,1/"
screwing = "commit,Screwing,T,1.25,1,1.8,Numeric,N,PASSED,Comentario,A,31250,2900,3500,Numeric,degrees,FAILED,Comentario,PX,50,47,55,Numeric,mm,PASSED,Comentario,PY,150,140,160,Numeric,mm,PASSED,Comentario,1/"
inspection_vs = "commit,Inspection,VS,M,8000,7500,8500,Numeric,N,PASSED,Comentarios,PX,500,475,525,Numeric,mm,PASSED,Comentarios,PY,500,475,525,Numeric,mm,PASSED,Comentarios,1/"
inspection_xt = "commit,Inspection,XT,PX,500,475,525,Numeric,mm,PASSED,Comentarios,PY,500,475,525,Numeric,mm,PASSED,Comentarios,CPC,400,395,405,Numeric,mm,PASSED,Comentarios,CPE,400,395,405,Numeric,mm,PASSED,Comentarios,CAD,1,1,1,Boolean,DBU,PASSED,Comentarios,1/"
electrical = "commit,Electrical,Ct,1.25,1,1.8,Numeric,N,OK,Comentario,V,31250,2900,3500,Numeric,degrees,FAILED,Comentario,Cr,50,47,55,Numeric,mm,PASSED,Comentario,R,150,140,160,Numeric,mm,PASSED,Comentario,1/"

continuity_ok = 'commit,Continuity,Continuity1,10,50,F,PASS,20,Ejemplo de error del defecto,1/'

continuity_fail = 'commit,Continuity,Continuity1,10,50,F,FAIL,5,Ejemplo de error del defecto,1/'

leak1 = "commit,Leak,tiempo_prueba,resultado,PASSED/FAILED,unit,descripcion,extra1,extra2,1/"
leak2 = "commit,Leak,33.2 sec,14.25 psi,1,,descripcion,low_limit,High_limit,1/"
temperatura = "commit,Temperature,start (timestamp),salida al proceso (timestamp),temp_inicial,temp_final,unit,descripcion,extra1,extra2,1/"
welding = 'commit,Welding,welding_time,welding_power,100,mm,PASSED,description,1/'

cadenas = temperatura.split(',')
# print(len(cadenas))
name = "P210211-01-C:SANN25161400003"

def commit(cadena, name_piece):
    options = cadena.split(',')
    data_for_table = []
    # print(cadena)
    # return options[1]
    # print(len(options))
    
    match options[1]:
        case "Pressfit":
            # station = conexion.stations()
            if len(options) == 31:
                force = options[2:11]
                distance = options[11:20]
                speed = options[20:-2]
                # print(force)
                # print(distance)
                # print(speed)
                result = ""
                result_distance = ""
                result_speed = ""
                if force[6] =='1':
                    result = "PASS"
                else:
                    result = "FAIL"
                
                if distance[6] =='1':
                    result_distance = "PASS"
                else:
                    result_distance = "FAIL"
                
                if speed[6] =='1':
                    result_speed = "PASS"
                else:
                    result_speed = "FAIL"

                if force[0] == 'F' and distance[0] == 'D' and speed[0] == 'S':
                    force_measurement = conexion.parameters_pressfit(force,name_piece)
                    data_for_table.append([
                        "Force",  # Measurement
                        force[1],  # Value
                        force[2],  # Lower limit
                        force[3],  # Upper limit
                        force[4],  # Type
                        force[5],  # Unit
                        result
                        # force[8]   # Result
                    ])
                    distance_measurement = conexion.parameters_pressfit(distance,name_piece)
                    data_for_table.append([
                       "Distance",  # Measurement
                        distance[1],  # Value
                        distance[2],  # Lower limit
                        distance[3],  # Upper limit
                        distance[4],  # Type
                        distance[5],  # Unit
                        result_distance
                        # distance[8]   # Result
                    ])
                    speed_measurement = conexion.parameters_pressfit(speed,name_piece)
                    data_for_table.append([
                        "Speed",  # Measurement
                        speed[1],  # Value
                        speed[2],  # Lower limit
                        speed[3],  # Upper limit
                        speed[4],  # Type
                        speed[5],  # Unit
                        result_speed
                        # speed[8]   # Result
                    ])
                        
                    return "PASSED", data_for_table
                else:
                    return "FAILED", []
            else:
                return "FAILED", []
        case "Screwing":
            if len(options) == 36:
                torque = options[2:10]
                angle = options[10:18]
                px = options[18:26]
                py = options[26:-2]

                result_torque = ""
                result_angle = ""
                result_spx = ""
                result_spy = ""

                # print(torque)
                # print(angle)
                # print(px)
                # print(py)
                if torque[6] =='1':
                    result_torque = "PASS"
                else:
                    result_torque = "FAIL"
                
                if angle[6] =='1':
                    result_angle = "PASS"
                else:
                    result_angle = "FAIL"
                
                if px[6] =='1':
                    result_spx = "PASS"
                else:
                    result_spx = "FAIL"
                
                if py[6] =='1':
                    result_spy = "PASS"
                else:
                    result_spy = "FAIL"

                if torque[0] == 'T' and angle[0] == 'A' and px[0] == 'PX' and py[0] == 'PY':
                    torque_measurement = conexion.parameters_screwing(torque,name_piece)
                    if torque_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Torque",  # Measurement
                            torque[1],  # Value
                            torque[2],  # Lower limit
                            torque[3],  # Upper limit
                            torque[4],  # Type
                            torque[5],  # Unit
                            result_torque
                            # torque[8]   # Result
                        ])
                    angle_measurement = conexion.parameters_screwing(angle,name_piece)
                    if angle_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Angle",  # Measurement
                            angle[1],  # Value
                            angle[2],  # Lower limit
                            angle[3],  # Upper limit
                            angle[4],  # Type
                            angle[5],  # Unit
                            result_angle
                            # angle[8]   # Result
                        ])
                    px_measurement = conexion.parameters_screwing(px,name_piece)
                    if px_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Pull test",  # Measurement
                            px[1],  # Value
                            px[2],  # Lower limit
                            px[3],  # Upper limit
                            px[4],  # Type
                            px[5],  # Unit
                            result_spx
                            # px[8]   # Result
                        ])
                    py_measurement = conexion.parameters_screwing(py,name_piece)
                    if py_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Position y",  # Measurement
                            py[1],  # Value
                            py[2],  # Lower limit
                            py[3],  # Upper limit
                            py[4],  # Type
                            py[5],  # Unit
                            result_spy
                            # py[8]   # Result
                        ])

                    return "PASSED", data_for_table
                else:
                    return "FAILED", []
            else:
                return "FAILED", []
        case "Inspection":
            # station = conexion.stations()
            result_m = ""
            result_ipx = ""
            result_ipy = ""
            result_cpc = ""
            result_cpe = ""
            result_cad = ""
            
            if options[2] == "VS":
                if len(options) == 29:
                    if "M" in options and "PX" in options and "PY" in options:
                        startM = options.index("M")
                        endM = options.index("M")+8
                        startPx = options.index("PX")
                        endPx = options.index("PX")+8
                        startPy = options.index("PY")
                        endPy = options.index("PY")+8
                            
                        if endM != "PX" and endM != "PY":
                            measurement = options[startM:endM]
                            # print(measurement)
                        else:
                            return "FAILED", []

                        if endPx != "M" and endPx != "PY":
                            position_x = options[startPx:endPx]
                            # print(position_x)
                        else:
                            return "FAILED",[]
                                
                        if endPy != "M" and endPy != "PX":
                            position_y = options[startPy:endPy]
                            # print(position_y)
                        else:
                            return "FAILED",[]
                        
                        if measurement[6] =='1':
                            result_m = "PASS"
                        else:
                            result_m = "FAIL"
                        
                        if position_x[6] =='1':
                            result_ipx = "PASS"
                        else:
                            result_ipx = "FAIL"
                        
                        if position_y[6] =='1':
                            result_ipy = "PASS"
                        else:
                            result_ipy = "FAIL"
                                                        
                        measurementInspection = conexion.parameters_inspection_vs(measurement,name_piece)
                        data_for_table.append([
                            measurement[4],  # Measurement
                            measurement[1],  # Value
                            measurement[2],  # Lower limit
                            measurement[3],  # Upper limit
                            measurement[4],  # Type
                            measurement[5],  # Unit
                            result_m
                            # measurement[8]   # Result
                        ])
                        positionPx = conexion.parameters_inspection_vs(position_x,name_piece)
                        if positionPx != 'GENERAL_ERROR':
                            data_for_table.append([
                                position_x[4],  # Measurement
                                position_x[1],  # Value
                                position_x[2],  # Lower limit
                                position_x[3],  # Upper limit
                                position_x[4],  # Type
                                position_x[5],  # Unit
                                result_ipx
                            ])
                        positionPy = conexion.parameters_inspection_vs(position_y,name_piece)
                        if positionPy != 'GENERAL_ERROR':
                            data_for_table.append([
                                position_y[4],  # Measurement
                                position_y[1],  # Value
                                position_y[2],  # Lower limit
                                position_y[3],  # Upper limit
                                position_y[4],  # Type
                                position_y[5],  # Unit
                                result_ipy
                            ])

                        return "PASSED", data_for_table

                        # if(measurementInspection == "FAILED" or positionPx == "FAILED" or positionPy == "FAILED"):
                        #     return "FAILED",[]
                        # else:
                        #     return "PASSED", data_for_table
                    else:
                        return "FAILED",[]
                else:
                    return "FAILED",[]
                # print(options[2])
            elif options[2] == "XT":
                if len(options) == 45:
                    if "PX" in options and "PY" in options and "CPC" in options and "CPE" in options and "CAD" in options:
                        # print(options[2])
                        startPx2 = options.index("PX")
                        endPx2 = options.index("PX")+8
                        startPy2 = options.index("PY")
                        endPy2 = options.index("PY")+8
                        startCPC = options.index("CPC")
                        endCPC = options.index("CPC")+8
                        startCPE = options.index("CPE")
                        endCPE = options.index("CPE")+8
                        startCAD = options.index("CAD")
                        endCAD = options.index("CAD")+8

                        if endPx2 != "CPC" and endPx2 != "PY" and endPx2 != "CPE" and endPx2 != "CAD":
                            position_x2 = options[startPx2:endPx2]
                            # print(position_x2)
                        else:
                            return "FAILED",[]
                            
                        if endPy2 != "CPC" and endPy2 != "PX" and endPy2 != "CPE" and endPy2 != "CAD":
                            position_y2 = options[startPy2:endPy2]
                            # print(position_y2)
                        else:
                            return "FAILED",[]
                            
                        if endCPC != "PX" and endCPC != "PY" and endCPC != "CPE" and endCPC != "CAD":
                            cpc = options[startCPC:endCPC]
                            # print(cpc)
                        else:
                            return "FAILED",[]
                            
                        if endCPE != "PX" and endCPE != "PY" and endCPE != "CPC" and endCPE != "CAD":
                            cpe = options[startCPE:endCPE]
                            # print(cpe)
                        else:
                            return "FAILED",[]
                            
                        if endCAD != "PX" and endCAD != "PY" and endCAD != "CPC" and endCAD != "CPE":
                            cad = options[startCAD:endCAD]
                            # print(cad)
                        else:
                            return "FAILED",[]

                        
                        if position_x2[6] =='1':
                            result_ipx = "PASS"
                        else:
                            result_ipx = "FAIL"
                        
                        if position_y2[6] =='1':
                            result_ipy = "PASS"
                        else:
                            result_ipy = "FAIL"
                        
                        if cpc[6] =='1':
                            result_cpc = "PASS"
                        else:
                            result_cpc = "FAIL"
                        
                        if cpe[6] =='1':
                            result_cpe = "PASS"
                        else:
                            result_cpe = "FAIL"

                        if cad[6] =='1':
                            result_cad = "PASS"
                        else:
                            result_cad = "FAIL"


                        positionPxT = conexion.parameters_inspection_xt(position_x2,name_piece)
                        if positionPxT != 'GENERAL_ERROR':
                            data_for_table.append([
                                position_x2[4],  # Measurement
                                position_x2[1],  # Value
                                position_x2[2],  # Lower limit
                                position_x2[3],  # Upper limit
                                position_x2[4],  # Type
                                position_x2[5],  # Unit
                                result_ipx
                            ])
                        positionPyT = conexion.parameters_inspection_xt(position_y2,name_piece)
                        if positionPyT != 'GENERAL_ERROR':
                            data_for_table.append([
                                position_y2[4],  # Measurement
                                position_y2[1],  # Value
                                position_y2[2],  # Lower limit
                                position_y2[3],  # Upper limit
                                position_y2[4],  # Type
                                position_y2[5],  # Unit
                                result_ipy
                            ])
                        cpcT = conexion.parameters_inspection_xt(cpc,name_piece)
                        if cpcT != 'GENERAL_ERROR':
                            data_for_table.append([
                                cpc[4],  # Measurement
                                cpc[1],  # Value
                                cpc[2],  # Lower limit
                                cpc[3],  # Upper limit
                                cpc[4],  # Type
                                cpc[5],  # Unit
                                result_cpc
                            ])
                        cpeT = conexion.parameters_inspection_xt(cpe,name_piece)
                        if cpeT != 'GENERAL_ERROR':
                            data_for_table.append([
                                cpe[4],  # Measurement
                                cpe[1],  # Value
                                cpe[2],  # Lower limit
                                cpe[3],  # Upper limit
                                cpe[4],  # Type
                                cpe[5],  # Unit
                                result_cpe
                            ])
                        cadT = conexion.parameters_inspection_xt(cad,name_piece)
                        if cadT != 'GENERAL_ERROR':
                            data_for_table.append([
                                cad[4],  # Measurement
                                cad[1],  # Value
                                cad[2],  # Lower limit
                                cad[3],  # Upper limit
                                cad[4],  # Type
                                cad[5],  # Unit
                                result_cad
                            ])

                        return "PASSED", data_for_table
                    
                        # if(positionPxT == "FAILED" or positionPyT == "FAILED" or cpcT == "FAILED" or cpeT == "FAILED" or cadT == "FAILED"):
                        #     return "FAILED",[]
                        # else:
                        #     return "PASSED",data_for_table
                    else:
                        return "FAILED",[]
                else:
                    return "FAILED",[]          
            else:
                # print("Ninguna de las anteriores")
                return "FAILED",[]
        case "Electrical":
            result_electrical_continuity = ""
            result_voltage = ""
            result_current = ""
            result_resistance = ""

            if len(options) == 36:
                continuidad = options[2:10]
                voltaje = options[10:18]
                corriente = options[18:26]
                resistencia = options[26:-2]

                if continuidad[6] =='1':
                    result_electrical_continuity = "PASS"
                else:
                    result_electrical_continuity = "FAIL"
                        
                if voltaje[6] =='1':
                    result_voltage = "PASS"
                else:
                    result_voltage = "FAIL"
                        
                if corriente[6] =='1':
                    result_current = "PASS"
                else:
                    result_current = "FAIL"
                        
                if resistencia[6] =='1':
                    result_resistance = "PASS"
                else:
                    result_resistance = "FAIL"

                if continuidad[0] == 'Ct' and voltaje[0] == 'V' and corriente[0] == 'Cr' and resistencia[0] == 'R':
                    continuidad_measurement = conexion.parameters_electrical(continuidad,name_piece)
                    if continuidad_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            continuidad[1],  # Value
                            continuidad[2],  # Lower limit
                            continuidad[3],  # Upper limit
                            continuidad[4],  # Type
                            continuidad[5],  # Unit
                            result_electrical_continuity
                        ])
                    voltaje_measurement = conexion.parameters_electrical(voltaje,name_piece)
                    if voltaje_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            voltaje[1],  # Value
                            voltaje[2],  # Lower limit
                            voltaje[3],  # Upper limit
                            voltaje[4],  # Type
                            voltaje[5],  # Unit
                            result_voltage
                        ])
                    corriente_measurement = conexion.parameters_electrical(corriente,name_piece)
                    if corriente_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            corriente[1],  # Value
                            corriente[2],  # Lower limit
                            corriente[3],  # Upper limit
                            corriente[4],  # Type
                            corriente[5],  # Unit
                            result_current
                        ])
                    resistencia_measurement = conexion.parameters_electrical(resistencia,name_piece)
                    if resistencia_measurement != 'GENERAL_ERROR':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            resistencia[1],  # Value
                            resistencia[2],  # Lower limit
                            resistencia[3],  # Upper limit
                            resistencia[4],  # Type
                            resistencia[5],  # Unit
                            result_resistance
                        ])


                    return "PASSED",data_for_table
                else:
                    return "FAILED",[]
            else:
                return "FAILED",[]
        case "Continuity":
            if len(options) == 11:
                result_continuity = ""

                if options[6] =='1':
                    result_continuity = "PASS"
                else:
                    result_continuity = "FAIL"

                commits = conexion.parameters_continuity(options)
                data_for_table.append([
                    "Continuity",  # Measurement
                    options[7],  # Value
                    options[3],  # Lower limit
                    options[4],  # Upper limit
                    options[8],  # Type
                    options[5],  # Unit
                    result_continuity
                ])
                return "PASSED",data_for_table
            else:
                return "FAILED" ,[]
        case "Leak":            
            if len(options) == 11:
                result_leak = ""

                if options[4] =='1':
                    result_leak = "PASS"
                else:
                    result_leak = "FAIL"
                commits = conexion.parameters_leak(options)
                data_for_table.append([
                    "Leaktest",  # Measurement
                    options[3],  # Value
                    options[7],  # Lower limit
                    options[8],  # Upper limit
                    options[2],  # tiempo_prueba
                    options[5],  # Fuga
                    result_leak
                ])
                return "PASSED",data_for_table
            else:
                return "FAILED",[]
        case "Temperature":
            if len(options) == 12:
                result_temperatura = ""

                if options[8] =='1':
                    result_temperatura = "PASS"
                else:
                    result_temperatura = "FAIL"
                commits = conexion.parameters_temperature(options)
                data_for_table.append([
                    options[1],  # Measurement
                    options[2],  # Value
                    options[3],  # Lower limit
                    options[4],  # Upper limit
                    options[5],  # Type
                    options[6],  # Unit
                    result_temperatura
                ])
                return "PASSED",data_for_table
            else:
                return "FAILED",[]
        case "Welding":
            welding = 'commit,Welding,welding_time,welding_power,100,mm,PASSED,description,1/'
            if len(options) == 10:
                result_welding = ""

                if options[6] =='1':
                    result_welding = "PASS"
                else:
                    result_welding = "FAIL"
                commits = conexion.parameters_welding(options)
                data_for_table.append([
                    options[1],  # Measurement
                    options[2],  # Value
                    options[3],  # Lower limit
                    options[4],  # Upper limit
                    "-",  # Type
                    options[5],  # Unit
                    result_welding
                ])
                return "PASSED",data_for_table
            else:
                return "FAILED",[]
        case _:
            # print("default")
            return "FAILED",[]

# commit(temperatura,name)