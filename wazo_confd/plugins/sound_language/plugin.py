# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.ari import Client as ARIClient

from .resource import SoundLanguageList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        ari_client = ARIClient(**config['ari'])
        service = build_service(ari_client)

        api.add_resource(
            SoundLanguageList, '/sounds/languages', resource_class_args=(service,)
        )
