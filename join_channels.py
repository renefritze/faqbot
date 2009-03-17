from ParseConfig import *
import string
from utilities import *
class Main:
	joined_channels = 0
	def getFAQ(self,key,socket):
	    socket.send("SAYPRIVATE _koshi_007 %s\n" % (key))

	def oncommandfromserver(self,command,args,socket):
	    if self.joined_channels != 1:
		cmns = parselist(self.app.config["channels"],',')
		socket.send("JOIN %s\n" % (cmns[0]))
		self.joined_channels = 1
	def onload(self,tasc):
	  self.app = tasc.main