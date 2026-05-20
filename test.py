import conexion

data_for_table = []
pressfit = "commit,Pressfit,F,50,10,100,Numeric,N,PASSED,Comentarios,dwell_time,D,500,498,502,Numeric,mm,PASSED,Comentarios,dwell_time,PIN1,,,,,,,,,PIN2,,,,,,,,,PIN3,,,,,,,,,PIN4,,,,,,,,,P1106394-71-P:SE4A25079000001,1/"
inspection_xt = "commit,Inspection,XT,IT1,500,475,525,Numeric,mm,PASSED,Comentarios,IT2,500,475,525,Numeric,mm,PASSED,Comentarios,IT3,400,395,405,Numeric,mm,PASSED,Comentarios,IT4,400,395,405,Numeric,mm,PASSED,Comentarios,IT5,1,1,1,Boolean,DBU,PASSED,Comentarios,IT6,500,475,525,Numeric,mm,PASSED,Comentarios,IT7,500,475,525,Numeric,mm,PASSED,Comentarios,IT8,400,395,405,Numeric,mm,PASSED,Comentarios,IT9,400,395,405,Numeric,mm,PASSED,Comentarios,IT10,1,1,1,Boolean,DBU,PASSED,Comentarios,P1106394-71-P:SE4A25079000001,1/"
graph_image = 'commit,Graph,data1,data_image,description,data2,,,P1106394-71-P:SE4A25079000001,1/'
# print(pressfit.split(","))
# print(len(pressfit.split(","))) #59
# print(len(inspection_xt.split(","))) #86
print(len(graph_image.split(","))) #11

data1 = graph_image.split(",")[3:5]
data2 = graph_image.split(",")[6:8]
data1.append(graph_image.split(",")[-2])
data2.append(graph_image.split(",")[-2])

commit_data1 = conexion.parameters_graph(data1)
if commit_data1 == 'FAILED':
    # return "FAILED", []
    print("FAILED")
elif commit_data1 == 'GENERAL_ERROR':
    print("GENERAL_ERROR")
else:
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
    # return "FAILED", []
    print("FAILED")
else:
    data_for_table.append([
        data2[0],  # Measurement
        data2[1],  # Value
        "-",         # Lower limit
        "-",         # Upper limit
        "-",         # Type
        "-",         # Unit
        "-"          # Result
    ])
# return "PASSED",data_for_table

print(data1)
print(data2)

force = pressfit.split(",")[2:11]
distance = pressfit.split(",")[11:20]
pin1 = pressfit.split(",")[20:29]
pin2 = pressfit.split(",")[29:38]
pin3 = pressfit.split(",")[38:47]
pin4 = pressfit.split(",")[47:56]

IT1 = inspection_xt.split(",")[3:11]
IT2 = inspection_xt.split(",")[11:19]
IT3 = inspection_xt.split(",")[19:27]
IT4 = inspection_xt.split(",")[27:35]
IT5 = inspection_xt.split(",")[35:43]
IT6 = inspection_xt.split(",")[43:51]
IT7 = inspection_xt.split(",")[51:59]
IT8 = inspection_xt.split(",")[59:67]
IT9 = inspection_xt.split(",")[67:75]
IT10 = inspection_xt.split(",")[75:83]

# force = force.append(pressfit.split(",")[56])
# print(force)
# print(distance)
# print(pin1)
# print(pin2)
# print(pin3)
# print(pin4)
# print(pressfit.split(",")[56])
# print(pressfit.split(",")[-2])

# force_measurement = conexion.parameters_pressfit(force,pressfit.split(",")[-2])
# if force_measurement != 'GENERAL_ERROR' and force_measurement != 'FAILED':
#     data_for_table.append([
#     force[0],  # Measurement
#     force[1],  # Value
#     force[2],  # Lower limit
#     force[3],  # Upper limit
#     force[4],  # Type
#     force[5],  # Unit
#     force[6]   # Result
#     # force[8]   # Result
# ])
# elif force_measurement == 'FAILED':
#     # return "FAILED", []
#     print("FAILED")
# distance_measurement = conexion.parameters_pressfit(distance,pressfit.split(",")[-2])
# if distance_measurement != 'GENERAL_ERROR' and distance_measurement != 'FAILED':
#     data_for_table.append([
#     distance[0],  # Measurement
#     distance[1],  # Value
#     distance[2],  # Lower limit
#     distance[3],  # Upper limit
#     distance[4],  # Type
#     distance[5],  # Unit
#     distance[6]   # Result
#     # distance[8]   # Result
# ])
# elif distance_measurement == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# pin1_measurement = conexion.parameters_pressfit(pin1,pressfit.split(",")[-2])
# if pin1_measurement != 'GENERAL_ERROR' and pin1_measurement != 'FAILED':
#     data_for_table.append([
#     pin1[0],  # Measurement
#     pin1[1],  # Value
#     pin1[2],  # Lower limit
#     pin1[3],  # Upper limit
#     pin1[4],  # Type
#     pin1[5],  # Unit
#     pin1[6]   # Result
#     # pin1[8]   # Result
# ])
# elif pin1_measurement == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# pin2_measurement = conexion.parameters_pressfit(pin2,pressfit.split(",")[-2])
# if pin2_measurement != 'GENERAL_ERROR' and pin2_measurement != 'FAILED':
#     data_for_table.append([
#     pin2[0],  # Measurement
#     pin2[1],  # Value
#     pin2[2],  # Lower limit
#     pin2[3],  # Upper limit
#     pin2[4],  # Type
#     pin2[5],  # Unit
#     pin2[6]   # Result
#     # pin2[8]   # Result
# ])
# elif pin2_measurement == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# pin3_measurement = conexion.parameters_pressfit(pin3,pressfit.split(",")[-2])
# if pin3_measurement != 'GENERAL_ERROR' and pin3_measurement != 'FAILED':
#     data_for_table.append([
#     pin3[0],  # Measurement
#     pin3[1],  # Value
#     pin3[2],  # Lower limit
#     pin3[3],  # Upper limit
#     pin3[4],  # Type
#     pin3[5],  # Unit
#     pin3[6]   # Result
#     # pin3[8]   # Result
# ])
# elif pin3_measurement == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# pin4_measurement = conexion.parameters_pressfit(pin4,pressfit.split(",")[-2])
# if pin4_measurement != 'GENERAL_ERROR' and pin4_measurement != 'FAILED':
#     data_for_table.append([
#     pin4[0],  # Measurement
#     pin4[1],  # Value
#     pin4[2],  # Lower limit
#     pin4[3],  # Upper limit
#     pin4[4],  # Type
#     pin4[5],  # Unit
#     pin4[6]   # Result
#     # pin4[8]   # Result
# ])
# elif pin4_measurement == 'FAILED':
#     print("FAILED")
    # return "FAILED", []
# print(force_measurement)

# print(IT1)
# print(IT2)
# print(IT3)
# print(IT4)
# print(IT5)
# print(IT6)
# print(IT7)
# print(IT8)
# print(IT9)
# print(IT10)
# print(inspection_xt.split(",")[-2])

# item1 = conexion.parameters_inspection_xt(IT1,inspection_xt.split(",")[-2])
# if item1 != 'GENERAL_ERROR' and item1 != 'FAILED':
#     data_for_table.append([
#     IT1[0],  # Measurement
#     IT1[1],  # Value
#     item1[2],  # Lower limit
#     IT1[3],  # Upper limit
#     IT1[4],  # Type
#     IT1[5],  # Unit
#     IT1[6]   # Result
# ])
# elif item1 == 'FAILED':
#     # return "FAILED", []
#     print("FAILED")
# item2 = conexion.parameters_inspection_xt(IT2,inspection_xt.split(",")[-2])
# if item2 != 'GENERAL_ERROR' and item2 != 'FAILED':
#     data_for_table.append([
#     IT2[0],  # Measurement
#     IT2[1],  # Value
#     IT2[2],  # Lower limit
#     IT2[3],  # Upper limit
#     IT2[4],  # Type
#     IT2[5],  # Unit
#     IT2[6]   # Result
# ])
# elif item2 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item3 = conexion.parameters_inspection_xt(IT3,inspection_xt.split(",")[-2])
# if item3 != 'GENERAL_ERROR' and item3 != 'FAILED':
#     data_for_table.append([
#     IT3[0],  # Measurement
#     IT3[1],  # Value
#     IT3[2],  # Lower limit
#     IT3[3],  # Upper limit
#     IT3[4],  # Type
#     IT3[5],  # Unit
#     IT3[6]   # Result
#     # IT3[8]   # Result
# ])
# elif item3 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item4 = conexion.parameters_inspection_xt(IT4,inspection_xt.split(",")[-2])
# if item4 != 'GENERAL_ERROR' and item4 != 'FAILED':
#     data_for_table.append([
#     IT4[0],  # Measurement
#     IT4[1],  # Value
#     IT4[2],  # Lower limit
#     IT4[3],  # Upper limit
#     IT4[4],  # Type
#     IT4[5],  # Unit
#     IT4[6]   # Result
#     # IT4[8]   # Result
# ])
# elif item4 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item5 = conexion.parameters_inspection_xt(IT5,inspection_xt.split(",")[-2])
# if item5 != 'GENERAL_ERROR' and item5 != 'FAILED':
#     data_for_table.append([
#     IT5[0],  # Measurement
#     IT5[1],  # Value
#     IT5[2],  # Lower limit
#     IT5[3],  # Upper limit
#     IT5[4],  # Type
#     IT5[5],  # Unit
#     IT5[6]   # Result
#     # IT5[8]   # Result
# ])
# elif item5 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item6 = conexion.parameters_inspection_xt(IT6,inspection_xt.split(",")[-2])
# if item6 != 'GENERAL_ERROR' and item6 != 'FAILED':
#     data_for_table.append([
#     IT6[0],  # Measurement
#     IT6[1],  # Value
#     IT6[2],  # Lower limit
#     IT6[3],  # Upper limit
#     IT6[4],  # Type
#     IT6[5],  # Unit
#     IT6[6]   # Result
#     # IT6[8]   # Result
# ])
# elif item6 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []

# item7 = conexion.parameters_inspection_xt(IT7,inspection_xt.split(",")[-2])
# if item7 != 'GENERAL_ERROR' and item7 != 'FAILED':
#     data_for_table.append([
#     IT7[0],  # Measurement
#     IT7[1],  # Value
#     IT7[2],  # Lower limit
#     IT7[3],  # Upper limit
#     IT7[4],  # Type
#     IT7[5],  # Unit
#     IT7[6]   # Result
#     # IT7[8]   # Result
# ])
# elif item7 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item8 = conexion.parameters_inspection_xt(IT8,inspection_xt.split(",")[-2])
# if item8 != 'GENERAL_ERROR' and item8 != 'FAILED':
#     data_for_table.append([
#     IT8[0],  # Measurement
#     IT8[1],  # Value
#     IT8[2],  # Lower limit
#     IT8[3],  # Upper limit
#     IT8[4],  # Type
#     IT8[5],  # Unit
#     IT8[6]   # Result
#     # IT8[8]   # Result
# ])
# elif item8 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item9 = conexion.parameters_inspection_xt(IT9,inspection_xt.split(",")[-2])
# if item9 != 'GENERAL_ERROR' and item9 != 'FAILED':
#     data_for_table.append([
#     IT9[0],  # Measurement
#     IT9[1],  # Value
#     IT9[2],  # Lower limit
#     IT9[3],  # Upper limit
#     IT9[4],  # Type
#     IT9[5],  # Unit
#     IT9[6]   # Result
#     # IT9[8]   # Result
# ])
# elif item9 == 'FAILED':
#     print("FAILED")
#     # return "FAILED", []
# item10 = conexion.parameters_inspection_xt(IT10,inspection_xt.split(",")[-2])
# if item10 != 'GENERAL_ERROR' and item10 != 'FAILED':
#     data_for_table.append([
#     IT10[0],  # Measurement
#     IT10[1],  # Value
#     IT10[2],  # Lower limit
#     IT10[3],  # Upper limit
#     IT10[4],  # Type
#     IT10[5],  # Unit
#     IT10[6]   # Result
#     # IT10[8]   # Result
# ])
# elif item10 == 'FAILED':
#     print("FAILED")
    # return "FAILED", []