from PyQt5 import QtWidgets,QtGui,QtCore
from .PyQtFrames.chatWidget import ChatWidget
from .PyQtFrames.toolBarWidget import ToolBar
from .PyQtFrames.videoFrame import VideoFrame
from pyngrok import ngrok,conf
from .Video.player import Player
from .Chat.server import ChatServer
import sys, os, json, base64, threading, time, random, string, pyperclip, urllib

DEBUG = False

class MainClass(QtWidgets.QMainWindow):

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self,None)
		self.isPaused = True
		self.isHost = False
		self.name = None
		self.videoServer = None
		self.finalString = None
		self.chatTunnel = None
		self.chatServer = None
		self.videoTunnel = None
		self.player = Player()
		self.askForName()
		self.createUI()
		self.createRandomUserPassword()
		with open('config.json','r') as f:
			self.configuration=json.load(f)
	
	def createUI(self):
		self.mainWidget = QtWidgets.QWidget()
		self.setCentralWidget(self.mainWidget)
		#Menu
		self.menuBar = self.menuBar()
		menu = self.menuBar.addMenu('Options')
		#Host
		host = QtWidgets.QAction('Host a Video', self)
		host.triggered.connect(self.createHost)
		#Client
		client = QtWidgets.QAction('Connect to Host', self)
		client.triggered.connect(self.createClient)
		#Close
		close = QtWidgets.QAction('Close App', self)
		close.triggered.connect(sys.exit)

		menu.addAction(host)
		menu.addAction(client)
		menu.addAction(close)

		#Adding Differet Frames and Widgets
		self.videoFrame = VideoFrame()
		self.chatWidget = ChatWidget(self.name)
		self.toolBar = ToolBar(self.player,self)
		#FinalLayout
		self.vBoxLayout = QtWidgets.QVBoxLayout()
		self.upperBoxLayout = QtWidgets.QGridLayout()
		self.upperBoxLayout.setColumnStretch(0,2)
		self.upperBoxLayout.addWidget(self.videoFrame, 0, 0, 1, 1)
		self.upperBoxLayout.addWidget(self.chatWidget, 0, 1, 1, 6)
		self.vBoxLayout.addLayout(self.upperBoxLayout)
		self.vBoxLayout.addWidget(self.toolBar)
		self.setLayout(self.vBoxLayout)
		self.mainWidget.setLayout(self.vBoxLayout)

		#Creating a Timer to update GUI every 100ms
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.updateUI)

		#Creating a Timer which would send Data Packets every 1second to connected clients if the current Instance is host.
		self.videoSyncTimer = QtCore.QTimer(self)
		self.videoSyncTimer.setInterval(1000)
		self.videoSyncTimer.timeout.connect(self.sendTimeStamp)

	def updateUI(self):
		mediaPos = int(self.player.getPosition()*1000)
		self.toolBar.positionSlider.setValue(mediaPos)
		if not self.player.isPlaying():
			self.timer.stop()
			self.videoSyncTimer.stop()
			if not self.isPaused:
				self.toolBar.stop()

	def sendTimeStamp(self):
		mediaPos = int(self.player.getAbsolutePosition()/1000)
		finalString = f'2345TimeStamp:{not self.player.isPlaying()}:{mediaPos}'
		self.chatServer.broadCast(finalString, None)

	def receiveTimeStamp(self, msg):
		_, hostPaused, timeStamp = msg.split(':')
		timeStamp = int(timeStamp)
		hostPaused = hostPaused == 'True'
		if abs(self.player.getAbsolutePosition()/1000-timeStamp)>2:
			self.player.setTime(timeStamp*1000)
		if (not hostPaused and not self.player.isPlaying()) or (hostPaused and self.player.isPlaying()):
			self.player.playPause()
		
	def createRandomUserPassword(self):
		self._userName = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
		self._password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

	def _getConcatUserPassword(self):
		return f'{self._userName}:{self._password}'

	def askForName(self):
		name,okPressed=QtWidgets.QInputDialog.getText(None, "Enter your NickName", "Enter your NickName:",QtWidgets.QLineEdit.Normal,"")
		if not okPressed or not name:
			self.name='NoobMaster69'
		self.name=name
	
	def createNgrokTunnels(self,fileFolder):
		ngrok.set_auth_token(self.configuration['ngrokAuthKey'])
		conf.get_default().ngrok_path = self.configuration['ngrokPath']
		class b:
			def __init__(self,a):
				self.public_url=a
		if not DEBUG:
			self.videoTunnel = ngrok.connect(f'file:///{fileFolder}','http',auth=f'{self._getConcatUserPassword()}')
			self.chatTunnel = ngrok.connect(self.configuration['chatServerPort'],'tcp')
		else:
			fileName = [i for i in __import__('os').listdir(fileFolder) if i.endswith('.mp4')][0]
			self.videoTunnel = b(f"{fileFolder}/{fileName}")
			self.chatTunnel = b(f'tcp://0.0.0.0:{self.configuration["chatServerPort"]}')

	def createHost(self):
		self.cleanUp()
		fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose video file which you wanna stream.', os.path.expanduser('~'))
		if not fileName[0]:
			return
		filePath = fileName[0]
		fileFolder = '/'.join(filePath.split('/')[:-1])
		fileName = filePath.split('/')[-1]
		self.createNgrokTunnels(fileFolder)
		self.chatServer = ChatServer('0.0.0.0' ,self.configuration['chatServerPort'],self._getConcatUserPassword())
		threading.Thread(target=self.chatServer.listenForConnections,daemon=True).start()
		time.sleep(1)
		self.chatWidget.intializeClient('0.0.0.0', self.configuration['chatServerPort'], self._getConcatUserPassword(), True)
		self.toolBar.volumeSlider.setEnabled(True)
		self.toolBar.playButton.setEnabled(True)
		self.toolBar.stopButton.setEnabled(True)
		self.toolBar.positionSlider.setEnabled(True)
		self.isHost = True
		# self.chatWidget.client.timeStampTrigger.connect(self.receiveTimeStamp)
		windowName = self.player.openFileOrUrl(filePath)
		self.setWindowTitle(windowName)
		self.player.setWindowToPyQT(self.videoFrame.winId())
		self.finalString = ';;;'.join([self.chatTunnel.public_url, self.videoTunnel.public_url, urllib.parse.quote(fileName), self._getConcatUserPassword()])
		self.finalString = base64.b64encode(self.finalString.encode('ascii')).decode('ascii')
		msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information , 'Copy to ClipBoard', 'Click on Yes to copy the String to ClipBoard you can then send it to your friend to add them in your session.')
		msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		msgBox.buttonClicked.connect(self.copyToClipBoard)
		msgBox.exec_()
		self.videoSyncTimer.start()

	def createClient(self):
		self.cleanUp()
		b64string,okPressed = QtWidgets.QInputDialog.getText(None, "Enter the String given to you","Enter The String given to you by Others.", QtWidgets.QLineEdit.Normal,"")
		if not okPressed or not b64string:
			return 
		try:
			decodedStrings = base64.b64decode(b64string).decode('ascii').split(';;;')
			self.chatWidget.intializeClient(decodedStrings[0].split(':')[1][2:], int(decodedStrings[0].split(':')[2]), decodedStrings[3], False)
			if not DEBUG:
				videoUrl = decodedStrings[1].split('//')
				videoUrl = videoUrl[0] + '//' + decodedStrings[3] + '@' + videoUrl[1] + '/' + decodedStrings[2]
			else:
				videoUrl = decodedStrings[1]

		except (IndexError, base64.binascii.Error) as e:
			msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, 'Invalid String', 'The String Given is either invalid or malfunctioned.')
			msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
			msgBox.exec_()
			return
		
		self.chatWidget.client.timeStampTrigger.connect(self.receiveTimeStamp)
		windowName = self.player.openFileOrUrl(videoUrl)
		self.setWindowTitle(windowName)
		self.player.setWindowToPyQT(self.videoFrame.winId())
		self.toolBar.playButton.setEnabled(False)
		self.toolBar.stopButton.setEnabled(False)
		self.toolBar.positionSlider.setEnabled(False)
		self.toolBar.volumeSlider.setEnabled(True)
		self.isHost = False
		self.player.playPause()
		self.player.playPause()

	def copyToClipBoard(self,button):
		if button.text=='No':
			return
		pyperclip.copy(self.finalString)

	def cleanUp(self):
		if self.videoTunnel and self.chatTunnel:
			ngrok.disconnect(self.videoTunnel.public_url)
			ngrok.disconnect(self.chatTunnel.public_url)
		self.chatWidget.cleanUp()
		if self.chatServer:
			self.chatServer.cleanUp()
