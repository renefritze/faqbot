# -*- coding: utf-8 -*-
import string
from time import *
from jinja2 import Environment, FileSystemLoader

from tasbot.utilities import createFileIfMissing
from tasbot.config import Config
from tasbot.plugin import IPlugin, Command
from tasbot.customlog import Log


class Main(IPlugin):
	def __init__(self, name, tasclient):
		IPlugin.__init__(self, name, tasclient)
		self.chans = []
		self.admins = []
		self.faqs = dict()
		self.faqlinks = dict()
		self.sortedlinks = {}
		self.filename = ""
		self.last_faq = ""
		self.last_time = time()
		self.min_pause = 5.0
		self.logger.debug(self.commands)

	@IPlugin._num_args(4)
	@IPlugin._not_self
	def cmd_said_faq(self, args, socket):
		now = time()
		user = args[1]
		diff = now - self.last_time
		if diff > self.min_pause :
			self.print_faq( socket, args[0], args[3] )
		self.last_time = time()

	@IPlugin._num_args()
	@IPlugin._not_self
	def cmd_said_faqlist(self,args, socket):
		if len(self.faqs) > 0:
			faqstring = "available faq items are: "
		else:
			faqstring = "no faq items avaliable"
		for key in self.faqs:
			faqstring += key + " "
		socket.send("SAY %s %s\n" % (args[0],faqstring ))
	
	@IPlugin._num_args(4)
	@IPlugin._admin_only
	def cmd_said_faqlearn(self,args, socket):
		def addFaq( key, args ):
			msg = " ".join( args )
			if msg != "" :
				msg = msg.replace( "\\n", '\n' )
				self.faqs[key.lower()] = msg.lower()
			self._save_faqs()
		addFaq( args[3], args[4:] )
		self.tasclient.saypm( args[1], 'saved')

	def oncommandfromserver(self, command, args, socket):
		if len(args) <= 2:
			return
		try:				
			for trigger,funcname in self.commands[command]:
				if trigger == args[2]:
					func = getattr(self, funcname)
					func(args, socket)
		except KeyError:
			pass
		except Exception,e:
			self.logger.exception(e)
		#these should work in both pm and channel
		if command.startswith("SAID") and len(args) > 2 and args[1] != self.faqbotname:
			if args[2] == "!faqlink" and args[1] in self.admins and len(args) > 4:
				self.addFaqLink( args[3], args[4:] )
				return
			elif args[2] == "!writehtml" and args[1] in self.admins:
				self.output_html()
				return
			else:
				msg = " ".join( args[2:] ).lower()
				for phrase in self.sortedlinks:
					if msg.find( phrase ) >= 0:
						faqkey = self.faqlinks[phrase]
						Log.notice( "autodetected message: \"%s\" faq found:" %(msg,faqkey))
						now = time()
						diff = now - self.last_time
						if diff > self.min_pause :
							self.print_faq( socket, args[0], faqkey )
						self.last_time = time()
						return

	def print_faq( self, socket, channel, faqname ):
		msg = self.faqs[faqname]
		lines = msg.split('\n')
		for line in lines :
			socket.send("SAY %s %s\n" % (channel,line))

	def _load_faqs( self ):
		createFileIfMissing(self.faqfilename)
		with open(self.faqfilename,'r') as faqfile:
			content = faqfile.read()
			entries = content.split('|')
			i = 0
			while i < len(entries) - 1  :
				self.faqs[entries[i].lower()] = entries[i+1]
				i += 2

	def _load_faqlinks( self ):
		createFileIfMissing(self.faqlinksfilename)
		with open(self.faqlinksfilename,'r') as faqlinksfile:
			content = faqlinksfile.read()
			entries = content.split('|')
			i = 0
			while i < len(entries) - 1  :
				self.faqlinks[entries[i].lower()] = entries[i+1].lower()
				i += 2
			self.sortedlinks = sorted( self.faqlinks, key=len, reverse=True )

	def _save_faqs( self ):
		with open(self.faqfilename,'w') as faqfile:
			for key,msg in self.faqs.items():
				faqfile.write( key + "|" + msg + "|" )
			faqfile.flush()

	def _saveFaqLinks( self ):
		with open(self.faqlinksfilename,'w') as faqlinksfile:
			for key,msg in self.faqlinks.items():
				faqlinksfile.write( key + "|" + msg + "|" )
			faqlinksfile.flush()

	def addFaqLink( self, key, args ):
		msg = " ".join( args )
		if msg != "" :
			self.faqlinks[msg.lower()] = key.lower()
			self.sortedlinks = sorted( self.faqlinks, key=len, reverse=True )
		self.saveFaqLinks()

	def ondestroy( self ):
		self._save_faqs()
		self._saveFaqLinks()

	def onload(self,tasc):
	  self.app = tasc.main
	  self.chans = self.app.config.GetOptionList('join_channels',"channels")
	  self.admins = self.app.config.GetOptionList('tasbot',"admins")
	  self.faqfilename = self.app.config.get('faq',"faqfile")
	  self.faqlinksfilename = self.app.config.get('faq',"faqlinksfile")
	  self.faqbotname = self.app.config.get('tasbot',"nick")
	  self._load_faqs()
	  self._load_faqlinks()

	def output_html(self):
		output_fn='test.html'
		env = Environment(loader=FileSystemLoader('.'))
		template = env.get_template('htmloutput.jinja')
		with open(output_fn,'wb') as outfile:
			outfile.write( template.render(faqs=self.faqs) )