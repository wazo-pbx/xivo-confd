# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import IvrItem, IvrList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(IvrList, '/ivr', resource_class_args=(service,))

        api.add_resource(
            IvrItem, '/ivr/<int:id>', endpoint='ivr', resource_class_args=(service,)
        )
