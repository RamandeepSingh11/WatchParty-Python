import vlc,sys,platform,time
class Player:
	def __init__(self,args=[]):
		if sys.platform.startswith('linux'):
			args.append('--no-xlib')
		self.instance = vlc.Instance(args)
		self.instance.log_unset()
		self.player=self.instance.media_player_new()
		self.media=None

	def addOptions(self,args):
		if not self.media:
			return -1
		for arg in args:
			self.media.add_option(arg)
			
	def playPause(self):
		if self.player.is_playing():
			self.player.pause()
			return -1
		else:
			if self.player.play()==-1:
				return 0
			elif not self.player.is_playing():
				self.player.play()
			return 1

	def stop(self):
		self.player.stop()
		return 1

	def getPosition(self):
		return self.player.get_position()

	def getAbsolutePosition(self):
		return self.player.get_time()

	def setTime(self, time):
		return self.player.set_time(time)

	def isPlaying(self):
		return self.player.is_playing()

	def setWindowToPyQT(self,winfoId):
		if platform.system() == "Linux":
			self.player.set_xwindow(int(winfoId))
		elif platform.system() == "Windows":
			self.player.set_hwnd(int(winfoId))

	def openFileOrUrl(self,filePath=None):
		self.media=self.instance.media_new(filePath)
		self.player.set_media(self.media)
		self.media.parse()
		return self.media.get_meta(0)

	def getVolume(self):
		return self.player.audio_get_volume()

	def setVolume(self,volume):
		self.player.audio_set_volume(volume)

	def seek(self,position):
		self.player.set_position(position / 1000.0)

	def cleanup(self):
		self.player.stop()

	def __del__(self):
		self.cleanup()