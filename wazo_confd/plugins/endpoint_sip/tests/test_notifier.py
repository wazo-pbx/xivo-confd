# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from mock import Mock

from xivo_bus.resources.endpoint_sip.event import (
    CreateSipEndpointEvent,
    CreateSipEndpointTemplateEvent,
    DeleteSipEndpointEvent,
    DeleteSipEndpointTemplateEvent,
    EditSipEndpointEvent,
    EditSipEndpointTemplateEvent,
)

from ..notifier import SipEndpointNotifier, SipTemplateNotifier


SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_pjsip.so', 'dialplan reload'],
    'agentbus': [],
}


class TestSipEndpointNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip = Mock(
            uuid=str(uuid.uuid4()),
            tenant_uuid=str(uuid.uuid4()),
            label='label',
            auth_section_options=[['username', 'username']],
            trunk={'id': 2},
            line=None,
        )
        self.sip.name = 'limitation of mock instantiation with name ...'
        self.sip_serialized = {
            'uuid': self.sip.uuid,
            'tenant_uuid': self.sip.tenant_uuid,
            'name': self.sip.name,
            'auth_section_options': self.sip.auth_section_options,
            'label': self.sip.label,
            'trunk': self.sip.trunk,
            'line': self.sip.line,
        }

        self.notifier = SipEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sip_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateSipEndpointEvent(self.sip_serialized)

        self.notifier.created(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditSipEndpointEvent(self.sip_serialized)

        self.notifier.edited(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSipEndpointEvent(self.sip_serialized)

        self.notifier.deleted(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)


class TestSipTemplateNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip = Mock()
        self.notifier = SipTemplateNotifier(self.sysconfd, self.bus)

    def test_when_sip_template_created_then_event_sent_on_bus(self):
        expected_event = CreateSipEndpointTemplateEvent({})

        self.notifier.created(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_template_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_template_edited_then_event_sent_on_bus(self):
        expected_event = EditSipEndpointTemplateEvent({})

        self.notifier.edited(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_template_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_template_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSipEndpointTemplateEvent({})

        self.notifier.deleted(self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
