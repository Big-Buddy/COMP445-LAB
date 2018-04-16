import socket
import sys
import json
import threading
import datetime as dt

def sender(user_name, ip_address,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (ip_address, port)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
	
	while(True):
		user_message = input()
		message = json.dumps({'user_name' : user_name, 'user_message' : user_message})
		sent = sock.sendto(message.encode(), server_address)

def receiver(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('', port)
	sock.bind(server_address)

	while(True):
		data, address = sock.recvfrom(1024)
		message = json.loads(data.decode())
		print(str(dt.datetime.now()) + " [" + message['user_name'] + "] " + message['user_message'])

port = int(sys.argv[1])

threading.Thread(target=receiver, args=(port,)).start()

user_name = input('Enter your name: ')
threading.Thread(target=sender, args=(user_name, '255.255.255.255', port)).start()