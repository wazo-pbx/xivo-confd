# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import abc
import re
import json

from flask import url_for

from xivo_dao.helpers import errors
from xivo_confd.helpers.converter import Parser, Mapper, Builder
from xivo_dao.resources.func_key.model import FuncKey
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.features import dao as feature_dao

from xivo_dao.resources.func_key.model import UserDestination, \
    GroupDestination, QueueDestination, ConferenceDestination, \
    PagingDestination, BSFilterDestination, ServiceDestination, \
    CustomDestination, ForwardDestination, TransferDestination, \
    ParkPositionDestination, ParkingDestination, AgentDestination, \
    OnlineRecordingDestination

from xivo_dao.resources.func_key_template.model import UserTemplate

from xivo_confd.helpers.mooltiparse import Document, Field, \
    Int, Boolean, Unicode, Dict, \
    Required, Choice, Regexp

from xivo_confd.helpers.converter import Converter, ResourceSerializer


EXTEN_REGEX = re.compile(r'[A-Z0-9+*]+')


class JsonParser(Parser):

    def parse(self, request):
        return request.json


class TemplateValidator(object):

    def __init__(self, funckey_validator):
        self.funckey_validator = funckey_validator

    DOCUMENT = Document([
        Field('id', Int()),
        Field('name', Unicode()),
        Field('keys', Dict())
    ])

    def validate(self, mapping, action=None):
        self.DOCUMENT.validate(mapping, action)
        keys = mapping.get('keys', {})
        self.validate_keys(keys)

    def validate_keys(self, key_mapping):
        for pos, mapping in key_mapping.iteritems():
            if pos <= 0:
                raise errors.wrong_type('keys', 'numeric positions')
            if not isinstance(mapping, dict):
                raise errors.wrong_type('keys', 'dict-like structures')
            self.funckey_validator.validate(mapping)


class FuncKeyValidator(object):

    DOCUMENT = Document([
        Field('label', Unicode()),
        Field('blf', Boolean()),
        Field('destination', Dict(), create=[Required()])
    ])

    def __init__(self, builders):
        self.builders = builders

    def validate(self, mapping, action=None):
        self.DOCUMENT.validate(mapping, action)

        if 'destination' in mapping:
            self.validate_destination(mapping['destination'])

    def validate_destination(self, destination):
        dest_type = destination.get('type')

        if not dest_type:
            raise errors.param_not_found('destination', 'type')

        if dest_type not in self.builders:
            raise errors.param_not_found('destination', 'type')

        builder = self.builders[dest_type]
        builder.validate(destination)


class TemplateMapper(object):

    def __init__(self, funckey_mapper):
        self.funckey_mapper = funckey_mapper

    def for_decoding(self, mapping):
        if 'keys' in mapping:
            mapping['keys'] = {int(pos): funckey
                               for pos, funckey in mapping['keys'].iteritems()}
        return mapping

    def for_encoding(self, model):
        mapping = {field: getattr(model, field)
                   for field in model.FIELDS
                   if field not in ['keys', 'private']}
        mapping['keys'] = {pos: self.funckey_mapper.for_encoding(funckey)
                           for pos, funckey in model.keys.iteritems()}
        return mapping


class FuncKeyMapper(Mapper):

    def __init__(self, builders):
        self.builders = builders

    def for_decoding(self, mapping):
        return mapping

    def for_encoding(self, model):
        mapping = {field: getattr(model, field)
                   for field in model.FIELDS
                   if field != 'destination'}
        mapping['destination'] = self.map_destination(model.destination)
        return mapping

    def map_destination(self, destination):
        builder = self.builders[destination.type]
        return builder.to_mapping(destination)


class TemplateBuilder(Builder):

    def __init__(self, validator, funckey_builder):
        self.validator = validator
        self.funckey_builder = funckey_builder

    def create(self, mapping):
        self.validator.validate(mapping, 'create')
        key_mapping = mapping.get('keys', {})
        funckeys = self.create_funckeys(key_mapping)
        return FuncKeyTemplate(name=mapping.get('name'),
                               keys=funckeys)

    def update(self, model, mapping):
        self.validator.validate(mapping, 'update')
        model.name = mapping.get('name', model.name)

        key_mapping = mapping.get('keys', {})
        self.update_funckeys(model.keys, key_mapping)

    def create_funckeys(self, key_mapping):
        return {pos: self.funckey_builder.create(funckey)
                for pos, funckey in key_mapping.iteritems()}

    def update_funckeys(self, old_mapping, new_mapping):
        for pos, mapping in new_mapping.iteritems():
            self.funckey_builder.update(old_mapping[pos], mapping)


class FuncKeyBuilder(Builder):

    def __init__(self, validator, builders):
        self.validator = validator
        self.builders = builders

    def description(self):
        return [b.description() for b in self.builders.values()]

    def create(self, mapping):
        self.validator.validate(mapping, 'create')
        destination = self.build_destination(mapping['destination'])

        funckey = FuncKey(destination=destination)
        if 'label' in mapping:
            funckey.label = mapping['label']
        if 'blf' in mapping:
            funckey.blf = mapping['blf']

        return funckey

    def update(self, model, mapping):
        self.validator.validate(mapping, 'update')

        for field, value in mapping.iteritems():
            if field != 'destination':
                setattr(model, value)

        if 'destination' in mapping:
            model.destination = self.build_destination(mapping['destination'])

    def build_destination(self, destination):
        builder = self.builders[destination['type']]
        return builder.build(destination)


class DestinationBuilder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def fields(self):
        return

    @abc.abstractproperty
    def destination(self):
        return

    @abc.abstractmethod
    def to_model(self, destination):
        pass

    def description(self):
        return {'type': self.destination,
                'parameters': self.parameters()}

    def parameters(self):
        return [{'name': field.name} for field in self.fields]

    def build(self, destination):
        self.validate(destination)
        return self.to_model(destination)

    def validate(self, destination):
        for field in self.fields:
            field.validate(destination.get(field.name))

    def to_mapping(self, destination):
        mapping = {field.name: getattr(destination, field.name)
                   for field in self.fields}
        mapping['type'] = self.destination
        mapping['href'] = self.url(destination)
        return mapping

    def url(self, destination):
        return None


class UserDestinationBuilder(DestinationBuilder):

    destination = 'user'

    fields = [Field('user_id', Int(), Required())]

    def parameters(self):
        return [{'name': 'user_id',
                 'collection': url_for('users.search')}]

    def to_model(self, destination):
        return UserDestination(user_id=destination['user_id'])

    def url(self, destination):
        return url_for('users.get', resource_id=destination.user_id, _external=True)


class GroupDestinationBuilder(DestinationBuilder):

    destination = 'group'

    fields = [Field('group_id', Int(), Required())]

    def to_model(self, destination):
        return GroupDestination(group_id=destination['group_id'])


class QueueDestinationBuilder(DestinationBuilder):

    destination = 'queue'

    fields = [Field('queue_id', Int(), Required())]

    def to_model(self, destination):
        return QueueDestination(queue_id=destination['queue_id'])


class ConferenceDestinationBuilder(DestinationBuilder):

    destination = 'conference'

    fields = [Field('conference_id', Int(), Required())]

    def to_model(self, destination):
        return ConferenceDestination(conference_id=destination['conference_id'])


class PagingDestinationBuilder(DestinationBuilder):

    destination = 'paging'

    fields = [Field('paging_id', Int(), Required())]

    def to_model(self, destination):
        return PagingDestination(paging_id=destination['paging_id'])


class BSFilterDestinationBuilder(DestinationBuilder):

    destination = 'bsfilter'

    fields = [Field('filter_member_id', Int(), Required())]

    def to_model(self, destination):
        return BSFilterDestination(filter_member_id=destination['filter_member_id'])


class ServiceDestinationBuilder(DestinationBuilder):

    destination = 'service'

    fields = [Field('service', Unicode(), Required())]

    def parameters(self):
        services = [e.service for e in extension_dao.find_all_service_extensions()]
        return [{'name': 'service',
                 'values': services}]

    def to_model(self, destination):
        return ServiceDestination(service=destination['service'])


class CustomDestinationBuilder(DestinationBuilder):

    destination = 'custom'

    fields = [Field('exten', Unicode(), Required(), Regexp(EXTEN_REGEX))]

    def to_model(self, destination):
        return CustomDestination(exten=destination['exten'])


class ForwardDestinationBuilder(DestinationBuilder):

    destination = 'forward'

    fields = [Field('forward',
                    Unicode(),
                    Required(), Choice(['noanswer', 'busy', 'unconditional'])),
              Field('exten',
                    Unicode(),
                    Regexp(EXTEN_REGEX))
              ]

    def parameters(self):
        forwards = [e.forward for e in extension_dao.find_all_forward_extensions()]
        return [{'name': 'exten'},
                {'name': 'forward',
                 'values': forwards}]

    def to_model(self, destination):
        return ForwardDestination(forward=destination['forward'],
                                  exten=destination.get('exten'))


class TransferDestinationBuilder(DestinationBuilder):

    destination = 'transfer'

    fields = [Field('transfer',
                    Unicode(),
                    Required(), Choice(['blind', 'attended'])),
              ]

    def parameters(self):
        transfers = [e.transfer for e in feature_dao.find_all_transfer_extensions()]
        return [{'name': 'transfer',
                 'values': transfers}]

    def to_model(self, destination):
        return TransferDestination(transfer=destination['transfer'])


class ParkPositionDestinationBuilder(DestinationBuilder):

    destination = 'park_position'

    fields = [Field('position',
                    Int(),
                    Required())
              ]

    def to_model(self, destination):
        return ParkPositionDestination(position=destination['position'])


class ParkingDestinationBuilder(DestinationBuilder):

    destination = 'parking'

    fields = []

    def to_model(self, destination):
        return ParkingDestination()


class AgentDestinationBuilder(DestinationBuilder):

    destination = 'agent'

    fields = [Field('action',
                    Unicode(),
                    Required(), Choice(['login', 'logout', 'toggle'])),
              Field('agent_id', Int(), Required())]

    def parameters(self):
        actions = [e.action for e in extension_dao.find_all_agent_action_extensions()]
        return [{'name': 'agent_id'},
                {'name': 'action',
                 'values': actions}]

    def to_model(self, destination):
        return AgentDestination(action=destination['action'],
                                agent_id=destination['agent_id'])


class OnlineRecordingDestinationBuilder(DestinationBuilder):

    destination = 'onlinerec'

    fields = []

    def to_model(self, destination):
        return OnlineRecordingDestination()


class FuncKeyConverter(Converter):

    def description(self):
        description = self.builder.description()
        return json.dumps(description)


def build_destinations(exclude=None):
    exclude = exclude or []
    destinations = {'user': UserDestinationBuilder(),
                    'group': GroupDestinationBuilder(),
                    'queue': QueueDestinationBuilder(),
                    'conference': ConferenceDestinationBuilder(),
                    'paging': PagingDestinationBuilder(),
                    'service': ServiceDestinationBuilder(),
                    'custom': CustomDestinationBuilder(),
                    'forward': ForwardDestinationBuilder(),
                    'transfer': TransferDestinationBuilder(),
                    'park_position': ParkPositionDestinationBuilder(),
                    'parking': ParkingDestinationBuilder(),
                    'bsfilter': BSFilterDestinationBuilder(),
                    'agent': AgentDestinationBuilder(),
                    'onlinerec': OnlineRecordingDestinationBuilder(),
                    }

    for name in exclude:
        del destinations[name]

    return destinations


def build_funckey_converter(exclude=None):
    destinations = build_destinations(exclude)
    parser = JsonParser()
    funckey_validator = FuncKeyValidator(destinations)
    funckey_mapper = FuncKeyMapper(destinations)
    funckey_builder = FuncKeyBuilder(funckey_validator, destinations)
    serializer = ResourceSerializer({})
    return FuncKeyConverter(parser, funckey_mapper, serializer, funckey_builder)


def build_template_converter(funckey_converter):
    parser = JsonParser()

    template_validator = TemplateValidator(funckey_converter.builder.validator)
    template_mapper = TemplateMapper(funckey_converter.mapper)
    template_builder = TemplateBuilder(template_validator, funckey_converter.builder)
    serializer = ResourceSerializer({'func_key_templates': 'id'})

    converter = Converter(parser, template_mapper, serializer, template_builder)

    return converter


def build_association_converter(content_parser):
    document = content_parser.document(
        Field('user_id', Int()),
        Field('template_id', Int())
    )

    converter = Converter.association(document, UserTemplate,
                                      links={'users': 'user_id',
                                             'func_key_templates': 'template_id'})

    return converter
