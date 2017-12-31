# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import OutcallItem, OutcallList
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core['api']
        service = build_service()

        api.add_resource(
            OutcallList,
            '/outcalls',
            resource_class_args=(service,)
        )

        api.add_resource(
            OutcallItem,
            '/outcalls/<int:id>',
            endpoint='outcalls',
            resource_class_args=(service,)
        )
