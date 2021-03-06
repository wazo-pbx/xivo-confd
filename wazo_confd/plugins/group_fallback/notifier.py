# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import EditGroupFallbackEvent

from wazo_confd import bus


class GroupFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, group):
        event = EditGroupFallbackEvent(group.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupFallbackNotifier(bus)
