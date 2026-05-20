__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

# maria DB
import conexion


pressfit = "commit,Pressfit,F,50,10,100,Numeric,N,PASSED,Comentarios,dwell_time,D,500,498,502,Numeric,mm,PASSED,Comentarios,dwell_time,S,100,95,110,Numeric,mm/s,PASSED,Comentarios,dwell_time,P2173404-00-C:SEYU26061A0764,1/"
screwing = "commit,Screwing,T,1.25,1,1.8,Numeric,N,PASSED,Comentario,A,31250,2900,3500,Numeric,degrees,FAILED,Comentario,PX,50,47,55,Numeric,mm,PASSED,Comentario,PY,150,140,160,Numeric,mm,PASSED,Comentario,4,P2173404-00-C:SEYU26061A0765,1/"
inspection_vs = "commit,Inspection,VS,M,8000,7500,8500,Numeric,N,PASSED,Comentarios,PX,500,475,525,Numeric,mm,PASSED,Comentarios,PY,500,475,525,Numeric,mm,PASSED,Comentarios,P2173404-00-C:SEYU26061A0766,1/"
inspection_xt = "commit,Inspection,XT,PX,500,475,525,Numeric,mm,PASSED,Comentarios,PY,500,475,525,Numeric,mm,PASSED,Comentarios,CPC,400,395,405,Numeric,mm,PASSED,Comentarios,CPE,400,395,405,Numeric,mm,PASSED,Comentarios,CAD,1,1,1,Boolean,DBU,PASSED,Comentarios,P2173404-00-C:SEYU26061A0765,1/"
electrical = "commit,Electrical,Ct,1.25,1,1.8,Numeric,N,OK,Comentario,V,31250,2900,3500,Numeric,degrees,FAILED,Comentario,Cr,50,47,55,Numeric,mm,PASSED,Comentario,R,150,140,160,Numeric,mm,PASSED,Comentario,P2173404-00-C:SEYU26061A0765,1/"

continuity_ok = 'commit,Continuity,Continuity1,10,50,F,PASS,20,Ejemplo de error del defecto,P2173404-00-C:SEYU26061A0765,1/'

continuity_fail = 'commit,Continuity,Continuity1,10,50,F,FAIL,5,Ejemplo de error del defecto,1/'

leak1 = "commit,Leak,tiempo_prueba,resultado,PASSED/FAILED,unit,descripcion,extra1,extra2,1/"
leak2 = "commit,Leak,Numeric,14.25,PASSED,psi,DESCRIPCION,1.0,1.0,Leak,P2173404-00-C:SEYU26061A0765,1/"
temperatura = "commit,Temperature,start (timestamp),salida al proceso (timestamp),temp_inicial,temp_final,unit,descripcion,extra1,extra2,P2173404-00-C:SEYU26061A0765,1/"
welding = 'commit,Welding,welding_time,welding_power,100,mm,PASSED,description,P2173404-00-C:SEYU26061A0765,1/'

heatstake = 'commit,Heatstake,heatstake,cicle_time,serial_number(P2173404-00-C:SEYU26061A0765),program_name,times_tamp,grade,description,1/'
heatstake = "commit,Heatstake,heatstake,cicle_time,P2173404-00-C:SEYU26061A0765,program_name,times_tamp,grade,description,1/"

graph_image = 'commit,Graph,graph,data_image,description,P2173404-00-C:SEYU26061A0765,1/'

cadenas = temperatura.split(',')
# print(len(cadenas))
name = "P2173404-00-C:SEYU26061A0765"

def commit(cadena, name_piece):
    options = cadena.split(',')
    data_for_table = []
    # print(cadena)
    # return options[1]
    # print(len(options))
    
    match options[1]:
        case "Pressfit":
            # station = conexion.stations()
            # print(options)
            # print(len(options))
            # print(options[-3])
            if len(options) == 59:
                force = options[2:11]
                distance = options[11:20]
                pin1 = options[20:29]
                pin2 = options[29:38]
                pin3 = options[38:47]
                pin4 = options[47:56]
                # print(force)
                # print(distance)
                # print(speed)
                
                force_measurement = conexion.parameters_pressfit(force,options[-3])
                if force_measurement != 'GENERAL_ERROR' and force_measurement != 'FAILED':
                    data_for_table.append([
                    force[0],  # Measurement
                    force[1],  # Value
                    force[2],  # Lower limit
                    force[3],  # Upper limit
                    force[4],  # Type
                    force[5],  # Unit
                    force[6]   # Result
                    # force[8]   # Result
                ])
                elif force_measurement == 'FAILED':
                    return "FAILED", []
                    # print("FAILED")
                distance_measurement = conexion.parameters_pressfit(distance,options[-3])
                if distance_measurement != 'GENERAL_ERROR' and distance_measurement != 'FAILED':
                    data_for_table.append([
                    distance[0],  # Measurement
                    distance[1],  # Value
                    distance[2],  # Lower limit
                    distance[3],  # Upper limit
                    distance[4],  # Type
                    distance[5],  # Unit
                    distance[6]   # Result
                    # distance[8]   # Result
                ])
                elif distance_measurement == 'FAILED':
                    # print("FAILED")
                    return "FAILED", []
                pin1_measurement = conexion.parameters_pressfit(pin1,options[-3])
                if pin1_measurement != 'GENERAL_ERROR' and pin1_measurement != 'FAILED':
                    data_for_table.append([
                    pin1[0],  # Measurement
                    pin1[1],  # Value
                    pin1[2],  # Lower limit
                    pin1[3],  # Upper limit
                    pin1[4],  # Type
                    pin1[5],  # Unit
                    pin1[6]   # Result
                    # pin1[8]   # Result
                ])
                elif pin1_measurement == 'FAILED':
                    # print("FAILED")
                    return "FAILED", []
                pin2_measurement = conexion.parameters_pressfit(pin2,options[-3])
                if pin2_measurement != 'GENERAL_ERROR' and pin2_measurement != 'FAILED':
                    data_for_table.append([
                    pin2[0],  # Measurement
                    pin2[1],  # Value
                    pin2[2],  # Lower limit
                    pin2[3],  # Upper limit
                    pin2[4],  # Type
                    pin2[5],  # Unit
                    pin2[6]   # Result
                    # pin2[8]   # Result
                ])
                elif pin2_measurement == 'FAILED':
                    # print("FAILED")
                    return "FAILED", []
                pin3_measurement = conexion.parameters_pressfit(pin3,options[-3])
                if pin3_measurement != 'GENERAL_ERROR' and pin3_measurement != 'FAILED':
                    data_for_table.append([
                    pin3[0],  # Measurement
                    pin3[1],  # Value
                    pin3[2],  # Lower limit
                    pin3[3],  # Upper limit
                    pin3[4],  # Type
                    pin3[5],  # Unit
                    pin3[6]   # Result
                    # pin3[8]   # Result
                ])
                elif pin3_measurement == 'FAILED':
                    # print("FAILED")
                    return "FAILED", []
                pin4_measurement = conexion.parameters_pressfit(pin4,options[-3])
                if pin4_measurement != 'GENERAL_ERROR' and pin4_measurement != 'FAILED':
                    data_for_table.append([
                    pin4[0],  # Measurement
                    pin4[1],  # Value
                    pin4[2],  # Lower limit
                    pin4[3],  # Upper limit
                    pin4[4],  # Type
                    pin4[5],  # Unit
                    pin4[6]   # Result
                    # pin4[8]   # Result
                ])
                elif pin4_measurement == 'FAILED':
                    # print("FAILED")
                    return "FAILED", []
                
                return "PASSED", data_for_table
            else:
                return "FAILED", []
        case "Screwing":
            # print(options)
            # print(len(options))
            # print(options[-4])
            if len(options) == 38:
                torque = options[2:10]
                angle = options[10:18]
                px = options[18:26]
                py = options[26:-4]

                result_torque = ""
                result_angle = ""
                result_spx = ""
                result_spy = ""

                torque.append(options[-4])
                angle.append(options[-4])
                px.append(options[-4])
                py.append(options[-4])
                # print(torque)
                # print(angle)
                # print(px)
                # print(py)
                if torque[6] =='PASSED':
                    result_torque = "PASS"
                else:
                    result_torque = "FAIL"
                
                if angle[6] =='PASSED':
                    result_angle = "PASS"
                else:
                    result_angle = "FAIL"
                
                if px[6] =='PASSED':
                    result_spx = "PASS"
                else:
                    result_spx = "FAIL"
                
                if py[6] =='PASSED':
                    result_spy = "PASS"
                else:
                    result_spy = "FAIL"

                if torque[0] == 'T' and angle[0] == 'A' and px[0] == 'PX' and py[0] == 'PY':
                    torque_measurement = conexion.parameters_screwing(torque,options[-3])
                    if torque_measurement != 'GENERAL_ERROR' and torque_measurement != 'FAILED':
                        data_for_table.append([
                            torque[0],# "Torque",  # Measurement
                            torque[1],  # Value
                            torque[2],  # Lower limit
                            torque[3],  # Upper limit
                            torque[4],  # Type
                            torque[5],  # Unit
                            result_torque
                            # torque[8]   # Result
                        ])
                    elif torque_measurement == 'FAILED':
                        return "FAILED", []
                    angle_measurement = conexion.parameters_screwing(angle,options[-3])
                    if angle_measurement != 'GENERAL_ERROR' and angle_measurement != 'FAILED':
                        data_for_table.append([
                            angle[0],  # Measurement
                            angle[1],  # Value
                            angle[2],  # Lower limit
                            angle[3],  # Upper limit
                            angle[4],  # Type
                            angle[5],  # Unit
                            result_angle
                            # angle[8]   # Result
                        ])
                    elif angle_measurement == 'FAILED':
                        return "FAILED", []
                    px_measurement = conexion.parameters_screwing(px,options[-3])
                    if px_measurement != 'GENERAL_ERROR' and px_measurement != 'FAILED':
                        data_for_table.append([
                            px[0],  # Measurement
                            px[1],  # Value
                            px[2],  # Lower limit
                            px[3],  # Upper limit
                            px[4],  # Type
                            px[5],  # Unit
                            result_spx
                            # px[8]   # Result
                        ])
                    elif px_measurement == 'FAILED':
                        return "FAILED", []
                    py_measurement = conexion.parameters_screwing(py,options[-3])
                    if py_measurement != 'GENERAL_ERROR' and py_measurement != 'FAILED':
                        data_for_table.append([
                            py[0],  # Measurement
                            py[1],  # Value
                            py[2],  # Lower limit
                            py[3],  # Upper limit
                            py[4],  # Type
                            py[5],  # Unit
                            result_spy
                            # py[8]   # Result
                        ])
                    elif py_measurement == 'FAILED':
                        return "FAILED", []

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
                if len(options) == 30:
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
                        
                        if measurement[6] =='PASSED':
                            result_m = "PASS"
                        else:
                            result_m = "FAIL"
                        
                        if position_x[6] =='PASSED':
                            result_ipx = "PASS"
                        else:
                            result_ipx = "FAIL"
                        
                        if position_y[6] =='PASSED':
                            result_ipy = "PASS"
                        else:
                            result_ipy = "FAIL"


                        measurementInspection = conexion.parameters_inspection_vs(measurement,options[-3])
                        if measurementInspection != 'GENERAL_ERROR' and measurementInspection != 'FAILED':
                            data_for_table.append([
                                position_x[4],  # Measurement
                                position_x[1],  # Value
                                position_x[2],  # Lower limit
                                position_x[3],  # Upper limit
                                position_x[4],  # Type
                                position_x[5],  # Unit
                                result_ipx
                            ])
                        elif measurementInspection == 'FAILED':
                            return "FAILED", []
                        positionPx = conexion.parameters_inspection_vs(position_x,options[-3])
                        if positionPx != 'GENERAL_ERROR' and positionPx != 'FAILED':
                            data_for_table.append([
                                position_x[4],  # Measurement
                                position_x[1],  # Value
                                position_x[2],  # Lower limit
                                position_x[3],  # Upper limit
                                position_x[4],  # Type
                                position_x[5],  # Unit
                                result_ipx
                            ])
                        elif positionPx == 'FAILED':
                            return "FAILED", []
                        positionPy = conexion.parameters_inspection_vs(position_y,options[-3])
                        if positionPy != 'GENERAL_ERROR' and positionPy != 'FAILED':
                            data_for_table.append([
                                position_y[4],  # Measurement
                                position_y[1],  # Value
                                position_y[2],  # Lower limit
                                position_y[3],  # Upper limit
                                position_y[4],  # Type
                                position_y[5],  # Unit
                                result_ipy
                            ])
                        elif positionPy == 'FAILED':
                            return "FAILED", []
                        
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
                if len(options) == 86:
                    IT1 = options[3:11]
                    IT2 = options[11:19]
                    IT3 = options[19:27]
                    IT4 = options[27:35]
                    IT5 = options[35:43]
                    IT6 = options[43:51]
                    IT7 = options[51:59]
                    IT8 = options[59:67]
                    IT9 = options[67:75]
                    IT10 = options[75:83]

                    item1 = conexion.parameters_inspection_xt(IT1,options[-3])
                    if item1 != 'GENERAL_ERROR' and item1 != 'FAILED':
                        data_for_table.append([
                        IT1[0],  # Measurement
                        IT1[1],  # Value
                        IT1[2],  # Lower limit
                        IT1[3],  # Upper limit
                        IT1[4],  # Type
                        IT1[5],  # Unit
                        IT1[6]   # Result
                    ])
                    elif item1 == 'FAILED':
                        return "FAILED", []
                        # print("FAILED")
                    item2 = conexion.parameters_inspection_xt(IT2,options[-3])
                    if item2 != 'GENERAL_ERROR' and item2 != 'FAILED':
                        data_for_table.append([
                        IT2[0],  # Measurement
                        IT2[1],  # Value
                        IT2[2],  # Lower limit
                        IT2[3],  # Upper limit
                        IT2[4],  # Type
                        IT2[5],  # Unit
                        IT2[6]   # Result
                    ])
                    elif item2 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item3 = conexion.parameters_inspection_xt(IT3,options[-3])
                    if item3 != 'GENERAL_ERROR' and item3 != 'FAILED':
                        data_for_table.append([
                        IT3[0],  # Measurement
                        IT3[1],  # Value
                        IT3[2],  # Lower limit
                        IT3[3],  # Upper limit
                        IT3[4],  # Type
                        IT3[5],  # Unit
                        IT3[6]   # Result
                        # IT3[8]   # Result
                    ])
                    elif item3 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item4 = conexion.parameters_inspection_xt(IT4,options[-3])
                    if item4 != 'GENERAL_ERROR' and item4 != 'FAILED':
                        data_for_table.append([
                        IT4[0],  # Measurement
                        IT4[1],  # Value
                        IT4[2],  # Lower limit
                        IT4[3],  # Upper limit
                        IT4[4],  # Type
                        IT4[5],  # Unit
                        IT4[6]   # Result
                        # IT4[8]   # Result
                    ])
                    elif item4 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item5 = conexion.parameters_inspection_xt(IT5,options[-3])
                    if item5 != 'GENERAL_ERROR' and item5 != 'FAILED':
                        data_for_table.append([
                        IT5[0],  # Measurement
                        IT5[1],  # Value
                        IT5[2],  # Lower limit
                        IT5[3],  # Upper limit
                        IT5[4],  # Type
                        IT5[5],  # Unit
                        IT5[6]   # Result
                        # IT5[8]   # Result
                    ])
                    elif item5 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item6 = conexion.parameters_inspection_xt(IT6,options[-3])
                    if item6 != 'GENERAL_ERROR' and item6 != 'FAILED':
                        data_for_table.append([
                        IT6[0],  # Measurement
                        IT6[1],  # Value
                        IT6[2],  # Lower limit
                        IT6[3],  # Upper limit
                        IT6[4],  # Type
                        IT6[5],  # Unit
                        IT6[6]   # Result
                        # IT6[8]   # Result
                    ])
                    elif item6 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []

                    item7 = conexion.parameters_inspection_xt(IT7,options[-3])
                    if item7 != 'GENERAL_ERROR' and item7 != 'FAILED':
                        data_for_table.append([
                        IT7[0],  # Measurement
                        IT7[1],  # Value
                        IT7[2],  # Lower limit
                        IT7[3],  # Upper limit
                        IT7[4],  # Type
                        IT7[5],  # Unit
                        IT7[6]   # Result
                        # IT7[8]   # Result
                    ])
                    elif item7 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item8 = conexion.parameters_inspection_xt(IT8,options[-3])
                    if item8 != 'GENERAL_ERROR' and item8 != 'FAILED':
                        data_for_table.append([
                        IT8[0],  # Measurement
                        IT8[1],  # Value
                        IT8[2],  # Lower limit
                        IT8[3],  # Upper limit
                        IT8[4],  # Type
                        IT8[5],  # Unit
                        IT8[6]   # Result
                        # IT8[8]   # Result
                    ])
                    elif item8 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item9 = conexion.parameters_inspection_xt(IT9,options[-3])
                    if item9 != 'GENERAL_ERROR' and item9 != 'FAILED':
                        data_for_table.append([
                        IT9[0],  # Measurement
                        IT9[1],  # Value
                        IT9[2],  # Lower limit
                        IT9[3],  # Upper limit
                        IT9[4],  # Type
                        IT9[5],  # Unit
                        IT9[6]   # Result
                        # IT9[8]   # Result
                    ])
                    elif item9 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    item10 = conexion.parameters_inspection_xt(IT10,options[-3])
                    if item10 != 'GENERAL_ERROR' and item10 != 'FAILED':
                        data_for_table.append([
                        IT10[0],  # Measurement
                        IT10[1],  # Value
                        IT10[2],  # Lower limit
                        IT10[3],  # Upper limit
                        IT10[4],  # Type
                        IT10[5],  # Unit
                        IT10[6]   # Result
                        # IT10[8]   # Result
                    ])
                    elif item10 == 'FAILED':
                        # print("FAILED")
                        return "FAILED", []
                    return "PASSED", data_for_table
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

            if len(options) == 37:
                continuidad = options[2:10]
                voltaje = options[10:18]
                corriente = options[18:26]
                resistencia = options[26:-3]

                print(continuidad)
                print(voltaje)
                print(corriente)
                print(resistencia)

                if continuidad[6] =='PASSED':
                    result_electrical_continuity = "PASS"
                else:
                    result_electrical_continuity = "FAIL"
                        
                if voltaje[6] =='PASSED':
                    result_voltage = "PASS"
                else:
                    result_voltage = "FAIL"
                        
                if corriente[6] =='PASSED':
                    result_current = "PASS"
                else:
                    result_current = "FAIL"
                        
                if resistencia[6] =='PASSED':
                    result_resistance = "PASS"
                else:
                    result_resistance = "FAIL"

                if continuidad[0] == 'Ct' and voltaje[0] == 'V' and corriente[0] == 'Cr' and resistencia[0] == 'R':
                    continuidad_measurement = conexion.parameters_electrical(continuidad,options[-3])
                    if continuidad_measurement != 'GENERAL_ERROR' and continuidad_measurement != 'FAILED':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            continuidad[1],  # Value
                            continuidad[2],  # Lower limit
                            continuidad[3],  # Upper limit
                            continuidad[4],  # Type
                            continuidad[5],  # Unit
                            result_electrical_continuity
                        ])
                    elif continuidad_measurement == 'FAILED':
                        return "FAILED", []
                    voltaje_measurement = conexion.parameters_electrical(voltaje,options[-3])
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
                    corriente_measurement = conexion.parameters_electrical(corriente,options[-3])
                    if corriente_measurement != 'GENERAL_ERROR' and corriente_measurement != 'FAILED':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            corriente[1],  # Value
                            corriente[2],  # Lower limit
                            corriente[3],  # Upper limit
                            corriente[4],  # Type
                            corriente[5],  # Unit
                            result_current
                        ])
                    elif corriente_measurement == 'FAILED':
                        return "FAILED", []
                    resistencia_measurement = conexion.parameters_electrical(resistencia,options[-3])
                    if resistencia_measurement != 'GENERAL_ERROR' and resistencia_measurement != 'FAILED':
                        data_for_table.append([
                            "Voltage",  # Measurement
                            resistencia[1],  # Value
                            resistencia[2],  # Lower limit
                            resistencia[3],  # Upper limit
                            resistencia[4],  # Type
                            resistencia[5],  # Unit
                            result_resistance
                        ])
                    elif resistencia_measurement == 'FAILED':
                        return "FAILED", []

                    return "PASSED",data_for_table
                else:
                    return "FAILED",[]
            else:
                return "FAILED",[]
        case "Continuity":
            if len(options) == 12:
                result_continuity = ""

                if options[6] =='PASSED':
                    result_continuity = "PASS"
                else:
                    result_continuity = "FAIL"

                commits = conexion.parameters_continuity(options)
                if commits == 'FAILED':
                    return "FAILED", []
                else:
                    data_for_table.append([
                        options[1],  # Measurement
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
            # print(options)        
            if len(options) == 13:
                result_leak = ""

                if options[4] =='PASSED':
                    result_leak = "PASS"
                else:
                    result_leak = "FAIL"
                commits = conexion.parameters_leak(options)
                if commits == 'FAILED':
                    return "FAILED", []
                else:
                    data_for_table.append([
                        options[9],  # Measurement
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
            if len(options) == 13:
                result_temperatura = ""

                if options[8] =='PASSED':
                    result_temperatura = "PASS"
                else:
                    result_temperatura = "FAIL"

                commits = conexion.parameters_temperature(options)
                if commits == 'FAILED':
                    return "FAILED", []
                else:
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
            if len(options) == 11:
                result_welding = ""

                if options[6] =='PASSED':
                    result_welding = "PASS"
                else:
                    result_welding = "FAIL"
                commits = conexion.parameters_welding(options)
                if commits == 'FAILED':
                    return "FAILED", []
                else:
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
        
        case "Heatstake":
            if len(options) == 11:
                commits = conexion.parameters_heatstake(options)
                print(commits)
                if commits == 'FAILED':
                    return "FAILED", []
                else:
                    data_for_table.append([
                        options[1],  # Measurement
                        options[3],  # Value
                        options[5],  # Lower limit
                        options[6],  # Upper limit
                        "-",         # Type
                        options[5],  # Unit
                        "-"          # Result
                    ])
                return "PASSED",data_for_table
            else:
                return "FAILED",[]
            
        case "Graph":
            if len(options) == 11:
                data1 = options[3:5]
                data2 = options[6:8]
                data1.append(options[-3])
                data2.append(options[-3])
                
                commit_data1 = conexion.parameters_graph(data1)
                if commit_data1 == 'FAILED':
                    return "FAILED", []
                elif commit_data1 != 'GENERAL_ERROR' and commit_data1 != 'FAILED':
                    data_for_table.append([
                        data1[0],  # Measurement
                        data1[1],  # Value
                        "-",         # Lower limit
                        "-",         # Upper limit
                        "-",         # Type
                        "-",         # Unit
                        "-"          # Result
                    ])
                # return "PASSED",data_for_table

                commit_data2 = conexion.parameters_graph(data2)
                if commit_data2 == 'FAILED':
                    return "FAILED", []
                elif commit_data2 != 'GENERAL_ERROR' and commit_data2 != 'FAILED':
                    data_for_table.append([
                        data2[0],  # Measurement
                        data2[1],  # Value
                        "-",         # Lower limit
                        "-",         # Upper limit
                        "-",         # Type
                        "-",         # Unit
                        "-"          # Result
                    ])
                return "PASSED",data_for_table
            else:
                return "FAILED",[]
            
        case _:
            # print("default")
            return "FAILED",[]
            

# commit(graph_image,name)