# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import string
import random
from functools import wraps
from hamcrest import (assert_that,
                      contains,
                      has_entries)

from ..helpers import scenarios as s
from ..helpers import fixtures
from ..helpers import associations as a
from . import confd


FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def extension(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        exten = ''.join(random.choice(string.digits) for _ in range(10))

        extension = {'exten': exten, 'context': 'default'}
        new_args = list(args) + [extension]
        return func(*new_args, **kwargs)
    return decorated


@fixtures.group()
@extension
def test_associate_errors(group, extension):
    response = confd.groups(FAKE_ID).members.extensions.put(extensions=[extension])
    response.assert_status(404)

    url = confd.groups(group['id']).members.extensions.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'extensions', 123
    yield s.check_bogus_field_returns_error, url, 'extensions', None
    yield s.check_bogus_field_returns_error, url, 'extensions', True
    yield s.check_bogus_field_returns_error, url, 'extensions', 'string'
    yield s.check_bogus_field_returns_error, url, 'extensions', [123]
    yield s.check_bogus_field_returns_error, url, 'extensions', [None]
    yield s.check_bogus_field_returns_error, url, 'extensions', ['string']
    yield s.check_bogus_field_returns_error, url, 'extensions', [{}]

    regex = r'extensions.*priority'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'priority': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'priority': 'string'}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'priority': []}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'priority': {}}], regex

    regex = r'extensions.*exten'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'exten': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'exten': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'exten': []}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'exten': {}}], regex

    regex = r'extensions.*context'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'context': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'context': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'context': []}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'extensions', [{'context': {}}], regex


@fixtures.group()
@extension
def test_associate(group, extension):
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension])
    response.assert_updated()


@fixtures.group()
@extension
@extension
@extension
def test_associate_multiple_with_priority(group, extension1, extension2, extension3):
    extension1['priority'], extension2['priority'], extension3['priority'] = 4, 1, 2
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension1, extension2, extension3])
    response.assert_updated()

    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(
        members=has_entries(extensions=contains(has_entries(exten=extension2['exten'],
                                                            context=extension2['context'],
                                                            priority=1),
                                                has_entries(exten=extension3['exten'],
                                                            context=extension3['context'],
                                                            priority=2),
                                                has_entries(exten=extension1['exten'],
                                                            context=extension1['context'],
                                                            priority=4)))
    ))


@fixtures.group()
@extension
def test_associate_same_extension(group, extension):
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension, extension])
    response.assert_status(400)


@fixtures.group()
@extension
@extension
def test_get_extensions_associated_to_group(group, extension1, extension2):
    with a.group_member_extension(group, extension2, extension1):
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            members=has_entries(extensions=contains(has_entries(exten=extension2['exten'],
                                                                context=extension2['context']),
                                                    has_entries(exten=extension1['exten'],
                                                                context=extension1['context'])))
        ))


@fixtures.group()
@extension
@extension
def test_dissociate(group, extension1, extension2):
    with a.group_member_extension(group, extension1, extension2):
        response = confd.groups(group['id']).members.extensions.put(extensions=[])
        response.assert_updated()


@fixtures.group()
@extension
@extension
def test_delete_group_when_group_and_extension_associated(group, extension1, extension2):
    with a.group_member_extension(group, extension1, extension2, check=False):
        confd.groups(group['id']).delete().assert_deleted()

        deleted_group = confd.groups(group['id']).get
        yield s.check_resource_not_found, deleted_group, 'Group'


@fixtures.group()
@extension
def test_bus_events(group, extension):
    url = confd.groups(group['id']).members.extensions.put
    body = {'extensions': [extension]}
    yield s.check_bus_event, 'config.groups.members.extensions.updated', url, body