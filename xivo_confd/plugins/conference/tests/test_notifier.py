# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import Mock

from xivo_bus.resources.conference.event import (CreateConferenceEvent,
                                                 EditConferenceEvent,
                                                 DeleteConferenceEvent)

from ..notifier import ConferenceNotifier

EXPECTED_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload app_confbridge.so'],
                     'agentbus': []}


class TestConferenceNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.conference = Mock(id=1234)

        self.notifier = ConferenceNotifier(self.bus, self.sysconfd)

    def test_when_conference_created_then_dialplan_reloaded(self):
        self.notifier.created(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_created_then_event_sent_on_bus(self):
        expected_event = CreateConferenceEvent(self.conference.id)

        self.notifier.created(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_conference_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_edited_then_event_sent_on_bus(self):
        expected_event = EditConferenceEvent(self.conference.id)

        self.notifier.edited(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_conference_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteConferenceEvent(self.conference.id)

        self.notifier.deleted(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)