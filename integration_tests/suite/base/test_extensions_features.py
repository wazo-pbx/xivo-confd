# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    is_not,
)

from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from . import confd

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.features.get
    for check in s.search_error_checks(url):
        yield check


def test_get_errors():
    url = confd.extensions.features(FAKE_ID).get
    yield s.check_resource_not_found, url, 'Extension'


@fixtures.extension_feature()
def test_put_errors(extension):
    url = confd.extensions.features(FAKE_ID).put
    yield s.check_resource_not_found, url, 'Extension'

    url = confd.extensions.features(extension['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'exten', None
    yield s.check_bogus_field_returns_error, url, 'exten', True
    yield s.check_bogus_field_returns_error, url, 'exten', 'ABC123'
    yield s.check_bogus_field_returns_error, url, 'exten', 'XXXX'
    yield s.check_bogus_field_returns_error, url, 'exten', {}
    yield s.check_bogus_field_returns_error, url, 'exten', []


def test_create_unimplemented():
    response = confd.extensions.features.post()
    response.assert_status(405)


@fixtures.extension_feature()
def test_delete_unimplemented(extension):
    response = confd.extensions.features(extension['id']).delete()
    response.assert_status(405)


@fixtures.extension_feature(exten='4999')
@fixtures.extension_feature(exten='9999')
def test_search(extension, hidden):
    url = confd.extensions.features
    searches = {'exten': '499'}

    for field, term in searches.items():
        yield check_search, url, extension, hidden, field, term


def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)

    expected_extension = has_item(has_entry(field, extension[field]))
    hidden_extension = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)

    response = url.get(**{field: extension[field]})

    expected_extension = has_item(has_entry('id', extension['id']))
    hidden_extension = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)


@fixtures.extension_feature(exten='9998')
@fixtures.extension_feature(exten='9999')
def test_sorting_offset_limit(extension1, extension2):
    url = confd.extensions.features.get
    yield s.check_sorting, url, extension1, extension2, 'exten', '999'

    yield s.check_offset, url, extension1, extension2, 'exten', '999'
    yield s.check_offset_legacy, url, extension1, extension2, 'exten', '999'

    yield s.check_limit, url, extension1, extension2, 'exten', '999'


@fixtures.extension_feature()
def test_get(extension):
    response = confd.extensions.features(extension['id']).get()
    assert_that(response.item, has_entries(
        exten=extension['exten'],
        context=extension['context'],
        feature=extension['feature'],
        commented=False,
    ))


@fixtures.extension_feature()
def test_edit_minimal_parameters(extension):
    response = confd.extensions.features(extension['id']).put()
    response.assert_updated()


@fixtures.extension_feature()
def test_edit_all_parameters(extension):
    parameters = {'exten': '*911',
                  'commented': True}

    response = confd.extensions.features(extension['id']).put(**parameters)
    response.assert_updated()

    response = confd.extensions.features(extension['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.extension_feature(exten='1234')
@fixtures.extension_feature()
def test_edit_with_same_extension(extension1, extension2):
    response = confd.extensions.features(extension2['id']).put(exten=extension1['exten'])
    response.assert_match(400, e.resource_exists('Extension'))


@fixtures.extension_feature()
def test_bus_events(extension):
    yield s.check_bus_event, 'config.extension_feature.edited', confd.extensions.features(extension['id']).put
