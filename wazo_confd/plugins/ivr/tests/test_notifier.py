# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from xivo_bus.resources.ivr.event import CreateIvrEvent, DeleteIvrEvent, EditIvrEvent
from xivo_dao.alchemy.ivr import IVR

from ..notifier import IvrNotifier


SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload'], 'agentbus': []}


class TestIvrNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.ivr = Mock(IVR, id=2)

        self.notifier = IvrNotifier(self.bus, self.sysconfd)

    def test_when_ivr_created_then_event_sent_on_bus(self):
        expected_event = CreateIvrEvent(self.ivr.id)

        self.notifier.created(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_ivr_edited_then_event_sent_on_bus(self):
        expected_event = EditIvrEvent(self.ivr.id)

        self.notifier.edited(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_ivr_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteIvrEvent(self.ivr.id)

        self.notifier.deleted(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
