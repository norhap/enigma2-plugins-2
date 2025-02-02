# -*- coding: utf-8 -*-
# for localized messages
from . import _, config

# GUI (Screens)
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from AutoTimerEditor import AutoTimerEditor, AutoTimerChannelSelection
from AutoTimerImporter import AutoTimerImportSelector
from AutoTimerPreview import AutoTimerPreview
from AutoTimerSettings import AutoTimerSettings
from AutoTimerWizard import AutoTimerWizard

# GUI (Components)
from AutoTimerList import AutoTimerList
from Components.ActionMap import HelpableActionMap
from Components.Sources.StaticText import StaticText
from enigma import getDesktop


class AutoTimerOverviewSummary(Screen):
	skin = """
	<screen position="0,0" size="132,64">
		<widget source="parent.Title" render="Label" position="6,4" size="120,21" font="Regular;18" />
		<widget source="entry" render="Label" position="6,25" size="120,21" font="Regular;16" />
		<widget source="global.CurrentTime" render="Label" position="56,46" size="82,18" font="Regular;16" >
			<convert type="ClockToText">WithSeconds</convert>
		</widget>
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self["entry"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, text):
		self["entry"].text = text


HD = False
if getDesktop(0).size().width() >= 1280:
	HD = True


class AutoTimerOverview(Screen, HelpableScreen):
	"""Overview of AutoTimers"""
	if HD:
		skin = """<screen name="AutoTimerOverview" position="center,center" size="680,480" title="AutoTimer Overview">
				<ePixmap position="0,0" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
				<ePixmap position="160,0" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
				<ePixmap position="320,0" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
				<ePixmap position="480,0" zPosition="1" size="35,25" pixmap="buttons/key_menu.png" alphatest="on" />
				<widget source="key_green" render="Label" position="10,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;17" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget source="key_yellow" render="Label" position="160,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;17" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget source="key_blue" render="Label" position="320,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;17" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget name="entries" position="5,45" size="450,425" scrollbarMode="showOnDemand" />
			</screen>"""
	else:
		skin = """<screen name="AutoTimerOverview" position="center,center" size="460,280" title="AutoTimer Overview">
				<ePixmap position="0,0" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
				<ePixmap position="140,0" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
				<ePixmap position="280,0" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
				<ePixmap position="422,10" zPosition="1" size="35,25" pixmap="buttons/key_menu.png" alphatest="on" />
				<widget source="key_green" render="Label" position="0,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget source="key_yellow" render="Label" position="140,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget source="key_blue" render="Label" position="280,0" zPosition="1" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
				<widget name="entries" position="5,45" size="450,225" scrollbarMode="showOnDemand" />
			</screen>"""

	def __init__(self, session, autotimer):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		# Save autotimer
		self.autotimer = autotimer

		self.changed = False

		# Button Labels
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Delete"))
		self["key_blue"] = StaticText(_("Add"))

		# Create List of Timers
		self["entries"] = AutoTimerList(autotimer.getSortedTupleTimerList())

		# Summary
		self.onChangedEntry = []
		self["entries"].onSelectionChanged.append(self.selectionChanged)

		# Define Actions
		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
				"ok": (self.ok, _("Edit selected AutoTimer")),
				"cancel": (self.cancel, _("Close and forget changes")),
			}
		)

		self["MenuActions"] = HelpableActionMap(self, "MenuActions",
			{
				"menu": (self.menu, _("Open Context Menu"))
			}
		)

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
				"red": self.cancel,
				"green": (self.save, _("Close and save changes")),
				"yellow": (self.remove, _("Remove selected AutoTimer")),
				"blue": (self.add, _("Add new AutoTimer")),
			}
		)

		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.firstExec)

	def firstExec(self):
		from plugin import autotimerHelp
		if config.plugins.autotimer.show_help.value and autotimerHelp:
			config.plugins.autotimer.show_help.value = False
			config.plugins.autotimer.show_help.save()
			autotimerHelp.open(self.session)

	def setCustomTitle(self):
		from plugin import AUTOTIMER_VERSION
		self.setTitle(_("AutoTimer overview") + _(" - Version: ") + AUTOTIMER_VERSION)

	def createSummary(self):
		return AutoTimerOverviewSummary

	def selectionChanged(self):
		sel = self["entries"].getCurrent()
		text = sel and sel.name or ""
		for x in self.onChangedEntry:
			try:
				x(text)
			except Exception:
				pass

	def add(self):
		newTimer = self.autotimer.defaultTimer.clone()
		newTimer.id = self.autotimer.getUniqueId()

		if config.plugins.autotimer.editor.value == "wizard":
			self.session.openWithCallback(
				self.addCallback,
				AutoTimerWizard,
				newTimer
			)
		elif config.plugins.autotimer.editor.value == "epg":
			self.session.openWithCallback(
				self.refresh,
				AutoTimerChannelSelection,
				self.autotimer
			)
		else:
			self.session.openWithCallback(
				self.addCallback,
				AutoTimerEditor,
				newTimer
			)

	def editCallback(self, ret):
		if ret:
			self.changed = True
			self.refresh()

	def addCallback(self, ret):
		if ret:
			self.changed = True
			self.autotimer.add(ret)
			self.refresh()

	def importCallback(self, ret):
		if ret:
			self.session.openWithCallback(
				self.addCallback,
				AutoTimerEditor,
				ret
			)

	def refresh(self, res=None):
		# Re-assign List
		cur = self["entries"].getCurrent()
		self["entries"].setList(self.autotimer.getSortedTupleTimerList())
		self["entries"].moveToEntry(cur)

	def ok(self):
		# Edit selected Timer
		current = self["entries"].getCurrent()
		if current is not None:
			self.session.openWithCallback(
				self.editCallback,
				AutoTimerEditor,
				current
			)

	def remove(self):
		# Remove selected Timer
		cur = self["entries"].getCurrent()
		if cur is not None:
			title = _("Message\nDo you really want to delete %s?") % (cur.name)
			list = ((_("Yes, and delete all timers generated by this autotimer"), "yes_delete"),
			(_("Yes, but keep timers generated by this autotimer"), "yes_keep"),
			(_("No"), "no"))
			self.session.openWithCallback(
				self.removeCallback,
				ChoiceBox,
				title=title,
				list=list,
				selection=0
			)

	def removeCallback(self, answer):
		cur = self["entries"].getCurrent()
		if answer:
			if (answer[1] != "no") and cur:
				self.autotimer.remove(cur.id)
				self.refresh()
				if (answer[1] == "yes_delete"):
					import NavigationInstance
					from RecordTimer import RecordTimerEntry
					recordHandler = NavigationInstance.instance.RecordTimer
					for timer in recordHandler.timer_list[:]: # '[:]' for working on a copy, avoid processing a changing list
						#print('[AutoTimerOverview] checking whether timer should be deleted: ', timer)
						if timer:
							for entry in timer.log_entries:
								if len(entry) == 3:
									#print('[AutoTimerOverview] checking line: ', entry[2])
									if entry[2] == '[AutoTimer] Try to add new timer based on AutoTimer ' + cur.name + '.':
										NavigationInstance.instance.RecordTimer.removeEntry(timer)
										break

	def cancel(self):
		if self.changed:
			self.session.openWithCallback(
				self.cancelConfirm,
				MessageBox,
				_("Really close without saving settings?")
			)
		else:
			self.close(None)

	def cancelConfirm(self, ret):
		if ret:
			# Invalidate config mtime to force re-read on next run
			self.autotimer.configMtime = -1

			# Close and indicated that we canceled by returning None
			self.close(None)

	def menu(self):
		list = [
			(_("Preview"), "preview"),
			(_("Import existing Timer"), "import"),
			(_("Import from EPG"), "import_epg"),
			(_("Setup"), "setup"),
			(_("Edit new timer defaults"), "defaults"),
			(_("Clone selected timer"), "clone"),
			(_("Create a new timer using the classic editor"), "newplain"),
			(_("Create a new timer using the wizard"), "newwizard")
		]

		from plugin import autotimerHelp
		if autotimerHelp:
			list.insert(0, (_("Help"), "help"))
			list.insert(1, (_("Frequently asked questions"), "faq"))

		self.session.openWithCallback(
			self.menuCallback,
			ChoiceBox,
			title=_("AutoTimer Context Menu"),
			list=list,
		)

	def openPreview(self, timers, skipped):
		self.session.open(
			AutoTimerPreview,
			timers
		)

	def menuCallback(self, ret):
		ret = ret and ret[1]
		if ret:
			if ret == "help":
				from plugin import autotimerHelp
				autotimerHelp.open(self.session)
			elif ret == "faq":
				from Plugins.SystemPlugins.MPHelp import PluginHelp, XMLHelpReader
				from Tools.Directories import resolveFilename, SCOPE_PLUGINS
				reader = XMLHelpReader(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/faq.xml"))
				autotimerFaq = PluginHelp(*reader)
				autotimerFaq.open(self.session)
			elif ret == "preview":
				# todo timeout / error handling
				self.autotimer.parseEPG(simulateOnly=True, callback=self.openPreview)
			elif ret == "import":
				newTimer = self.autotimer.defaultTimer.clone()
				newTimer.id = self.autotimer.getUniqueId()

				self.session.openWithCallback(
					self.importCallback,
					AutoTimerImportSelector,
					newTimer
				)
			elif ret == "import_epg":
				self.session.openWithCallback(
					self.refresh,
					AutoTimerChannelSelection,
					self.autotimer
				)
			elif ret == "setup":
				self.session.open(
					AutoTimerSettings
				)
			elif ret == "defaults":
				self.session.open(
					AutoTimerEditor,
					self.autotimer.defaultTimer,
					editingDefaults=True
				)
			elif ret == "newwizard":
				newTimer = self.autotimer.defaultTimer.clone()
				newTimer.id = self.autotimer.getUniqueId()

				self.session.openWithCallback(
					self.addCallback, # XXX: we could also use importCallback... dunno what seems more natural
					AutoTimerWizard,
					newTimer
				)
			elif ret == "newplain":
				newTimer = self.autotimer.defaultTimer.clone()
				newTimer.id = self.autotimer.getUniqueId()

				self.session.openWithCallback(
					self.addCallback,
					AutoTimerEditor,
					newTimer
				)
			elif ret == "clone":
				current = self["entries"].getCurrent()
				if current is not None:
					newTimer = current.clone()
					newTimer.id = self.autotimer.getUniqueId()

					self.session.openWithCallback(
						self.addCallback,
						AutoTimerEditor,
						newTimer
					)

	def save(self):
		# Just close here, saving will be done by cb
		self.close(self.session)
