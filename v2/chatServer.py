import sys
import logging
import socket
import SocketServer
import threading
import thread
import chatServerRcv
import chatServerSnd

import protocol_pb2

class socket_valid:
	def __init__(self):
		self.resend = 0
		self.puzzle = ""
		self.flag = 0

	def addresend():
		self.resend = self.resend + 1

	def resendclear():
		self.resend = 0

	def getresend():
		return self.resend

	def resetflag():
		self.flag = 0

	def setflag():
		self.flag = 1

	def getflag():
		return self.flag



VERSION = '0.1'
MAX_RESEND = 10

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
	7: chatServerRcv.quit	
	}

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

		blackflag = 1
		# send first puzzle to validate
		#########################
		puzzle = '0' #### should be a function by Dimitris
		##### Send package to client.
		chatServerSnd.puzzle_send(self.request, puzzle, VERSION)
		#########################

		# # receive package
		# self.message = self.request.recv(1024)
		# if len(self.message) == 0:
		# 	print("Check The Issue Here.")
		# 	raise KeyboardInterrupt

		# package = protocol_pb2.Client2Server()
		# package.ParseFromString(self.message)

		# # check the package see if the puzzle is solved.
		# if package.opcode != 9:
		# 	# blacklist
		# 	###############################
		# 	blackflag = 0
		# else:
		# 	# check the result, res is boolean
		# 	res = chatServerRcv.puzzle_check(package, self.request, self.server.data, self.server.lock, VERSION, puzzle)
		# 	if res:
		# 		# whitelist
		# 		self.server.whitelist[client_addr] = socket_counter(puzzle)
		# 	else:
		# 		#add client address to blacklist
		# 		#################################
		# 		blackflag = 0

		puzzleflag = 0 # if 1 then the server should send the puzzle again, 0 then not
		# first validation is done
		while True:
			try:
				self.message = self.request.recv(1024)
				if len(self.message) == 0:
					raise KeyboardInterrupt

				package = protocol_pb2.Client2Server()
				package.ParseFromString(self.message)	# parsing the package using Protocol Buffer

				if client_addr not in self.server.whitelist:
					self.server.whitelist[client_addr] = socket_valid()
				socket_obj = self.server.whitelist[client_addr]
				
				socket_obj.addresend()

				socket_obj.addwait()

				if package.opcode == 0:	   # in some case an empty package may be sent
					continue

				if socket_obj.getresend() > MAX_RESEND:
					puzzleflag = 1 # now we need to send a puzzle with the response to the client later
					socket_obj.resetflag() # restart every counter


				# socket_cnt.addresend()
				# socket_cnt.addwait()
				# if socket_cnt.getresend() > MAX_RESEND:
				# 	puzzleflag = 1
				# 	socket_cnt.resetflag()
				# if socket_cnt.getwait() >= MAX_WAIT && socket_cnt.getflag() == 0:
				# 	#add client address to blacklist
				# 	#################################
				# 	# delete client address from whitelist
				# 	del self.server.whitelist[client_addr]
				# 	break

			# except:
			# 	logging.critical('client connection dropped.')

				if puzzleflag == 1:
					#############################################
					puzzle = '1' # need function to generate puzzle
					#############################################
				if package.version == VERSION:
					try:
						OPCODES[package.opcode](package, self.request, self.server.data, self.server.lock, VERSION, puzzleflag, puzzle, socket_obj) # message that server sends to client 
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