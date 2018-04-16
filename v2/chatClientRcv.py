import logging
import sys


"""
All the functions in this file are used to print the message of the server, reporting on the 
success or failure of a specific operation. The message is received from the server specifying 
the success or failure of the requested operation is printed both in the screen and in the log file.

Arguments:
	server_socket: the socket through which we talk to the server
	msg: the message sent from the server to the client
"""

def create_account_success(server_socket, msg):
	print msg
	logging.info(msg)

def create_account_failure(server_socket, msg):
	print msg
	logging.info(msg)

def send_message_success(server_socket, msg):
	print msg
	logging.info(msg)

def send_message_failure_sender(server_socket, msg):
	print msg
	logging.info(msg)

def send_message_failure_receiver(server_socket, msg):
	print msg
	logging.info(msg)

def check_message_success(server_socket, msg):
	print msg
	logging.info('server returns all unread messages to the registered user.')

def check_message_failure(server_socket, msg):
	print msg
	logging.info(msg)

def delete_account_success(server_socket, msg):
	print msg
	logging.info(msg)

def delete_account_failure(server_socket, msg):
	print msg
	logging.info(msg)

def list_account_success(server_socket, msg):
	print msg
	logging.info(msg)

def quit_success(server_socket, msg):
	print msg
	logging.info(msg)
	server_socket.close()
	sys.exit()

def quit_failure(server_socket, msg):
	print msg
	logging.info(msg)

def log_in_success(server_socket, msg):
	print msg
	logging.info(msg)

def log_in_failure(server_socket, msg):
	print msg
	logging.info(msg)

def log_in_already(server_socket, msg):
	print msg
	logging.info(msg)

def log_in_other(server_socket, msg):
	print msg
	logging.info(msg)

def direct_send(server_socket, msg):
	print msg
	logging.info(msg)

def list_account_failure(server_socket, msg):
	print msg
	logging.info(msg)
