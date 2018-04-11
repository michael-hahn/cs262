import logging
import sys
from struct import unpack 

"""
All the functions in this file are used to print the message of the server, reporting on the 
success or failure of a specific operation. The message is received from the server specifying 
the success or failure of the requested operation is printed both in the screen and in the log file.

Arguments:
	server_socket: the socket through which we talk to the server
	msg: the package containing the message sent from the server to the client
"""

def create_account_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def create_account_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def send_message_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def send_message_failure_sender(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def send_message_failure_receiver(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def check_message_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info('server returns all unread messages to the registered user.')

def check_message_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def delete_account_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def delete_account_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def list_account_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def quit_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)
	server_socket.close()
	sys.exit()

def quit_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def log_in_success(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def log_in_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def log_in_already(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def log_in_other(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def direct_send(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)

def list_account_failure(server_socket, msg):
	msg_len = unpack('!I', msg[8:12])[0]
	message = msg[12:12+msg_len].decode('utf-8')
	print message
	logging.info(message)
