# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import MohItem, MohList, MohFileItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(MohList, '/moh', resource_class_args=(service,))

        api.add_resource(
            MohItem, '/moh/<uuid>', endpoint='moh', resource_class_args=(service,)
        )

        api.add_resource(
            MohFileItem,
            '/moh/<uuid>/files/<filename:filename>',
            endpoint='mohfileitem',
            resource_class_args=(service,),
        )
