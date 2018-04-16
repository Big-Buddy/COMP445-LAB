import socket
import json
import threading
import datetime as dt

def sender(ip_address,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (ip_address, port)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
	
	user_name = ''

	while(True):
		user_message = input()
		message = json.dumps(build_message(user_message, user_name))

		check = json.loads(message)
		if (check['command'] == 'LEAVE'):
			user_name = ''
		elif(check['command'] == 'JOIN'):
			user_name = json.loads(message)['user_name']

		sent = sock.sendto(message.encode(), server_address)

def receiver(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('', port)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.bind(server_address)

	while(True):
		data, address = sock.recvfrom(1024)
		message = json.loads(data.decode())
		if (message['user_message']):
			print(parse_message(message))

def build_message(user_message, user_name):
	if (user_message == '/leave'):
		return {'user_name' : user_name, 'command' : 'LEAVE', 'user_message' : ''}
	elif(user_message == '/join'):
		new_user_name = input('Enter your new username: ')
		return {'user_name' : new_user_name, 'command' : 'JOIN', 'user_message' : ''}
	else:
		if(user_name):
			return {'user_name' : user_name, 'command' : 'TALK', 'user_message' : user_message}
		else:
			print('\nYou need a username to chat, please /join')
			return {'user_name' : '', 'command' : '', 'user_message' : ''}

def parse_message(message):
	command = message['command']
	user_name = message['user_name']
	user_message = message['user_message']

	return {
		'TALK' : str(dt.datetime.now()) + ' [' + user_name + ']: ' + user_message,
		'JOIN' : str(dt.datetime.now()) + ' ' + user_name + ' has joined',
		'LEAVE' : user_name + ' has left the chat'
	}.get(command, '')

port = 10000

threading.Thread(target=receiver, args=(port,)).start()

threading.Thread(target=sender, args=('255.255.255.255', port)).start()