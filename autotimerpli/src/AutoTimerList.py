# -*- coding: utf-8 -*-
# for localized messages
from . import _

# GUI (Components)
from Components.MenuList import MenuList
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_VALIGN_BOTTOM
from Tools.LoadPixmap import LoadPixmap
from ServiceReference import ServiceReference
from Components.config import config
from Tools.FuzzyDate import FuzzyTime
from time import localtime, time, strftime, mktime
from Tools.Directories import resolveFilename, SCOPE_GUISKIN
from skin import parseColor, parseFont
import skin


class DAYS:
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6
	WEEKEND = 'weekend'
	WEEKDAY = 'weekday'


class AutoTimerList(MenuList):
	"""Defines a simple Component to show Timer name"""

	def __init__(self, entries):
		MenuList.__init__(self, entries, False, content=eListboxPythonMultiContent)
		self.style_autotimerslist = config.plugins.autotimer.style_autotimerslist.value
		if self.style_autotimerslist == "standard":
			font = skin.fonts.get("AutotimerList", ("Regular", 22, 25))
			self.l.setFont(0, gFont(font[0], font[1]))
			self.l.setBuildFunc(self.buildListboxEntry)
			self.l.setItemHeight(int(font[2]))
			self.colorDisabled = 0x606060
		else:
			self.l.setBuildFunc(self.buildListboxEntry)
			font = skin.fonts.get("AutotimerListExt0", ("Regular", 20))
			self.l.setFont(0, gFont(font[0], font[1]))
			font = skin.fonts.get("AutotimerListExt1", ("Regular", 17, 70))
			self.l.setFont(1, gFont(font[0], font[1]))
			self.l.setItemHeight(int(font[2]))

			(iconEnabled, iconDisabled, iconRecording, iconZapped) = skin.parameters.get("AutotimerListIcons", ("icons/lock_on.png", "icons/lock_off.png", "icons/timer_rec.png", "icons/timer_zap.png"))
			self.iconEnabled = LoadPixmap(resolveFilename(SCOPE_GUISKIN, iconEnabled))
			self.iconDisabled = LoadPixmap(resolveFilename(SCOPE_GUISKIN, iconDisabled))
			self.iconRecording = LoadPixmap(resolveFilename(SCOPE_GUISKIN, iconRecording))
			self.iconZapped = LoadPixmap(resolveFilename(SCOPE_GUISKIN, iconZapped))
			self.colorDisabled = 12368828

	def applySkin(self, desktop, parent):
		attribs = []
		if self.skinAttributes is not None:
			for (attrib, value) in self.skinAttributes:
				if attrib == "font":
					if self.style_autotimerslist == "standard":
						self.l.setFont(0, parseFont(value, ((1, 1), (1, 1))))
				elif attrib == "itemHeight":
					if self.style_autotimerslist == "standard":
						self.l.setItemHeight(int(value))
				elif attrib == "colorDisabled":
					if self.style_autotimerslist == "standard":
						self.colorDisabled = parseColor(value).argb()
				else:
					attribs.append((attrib, value))
		self.skinAttributes = attribs
		return MenuList.applySkin(self, desktop, parent)

	#
	#  | <Name of AutoTimer> |
	#
	def buildListboxEntry(self, timer):
		if self.style_autotimerslist == "standard":
			size = self.l.getItemSize()
			color = None
			if not timer.enabled:
				color = self.colorDisabled
			return [
				None,
				(eListboxPythonMultiContent.TYPE_TEXT, 5, 0, size.width() - 5, size.height(), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, timer.name, color, color)
			]
		else:
			if not timer.enabled:
				icon = self.iconDisabled
			else:
				icon = self.iconEnabled
			if timer.justplay:
				rectypeicon = self.iconZapped
			else:
				rectypeicon = self.iconRecording

			channels = []
			bouquets = []
			channel = ""
			if timer.services:
				for t in timer.services:
					channels.append(ServiceReference(t).getServiceName())
			if timer.bouquets:
				for t in timer.bouquets:
					bouquets.append(ServiceReference(t).getServiceName())
			if channels or bouquets:
				if channels:
					channel = _("[S]  ")
					channel += ", ".join(channels)
					channel += " "
				if bouquets:
					channel += _("[B]  ")
					channel += ", ".join(bouquets)
			else:
				channel = _("All channels")
				if timer.searchType == "favoritedesc":
					channel = _("[B]  ") + channel
			height = self.l.getItemSize().height()
			width = self.l.getItemSize().width()
			res = [None]
			x = (2 * width) // 3
			nx, ny, nw, nh = skin.parameters.get("AutotimerListTimerName", (52, 2, 26, 25))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, nx, ny, x - nw, nh, 0, RT_HALIGN_LEFT | RT_VALIGN_BOTTOM, timer.name))
			nx, ny, nw, nh = skin.parameters.get("AutotimerListChannels", (2, 47, 4, 25))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, nx, ny, width - nw, nh, 1, RT_HALIGN_LEFT | RT_VALIGN_BOTTOM, channel))

			if timer.include[3]:
				total = len(timer.include[3])
				count = 0
				days = []
				while count + 1 <= total:
					day = timer.include[3][count]
					day = {
						'0': _("Mon"),
						'1': _("Tue"),
						'2': _("Wed"),
						'3': _("Thur"),
						'4': _("Fri"),
						'5': _("Sat"),
						'6': _("Sun"),
						"weekend": _("Weekend"),
						"weekday": _("Weekday")
						}[day]
					days.append(day)
					count += 1
				days = ', '.join(days)
			else:
				days = _("Everyday")
			dx, ny, dw, nh = skin.parameters.get("AutotimerListDays", (1, 25, 5, 25))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, float(width) / 10 * 4.5 + dx, ny, float(width) / 10 * 5.5 - dw, nh, 1, RT_HALIGN_RIGHT | RT_VALIGN_BOTTOM, days))

			if timer.hasTimespan():
				nowt = time()
				now = localtime(nowt)
				begintime = int(mktime((now.tm_year, now.tm_mon, now.tm_mday, timer.timespan[0][0], timer.timespan[0][1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
				endtime = int(mktime((now.tm_year, now.tm_mon, now.tm_mday, timer.timespan[1][0], timer.timespan[1][1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
				timespan = ((" %s ... %s") % (FuzzyTime(begintime)[1], FuzzyTime(endtime)[1]))
			else:
				timespan = _("Any time")
			dx, ny, nw, nh = skin.parameters.get("AutotimerListHasTimespan", (154, 1, 150, 25))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, width - dx, ny, nw, nh, 1, RT_HALIGN_RIGHT | RT_VALIGN_BOTTOM, timespan))

			if timer.hasTimeframe():
				begin = strftime("%a, %d %b", localtime(timer.getTimeframeBegin()))
				end = strftime("%a, %d %b", localtime(timer.getTimeframeEnd()))
				timespan = (("%s ... %s") % (begin, end))
				nx, ny, nw, nh = skin.parameters.get("AutotimerListTimespan", (2, 25, 5, 25))
				res.append((eListboxPythonMultiContent.TYPE_TEXT, nx, ny, float(width) / 10 * 4.5 - nw, nh, 1, RT_HALIGN_LEFT | RT_VALIGN_BOTTOM, timespan))

			if icon:
				nx, ny, nw, nh = skin.parameters.get("AutotimerListIcon", (2, 3, 24, 25))
				res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, nx, ny, nw, nh, icon))
			nx, ny, nw, nh = skin.parameters.get("AutotimerListRectypeicon", (28, 5, 24, 25))
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, nx, ny, nw, nh, rectypeicon))
			devide = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "div-h.png"))
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, height - 2, width, 1, devide))
			return res

	def getCurrent(self):
		cur = self.l.getCurrentSelection()
		return cur and cur[0]

	def moveToEntry(self, entry):
		if entry is None:
			return

		idx = 0
		for x in self.list:
			if x[0] == entry:
				self.instance.moveSelectionTo(idx)
				break
			idx += 1
