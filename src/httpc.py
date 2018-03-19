"""
Usage: 
	httpc.py (get | post) [-v] [-h=<key:value> ...] [-d=<inline-data> | -f=<file>] [-o=<file>] URL

Arguments:
	URL target http server

Options:	
	-v               prints status messages and their headers, and contents of the response
	-h=<key:value>   pass header values to http get or post
	-d=<inline-data> associate http request with some data entered into the cmd line
	-f=<file>        associate http request with data from file
	-o=<file> 		 output http response to a file

"""

from docopt import docopt
from urllib.parse import urlparse
import socket
import sys
import json

def get(args):
	#resolving host and query
	url = urlparse(args["URL"])
	host = url.hostname
	path = "/" if len(url.path) < 1 else url.path
	query = "" if len(url.query) < 1 else "?" + url.query

	if(not host):
		host = socket.gethostbyname(socket.gethostname())

	#resolving header
	headers = args["-h"]
	header = "Host: "+ str(host)
	for h in headers:
		head = h.split(":", 1)
		header = header + "\r\n" + head[0] + ": " + head[1]

	#making the request
	request = "GET "+path+query+" HTTP/1.0\r\n"+header+"\r\n\r\n"
	request = request.encode('utf-8')
	
	#sending the request
	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, 8080))
	s.send(request)
	result = s.recv(10000)
	s.close()

	#do different things depending on verbosity
	verbose = args["-v"]
	response = ""

	temp = result.decode().split("\n\n")
	if(not(len(temp) > 1)):
		temp = result.decode().split("\r\n\r\n")
	start = 0 if verbose else 1
	for x in range(start, len(temp)):
		response = response + temp[x]
		if x == 0:
			response = response + "\n\n"

	return response
		
def post(args):
	#resolving host and query
	url = urlparse(args["URL"])
	host = url.hostname
	path = "/" if len(url.path) < 1 else url.path
	query = "" if len(url.query) < 1 else "?" + url.query

	if(not host):
		host = socket.gethostbyname(socket.gethostname())

	#resolving header
	headers = args["-h"]
	header = "Host: "+ str(host)
	for h in headers:
		head = h.split(":", 1)
		header = header + "\r\n" + head[0] + ": " + head[1]

	#get the dataz
	if(args["-d"]):
		data = args["-d"]
	elif(args["-f"]):
		with open(args["-f"]) as f:
			data = f.read()
	datalength = len(data)

	#making the request
	request = "POST "+path+query+" HTTP/1.0\r\n"+header+"\r\nContent-Length: "+str(datalength)+"\r\n\r\n"+data
	request = request.encode('utf-8')

	#sending the request
	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, 8080))
	s.send(request)
	result = s.recv(10000)
	s.close()

	#do different things depending on verbosity
	verbose = args["-v"]
	response = ""

	temp = result.decode().split("\n\n")
	if(not(len(temp) > 1)):
		temp = result.decode().split("\r\n\r\n")
	start = 0 if verbose else 1
	for x in range(start, len(temp)):
		response = response + temp[x]
		if x == 0:
			response = response + "\n\n"

	return response

if __name__ == '__main__':
    arguments = docopt(__doc__, help=False, version='1.0.0rc2')
    ## Arguments is essentially a kind of JSON-like object that has each option/argument bool/actual value inside it (depending on whether option accepts an argument)
    ## We can then use these values and do something with them
    if(arguments["get"] and (arguments["-f"] or arguments["-d"])):
    	print("You cannot use -d or -f with a GET request")
    	sys.exit()
    if(arguments["post"] and not (arguments["-f"]) and not (arguments["-d"])):
    	print("You cannot use post without associating some data")
    	sys.exit()
    
    #delete this once you feel everything works. purely for debugging
    ##print(arguments)

    #Do the actual GET/POST and get the response
    response = ""
    if(arguments["get"]):
    	response = get(arguments)
    elif(arguments["post"]):
    	response = post(arguments)

    #After GET/POST, output response to file if wanted
    if(arguments["-o"]):
    	file = open(arguments["-o"], 'w')
    	file.write(response)
    	file.close()

    print(str(response))
