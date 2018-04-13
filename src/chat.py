import socket
import sys
import json

def sender(user_name, ip_address,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (ip_address, port)
	
	while(True):
		user_message = input('Send a message: ')

		try:
			sent = sock.sendto(message, server_address)
		finally:
			sock.close()

def receiver(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', port)
	sock.bind(server_address)

	while(True):
		data, address = sock.recvfrom(1024)
		print(data + ' from ' + address)

option = sys.argv[1]
port = sys.argv[2]

if(option == 'server'):
	receiver(port)
elif(option == 'client'):
	sender('localhost', port)
	
