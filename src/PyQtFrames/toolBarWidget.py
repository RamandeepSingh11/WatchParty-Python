from PyQt5 import QtGui,QtWidgets,QtCore

class ToolBar(QtWidgets.QWidget):

	def __init__(self, player, parentClass):
		super().__init__()
		self.createUI()
		self.player = player
		self.parentClass = parentClass
	
	def createUI(self):
		#Main Layout
		self.mainLayout = QtWidgets.QVBoxLayout()

		#Position Slider
		self.positionSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
		self.positionSlider.setToolTip('Position')
		self.positionSlider.setMaximum(1000)
		self.positionSlider.sliderMoved.connect(self.setPosition)
		self.positionSlider.sliderPressed.connect(self.setPosition)
		self.positionSlider.setEnabled(False)

		#Button Layout
		self.hButtonBox = QtWidgets.QHBoxLayout()

		#Play Button
		self.playButton = QtWidgets.QPushButton('Play')
		self.hButtonBox.addWidget(self.playButton)
		self.playButton.clicked.connect(self.playPause)
		self.playButton.setEnabled(False)

		#Stop Button
		self.stopButton = QtWidgets.QPushButton('Stop')
		self.hButtonBox.addWidget(self.stopButton)
		self.stopButton.clicked.connect(self.stop)
		self.stopButton.setEnabled(False)

		#Volume Button
		self.hButtonBox.addStretch(1)
		self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
		self.volumeSlider.setMaximum(100)
		self.volumeSlider.setValue(20)
		self.volumeSlider.setToolTip('Volume')
		self.hButtonBox.addWidget(self.volumeSlider)
		self.volumeSlider.valueChanged.connect(self.setVolume)
		self.volumeSlider.setEnabled(False)

		#Formatting
		self.mainLayout.addWidget(self.positionSlider)
		self.mainLayout.addLayout(self.hButtonBox)
		self.setLayout(self.mainLayout)

	def setVolume(self, volume):
		self.player.setVolume(volume)

	def playPause(self):
		res = self.player.playPause()
		if res == -1:
			self.playButton.setText('Play')
			self.parentClass.isPaused = True
			self.parentClass.timer.stop()
		elif res ==  0:
			return
		else:
			self.playButton.setText('Pause')
			self.parentClass.timer.start()
			self.isPaused = False

	def setPosition(self):
		self.parentClass.timer.stop()
		position = self.positionSlider.value()
		self.player.seek(position)
		self.parentClass.timer.start()

	def stop(self):
		self.player.stop()
		self.playButton.setText('Play')
		self.playButton.setEnabled(False)
		self.stopButton.setEnabled(False)
		self.positionSlider.setEnabled(False)
		self.volumeSlider.setEnabled(False)
		self.parentClass.cleanUp()