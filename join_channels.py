from ParseConfig import *
import string
from utilities import *
class Main:
	joined_channels = 0
	admins = []
	
	def oncommandfromserver(self,command,args,socket):
	    if self.joined_channels != 1:
		cmns = parselist(self.app.config["channels"],',')
		socket.send("JOIN %s\n" % (cmns[0]))
		self.joined_channels = 1
	    #if command == "SAID" and len(args) > 2 and args[2] == !channel
	def onload(self,tasc):
	    self.app = tasc.main
	    self.admins = parselist(self.app.config["admins"],',')