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

def run_server(port, dir_path):
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
            request = data.decode()

            request_buffer = request.split("\n\n")
            if(not(len(request_buffer) > 1)):
                request_buffer = request.split("\r\n")
            print(request_buffer)
            method = request_buffer[0]
            response = ""

            file_flag = False

            for x in request_buffer:
                    if("file" in x):
                        file_flag = True
                        file_name = x[7:]

            if("POST" in method):
                write_data = request_buffer[len(request_buffer)-1]
                response = post(dir_path, file_name, write_data)
            elif("GET" in method):
                if(file_flag):
                    #response = get_file_content(dir_path, file_name)
                else:
                    #response = get_dir_list(dir_path)
                    
            conn.sendall(response.encode())
    finally:
        conn.close()


def get_dir_list(dir_path):
    file_list_text = ''
    for filesnames in os.walk(dirpath):
        for filename in filenames:
            list_text.append(filename + '\n')
    return file_list_text

def get_file_content(dir_path, file_name):
    f = open(dir_path+file_name, 'r')
    file_content = f.read()
    return file_content

def post(dir_path, file_name, write_data):
    f = open(dir_path+file_name, 'w')
    f.write(write_data)

if __name__ == '__main__':
	arguments = docopt(__doc__, help=False, version='1.0.0rc2')

	port = 8080
	dir_path = os.getcwd()
	
	##Overwrite defaults if necessary
	if(arguments["-p"]):
		port = int(arguments["-p"])
	if(arguments["-d"]):
		dir_path = arguments["-d"]
    
	run_server(port, dir_path)	

	print(arguments)
