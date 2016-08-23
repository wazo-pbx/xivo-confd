# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.resources.user import dao as user_dao

from xivo_confd import api
from xivo_confd.plugins.user_agent.service import build_service
from xivo_confd.plugins.user_agent.resource import UserAgentList, UserAgentItem


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserAgentItem,
                         '/users/<int:user_id>/agents/<int:agent_id>',
                         '/users/<uuid:user_id>/agents/<int:agent_id>',
                         endpoint='user_agents',
                         resource_class_args=(service, user_dao)
                         )
        api.add_resource(UserAgentList,
                         '/users/<int:user_id>/agents',
                         '/users/<uuid:user_id>/agents',
                         resource_class_args=(service, user_dao)
                         )
