__author__ = "Edgar Bonilla Rivas"
__copyright__ = "Copyright (C) 2025 Author Name"
__license__ = "AUTOMATYCO"
__version__ = "v2.0.0"

import os

contador = 0

def connection_message (connection):
    if connection == "Conectado":
        contador = 1
        print(connection)
        return contador
    else:
        contador = 2
        print(connection)
        if os.name == 'nt':
            # For Windows operating system
            os.system('shutdown /s /t 0')
        elif os.name == 'posix':
            # For Unix/Linux/Mac operating systems
            os.system('sudo shutdown now')
        # os.system("shutdown /s /t 1")
        return contador

def tester():
    test = connection_message("Desconectado")
    print(test)

tester()
# connection_message("Desconectado")