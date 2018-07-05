# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.call_pickup import dao as call_pickup_dao

from xivo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


def build_service():
    return CRUDService(call_pickup_dao,
                       build_validator(),
                       build_notifier())