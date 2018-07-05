# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.agent import dao as agent_dao

from xivo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('number',
                        lambda number: agent_dao.find_by(number=number),
                        'Agent')
        ],
        edit=[
            Optional('number',
                     UniqueFieldChanged('number', agent_dao, 'Agent'))
        ],
    )