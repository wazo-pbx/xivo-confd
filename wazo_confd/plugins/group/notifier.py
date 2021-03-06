# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import (
    CreateGroupEvent,
    EditGroupEvent,
    DeleteGroupEvent,
)

from wazo_confd import bus, sysconfd


class GroupNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, group):
        self.send_sysconfd_handlers()
        event = CreateGroupEvent(group.id)
        self.bus.send_bus_event(event)

    def edited(self, group):
        self.send_sysconfd_handlers()
        event = EditGroupEvent(group.id)
        self.bus.send_bus_event(event)

    def deleted(self, group):
        self.send_sysconfd_handlers()
        event = DeleteGroupEvent(group.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupNotifier(bus, sysconfd)
