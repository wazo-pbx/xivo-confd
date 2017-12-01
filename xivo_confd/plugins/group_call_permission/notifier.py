# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.group_call_permission.event import (
    GroupCallPermissionAssociatedEvent,
    GroupCallPermissionDissociatedEvent,
)


class GroupCallPermissionNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, call_permission):
        event = GroupCallPermissionAssociatedEvent(group.id, call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, group, call_permission):
        event = GroupCallPermissionDissociatedEvent(group.id, call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return GroupCallPermissionNotifier(bus)