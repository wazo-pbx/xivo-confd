# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.confbridge.event import (
    EditConfBridgeWazoDefaultBridgeEvent,
    EditConfBridgeWazoDefaultUserEvent,
)

from wazo_confd import bus, sysconfd


class ConfBridgeConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, confbridge):
        if section_name == 'wazo_default_bridge':
            event = EditConfBridgeWazoDefaultBridgeEvent()
            self.bus.send_bus_event(event)
        elif section_name == 'wazo_default_user':
            event = EditConfBridgeWazoDefaultUserEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload app_confbridge.so'])


def build_notifier():
    return ConfBridgeConfigurationNotifier(bus, sysconfd)
