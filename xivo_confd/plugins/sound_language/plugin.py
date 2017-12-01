# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .ari import Client as ARIClient
from .resource import SoundLanguageList
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        ari_client = ARIClient(**core.config['ari'])
        service = build_service(ari_client)

        api.add_resource(
            SoundLanguageList,
            '/sounds/languages',
            resource_class_args=(service,)
        )