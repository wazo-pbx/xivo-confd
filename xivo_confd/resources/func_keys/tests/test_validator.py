# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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
from mock import Mock, sentinel
from hamcrest import assert_that, calling, raises

from xivo_dao.resources.extension.model import ServiceExtension, ForwardExtension, \
    AgentActionExtension
from xivo_dao.resources.features.model import TransferExtension
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate
from xivo_dao.resources.func_key.model import FuncKey, \
    ServiceDestination, ForwardDestination, TransferDestination, \
    AgentDestination, ParkPositionDestination

from xivo_dao.helpers.exception import InputError

from xivo_confd.helpers.validator import Validator
from xivo_confd.resources.func_keys.validator import FuncKeyMappingValidator
from xivo_confd.resources.func_keys.validator import FuncKeyValidator, \
    ServiceValidator, ForwardValidator, TransferValidator, AgentActionValidator, \
    ParkPositionValidator


class TestFuncKeyMappingValidator(unittest.TestCase):

    def setUp(self):
        self.funckey_validator = Mock(FuncKeyValidator)
        self.validator = FuncKeyMappingValidator(self.funckey_validator)

    def test_given_func_key_mapping_when_validating_then_validates_each_func_key(self):
        first_funckey = Mock(FuncKey)
        second_funckey = Mock(FuncKey)

        template = FuncKeyTemplate(keys={1: first_funckey,
                                         2: second_funckey})

        self.validator.validate(template)

        self.funckey_validator.validate.assert_any_call(first_funckey)
        self.funckey_validator.validate.assert_any_call(second_funckey)


class TestFuncKeyValidator(unittest.TestCase):

    def setUp(self):
        self.first_dest_validator = Mock(Validator)
        self.second_dest_validator = Mock(Validator)
        self.validator = FuncKeyValidator({'foobar': [self.first_dest_validator,
                                                      self.second_dest_validator]})

    def test_given_no_validator_for_destination_when_validating_then_raises_error(self):
        destination = Mock(type='spam')

        model = FuncKey(destination=destination)

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_multiple_validators_for_destination_when_validating_then_calls_each_validator(self):
        destination = Mock(type='foobar')
        model = FuncKey(destination=destination)

        self.validator.validate(model)

        self.first_dest_validator.validate.assert_called_once_with(destination)
        self.second_dest_validator.validate.assert_called_once_with(destination)


class TestServiceValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = ServiceValidator(self.dao)

    def test_given_service_does_not_exist_when_validating_then_raises_error(self):
        self.dao.find_all_service_extensions.return_value = []

        destination = ServiceDestination(service='enablevm')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_service_exists_when_validating_then_validation_passes(self):
        service_extensions = [ServiceExtension(id=sentinel.extension_id,
                                               exten='*25',
                                               service='enablednd'),
                              ServiceExtension(id=sentinel.extension_id,
                                               exten='*90',
                                               service='enablevm')]
        self.dao.find_all_service_extensions.return_value = service_extensions

        destination = ServiceDestination(service='enablevm')

        self.validator.validate(destination)

        self.dao.find_all_service_extensions.assert_called_once_with()


class TestForwardValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = ForwardValidator(self.dao)

    def test_given_forward_does_not_exist_when_validating_then_raises_error(self):
        self.dao.find_all_forward_extensions.return_value = []

        destination = ForwardDestination(forward='noanswer')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_forward_exists_when_validating_then_validation_passes(self):
        forward_extensions = [ForwardExtension(id=sentinel.extension_id,
                                               exten='*23',
                                               forward='busy'),
                              ForwardExtension(id=sentinel.extension_id,
                                               exten='*22',
                                               forward='noanswer')]
        self.dao.find_all_forward_extensions.return_value = forward_extensions

        destination = ForwardDestination(forward='busy')

        self.validator.validate(destination)

        self.dao.find_all_forward_extensions.assert_called_once_with()


class TestTransferValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = TransferValidator(self.dao)

    def test_given_transfer_does_not_exist_when_validating_then_raises_error(self):
        self.dao.find_all_transfer_extensions.return_value = []

        destination = TransferDestination(transfer='blind')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_transfer_exists_when_validating_then_validation_passes(self):
        transfer_extensions = [TransferExtension(id=sentinel.extension_id,
                                                 exten='*1',
                                                 transfer='blind'),
                               TransferExtension(id=sentinel.extension_id,
                                                 exten='*2',
                                                 transfer='attended')]
        self.dao.find_all_transfer_extensions.return_value = transfer_extensions

        destination = TransferDestination(transfer='blind')

        self.validator.validate(destination)

        self.dao.find_all_transfer_extensions.assert_called_once_with()


class TestAgentActionValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = AgentActionValidator(self.dao)

    def test_given_agent_action_does_not_exist_when_validating_then_raises_error(self):
        self.dao.find_all_agent_action_extensions.return_value = []

        destination = AgentDestination(action='login')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_agent_action_exists_when_validating_then_validation_passes(self):
        agent_action_extensions = [AgentActionExtension(id=sentinel.extension_id,
                                                        exten='*31',
                                                        action='login'),
                                   AgentActionExtension(id=sentinel.extension_id,
                                                        exten='*32',
                                                        action='logoff')]
        self.dao.find_all_agent_action_extensions.return_value = agent_action_extensions

        destination = AgentDestination(action='login')

        self.validator.validate(destination)

        self.dao.find_all_agent_action_extensions.assert_called_once_with()


class TestParkPositionValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.dao.find_park_position_range.return_value = (701, 750)
        self.validator = ParkPositionValidator(self.dao)

    def test_given_position_under_minimum_then_raises_error(self):
        destination = ParkPositionDestination(position=600)

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_position_over_maximum_then_raises_error(self):
        destination = ParkPositionDestination(position=800)

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_position_on_minimum_position_then_validation_passes(self):
        destination = ParkPositionDestination(position=701)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()

    def test_given_position_on_maximum_position_then_validation_passes(self):
        destination = ParkPositionDestination(position=750)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()

    def test_given_position_inside_range_then_validation_passes(self):
        destination = ParkPositionDestination(position=710)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()