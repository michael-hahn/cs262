import sys
import logging
import protocol_pb2
from time import time

def send_package(server_socket, serialized_package):
	"""
	This function sends a package from the client to the server. It catches an exception if
	the connection is down and terminates the client after writing an error message in the log file.
	
	Arguments:
		server_socket: the socket through which we talk to the server
		serialized_package: the package to be transmitted through the socket
	"""
	try:
		server_socket.send(serialized_package)
	except:
		#close the client if the connection is down
		logging.critical('server connection dropped.')
		sys.exit()

def create_approved(version, server_socket):
	logging.info('client solved the puzzle, do create_account')
	# print('client solved the puzzle, do create_account')
	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 20
	send_package(server_socket, package.SerializeToString())

def evil_msg(version, server_socket):
	# fakemsg = str(time())
	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 4

	# package.msg = fakemsg
	send_package(server_socket, package.SerializeToString())


def create_account(version, server_socket):
	"""
	This function is responsible for sending a package to the server with the message to create
	a new account. The user specifies the account name which should be at most 25 characters, otherwise
	an error message is printed.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client creating an account.')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 1

	print 'Please enter a new account name (25 characters max):'
	while True:
		try:
			buf = raw_input('>> ')
		except ValueError:
			continue
        
		if(len(buf) > 0 and len(buf) <= 25):
			package.msg = buf
			break
		else:
			print 'Invalid name. Try again please (Remember: 25 characters max).'
			continue
	send_package(server_socket, package.SerializeToString())

def log_in(version, server_socket):
	"""
	This function is responsible for sending a package to the server with the message to log in
	to an account. The user specifies the account name which should be at most 25 characters, otherwise
	an error message is printed.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client logs in')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 2

	print 'Please enter your account name:'
	while True:
		try:
			acc_src = raw_input('>> ')
		except ValueError:
			continue

		if(len(acc_src) > 0 and len(acc_src) <= 25):
			package.msg = acc_src
			break
		else:
			print 'Invalid name. Try again please (Remember: 25 characters max).'
			continue
	send_package(server_socket, package.SerializeToString())

def send_message(version, server_socket):
	"""
	This function is responsible for sending a package to the server with the message to send a message
	to an account. The user specifies the account name of the recipient which should be at most 25 characters, otherwise
	an error message is printed, and the message itself which should be at most 100 characters, otherwise
	an error message is printed.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client sends a message')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 3

	print 'Please enter the destination account name:'
	while True:
		try:
			acc_dst = raw_input('>> ')
		except ValueError:
			continue

		if(len(acc_dst) > 0 and len(acc_dst) <= 25):
			package.receiver = acc_dst
			break
		else:
			print 'Invalid name. Try again please (Remember: 25 characters max).'
			continue

	print 'Please enter your message (100 characters max):'
	while True:
		try:
			msg = raw_input('>> ')
		except ValueError:
			continue

		if(len(msg) > 0 and len(msg) <= 100):
			package.msg = msg
			break
		else:
			print 'Message length is not within the specs. Try again please (Remember: 100 characters max).'
			continue
		break
	send_package(server_socket, package.SerializeToString())

def check_message(version, server_socket):
	"""
	This function is responsible for sending a package to the server to request all the
	messages received during the time that the client was logged out.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client checks unread messages sent to him/her')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 4

	send_package(server_socket, package.SerializeToString())

def delete_account(version, server_socket):
	"""
	This function is responsible for sending a package to the server to request the deletion
	of the client's account.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client deletes a register account')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 5

	print """ Warning: This action is not reversible! You will see all the unread messages, however. """
	send_package(server_socket, package.SerializeToString())

def list_account(version, server_socket):
	"""
	This function is responsible for sending a package to the server to request a list of all the account
	names that match a given regular expression specified by the user.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('list the account(s) that match the criteria')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 6

	print """
	Please enter the criteria: 
	(To list all the accounts, type *; Use text wildcard '_' to match any one character)
	"""
	while True:
		try:
			acc_src = raw_input('>> ')
		except ValueError:
			continue
		package.msg = acc_src
		break
	send_package(server_socket, package.SerializeToString())

def quit(version, server_socket):
	"""
	This function is responsible for sending a package to the server to request a log out
	for the client.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client wants to quit the system.')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 7

	send_package(server_socket, package.SerializeToString())

def inform_dead(version, server_socket):
	"""
	This function informs the server that the client is forced quitted unexpected.

	Arguments:
		version: the version of the protocol
		server_socket: the socket through which we talk to the server
	"""
	logging.info('client being forced quitted')

	package = protocol_pb2.Client2Server()
	package.version = version
	package.opcode = 7

	send_package(server_socket, package.SerializeToString())
