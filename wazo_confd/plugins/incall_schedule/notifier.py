# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.incall_schedule.event import (
    IncallScheduleAssociatedEvent,
    IncallScheduleDissociatedEvent,
)

from wazo_confd import bus


class IncallScheduleNotifier:
    def __init__(self, bus):
        self._bus = bus

    def associated(self, incall, schedule):
        event = IncallScheduleAssociatedEvent(incall.id, schedule.id)
        self._bus.send_bus_event(event)

    def dissociated(self, incall, schedule):
        event = IncallScheduleDissociatedEvent(incall.id, schedule.id)
        self._bus.send_bus_event(event)


def build_notifier():
    return IncallScheduleNotifier(bus)
