from PyQt5 import QtGui,QtWidgets,QtCore
from ..Chat.client import ChatClient
import sys,socket, threading


class ChatWidget(QtWidgets.QWidget):
	def __init__(self,name):
		super().__init__()
		self.name=name
		self.client=None
		self.initUI()

	def initUI(self):
		self.chatMessages=QtWidgets.QListWidget()
		self.inputBox=QtWidgets.QTextEdit()
		self.inputBox.installEventFilter(self)
		self.scrollBar=QtWidgets.QScrollBar()
		self.scrollBar.setStyleSheet('background : lightgrey;')
		self.chatMessages.setVerticalScrollBar(self.scrollBar)
		self.inputBox.setFixedHeight(
			int(
				self.inputBox.fontMetrics().lineSpacing()*3+self.inputBox.document().documentMargin()*2+self.inputBox.frameWidth()*2-1
			)
		)
		self.sendButton=QtWidgets.QPushButton('Send')
		self.sendButton.clicked.connect(self.onClickSend)
		grid=QtWidgets.QGridLayout()
		grid.setSpacing(3)
		grid.addWidget(self.chatMessages, 0, 0, 1, 3)
		grid.addWidget(self.inputBox, 1, 0, 1, 1)
		grid.addWidget(self.sendButton, 1, 2)
		grid.setRowStretch(0, 1)
		grid.setColumnStretch(0, 1)
		self.setLayout(grid)
		self.sendButton.setEnabled(False)
		self.inputBox.setEnabled(False)
	
	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.KeyPress and obj is self.inputBox:
			if event.key() == QtCore.Qt.Key_Return and self.inputBox.hasFocus():
				self.onClickSend()
				self.inputBox.setText('')
		return super().eventFilter(obj, event)

	def intializeClient(self, addr, port, userPassword, isHost):
		if self.client:
			self.client.quit()
		self.client = ChatClient(addr,port, isHost)
		#self.client.reciveMessage.connect(self.addMessage)
		self.client.receiveMessageTrigger.connect(self.addMessage)
		threading.Thread(target= self.client.listenForIncomingMessages, daemon= True).start()
		self.client.sendMessage(userPassword)
		self.client.sendMessage('1234joined: '+self.name)
		self.sendButton.setEnabled(True)
		self.inputBox.setEnabled(True)

	def onClickSend(self):
		msg = self.inputBox.toPlainText()
		if not msg:
			return
		self.addMessage(self.name+': '+msg)
		self.client.sendMessage(self.name+': '+msg)

	def addMessage(self,msg):
		self.chatMessages.addItem(QtWidgets.QListWidgetItem(msg))
		self.inputBox.setText('')

	def cleanUp(self):
		if self.client:
			self.client.quit()