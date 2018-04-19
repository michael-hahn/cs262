import sys
import socket
import logging
import protocol_pb2
import chatClientSnd
import chatClientRcv
import select
from time import gmtime, strftime

VERSION = '0.1'

"""
Operation codes found in the packages from the server to the client.
"""
OPCODES = {
	# operation code for packages sent from the server to report the successful creation of a new account
	1: chatClientRcv.create_account_success,
	# operation code for packages sent from the server to report the failure in creation of a new account
	2: chatClientRcv.create_account_failure,
	# operation code for packages sent from the server to report successful sent of a message to another user
	3: chatClientRcv.send_message_success,
	# operation code for packages sent from the server to report failure in sending a message to another user
	# because the client is not logged in
	4: chatClientRcv.send_message_failure_sender,
	# operation code for packages sent from the server to report failure in sending a message to another user
	# because the recipient does not exist
	5: chatClientRcv.send_message_failure_receiver,
	# operation code for packages sent from the server to report successful delivery of all unread messages of the client
	6: chatClientRcv.check_message_success,
	# operation code for packages sent from the server to report failure in delivery of all unread messages of the client
	7: chatClientRcv.check_message_failure,
	# operation code for packages sent from the server to report successful deletion of the client's account
	8: chatClientRcv.delete_account_success,
	# operation code for packages sent from the server to report failure in deleting the client's account
	9: chatClientRcv.delete_account_failure,
	# operation code for packages sent from the server to report successful listing of all the account
	# matching the criteria of the client
	10: chatClientRcv.list_account_success,
	# operation code for packages sent from the server to report successful log out of the client
	11: chatClientRcv.quit_success,
	# operation code for packages sent from the server to report failure in logging out
	12: chatClientRcv.quit_failure,
	# operation code for packages sent from the server to report successful log in of the client
	13: chatClientRcv.log_in_success,
	# operation code for packages sent from the server to report failure in logging in because the requested
	# account name does not exist
	14: chatClientRcv.log_in_failure,
	# operation code for packages sent from the server to report that the client is already logged in in this account
	15: chatClientRcv.log_in_already,
	# operation code for packages sent from the server to report that the client is logged in in another account
	16: chatClientRcv.log_in_other,
	# operation code for packages sent from the server to report successful direct sent of a message to another user
	17: chatClientRcv.direct_send,
	# operation code for packages sent from the server to report failure in listing the requested accounts
	18: chatClientRcv.list_account_failure}


def client_input():
	"""This function allows the client to choose the operation it wants to perform."""
	
	print """
	Connected to the chat server. Please enter the index to execute a function:
	(1) Create an account
	(2) Log in
	(3) Send a message
	(4) Checked unread message
	(5) Delete an account
	(6) List accounts
	(7) Quit
	"""
	client_input = raw_input('>> ')
	return client_input

def interpret_input(client_action, server_socket):
	"""
	This function takes as arguments the action specified by the user and the socket in which the server runs
	and calls the function that is associated with that action.
	If the user provided an invalid action code then it prints an error message and calls client_input() again.

	Arguments:
		client_action: the code of the action chosen by the user (is about to be requested from the server)
		server_socket: the socket through which the client talks with the server
	"""
	if client_action == str(1):
		chatClientSnd.create_account(VERSION, server_socket)
	elif client_action == str(2):
		chatClientSnd.log_in(VERSION, server_socket)
	elif client_action == str(3):
		chatClientSnd.send_message(VERSION, server_socket)
	elif client_action == str(4):
		chatClientSnd.check_message(VERSION, server_socket)
	elif client_action == str(5):
		chatClientSnd.delete_account(VERSION, server_socket)
	elif client_action == str(6):
		chatClientSnd.list_account(VERSION, server_socket)
	elif client_action == str(7):
		chatClientSnd.quit(VERSION, server_socket)
	else:
		print "Invalid operation. Try Again."
		logging.warning('client inputs an invalid operation. Asked to input again.')
		reattempt = client_input()
		interpret_input(reattempt, server_socket)

def get_response(server_socket):
	"""
	This function handles the response of the server to a client's request. If at any point connection is lost
	with the server then it prints an error message and terminates the program.
	
	Once the function receives a package it checks whether the server uses the same version with the client. If not it 
	prints an error message in the log file and terminates.
	
	Arguments:
		server_socket: the socket through which the client speaks with the server.
	"""
	while True:
		try:
			buf = server_socket.recv( 1024 )
		except:
			print 'Lost connection with the server.'
			logging.critical('lost connection with the server.')
			sys.exit()

		if len(buf) != 0:
			package = protocol_pb2.Server2Client()
			package.ParseFromString(buf)

			if package.version == VERSION:
				try:
					OPCODES[package.opcode](server_socket, package.msg)
					return
				except:
					logging.critical('unexpected fatal error occurred. Check client get_response.')
					sys.exit()
			else:
				logging.critical('server uses a different version.')
				sys.exit()
		else:
			logging.critical('connection to server lost at get_response')
			print "Server is down."
			sys.exit()

if __name__ == '__main__':
	"""
	This function starts a new client. It takes exactly 2 command line arguements that specify the location
	of the server the client will talk to. If wrong number of arguments is passed then it prints an error message 
	and terminates, otherwise it attempts to connect to the server. If server is unreachable then it prints an error
	message and terminates.
	
	If connection is established normally then communication can start. The user specifies an action, the respective
	function is called and the response of the server is handled.
	
	Arguments:
		argv[1]: <server_host address>  (usually localhost)
		argv[2]: <server_port>		(it should be 8080)
	"""
	client_init_time = strftime('%Y-%m-%d-%I:%M:%S-%p', gmtime())
	client_log_name = 'client-' + client_init_time + '.log'
	logging.basicConfig(filename=client_log_name, format='%(levelname)s: [%(asctime)s] %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %I:%M:%S %p')
	logging.debug('chat client logging initiated.')

	if(len(sys.argv) != 3):
		logging.critical('client program forced exit due to wrong number of arguments')
		print "FATAL: Usage 'python chatClient.py <hostname> <port>'"
		sys.exit()
		
	server_host = sys.argv[1]
	server_port = sys.argv[2]

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.connect((server_host, int(server_port)))
	except:
		logging.critical('client cannot connect to the server at %s:%s', server_host, server_port)
		print "FATAL: Connection to " + server_host + ":" + server_port + " failed."
		sys.exit()

	while True:
		try:
			print """
				Connected to the chat server. Please enter the index to execute a function:
				(1) Create an account
				(2) Log in
				(3) Send a message
				(4) Checked unread message
				(5) Delete an account
				(6) List accounts
				(7) Quit
				"""
			sys.stdout.write(">> ")
			sys.stdout.flush()

			listen_from = [server_socket, sys.stdin]
			reads, writes, err = select.select(listen_from, [], [])

			for src in reads:
				if src == server_socket:
					get_response(server_socket)
				else:
					client_action = sys.stdin.readline().strip("\n")
					# client_action = client_input()
					interpret_input(client_action, server_socket)
					get_response(server_socket)
					
		except:
			chatClientSnd.inform_dead(VERSION, server_socket)
			sys.exit()
