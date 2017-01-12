# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from flask import request

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import UsersUUIDSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError


class SwitchboardMemberUserItem(ConfdResource):

    schema = UsersUUIDSchema

    def __init__(self, service, switchboard_dao, user_dao):
        super(SwitchboardMemberUserItem, self).__init__()
        self.service = service
        self.switchboard_dao = switchboard_dao
        self.user_dao = user_dao

    @required_acl('confd.switchboards.{switchboard_id}.members.users.update')
    def put(self, switchboard_id):
        switchboard = self.switchboard_dao.get(switchboard_id)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_member_users(switchboard, users)

        return '', 204