# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import IAXCallNumberLimitsList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            IAXCallNumberLimitsList,
            '/asterisk/iax/callnumberlimits',
            resource_class_args=(service,),
        )
