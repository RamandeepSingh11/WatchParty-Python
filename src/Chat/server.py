import socket, threading, os, select, struct

class ChatServer:
	
	def __init__(self, ip, port, auth, maxNumOfConnections=5):
		self.clientLists = set()
		self.serverSocket = None
		self.auth = auth
		self.authTimeout = 5
		self.ip, self.port = ip, port
		self.maxNumOfConnections = maxNumOfConnections
		self.createListeningServer()
	
	def createListeningServer(self):
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSocket.bind((self.ip, self.port))
		self.serverSocket.listen(self.maxNumOfConnections)
	
	def listenForConnections(self):
		while True:
			conn, (ip, port) = self.serverSocket.accept()
			messageSize = self.receiveMessageWithTimeout(conn, 2)
			if messageSize is None:
				conn.close()
				continue
			try:
				messageSize = struct.unpack('h', messageSize)[0]
			except struct.error:
				conn.close()
				continue
			message = self.receiveMessageWithTimeout(conn, messageSize)
			if not message or message.decode('utf-8') != self.auth:
				conn.close()
				continue
			self.clientLists.add(conn)
			threading.Thread(target = self.receiveForever, args = (conn,), daemon=True).start()
	
	def receiveMessageWithTimeout(self, conn, sizeOfMessage):
		receiveMessage, dummy1, dummy2 = select.select([conn], [], [], self.authTimeout)
		if not receiveMessage:
			return None
		return receiveMessage[0].recvfrom(sizeOfMessage)[0]

	def receiveMessage(self, conn):
		try:
			binMessageSize = conn.recv(2)
			if not binMessageSize:
				return None
			messageSize = struct.unpack('h', binMessageSize)[0]
			message = conn.recv(messageSize)
			if not message:
				return None
			return message.decode('utf-8')
		except (struct.error, ConnectionResetError):
			return None
	
	def receiveForever(self, conn):
		while True:
			message = self.receiveMessage(conn)
			if not message:
				conn.close()
				self.clientLists.remove(conn)
				return
			self.broadCast(message, conn)
		conn.close()

	def broadCast(self, message, senderSocket):
		toBeDeleted = []
		for client in self.clientLists:
			conn = client
			if conn is senderSocket:
				continue
			if not self.sendMessage(message, conn):
				toBeDeleted.append(client)
		
		for client in toBeDeleted:
			self.clientLists.remove(client)

	def sendMessage(self, message, conn):
		messageSize = struct.pack('h', len(message))
		try:
			if not conn.send(messageSize) or not conn.send(message.encode('utf-8')):
				return None
			return True
		except OSError:
			return None
	
	def cleanUp(self):
		for client in self.clientLists:
			client.close()
		self.serverSocket.shutdown(socket.SHUT_RDWR)
		self.serverSocket.close()