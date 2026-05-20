__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

element = ['50', '10', '100']

def evaluation(element):
    value = float(element[0])
    lowerlimit = float(element[1])
    upperlimit = float(element[2])

    # if (value < upperlimit and value > lowerlimit):
    #     print("GTLT")
    # if (value < upperlimit and value >= lowerlimit):
    #     print("GELT")
    # if (value <= upperlimit and value > lowerlimit):
    #     print("GTLE")
    # if (value < lowerlimit or value > upperlimit):
    #     print("LTGT")
    # if (value <= lowerlimit or value >= upperlimit):
    #     print("LEGE")
    # if (value <= lowerlimit or value > upperlimit):
    #     print("LEGT")
    # if (value < lowerlimit or value >= upperlimit):
    #     print("LTGE")
    if lowerlimit ==0 and upperlimit == 0:
        return "LOG"
    elif lowerlimit == upperlimit:
        return("EQ")
    elif (value <= upperlimit and value >= lowerlimit):
        return("GELE")

    elif (value <= lowerlimit or value >= upperlimit):
        return("GELE")

# evaluation(element)