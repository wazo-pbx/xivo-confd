# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from .resource import IncallScheduleItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            IncallScheduleItem,
            '/incalls/<int:incall_id>/schedules/<int:schedule_id>',
            endpoint='incall_schedules',
            resource_class_args=(service, incall_dao, schedule_dao),
        )
