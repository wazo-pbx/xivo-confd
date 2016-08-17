# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors

from flask import url_for, request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class LineExtensionSchema(BaseSchema):
    line_id = fields.Integer()
    extension_id = fields.Integer(required=True)
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('extensions',
                          field='extension_id',
                          target='id'))


class LineExtensionResource(ConfdResource):

    def __init__(self, service, line_dao, extension_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao


class LineExtensionList(LineExtensionResource):

    schema = LineExtensionSchema()

    @required_acl('confd.lines.{line_id}.extensions.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        items = self.service.list(line.id)
        return {'total': len(items),
                'items': self.schema.dump(items, many=True).data}

    @required_acl('confd.lines.{line_id}.extensions.create')
    def post(self, line_id):
        return self.post_deprecated(line_id)

    def post_deprecated(self, line_id):
        line = self.line_dao.get(line_id)
        extension = self.get_extension_or_fail()
        line_extension = self.service.associate(line, extension)
        headers = self.build_headers(line_extension)
        return self.schema.dump(line_extension).data, 201, headers

    def build_headers(self, model):
        url = url_for('line_extensions',
                      extension_id=model.extension_id,
                      line_id=model.line_id,
                      _external=True)
        return {'Location': url}

    def get_extension_or_fail(self):
        form = self.schema.load(request.get_json()).data
        try:
            return self.extension_dao.get(form['extension_id'])
        except NotFoundError:
            raise errors.param_not_found('extension_id', 'Extension')


class LineExtensionItem(LineExtensionResource):

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.delete')
    def delete(self, line_id, extension_id):
        line = self.line_dao.get(line_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(line, extension)
        return '', 204

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.update')
    def put(self, line_id, extension_id):
        line = self.line_dao.get(line_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(line, extension)
        return '', 204
