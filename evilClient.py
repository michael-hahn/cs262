import sys
import socket
import logging
import chatClientSnd
import chatClientRcv
import select
from time import gmtime, strftime, sleep
from struct import unpack

VERSION = 1

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
			chatClientSnd.evil_msg(VERSION, server_socket)
			sleep(1)
		except:
			chatClientSnd.inform_dead(VERSION, server_socket)
			sys.exit()
