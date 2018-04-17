import socket
import json
import threading
import datetime as dt
import time

class sender(threading.Thread):
	def __init__(self, ip, port):
			threading.Thread.__init__(self)
			self.running = 1
			self.port = port
			self.user_name = ''
			self.ip = ip
			self.joined = False

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = (self.ip, self.port)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

		while(self.running == 1):
			if (self.joined == False):
				self.user_name = input('Enter your username: ')
				self.joined = True
				init_message = json.dumps(sender.build_message('/join'))
				sock.sendto(init_message.encode(), server_address)

			user_message = input()

			if(user_message):
				if(user_message == '/leave'):
					message = json.dumps(sender.build_message(user_message))
					quitting = json.dumps(sender.build_message('/quit'))

					sock.sendto(message.encode(), server_address)
					sock.sendto(quitting.encode(), ('localhost', port))
				elif(user_message == '/who'):
					message = json.dumps(sender.build_message(user_message))
					sock.sendto(message.encode(), ('localhost', port))
				else:
					message = json.dumps(sender.build_message(user_message))

					sock.sendto(message.encode(), server_address)

			time.sleep(0)

	def kill(self):
		self.running = 0

	def build_message(self, user_message):
		if (user_message == '/leave'):
			return {'user_name' : self.user_name, 'command' : 'LEAVE', 'user_message' : ''}
		elif(user_message == '/join'):
			return {'user_name' : self.user_name, 'command' : 'JOIN', 'user_message' : ''}
		elif(user_message == '/quit'):
			return {'user_name' : self.user_name, 'command' : 'QUIT', 'user_message' : ''}
		elif(user_message == '/who'):
			return {'user_name' : self.user_name, 'command' : 'WHO', 'user_message' : ''}
		elif(user_message == '/ping'):
			return {'user_name' : self.user_name, 'command' : 'PING', 'user_message' : ''}
		else:
			return {'user_name' : self.user_name, 'command' : 'TALK', 'user_message' : user_message}

	def ping(self, sock):
		ping = json.dumps(sender.build_message('/ping'))
		sock.sendto(ping.encode(), (self.ip, self.port))

class receiver(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.running = 1
		self.port = port
		self.user_list = set()

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('', self.port)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.bind(server_address)

		while(self.running == 1):
			data, address = sock.recvfrom(1024)
			message = json.loads(data.decode())

			if (message['command'] == 'QUIT'):
				print('Bye!')
				sender.kill()
				receiver.kill()
			elif (message['command'] == 'PING'):
				self.user_list.add(message['user_name'])
			else:
				print(receiver.parse_message(message, sock))
			
			time.sleep(0)

	def kill(self):
		self.running = 0

	def parse_message(self, message, sock):
		command = message['command']
		user_name = message['user_name']
		user_message = message['user_message']
		separator = ', '

		if (command == 'JOIN'):
			self.user_list.add(user_name)
			sender.ping(sock)
			sorted(self.user_list)
		elif(command == 'LEAVE'):
			self.user_list.discard(message['user_name'])

		return {
			'TALK' : str(dt.datetime.now()) + ' [' + user_name + ']: ' + user_message,
			'JOIN' : str(dt.datetime.now()) + ' ' + user_name + ' has joined',
			'LEAVE' : str(dt.datetime.now()) + ' ' + user_name + ' has left the chat',
			'WHO' : str(dt.datetime.now()) + ' Connected users: ' + separator.join(self.user_list)
		}[command]

### MAIN
port = 10000
ip = '255.255.255.255'

sender = sender(ip, port)
receiver = receiver(port)
sender.start()
receiver.start()