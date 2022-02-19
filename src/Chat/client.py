import socket, struct
from PyQt5 import QtCore


class ChatClient(QtCore.QObject):

	receiveMessageTrigger = QtCore.pyqtSignal(str)
	timeStampTrigger = QtCore.pyqtSignal(str)

	def __init__(self, addr, port, isHost):
		QtCore.QThread.__init__(self)
		self.clientSocket = None
		self.addr = addr
		self.port = port
		self.isHost = isHost
		self.intializeSocket()

	def intializeSocket(self):
		try:
			self.clientSocket = socket.socket()
			self.clientSocket.connect((self.addr, self.port))
			return True
		except:
			return None
	
	def receiveMessage(self):
		try:
			binMessageSize = self.clientSocket.recv(2)
			if not binMessageSize:
				return None
			messageSize = struct.unpack('h', binMessageSize)[0]
			message = self.clientSocket.recv(messageSize)
			if not message:
				return None
			return message.decode('utf-8')
		except struct.error:
			return None

	def listenForIncomingMessages(self):
		while True:
			message = self.receiveMessage()
			if not message:
				return None
			if message.startswith('1234joined'):
				user = message.split(':')[1]
				message = user + " has joined the chat."
			if message.startswith('2345TimeStamp'):
				if not self.isHost:
					self.timeStampTrigger.emit(message)
				continue
			self.receiveMessageTrigger.emit(message)

	def sendMessage(self, message):
		messageSize = struct.pack('h', len(message))
		if not self.clientSocket.send(messageSize) or not self.clientSocket.send(message.encode('utf-8')):
			return None
		return True

	def __del__(self):
		self.clientSocket.close()