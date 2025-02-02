# -*- coding: utf-8 -*-
# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.


class Enum:
    group = None

    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return '<%s: %s>' % (self.group, self.label)

    def __str__(self):
        return self.label


class StatusEnum(Enum):
    group = 'Status'


OFFLINE = Enum('Offline')
ONLINE = Enum('Online')
AWAY = Enum('Away')


class OfflineError(Exception):
    print("[dreamIRC] offline - %s" % Exception)
    """The requested action can't happen while offline."""
