# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length, NoneOf, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

from .storage import RESERVED_DIRECTORIES

ASTERISK_CATEGORY = 'system'
RESERVED_DIRECTORIES_ERROR = "The following name are reserved for internal usage: {}".format(RESERVED_DIRECTORIES)
DIRECTORY_REGEX = r'^[a-zA-Z0-9]{1}[-_.a-zA-Z0-9]+$'


class SoundFormatSchema(BaseSchema):
    format = fields.String()
    language = fields.String()
    text = fields.String()


class SoundFileSchema(BaseSchema):
    name = fields.String()
    formats = fields.Nested(SoundFormatSchema, many=True)


class SoundSchema(BaseSchema):
    name = fields.String(validate=[Length(max=149, min=1),
                                   NoneOf([ASTERISK_CATEGORY]),
                                   NoneOf(RESERVED_DIRECTORIES, error=RESERVED_DIRECTORIES_ERROR),
                                   Regexp(DIRECTORY_REGEX)],
                         required=True)
    files = fields.Nested(SoundFileSchema, many=True, dump_only=True)

    links = ListLink(Link('sounds', field='name'))
