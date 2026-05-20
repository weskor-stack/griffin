__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import platform
import socket
import os

def getName():
    plataform2 = platform.node()
    socket_name = socket.gethostname()
    system = os.environ['COMPUTERNAME']

    #print(plataform2)
    return plataform2

#getName()