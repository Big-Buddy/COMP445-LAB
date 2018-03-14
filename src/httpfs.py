"""
Usage: 
	httpfs.py [-v] [-p=<port>] [-d=<dir_path>]

Options:	
	-v            prints debuggin messages
	-p=<port>     specifies the port number the server will listen and serve at (DEFAULT: 8080)
	-d=<dir_path> specifies the directory that the server will use to read/write requested files (DEFAULT: current directory when app is launched)

"""

from docopt import docopt
from urllib.parse import urlparse
import socket
import sys
import json
import os
import threading

def run_server(port):
    print('Server hosted by', socket.gethostname())
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((socket.gethostname(), port))
        listener.listen(5)
        print('Server is listening at', port)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    finally:
        listener.close()

def handle_client(conn, addr):
    print('New client from', addr)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            ##SERVE THE REQUEST
            # IF GET return all files @ dir_path

            # IF GET W/ FILENAME return the content of file RETURN ERROR IF FILE DNE

            # IF POST W/ FILENAME create new file with that name OR overwrite existing file with content body of request

            ##SEND BACK THE RESPONSE
            conn.sendall(data)
    finally:
        conn.close()

if __name__ == '__main__':
	arguments = docopt(__doc__, help=False, version='1.0.0rc2')

	port = 8080
	dir_path = os.getcwd()
	
	##Overwrite defaults if necessary
	if(arguments["-p"]):
		port = int(arguments["-p"])
	if(arguments["-d"]):
		dir_path = arguments["-d"]
    
	run_server(port)	

	print(arguments)
