from src.mainWindow import MainClass
from PyQt5 import QtWidgets
import sys

def main():
	try:
		app=QtWidgets.QApplication(sys.argv)
		mainWindow=MainClass()
		mainWindow.show()
		mainWindow.resize(1280, 720)
		sys.exit(app.exec_())
	except KeyboardInterrupt:
		mainWindow.cleanUp()
		sys.exit(0)

if __name__ == '__main__':
	main()