# Wire Protocols
### Requirements
* We use Google's Protocol Buffers. Although you may not need to download the compiler, you should download the Protocol Buffers runtime (v3.5.1).
* We implemented and tested our code fully on Python 2.7. You should probably run it on that version as well. Otherwise, for example (if you run on Python 3.5/3.6), print statement probably will not work.
* Tested on Mac and Linux machines. Probably will not work on Windows.

### Assumptions

We made the assumptions that the account name and the message have a maximum length of 25 and 100 characters respectively.

### Semantics of Deleting an account

We decided to deliver all undelivered messages in the user before deleting its account, and subsequently proceed with the deletion. Hence, the user that asks for his/her account to be deleted sees all the messages that hadn't read yet and after that receives confirmation from the server that his/her account was successfully deleted (unless an error occurs).

### Instructions
Run the server on your console:
```
python chatServer.py
```
The server will print out its IP address for you.

Then run as many clients as you want. Make sure you run them on seperate console tabs:
```
python chatClient.py <server_host_address> 8080
```
(`<server_host_address>` can usually be `localhost`)

To quit a client, you can either use the Quit command from the Client's interface or you can force quit (Ctr+C). To quit the server you need to quit all the clients first 
and then use Ctr+C or kill the process through the following command:
```
kill -9 <server_process_id>
```
If you try to force quit (Ctr+C) the server while there are clients still running, the server will be running until all clients quit.

### Wire protocol

There are two forms of packages that are exchanged over the wire:
* packages from the client to the server. They contain the following:

```
message Client2Server {
        string version = 1;   // the version of the protocol
        int32 opcode = 2;     // the code of the operation requested
        string sender = 3;    // the account name of the client
        string receiver = 4;  // the account name of the recipient (when messaging another user)
        string msg = 5;       // the message (for example the message to be delivered to another recipient
                              // a pattern for listing only the accounts matching it)
}
```

* packages from the server to the client. They contain the following:

```
 message Server2Client {
        string version = 1;   // the version of the protocol
        int32 opcode = 2;     // the code of the operation requested
        string msg = 3;       // the message for the server indicating the success of failure
                              // of the request
}
```

As we mentioned before, in this assignment we used Google's Protocol Buffers. Hence, we put the description of these two packages in the file protocol.proto and subsequently we use the following command:

```
protoc -I=. --python_out=. protocol.proto
```

to generate Python code for our protocol.

### Design

We organised the client and the server into 3 separate files each: chatClient.py, chatClientRcv.py and chatClientSnd.py for the client and chatServer.py, chatServerRcv.py and chatServerSnd.py for the server.

* chatClient.py   : This file is responsible for starting a new client and sending requests of the user to the server.
* chatClientRcv.py: This file contains functions that just print the success/error messages returned from the server as a
                  result of the requests of the client.
* chatClientSnd.py: This file contains code that is responsible for generating the packages that are send to the server 
                  based on the requests of the user (see also the next section describing Client-Server Communication).

* chatServer.py   : This file is responsible for initializing the server thread.
* chatServerRcv.py: This file contains code that runs after a request from the client's side. Once an action is requested from
                  the client, a function from this file is called to satisfy the request.
* chatServerSnd.py: This file contains code that is responsible for generating packages containing confirmation or
                  error messages that are sent back to the client.

The server keeps a dictionary with the records for all the clients in the system. Each entry in the dictionary has a key, which is the name of an account, and a value, which is an object of the class Client (defined in the file chatServerRcv.py). This object contains the value of the socket through which the client speaks to the server or None if the user associated with this account is currently off-line, i.e. it does not speak with the server. Additionally it contains a queue of strings, which is the list of undelivered messages for this client, i.e. the messages that were sent to this client while he/she was off-line.

The dictionary is protected from simultaneous write requests through a lock that assures the consistency of the data. Whenever the server needs to recover the entry of a specific client locks the dictionary and upon modifying it (e.g. add a new message to the queue of undelivered messages) releases the lock so that the server can serve requests from other clients. The following requests from the client are supported:

* create_account: creates a new account by adding a new entry in the dictionary. If the name already exists then no account is created and an error message is returned.
* log_in: every time that a user requests to log in we check whether the user is already registered in the system and we set the value of the socket in the user's record to be the current socket. Hence, the server knows where to deliver messages with that recipient. If another user is logged in in that account he/she is forced to logout since their account is accessed from some other client. If the account name does not exist in the dictionary, then the log in fails and an error message is returned.
* send_message: a message is sent from one user to another. If the client is not logged in into an account then the request will fail and an error message will be returned. If the recipient does not exist in the dictionary (is not a valid account) then the request will fail and an error message will be returned. If the recipient is logged in then he/she will receive the message immediately, otherwise it will be stored in the queue of undelivered messages in the recipient's entry in the dictionary.
* check_message: if the client is logged in into an account then all the undelivered messaged in this account's entry in the dictionary are returned and message queue is flushed. Otherwise, the request fails and an error message is delivered.
* delete_account: if the client is logged in into an account then all the undelivered messaged in this account's entry in the dictionary are returned and subsequently the account is deleted by removing the dictionary entry associated with it.
* list_accounts: the user specifies some criteria (in the form of a regular expression) and the server returns all the account names matching these criteria.
* quit: the socket attribute in the dictionary entry of the account previously logged in is set to None, indicating that the user is off-line and cannot receive direct messages anymore, and subsequently the client program terminates. An exception appears in the server's console because we additionally kill the thread serving this client.
If no account was logged in from this client then an error message is returned mentioning that the user needs to login before logging out.
* Ctl+C: if the user is logged in into some account then the socket attribute in the dictionary entry of the account previously logged in is set to None, 
indicating that the user is off-line and cannot receive direct messages anymore, and subsequently the client program terminates. 
Otherwise, the client program terminates with no further action. In both cases an exception appears in the server's console because we additionally kill the thread serving this client.


### Client-Server Communication

At every step, the user specifies one of the following seven actions:
```
	(1) Create an account
	(2) Log in
	(3) Send a message
	(4) Check unread message
	(5) Delete an account
	(6) List accounts
	(7) Quit
```
Based on the request of the user, the client sends a package to the server with the appropriate operation code (and the rest of the important information, e.g. the name of the account to log-in for a log-in request). The server handles the request and sends back a package to the client to confirm that the request was handled successfully, or to provide an error message if the request could not be carried out. Hence, the client knows how to proceed based on the error that it received (e.g. invalid name for logging-in, try again).


### Failures

* Server: If the server fails, the clients detect the failure and terminate with an error.
* Client: If a client fails the server won't know immediately. There are two cases for which the failure will be detected:
	- the client reattempts to log in. In that case, the server will still have the client in the dictionary as active              since it won't have set the socket free. It will free it from the previous value of the socket and it will be                  assigned to the new value.
	- a message is delivered for that client. Then, since the server can see the client active (from the dictionary), it 
          will try to deliver the message immediately. If it doesn't receive a confirmation from the client then it assumes  
          that the client has failed, it sets its socket to None (client is off-line) and stores the message in the queue of
          undelivered messages for that client.
