# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(line_id, endpoint_id, check=True):
    response = confd.lines(line_id).endpoints.sccp(endpoint_id).put()
    if check:
        response.assert_ok()


def dissociate(line_id, endpoint_id, check=True):
    response = confd.lines(line_id).endpoints.sccp(endpoint_id).delete()
    if check:
        response.assert_ok()
