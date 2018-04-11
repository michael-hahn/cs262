import protocol_pb2
import logging
from struct import pack

def send_package(client_socket, serialized_package):
	"""
	This function sends a package from the server to the client.
	It catches an exception and writes an error message in the log if the connection is shut down.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		serialized_package: the package about to be sent (serialized using SerializeToString method)
	"""
	try:
		client_socket.send(serialized_package)
	except:
		logging.critical('client connection dropped in send_package.')

def create_account_success(client_socket, account_name, version):
	"""
	Sends a package to the client with a message to report that a new account was created successfully.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name used by the client
		version: the version of the wire protocol
	"""
	logging.info('server informs client that a new account is created successfully.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 1
	package = pack('!I', version) + pack('!I', 1)
	msg = "New account " + account_name + " is created successfully."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)


def create_account_failure(client_socket, account_name, version):
	"""
	Sends a package to the client with a message to report that the account name
	that was asked already exists and hence the new account was not created successfully.

	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name used by the client
		version: the version of the wire protocol
	"""
	logging.info('server informs client that the account exists.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 2
	package = pack('!I', version) + pack('!I', 2)
	msg = "The account " + account_name + " exists already."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def send_message_success(client_socket, receiver, version):
	"""
	Sends a package to the client with a message to report that the message was delivered successfully
	to the account that was specified.

	Arguments:
		client_socket: the socket through which we talk with the client
		receiver: the account name to which we sent the message
		version: the version of the wire protocol
	"""
	logging.info('server informs client that the new message is sent successfully.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 3
	package = pack('!I', version) + pack('!I', 3)
	msg = "New message is sent to " + receiver + " successfully."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def send_message_failure_sender(client_socket, receiver, version):
	"""
	Sends a package to the client with a message to report that the message was not delivered to the
	account that was specified because the client has not logged in.

	Arguments:
		client_socket: the socket through which we talk with the client
		receiver: the account name to which we attempted to sent the message
		version: the version of the wire protocol
	"""
	logging.info('server informs client that he/she is not a registered user.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 4
	package = pack('!I', version) + pack('!I', 4)
	msg = "You need to log in first. You do not have an account to send message to " + receiver
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def send_message_failure_receiver(client_socket, receiver, version):
	"""
	Sends a package to the client with a message to report that the message was not delivered to the
	account that was specified because the recipient does not correspond to a valid account.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		receiver: the account name to which we attempted to sent the message
		version: the version of the wire protocol
	"""
	logging.info('server informs client that the recipient does not exist.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 5
	package = pack('!I', version) + pack('!I', 5)
	msg = "The recipient " + receiver + " does not exist."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def check_message_success(client_socket, message, version):
	"""
	Sends a package to the client with a message to report that all the unread messages were delivered successfully.

	Arguments:
		client_socket: the socket through which we talk with the client
		message: all the unread messages of the client concatenated in a string
		version: the version of the wire protocol
	"""
	logging.info('server returns all unread messages to the registered user.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 6
	package = pack('!I', version) + pack('!I', 6)
	msg = message
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def check_message_failure(client_socket, sender, version):
	"""
	Sends a package to the client with a message to report that the unread messages of the account
	could not be delivered because the client has not logged in in any account.

	Arguments:
		client_socket: the socket through which we talk with the client
		sender: not important for this function
		version: the version of the wire protocol
	"""
	logging.info('server informs client that he/she is not logged in to check message.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 7
	package = pack('!I', version) + pack('!I', 7)
	msg = "You need to logged in to check unread messages."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def delete_account_success(client_socket, message, version):
	"""
	Sends a package to the client with a message to report that the specified account was deleted successfully.

	Arguments:
		client_socket: the socket through which we talk with the client
		message: all the unread messages of the client that we just deleted the account of, concatenated in a string
		version: the version of the wire protocol
	"""

	logging.info('server successfully deleted the account and return all unread messages.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 8
	package = pack('!I', version) + pack('!I', 8)
	msg = message
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def delete_account_failure(client_socket, sender, version):
	"""
	Sends a package to the client with a message to report that no account was deleted
	because the client has not logged in.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		sender: not important for this function
		version: the version of the wire protocol
	"""
	logging.info('server informs client that unknown account cannot be deleted.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 9
	package = pack('!I', version) + pack('!I', 9)
	msg = "The unknown account cannot be deleted. You need to log in first."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def list_account_success(client_socket, results, version):
	"""
	Sends a package to the client with a message to report that all the requested account names were sent to it.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		results: all the accounts that matched the search criteria, concatenated in a string
		version: the version of the wire protocol
	"""
	logging.info('server returns to the client of all the matching accounts.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 10
	package = pack('!I', version) + pack('!I', 10)
	msg = "The accounts that match your criteria: \n" + results
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def quit_success(client_socket, sender, version):
	"""
	Sends a package to the client with a message to report that the client logged out successfully.

	Arguments:
		client_socket: the socket through which we talk with the client
		sender: the account name of the client
		version: the version of the wire protocol
	"""
	logging.info('server quits the client successfully.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 11
	package = pack('!I', version) + pack('!I', 11)
	msg = "You: " + sender + " has logged out successfully."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def quit_failure(client_socket, sender, version):
	"""
	Sends a package to the client with a message to report that the logout attempt failed
	because the client has not logged in in any account.

	Arguments:
		client_socket: the socket through which we talk with the client
		sender: the account name of the client
		version: the version of the wire protocol
	"""
	logging.info('server cannot quit an unknown client')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 12
	package = pack('!I', version) + pack('!I', 12)
	msg = "You need to log in first to log out."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def log_in_success(client_socket, account_name, version):
	"""
	Sends a package to the client with a message to report that the client successfully logged in in the
	specified account.

	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name where the client just logged in
		version: the version of the wire protocol
	"""
	logging.info('account %s is successfully logged in.', account_name)

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 13
	package = pack('!I', version) + pack('!I', 13)
	msg = "Account " + account_name + " is successfully logged in"
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def log_in_failure(client_socket, account_name, version):
	"""
	Sends a package to the client with a message to report that the log in attempt to the specified account
	name failed, because the requested account name does not exist in the server.

	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name where the client attempted to log in
		version: the version of the wire protocol
	"""
	logging.info('account %s cannot be logged in as it does not exist', account_name)

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 14
	package = pack('!I', version) + pack('!I', 14)
	msg = "Account " + account_name + " cannot be logged in. It does not exist."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def log_in_already(client_socket, account_name, version):
	"""
	Sends a package to the client with a message to report that the log in attempt to the specified account
	name failed, because the requested account is already logged in.
	
	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name where the client attempted to log in
		version: the version of the wire protocol
	"""
	logging.info('account %s has already logged in', account_name)

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 15
	package = pack('!I', version) + pack('!I', 15)
	msg = "Account " + account_name + " has already logged in."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)
 
def log_in_other(client_socket, acc, version):
	"""
	Sends a package to the client with a message to report that the log in attempt to the specified account
	name was successful, but another client was connected in the same socket, which was forced to log out.

	Arguments:
		client_socket: the socket through which we talk with the client
		account_name: the account name where the client attempted to log in
		version: the version of the wire protocol
	"""
	logging.info('account %s was logged in here. Now it is forced to log out. New account is now logged in.', acc)

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 16
	package = pack('!I', version) + pack('!I', 16)
	msg = "Account " + acc + " has logged in here. That account is forced to log out. You are now logged in."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)

def direct_send(receiver_socket, message, version):
	"""
	Sends a package to the client with a message to report that the requested message was delivered successfully
	to the account that was specified because the recipient was online.
	
	Arguments:
		receiver_socket: the socket through which we talk with the recipient of the message
		message: the that we are about to send to the recipient
		version: the version of the wire protocol
	"""
	logging.info('server sent the message directly to the receiver because it is online')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 17
	package = pack('!I', version) + pack('!I', 17)
	msg = message
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	try:
		receiver_socket.send(package)
		return True
	except:
		logging.critical('client connection dropped in send_package.')
		return False

def list_account_failure(client_socket, results, version):
	"""
	Sends a package to the client with a message to report that the list_account request could not succeed due
	to unexpected failure.
	
	Arguments:
		receiver_socket: the socket through which we talk with the recipient of the message
		results: not important in this function
		version: the version of the wire protocol
	"""
	logging.info('server had trouble listing accounts.')

	# package = protocol_pb2.Server2Client()
	# package.version = version
	# package.opcode = 18
	package = pack('!I', version) + pack('!I', 18)
	msg = "Server failed unexpectedly."
	utfbuf = msg.encode('utf-8')
	utfbuflen = len(utfbuf)
	package = package + pack('!I', utfbuflen) + utfbuf

	send_package(client_socket, package)
