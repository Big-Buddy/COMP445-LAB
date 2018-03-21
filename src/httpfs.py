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

def run_server(port, dir_path, verbosity):
    print('Server hosted by', socket.gethostname())
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((socket.gethostname(), port))
        listener.listen(5)
        print('Server is listening at', port)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr, verbosity)).start()
    finally:
        listener.close()

def handle_client(conn, addr, verbosity):
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
            method = request_buffer[0]
            response = ""

            file_flag = False
            file_name = ''

            for x in request_buffer:
                    if("file" in x):
                        file_flag = True
                        file_name = x[6:]

            if(verbosity):
                print("Request: " + method + " " + file_name)

            if(insecure_path(file_name)):
                response = "HTTP/1.0 403 FORBIDDEN\r\n" + "Content-Type: text\r\n\r\nThe directory you are trying to access is outside the working directory of the server. Access denied.\r\n"
                if(verbosity): print("Bad user ;-)")
            elif("POST" in method):
                write_data = request_buffer[len(request_buffer)-1]
                response = post(dir_path, file_name, write_data)
                if(verbosity):
                    if("403" in response):
                        print("Bad user ;-)")
                    else:
                        print("Good user!")
            elif("GET" in method):
                if(file_flag):
                    response = get_file_content(dir_path, file_name)
                    if(verbosity):
                        if("403" in response):
                            print("Bad user ;-)")
                        elif("404" in response):
                            print("Confused user!")
                        else:
                            print("Good user!")
                else:
                    response = get_dir_list(dir_path)
                    if(verbosity): print("Good user!")

            conn.sendall(response.encode('utf-8'))
    finally:
        conn.close()


def get_dir_list(dir_path):
    file_list_text = ''
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    for f in files:
        file_list_text = file_list_text + f + '\n'
    return "HTTP/1.0 200 OK\r\n" + "Content-Type: text\r\n\r\n" + file_list_text + "\r\n"

def get_file_content(dir_path, file_name):
    try:
        f = open(dir_path+file_name, 'r')
    except FileNotFoundError:
        return "HTTP/1.0 404 NOT FOUND\r\n" + "Content-Type: text/html\r\n\r\nThat file does not exist.\r\n"
    else:
        file_content = f.read()
        return "HTTP/1.0 200 OK\r\n" + "Content-Type: text\r\n\r\n" + file_content + "\r\n"

def post(dir_path, file_name, write_data):
    f = open(dir_path+file_name, 'w')
    f.write(write_data)
    raw_response = "target-directory: " + dir_path + '\n' + "target-file: " + file_name + '\n' + "data: " + write_data + '\n'
    return "HTTP/1.0 200 OK\r\n" + "Content-Type: text\r\n\r\n" + raw_response + "\r\n"

def insecure_path(file_name):
    insecure = False
    if("/.." in file_name):
        insecure = True
    return insecure

if __name__ == '__main__':
	arguments = docopt(__doc__, help=False, version='1.0.0rc2')

	port = 8080
	dir_path = os.getcwd()
	
	##Overwrite defaults if necessary
	if(arguments["-p"]):
		port = int(arguments["-p"])
	if(arguments["-d"]):
		dir_path = arguments["-d"]
    
	run_server(port, dir_path, arguments["-v"])	
