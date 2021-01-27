#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
	
	def handle(self):
		self.data = self.request.recv(1024).strip()
		print ("Got a request of: %s\n" % self.data)
		response = HTTPResponse()
		response.getResponse(self.data)
		self.request.sendall(bytearray(response.body,'utf-8'))

class HTTPResponse():
	def __init__(self):
		self.method = ""
		self.URL = ""
		self.httpVersion = ""
		self.ContentType = ""
		self.code = ""
		self.Location = ""
		self.statusText = {"200": "OK", "301": "Moved Permanently",
							 "404": "Not Found", "405": "Method Not Allowed", 
							 "500": "Internal Server Error"}
		self.body = ""

	def header(self):
		h = self.httpVersion + " " + self.code + " " + self.statusText[self.code] + " \r\n" +\
				"Content-Type: " + self.ContentType + "\r\n"
		if len(self.Location) > 0:
			h += "Location: " + self.Location + "\r\n"
		h+= "\r\n"
		print("----- Header -----")
		print(h)
		return h

	def printInfo(self):
		print("Method:", self.method)
		print("URL:", self.URL)
		print("HTTP version:", self.httpVersion)

	def checkForSecure(self):
		if "../" in self.URL:
			raise FileNotFoundError()

	def get301(self, url):
		msg = """
		<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
		<TITLE>301 Moved Permanently</TITLE><link rel="stylesheet" type="text/css"></HEAD><BODY>
		<H1 class="err">301</H1>
		<H2 class="msg"> The document has moved
		<A HREF=""" + url + """>here</A>.</H2>
		</BODY></HTML>
		"""
		#print(msg)
		return msg

	def get404(self):
		msg = """
		<!DOCTYPE html>
		<html>
		<head>
			<title>404 Page</title>
		        <meta http-equiv="Content-Type"
		        content="text/html;charset=utf-8"/>
		        <!-- check conformance at http://validator.w3.org/check -->
		        <link rel="stylesheet" type="text/css">
		</head>

		<body>
			<div class="eg">
				<h1 class="err"> 404 </h1>
				<h2 class="msg"> Sorry this is not a valid page, please try again and stay safe...</h2>
			</div>
		</body>
		</html> 
		"""
		return msg

	def get405(self, method):
		msg = """
		<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
		<TITLE>405 Method Not Allowed</TITLE><link rel="stylesheet" type="text/css"></HEAD><BODY>
		<H1 class="err">405</H1>
		<H2 class="msg">""" + method + """ Method Not Allowed</H2>
		</BODY></HTML>
		"""
		#print(msg)
		return msg

	def getError(self):
		msg = """
		<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
		<TITLE>500 Internal Server Error</TITLE><link rel="stylesheet" type="text/css"></HEAD><BODY>
		<H1 class="err">Oh No, the server got some error!</H1>
		<H2 class="msg">it will probably work next time...</H2>
		</BODY></HTML>
		"""
		#print(msg)
		return msg

	def getFile(self, fileName):
		with open(fileName, 'r') as f:
			return f.read()

	def getFileType(self):
		fileType = self.URL.split('.')[-1]
		if fileType == "html":
			self.ContentType = "text/html"
		elif fileType == "css":
			self.ContentType = "text/css"
		# else:
		# 	self.body = self.header() + self.getFile("www/404.html")

	def getResponse(self, requestData):
		try:
			s = requestData.decode("utf-8") 

			self.code = "200"
			# get method
			s = s.split(' ', 1)
			self.method = s[0]
			# get URL
			s = s[1]
			s = s.split(' ', 1)
			self.URL = "www" + s[0]
			
			# get http version
			s = s[1]
			s = s.split('\r\n', 1)
			self.httpVersion = s[0]

			self.printInfo()
			self.checkForSecure()

			if self.method != "GET":
				self.code = "405"
				self.ContentType = "text/html"
				#print(self.ContentType)
				self.body = self.header() + self.get405(self.method)
				return

			if self.URL[-1] == '/':
				self.URL += "index.html"
				#self.ContentType = "text/html"
				#print(self.ContentType)
				
				#self.content = self.header() + self.get301("index.html")
				#return
			self.getFileType()
			#print(self.ContentType)
			if len(self.body) > 0:
				return
			fileContent = self.getFile(self.URL)
			self.body = self.header() + fileContent
			return
		except IsADirectoryError:
			self.code = "301"
			d = self.URL.split('/')[-1]
			print("directory: ", d)
			self.Location = d + "/index.html"
			self.body = self.header() + self.get301(d + "/index.html")
			return
		except FileNotFoundError:
			self.code = "404"
			self.ContentType = "text/html"
			#print(self.ContentType)
			self.body = self.header() + self.get404() # self.getFile("www/404.html")
			return
		except BaseException as e:
			print(str(e))
			self.code = "500"
			self.ContentType = "text/html"
			#print(self.ContentType)
			self.body = self.header() + self.getError()
			return

if __name__ == "__main__":
	HOST, PORT = "localhost", 8080

	socketserver.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = socketserver.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
