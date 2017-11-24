# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_switchboard(**parameters):
    parameters.setdefault('name', generate_name())
    return add_switchboard(**parameters)


def add_switchboard(**parameters):
    response = confd.switchboards.post(parameters)
    return response.item


def delete_switchboard(switchboard_uuid, check=False):
    response = confd.switchboards(switchboard_uuid).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.switchboards.get()
    forbidden_names = set(d['name'] for d in response.items)
    return _random_name(forbidden_names)


def _random_name(forbidden_names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in forbidden_names:
        return _random_name(forbidden_names)
    return name