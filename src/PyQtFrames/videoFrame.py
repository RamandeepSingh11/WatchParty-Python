from PyQt5 import QtGui,QtWidgets

class VideoFrame(QtWidgets.QFrame):

	def __init__(self):
		super().__init__()
		self.createUI()

	def createUI(self):
		self.palette = self.palette()
		self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0 ,0 ,0))
		self.setPalette(self.palette)
		self.setAutoFillBackground(True)