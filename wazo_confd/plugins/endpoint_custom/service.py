# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_custom import dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


def build_service():
    return CRUDService(dao, build_validator(), build_notifier())
