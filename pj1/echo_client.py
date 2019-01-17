import sys
import socket

def connect(host,port):
	while True:
		msg=input("Please input: ")
		if msg=="":
			print("Please input something.\n")
			continue
		#connect to server
		clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.connect((host,port))
		clientsocket.send(msg.encode('utf8'))
		res=clientsocket.recv(1024)
		print(str(res.decode('utf8'))+"\n")
		clientsocket.close()

if __name__=="__main__":
	#invalid input
	if len(sys.argv)!=3:
		print ("Wrong arguments! Please use 'python3 echo_client.py <host> <port>'.\n")
	else:
		host=sys.argv[1]
		port=int(sys.argv[2])
		connect(host,port)


