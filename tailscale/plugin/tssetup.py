from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigText
from Components.Input import Input
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
from Plugins.Extensions.spazeMenu.plugin import esHD
from Plugins.Extensions.Tailscale.__init__ import _
import gettext
import os

class TailscaleSetup(Screen, ConfigListScreen):
	if esHD():
		skin="""<screen name="TailscaleSetup" position="center,120" size="1230,780">
			<eLabel name="" position="10,700" size="30,30" backgroundColor="red" />
			<eLabel name="" position="285,700" size="30,30" backgroundColor="green" />
			<eLabel name="" position="480,700" size="30,30" backgroundColor="yellow" />
			<eLabel name="" position="900,700" size="30,30" backgroundColor="blue" />
			<widget source="key_red" render="Label" position="50,695" size="230,45" zPosition="2" font="RegularHD; 20" halign="left" />
			<widget source="key_green" render="Label" position="325,695" size="100,45" zPosition="2" font="RegularHD; 22" halign="left" transparent="1" />
			<widget source="key_yellow" render="Label" position="520,695" size="350,45" zPosition="2" font="RegularHD; 20" halign="left" />
			<widget source="key_blue" render="Label" position="940,695" size="410,45" zPosition="2" font="RegularHD; 22" halign="left" transparent="1" />
			<widget name="config" position="10,10" size="1210,218" itemHeight="40" scrollbarMode="showNever" transparent="1" font="RegularHD; 22" />
			<widget name="description" position="20,500" size="1200,120" transparent="1" font="RegularHD; 20" />
			<widget name="HelpWindow" position="350,400" size="1,1" transparent="1" />
			</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ['TailscaleSetup']
		self.setup_title = _('Tailscale Settings')
		self.onChangedEntry = []
		self['OkCancelActions'] = ActionMap(['SetupActions', 'ColorActions', 'DirectionActions'],
		   {
		   'left': self.keyLeft,
		   'down': self.keyDown,
		   'up': self.keyUp,
		   'right': self.keyRight,
		   'cancel': self.keyCancel, 
		   'ok': self.keySave,
		   'red': self.keyCancel,
		   'green': self.keySave,
		   'yellow': self.keyYellow,
		   'blue': self.openKeyboard,
		   }, -1)
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self['key_red'] = StaticText(_('Cancel'))
		self['key_green'] = StaticText(_('OK'))
		self['key_yellow'] = StaticText(_('Load Auth Key'))
		self['key_blue'] = StaticText(_('Keyboard'))
		self["description"] = Label("")

		list = []
		list.append(getConfigListEntry(_('Automatic Start'), config.tailscale.autostart, _('Enable/Disable automatic start when enigma2 boots')))
		list.append(getConfigListEntry(_('Auth key'), config.tailscale.apikey, _('Auth key to register your device in Tailscale.\nPress yellow to load Auth Key from file located at /etc/keys/tailscale.key')))

		ConfigListScreen.__init__(self, list, session=session, on_change=self.changedEntry)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)
		self.Getinfo()
		if isinstance(self["config"].getCurrent()[1], ConfigText):
			if "HelpWindow" in self:
				if self["config"].getCurrent()[1].help_window and self["config"].getCurrent()[1].help_window.instance is not None:
					helpwindowpos = self["HelpWindow"].getPosition()
					from enigma import ePoint
					self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

	def cancel(self):
		for i in self['config'].list:
			i[1].cancel()
		self.close(False)

	def Getinfo(self):
		description = self['config'].getCurrent()[2]
		self['description'].setText(description)

	def checkInstalled(self):
		return fileExists('/usr/sbin/tailscaled')

	def autostart(self):
		if config.tailscale.autostart.getValue()==True:
			if self.checkInstalled():
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc2.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc3.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc4.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc5.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc0.d/K60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc1.d/K60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc6.d/K60tailscale-daemon')
		else:
			os.system('rm -f /etc/rc2.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc3.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc4.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc5.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc0.d/K60tailscale-daemon')
			os.system('rm -f /etc/rc1.d/K60tailscale-daemon')
			os.system('rm -f /etc/rc6.d/K60tailscale-daemon')

	def saveAll(self):
		for x in self['config'].list:
			x[1].save()
			
		config.tailscale.autostart.save()
		config.tailscale.apikey.save()
		configfile.save()
		self.autostart()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.Getinfo()
        
	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.Getinfo()

	def keyDown(self):
		self['config'].instance.moveSelection(self['config'].instance.moveDown)
		self.Getinfo()

	def keyUp(self):
		self['config'].instance.moveSelection(self['config'].instance.moveUp)
		self.Getinfo()

	def keySave(self):
		self.saveAll()
		os.system('tailscale up --authkey '+ config.tailscale.apikey.value)
		self.close()

	def keyYellow(self):
		filekey = '/etc/keys/tailscale.key'
		f = open(filekey, 'r')
		authkey = f.read()
		f.close()
		config.tailscale.apikey.value = authkey
		self.saveAll()

	def openKeyboard(self):
		self.session.openWithCallback(self.CallbackInput, VirtualKeyBoard, title=(_("Enter your Auth Key")), text=config.tailscale.apikey.getValue())

	def CallbackInput(self, id=None):
		if id:
			config.tailscale.apikey.setValue(id)
			self.session.open(MessageBox, _('Execution finished.'), type=MessageBox.TYPE_INFO, timeout=5)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self['config'].getCurrent()[0]

	def getCurrentValue(self):
		return str(self['config'].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
