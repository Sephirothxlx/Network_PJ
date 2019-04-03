import socket
import sys
import threading
import os

class myThread(threading.Thread):
	def __init__(self, clientsocket):
		threading.Thread.__init__(self)
		self.clientsocket = clientsocket
		# you can set the file directory path here
		self.prefixpath = "www"

	# extract useful information from request
	# return a dict
	def extractRequest(self,datagram):
		method=""
		url=""
		version=""
		s=""
		tag=1
		for c in datagram:
			if c!=' ' and tag==1:
				s+=c
			elif c==' ' and tag==1:
				tag=2
				method=s
				s=""
			elif c!=' ' and tag==2:
				s+=c
			elif c==' ' and tag==2:
				url=s
				tag=3
				s=""
			elif c!=' ' and c!='\r' and c!='\n' and tag==3:
				s+=c
			elif c=='\n' or c=='\r' and tag==3:
				version=s
				break
		if method=="" or url=="" or version=="":
			return {}
		return {'method':method,'url':url,'version':version}

	# handle redirect case
	def handleRedirect(self,version,newurl):
		return {'statuscode':'301','discription':'Moved Permanently','version':version,'location':newurl}

	# handle malformed case
	def handleMalformed(self):
		return {'statuscode':'400','discription':'Bad Request'}

	# handle Get and Head request
	# there may be 404 case
	def handleGetAndHead(self,url,version,tag):
		response={'version':version}
		if url!="":
			filename=url[1:]
		else:
			filename=""
		filepath=self.prefixpath+url
		if filename=="" or not os.path.exists(filepath):
			response['statuscode']='404'
			response['discription']='Not Found'
			return response
		else:
			response['statuscode']='200'
			response['discription']='OK'
			i=filename.rfind('.')
			extension=filename[i+1:]
			if extension=="":
				response['contenttype']='text/plain'
			else:
				if extension=="html":
					response['contenttype']='text/html'
				elif extension=="pdf":
					response['contenttype']='application/pdf'
				elif extension=="png":
					response['contenttype']='image/png'
				elif extension=="jpeg":
					response['contenttype']='image/jpeg'
				else:
					response['contenttype']='text/plain'
			if tag==1:
				f=open(filepath,'rb')
				response['content']=f.read()
		return response

	# handle 405 case
	def handleOther(self,version):
		return {'statuscode':'405','discription':'Method Not Allowed','version':version}

	# make a HTTP response
	# return header and data content
	def makeResponse(self,response):
		res=""
		if 'version' in response and response['version']!="":
			res+=response['version']
			res+=" "

		if 'statuscode' not in response or response['statuscode']=="":
			return [""]
		else:
			res+=response['statuscode']
			res+=" "

		if 'discription' not in response or response['discription']=="":
			return [""]
		else:
			res+=response['discription']
			res+="\r\n"

		if 'location' in response and response['location']!="":
			res+="Location: "
			res+=response['location']
			res+="\r\n"

		if 'contenttype' in response and response['contenttype']!="":
			res+="Content-Type: "
			res+=response['contenttype']
			res+="\r\n"

		if 'content' not in response or response['content']=="":
			res+="Content-Length: 0\r\n"
			res+="\r\n"
			return [res]
		else:
			res+="Content-Length: "
			res+=str(len(response['content']))
			res+="\r\n"

		res+="\r\n"
		data=response['content']
		return [res,data]

	def run(self):
		msg=0
		while True:
			msg=self.clientsocket.recv(1024)
			if not msg or msg=="":
				continue
			else:
				break
		datagram=str(msg.decode('utf8'))

		request=self.extractRequest(datagram)
		print("HTTP request information is: ")
		print(request)
		response={}

		# get the redirect file
		# store the content into a dict
		f=open('www/redirect.defs','r',encoding='utf-8')
		redirect = f.readlines()
		redirect_pair={}
		for x in redirect:
			temp=x.split(' ')
			redirect_pair[temp[0]]=temp[1][:-1]

		# deal with different cases
		if not request:
			response=self.handleMalformed()
		elif request['method']!="GET" and request['method']!="HEAD":
			response=self.handleOther(request['version'])
		elif request['url'] in redirect_pair:
			response=self.handleRedirect(request['version'],redirect_pair[request['url']])
		elif request['method']=="GET":
			response=self.handleGetAndHead(request['url'],request['version'],1)
		elif request['method']=="HEAD":
			response=self.handleGetAndHead(request['url'],request['version'],2)

		returnmsg=self.makeResponse(response)

		#send the HTTP response
		self.clientsocket.send(returnmsg[0].encode('utf8'))
		if len(returnmsg)==2:
			self.clientsocket.send(returnmsg[1])


if __name__ == "__main__":
	#invalid input
	if len(sys.argv)!=2:
		print("Wrong arguments! Please use 'python3 web_server.py <port>'")
	else:
		port=int(sys.argv[1])
		serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind(('127.0.0.1',port))
		serversocket.listen(8)

		print("Wait for a connection.")

		#multi-threads
		while True:
			#have a connection
			clientsocket, address=serversocket.accept()
			print('Initialize a new connection from %s'%str(address))
			thread = myThread(clientsocket)
			thread.start()