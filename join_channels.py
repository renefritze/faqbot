from ParseConfig import *
import string
from utilities import *
class Main:
	joined_channels = 0
	admins = []
	channels = []

	def onloggedin(self,socket):
		for chan in self.channels :
			socket.send("JOIN %s\n" % (chan))
		self.joined_channels = 1

	def oncommandfromserver(self,command,args,socket):
	    if command == "SAID" and len(args) > 3 and args[1] in self.admins:
		for chan in args[3:]:
			if args[2] == "!faqchan":
				socket.send("JOIN %s\n" % (chan))
				if not chan in self.channels:
					self.channels.append(chan)
					self.saveChannels()
			if args[2] == "!faq!chan":
				socket.send("LEAVE %s\n" % (chan))
				if chan in self.channels:
					self.channels.remove(chan)
					self.saveChannels()

	def saveChannels(self):
		savestring = ""
		for channel in self.channels:
			savestring += channel + ","
		self.app.config["channels"] = savestring

	def onload(self,tasc):
	    self.app = tasc.main
	    self.admins = parselist(self.app.config["admins"],',')
	    self.channels = parselist(self.app.config["channels"],',')
