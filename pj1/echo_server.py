import sys
import socket

def listen(port):
	serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind((socket.gethostname(),port))
	serversocket.listen(5)

	print("Wait for a connection.\n")

	while True:
		#have a connection
		clientsocket, address=serversocket.accept()
		print('Initialize a new connection from %s\n'%str(address))
		msg=0
		while True:
			msg=clientsocket.recv(1024)
			if not msg or msg=="":
				continue
			else:
				break
		print("client sends to server %s: %s\n"%(str(address),str(msg.decode('utf8'))))
		clientsocket.send(msg)
		clientsocket.close()

if __name__ == "__main__":
	#invalid input
	if len(sys.argv)!=2:
		print("Wrong arguments! Please use 'python3 echo_server.py <port>'\n")
	else:
		port=int(sys.argv[1])
		listen(port)