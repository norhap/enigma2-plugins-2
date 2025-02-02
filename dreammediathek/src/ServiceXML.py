# -*- coding: utf-8 -*-
from re import compile as re_compile
from os import path as os_path, symlink, listdir, unlink, readlink, remove

from xml.etree.cElementTree import parse as cet_parse
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_HDD, SCOPE_PLUGIN, SCOPE_GUISKIN
#WEBTV_STATIONS = "/etc/enigma2/webtv_stations.xml"
WEBTV_STATIONS = resolveFilename(SCOPE_PLUGIN, "Extensions/dreamMediathek/webtv_stations.xml")


class WebTVStations():
	"""Manages WebTVStations declared in a XML-Document."""

	def __init__(self):
		print("[WebTVStations] INIT")
		self.webtv_stations = {}

	def getWebTVStations(self, callback=None):
		webtv_stations = []
		self.webtv_stations = {}

		if not os_path.exists(WEBTV_STATIONS):
			return
		tree = cet_parse(WEBTV_STATIONS).getroot()

		def getValue(definitions, default):
			ret = ""
			Len = len(definitions)
			return Len > 0 and definitions[Len - 1].text or default

		for tvstation in tree.findall("tvstation"):
			data = {'provider': None, 'title': None, 'streamurl': None}
			try:
				data['provider'] = getValue(tvstation.findall("provider"), False)
				data['title'] = getValue(tvstation.findall("title"), False)
				data['streamurl'] = getValue(tvstation.findall("streamurl"), False)

				print("TVSTATION--->", data)
				self.webtv_stations[data['title']] = data
			except Exception as e:
				print("[WebTVStations] Error reading Stations:", e)

	def getWebTVStationsList(self):
		return sorted(self.webtv_stations.iterkeys())


iWebTVStations = WebTVStations()
