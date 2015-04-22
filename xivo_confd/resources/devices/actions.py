# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import Blueprint
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.device import notifier as device_notifier
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Dict
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain
from xivo_confd.resources.devices.service import DeviceService, LineDeviceAssociationService, DeviceValidator, SearchEngine
from xivo_confd.resources.devices.dao import ProvdDeviceDao, DeviceDao


class DeviceResource(CRUDResource):

    def __init__(self, device_service, association_service, converter):
        super(DeviceResource, self).__init__(device_service, converter)
        self.association_service = association_service

    def synchronize(self, device_id):
        device = self.service.get(device_id)
        self.service.synchronize(device)
        return ('', 204)

    def autoprov(self, device_id):
        device = self.service.get(device_id)
        self.service.reset_autoprov(device)
        return ('', 204)

    def associate_line(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.association_service.get_line(line_id)
        self.association_service.associate(line, device)
        return ('', 204)

    def remove_line(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.association_service.get_line(line_id)
        self.association_service.dissociate(line, device)
        return ('', 204)


def load(core_rest_api):
    document = core_rest_api.content_parser.document(
        Field('id', Unicode()),
        Field('ip', Unicode()),
        Field('mac', Unicode()),
        Field('sn', Unicode()),
        Field('plugin', Unicode()),
        Field('vendor', Unicode()),
        Field('model', Unicode()),
        Field('version', Unicode()),
        Field('description', Unicode()),
        Field('status', Unicode()),
        Field('template_id', Unicode()),
        Field('options', Dict())
    )

    blueprint = Blueprint('devices', __name__, url_prefix='/%s/devices' % config.API_VERSION)

    converter = Converter.resource(document, Device)

    provd_client = core_rest_api.provd_client()

    provd_dao = ProvdDeviceDao(provd_client.device_manager(),
                               provd_client.config_manager())

    device_dao = DeviceDao(provd_client, provd_dao)

    search_engine = SearchEngine(provd_dao)

    device_validator = DeviceValidator(device_dao, line_dao)

    association_service = LineDeviceAssociationService(line_dao,
                                                       extension_dao,
                                                       line_extension_dao,
                                                       device_dao)

    device_service = DeviceService(device_dao, device_validator, device_notifier, search_engine, line_dao)

    resource = DeviceResource(device_service, association_service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.search().decorate(resource.search)
    chain.get('/<resource_id>').decorate(resource.get)
    chain.create().decorate(resource.create)
    chain.edit('/<resource_id>').decorate(resource.edit)
    chain.delete('/<resource_id>').decorate(resource.delete)

    (chain
     .get('/<device_id>/synchronize')
     .decorate(resource.synchronize))

    (chain
     .get('/<device_id>/autoprov')
     .decorate(resource.autoprov))

    (chain
     .get('/<device_id>/associate_line/<int:line_id>')
     .limit_localhost()
     .decorate(resource.associate_line))

    (chain
     .get('/<device_id>/remove_line/<int:line_id>')
     .limit_localhost()
     .decorate(resource.remove_line))

    core_rest_api.register(blueprint)
