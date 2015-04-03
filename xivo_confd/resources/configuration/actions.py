# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from flask import request
from xivo_dao.data_handler.configuration import dao

from xivo_confd import config
from xivo_confd.helpers.mooltiparse import Field, Boolean
from xivo_confd.helpers.resource import DecoratorChain
from xivo_confd.helpers.converter import Converter


class LiveReload(object):

    def __init__(self, enabled):
        self.enabled = enabled


class LiveReloadService(object):

    def __init__(self, dao):
        self.dao = dao

    def get(self):
        return LiveReload(self.dao.is_live_reload_enabled())

    def edit(self, live_reload):
        data = {'enabled': live_reload.enabled}
        self.dao.set_live_reload_status(data)


class LiveReloadResource(object):

    def __init__(self, service, converter):
        self.service = service
        self.converter = converter

    def get(self):
        resource = self.service.get()
        response = self.converter.encode(resource)
        return (response, 200, {'Content-Type': 'application/json'})

    def edit(self):
        resource = self.service.get()
        self.converter.update(request, resource)
        self.service.edit(resource)
        return ('', 204)


def load(core_rest_api):
    blueprint = Blueprint('configuration',
                          __name__,
                          url_prefix='/%s/configuration' % config.API_VERSION)
    document = core_rest_api.content_parser.document(Field('enabled', Boolean()))
    converter = Converter.for_request(document, LiveReload)

    service = LiveReloadService(dao)
    resource = LiveReloadResource(service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.start().get('/live_reload').decorate(resource.get)
    chain.start().edit('/live_reload').decorate(resource.edit)

    core_rest_api.register(blueprint)
