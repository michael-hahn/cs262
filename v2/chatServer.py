import sys
import logging
import socket
import SocketServer
import threading
import thread
import chatServerRcv

import protocol_pb2

class socket_valid:
	def __init__(self):
		self.wait = 0
		self.resend = 0
	
	def addwait():
		self.wait = self.wait + 1

	def addresend():
		self.resend = self.resend + 1

	def waitclear():
		self.wait = 0

	def resentclear():
		self.resend = 0

	def getwait():
		return self.wait

	def getresend():
		return self.resend


VERSION = '0.1'
MAX_WAIT = 1
MAX_RESEND = 3

"""
Operation codes found in the packages from the client to the server.
"""
OPCODES = { 
	# operation code in packages sent for a create_account request from the client
	1: chatServerRcv.create_account,
	# operation code in packages sent for a log-in request from the client
	2: chatServerRcv.log_in,
	# operation code in packages sent for a send-message-to-another-client request from the client
	3: chatServerRcv.send_message,
	# operation code in packages sent for a get-my-unread-messages request from the client
	4: chatServerRcv.check_message,
	# operation code in packages sent for a delete-my-account request from the client
	5: chatServerRcv.delete_account,
	# operation code in packages sent for a list-all-accounts request from the client
	6: chatServerRcv.list_account,
	# operation code in packages sent for a log-out request from the client
	7: chatServerRcv.quit}

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	"""
	This class overwrites the superclass of all request handler objects, BaseRequestHandler.

	This concrete request handler subclass define a new handle method.
	A new instance of this subclass is created for each request.
	"""

	"""
	This method overwrites the superclass handle() method to implement communication to the clients.
	self.request is the TCP socket object.
	"""
	def handle(self):
		client_addr = self.client_address
		logging.info('client connected from: %s', client_addr)

		while True:
			try:
				self.message = self.request.recv(1024)

				if client_addr not in self.server.whitelist:
					self.server.whitelist[client_addr] = socket_counter()
				else:
					socket_cnt = self.server.whitelist[client_addr]
					socket_cnt.addresend()
					socket_cnt.addwait()
					if socket_cnt.getresend >= MAX_RESEND:
						# 

				if len(self.message) == 0:
					raise KeyboardInterrupt
			# except:
			# 	logging.critical('client connection dropped.')

				package = protocol_pb2.Client2Server()
				package.ParseFromString(self.message)	# parsing the package using Protocol Buffer

				if package.opcode == 0:	   # in some case an empty package may be sent
					continue

				if package.version == VERSION:
					try:
						OPCODES[package.opcode](package, self.request, self.server.data, self.server.lock, VERSION)
					except:
						logging.critical('unexpected fatal error occurred. Check server request handler.')
				else:
					logging.critical('client uses a different version.')
			except KeyboardInterrupt:
				logging.critical('Keyboard interrupt on Server.')
				thread.exit()
			except:
				logging.critical('client connection dropped.')


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	"""
	This class uses thread mix-in class to create multi-threaded asynchronous TCP server.
	It overwrites a method defined in TCPServer.

	Multiple requests therefore can be handled at the same time without blocking.
	However, a lock may be needed to protect the integrity of the shared server data, if any, 
	in case multiple clients modify the share data at the same time.
	"""
	pass

if __name__ == '__main__':
	"""
	This function initializes the TCP server as an instance of the class ThreadedTCPServer that listens to port 8080.
	
	The server contains a dictionary data structure server.data that contains information about all the
	accounts of the clients and is initialized to the empty dictinary since there are no users registered a-priory
	in the system. The integrity of this information is protected through server.lock for the case where
	multiple clients try to access this information simultaneously.
	"""
	logging.basicConfig(filename='server.log', format='%(levelname)s: [%(asctime)s] %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %I:%M:%S %p')
	logging.debug('chat server logging initiated.')

	HOST = ''
	PORT = 8080
	
	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	server.data = {}
	server.whitelist = {} # good clients are put into server's whitelist dictionary
	server.lock = threading.Lock()
	hostIP = socket.gethostbyname(socket.gethostname())
	print hostIP
	logging.info('server binds to: %s:%s', HOST, PORT)
	logging.info('server data structure initialized.')	
		
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.setDaemon(True)
	server_thread.start()
	logging.info('server thread spawned and started for incoming requests')

	while True:
		try:
			pass
		except:
			break