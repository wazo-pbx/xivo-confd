# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class IncallScheduleItem(ConfdResource):

    def __init__(self, service, incall_dao, schedule_dao):
        super(IncallScheduleItem, self).__init__()
        self.service = service
        self.incall_dao = incall_dao
        self.schedule_dao = schedule_dao

    @required_acl('confd.incalls.{incall_id}.schedules.{schedule_id}.delete')
    def delete(self, incall_id, schedule_id):
        incall = self.incall_dao.get(incall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.dissociate(incall, schedule)
        return '', 204

    @required_acl('confd.incalls.{incall_id}.schedules.{schedule_id}.update')
    def put(self, incall_id, schedule_id):
        incall = self.incall_dao.get(incall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.associate(incall, schedule)
        return '', 204