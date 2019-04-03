import socket
import sys
import time
import threading
import re

class PingClient(object):
	def __init__(self):
		self.ip=""
		self.port=0
		self.period=0
		self.timeout=0
		self.totaln=0
		self.transmittedn=0
		self.receiven=0
		self.lossn=0
		self.lossrate=0
		self.minrtt=0
		self.avgrtt=0
		self.maxrtt=0
		self.totaltime=0
		self.timeresult=[]

	# send ping msg and record data
	def send(self,clientsocket,serveraddr,timeout,i):
		msg="PING "+str(i)+" "+str(time.time())+"\r\n"
		stime=time.time()
		clientsocket.sendto(msg.encode('utf8'),serveraddr)
		self.transmittedn=self.transmittedn+1
		clientsocket.settimeout(timeout)
		try:
			receive=clientsocket.recvfrom(1024)
			etime=time.time()
			replyseq=receive[0].decode('utf8').split(' ')[1]
			replyip=receive[1][0]
			self.receiven=self.receiven+1
			elapsedtime=int((etime-stime)*1000)
			print("PONG "+replyip+": seq="+replyseq+" time="+str(elapsedtime)+" ms")
		except socket.timeout:
			self.lossn=self.lossn+1
		else:
			if self.minrtt==0:
				self.minrtt=elapsedtime
			else:
				self.minrtt=min(self.minrtt,elapsedtime)
			if self.maxrtt==0:
				self.maxrtt=elapsedtime
			else:
				self.maxrtt=max(self.maxrtt,elapsedtime)
			self.timeresult.append(elapsedtime)

	def execute(self,ip,port,count,period,timeout):
    	# output
		print("PING "+ip)
		self.ip=ip
		self.port=port
		self.totaln=count
		self.period=period
		self.timeout=timeout
		clientsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		serveraddr=(ip,port)

		starttime=time.time()
		threadset=[]
		# create timers
		for i in range(1,self.totaln+1):
			t=threading.Timer(period/1000*i,self.send,[clientsocket,serveraddr,timeout/1000,i])
			threadset.append(t)
			t.start()

		#wait for all the threads stopping
		for x in threadset:
			x.join()
		endtime=time.time()
		self.totaltime=int((endtime-starttime)*1000)
		clientsocket.close()

	# print result
	def printresult(self):
		self.lossrate=self.lossn/self.totaln*100
		print("--- "+self.ip+" ping statistics ---")
		print(str(self.totaln)+" transmitted, "+str(self.receiven)+" received, "+str(self.lossrate)+"%"+" loss, time "+str(self.totaltime)+" ms")
		# get the avg RTT
		if self.receiven!=0:
			total=0
			for x in self.timeresult:
				total=total+x
			self.avgrtt=int(total/self.receiven)
		print("rtt min/avg/max = "+str(self.minrtt)+"/"+str(self.avgrtt)+"/"+str(self.maxrtt)+" ms")

    # do it after a client is finished
	def clear(self):
		self.ip=""
		self.port=0
		self.period=0
		self.timeout=0
		self.totaln=0
		self.transmittedn=0
		self.receiven=0
		self.lossn=0
		self.lossrate=0
		self.minrtt=0
		self.avgrtt=0
		self.maxrtt=0
		self.totaltime=0
		self.timeresult=[]

if __name__ == "__main__":
	#invalid input
	if len(sys.argv)!=6:
		print("Wrong arguments! Please add all the 6 arguments correctly.")
	else:
		ip=""
		port=""
		count=""
		period=""
		timeout=""
		for i in range(1,6):
			if re.match("--server_ip=",sys.argv[i])!=None:
				ip=sys.argv[i][12:]
			elif re.match("--server_port=",sys.argv[i])!=None:
				try:
					port=int(sys.argv[i][14:])
				except Exception:
					print("Wrong arguments! Please add all the 6 arguments.")
					sys.exit()
			elif re.match("--count=",sys.argv[i])!=None:
				try:
					count=int(sys.argv[i][8:])
				except Exception:
					print("Wrong arguments! Please add all the 6 arguments.")
					sys.exit()
			elif re.match("--period=",sys.argv[i])!=None:
				try:
					period=int(sys.argv[i][9:])
				except Exception:
					print("Wrong arguments! Please add all the 6 arguments.")
					sys.exit()
			elif re.match("--timeout=",sys.argv[i])!=None:
				try:
					timeout=int(sys.argv[i][10:])
				except Exception:
					print("Wrong arguments! Please add all the 6 arguments.")
					sys.exit()
			else:
				print("Wrong arguments! Please add all the 6 arguments.")
				sys.exit()
		if ip=="" or port=="" or count=="" or period=="" or timeout=="":
			print("Wrong arguments! Please add all the 6 arguments correctly.")
			sys.exit()
		pc=PingClient()
		print()
		pc.execute(ip,port,count,period,timeout)
		print()
		pc.printresult()
		pc.clear()