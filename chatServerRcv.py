import sys
import threading
import logging
import chatServerSnd
import fnmatch
from struct import unpack

class Client:
	"""
	Server uses this class to record information for each client that has an account.
	
	We save the socket through which we talk to the client. If the client logs out or we detect that it failed
	then we use the reset_socket function to make its socket None. If it logs in again then we update the socket from
	None to the real value using the function set_socket.
	
	Attributes:
		socket: an integer denoting the socket through which we talk to the client or None if the client is not
			online or we detected that it failed.
		msg: a queue of messages (strings) that were received for the client while it was off-line or had failed.
	"""
	def __init__(self):
		"""Initializes an entry about a new client. Socket is set to None and no messages are to be delivered."""
		self.socket = None
		self.msg = []

	def set_socket(self, socket):
		"""Changes the value of the socket from None, once the client connencts."""
		self.socket = socket
		logging.debug('socket set.')

	def reset_socket(self):
		"""Sets the value of the socket to None whenever the client logs out or we detect that it failed."""
		self.socket = None
		logging.debug('socket reset.')

	def add_msg(self, msg):
		"""Adds a new message to the queue of undelivered messages for the client."""
		self.msg.append(msg)
		logging.debug('message added.')

	def display_all_msg(self):
		"""Deliver all undelivered messages to the client whenever it is requested or before deleting its account.""" 
		msg = ''
		for i in self.msg:
			msg = msg + i
		return msg

	def reset_msg_queue(self):
		"""Clear the message queue."""
		self.msg = []

	def get_socket(self):
		"""Return the socket assigned to the client."""
		return self.socket

def create_account(message, client_socket, data, lock, version):
	""" 
	Handles a message from a client to create a new account.

	If the account name already exists in the dictionary keeping the user records it returns an error,
	otherwise it creates a new account entry in the dictionary with the name requested as a key and 
	a new instance of Client as a value.

	Args:
		message: the encoded message (package) received from the client
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	
	"""
	account_name_len = unpack('!I', message[8:12])[0]
	account_name = message[12:12+account_name_len].decode('utf-8')

	lock.acquire()

	try:
		if account_name not in data:
			client_entry = Client()
			data[account_name] = client_entry
			chatServerSnd.create_account_success(client_socket, account_name, version)
			logging.info('server successfully created account.')
		else:
			chatServerSnd.create_account_failure(client_socket, account_name, version)
			logging.info('server cannot create a new account because it exists.')
	except:
		logging.warning('exception occurred when server runs create_account.')
		chatServerSnd.create_account_failure(client_socket, account_name, version)
	finally:
		lock.release()
		logging.info('server performed create_account.')

def log_in(message, client_socket, data, lock, version):
	"""
	Handles a message from a client to log in into an account.

	If the account name does not exist in the dictionary keeping the user records or the user of the account
	is already logged in it returns an error. Otherwise it updates the entry corresponding to that account 
	with the socket through which the client is connected. In that way the server can talk to the client.
	
	Args:
		message: the encoded message (package) received from the client
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	# account_name = package.msg    # the msg in the package contains the name of the account to log in
	account_name_len = unpack('!I', message[8:12])[0]
	account_name = message[12:12+account_name_len].decode('utf-8')

	lock.acquire()

	error = False

	try:
		if account_name in data:
			for acc in data:
				client_entry = data[acc]
				if client_socket == client_entry.get_socket():
					if acc == account_name:
						chatServerSnd.log_in_already(client_socket, account_name, version)
						logging.info('account has logged in already.')
						error = True
						break
					else:
						client_entry = data[acc]
						client_entry.reset_socket()

						new_client = data[account_name]
						new_client.set_socket(client_socket)
						chatServerSnd.log_in_other(client_socket, acc, version)
						logging.info('%s has logged in here. Forced logged out', acc)
						error = True
						break
			if not error:
				client_entry = data[account_name]
				client_entry.set_socket(client_socket)
				chatServerSnd.log_in_success(client_socket, account_name, version)
				logging.info('account is successfully logged in.')
		else:
			chatServerSnd.log_in_failure(client_socket, account_name, version)
			logging.info('the account cannot be logged in as it does not exist. Create an account first.')
			
	except:
		logging.warning('exception occurred when server runs log_in.')
		chatServerSnd.log_in_failure(client_socket, account_name, version)
	finally:
		lock.release()
		logging.info('server performed log_in.')

def send_message(message, client_socket, data, lock, version):
	"""
	Sends a message from one client to another client, specified in the package.

	If the receiver does not exist in the dictionary keeping the user records it returns an error. If the socket of the
	receiver is set to None (the receiver is off-line) we add the message in the queue of unread messages in the
	record of the receiver. If the socket of the receiver is not None then the receiver is either online or it 
	failed but we have not detected the failure yet. We try to deliver the message instantly. If we get a response from
	the receiver that the message was delivered then no further action is taken. If we do not hear back however, we
	consider the receiver to have failed, we reset its socket to None and add the message in the queue of unread messages
	in the record of the receiver.
		
	Args:
		message: the encoded message (package) received from the client (contains the protocol 
			 version and the account name of the receiver and the message to be sent)
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	# receiver = package.receiver	   # the receiver in the package contains the recipient of the message
	receiver_len = unpack('!I', message[8:12])[0]
	receiver = message[12:12+receiver_len].decode('utf-8')
	msg_len = unpack('!I', message[12+receiver_len:16+receiver_len])[0]
	msg = message[16+receiver_len:16+receiver_len+msg_len].decode('utf-8')
	
	lock.acquire()

	error = True

	try:
		if receiver not in data:
			chatServerSnd.send_message_failure_receiver(client_socket, receiver, version)
			logging.info('server cannot send the message to a non-existent user.')
		else:
			for acc in data:
				client_entry = data[acc]
				if client_entry.get_socket() == client_socket:
					sender = acc
					receiver_entry = data[receiver]
					new_message = sender + ":" + msg + "\n"

					receiver_socket = receiver_entry.get_socket()
					if not (receiver_socket is None):
						success = chatServerSnd.direct_send(receiver_socket, new_message, version)
					else:
						receiver_entry.add_msg(new_message)
						success = True
					if not success:
						receiver_entry.add_msg(new_message)
						receiver_entry.reset_socket()

					chatServerSnd.send_message_success(client_socket, receiver, version)
					logging.info('server successfully sent the message to %s.', receiver)
					error = False
			if error:
				chatServerSnd.send_message_failure_sender(client_socket, receiver, version)
				logging.info('sender is not a registered user on the server.')
	except:
		logging.warning('exception occurred when server runs send_message.')
		chatServerSnd.send_message_failure_receiver(client_socket, receiver, version)
	finally:
		lock.release()
		logging.info('server performed send_message.')

def check_message(package, client_socket, data, lock, version):
	"""
	Delivers all undelivered messages to a user.
	
	The server picks all the undelivered messages from the dictionary record for that client and sends them
	to it. Subsequently, it flushes the queue since there are no unread messages for that client.
	
	If the user is not logged in to an account then no messages are delivered and a failure message
	is printed in the log.
		
	Args:
		package: not useful in this function
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	error = True

	lock.acquire()

	try:
		for acc in data:
			client_entry = data[acc]
			if client_entry.get_socket() == client_socket:
				sender = acc
				message = client_entry.display_all_msg()
				client_entry.reset_msg_queue()
			
				chatServerSnd.check_message_success(client_socket, message, version)
				logging.info('server sent all unread messages to %s.', sender)
				error = False
		if error:
			sender = 'Unknown'
			chatServerSnd.check_message_failure(client_socket, sender, version)
			logging.info('sender is not logged in on the server to check message.')
	except:
		logging.warning('exception occurred when server runs check_message.')
		chatServerSnd.check_message_failure(client_socket, sender, version)
	finally:
		lock.release()
		logging.info('server performed check_message.')

def delete_account(package, client_socket, data, lock, version):
	"""
	Deletes the account of the user that is logged in.
	
	All the unread messages for the account to be deleted are sent to the client and subsequently the
	record in the dictionary regarding the account to be deleted is removed.
	
	If the client is not logged in to an account then no account is deleted and a 
	failure message is printed in the log.
		
	Args:
		package: not useful in this function
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	error = True

	lock.acquire()

	try:
		for acc in data:
			client_entry = data[acc]
			if client_entry.get_socket() == client_socket:
				sender = acc
				message = "The account " + sender + " is permanently deleted. You have the following unread messages:\n"
				message = message + client_entry.display_all_msg()
				del data[sender]
			
				chatServerSnd.delete_account_success(client_socket, message, version)
				logging.info('server successfully deleted the account %s.', sender)
				error = False
				break
		if error:
			sender = 'Unknown'
			chatServerSnd.delete_account_failure(client_socket, sender, version)
			logging.info('%s account to delete. Need to log in first.', sender)
	except:
		logging.warning('exception occurred when server runs delete_account.')
		chatServerSnd.delete_account_failure(client_socket, sender, version)
	finally:
		lock.release()
		logging.info('server performed delete_account.')

def list_account(message, client_socket, data, lock, version):
	"""
	List the names of all accounts that match the regular expression specified from the client,
	or the names of all accounts if none is given.
	
	Args:
		message: the encoded message (package) received from the client (contains a regular expression to be matched)
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	# criteria = package.msg    # user provides the matching criteria
	criteria_len = unpack('!I', message[8:12])[0]
	criteria = message[12:12+criteria_len].decode('utf-8')
	results = ""

	lock.acquire()

	try:
		for account_name in data:
			replaced_criteria = criteria.replace("_", "?")
			if fnmatch.fnmatch(account_name, replaced_criteria):
				results = results + account_name + '\n'
		chatServerSnd.list_account_success(client_socket, results, version)
		logging.info('server listed account that matched.')
	except:
		logging.warning('exception occurred when server runs list_account.')
		chatServerSnd.list_account_failure(client_socket, results, version)
	finally:
		lock.release()
		logging.info('server performed list_account.')

def quit(package, client_socket, data, lock, version):
	"""
	Allows a user to logout. Once a logout request is received we set the socket of the user to None,
	indicating that it is not active anymore hence it cannot receive direct messages. All messages for that
	user will be queued until it logs back in the system.
	
	If this function is called by a client that has not logged in then no socket is set to None and an
	error message is printed in the log.

	Args:
		package: not useful in this function
		client_socket: the socket through which the client connects
		data: the dictionary data structure that keeps the records for all clients in the system
		lock: a lock to the dictionary keeping the client records to make sure that the data remains consistent
			even if many clients are accessing it simultaneously
		version: the version of the protocol
	
	Returns:
		Nothing
	"""
	error = True

	lock.acquire()

	try:
		for acc in data:
			client_entry = data[acc]
			if client_entry.get_socket() == client_socket:
				sender = acc
				client_entry.reset_socket()
				chatServerSnd.quit_success(client_socket, sender, version)
				logging.info('server received quit signal from the client: %s.', sender)
				error = False
		if error:
			sender = 'Unknown'
			chatServerSnd.quit_failure(client_socket, sender, version)
			logging.info('unknown account to quit.')
	except:
		logging.warning('exception occurred when server runs quit.')
		chatServerSnd.quit_failure(client_socket, sender, version)
	finally:
		lock.release()
		logging.info('server performed quit.')







	
