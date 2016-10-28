# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s
from test_api.helpers.destination import invalid_destinations, valid_destinations

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


def test_get_errors():
    fake_ivr = confd.ivr(999999).get
    yield s.check_resource_not_found, fake_ivr, 'IVR'


def test_delete_errors():
    fake_ivr = confd.ivr(999999).delete
    yield s.check_resource_not_found, fake_ivr, 'IVR'


def test_post_errors():
    url = confd.ivr.post
    for check in error_checks(url):
        yield check


@fixtures.ivr()
def test_put_errors(ivr):
    url = confd.ivr(ivr['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'abort_sound', True
    yield s.check_bogus_field_returns_error, url, 'abort_sound', 123
    yield s.check_bogus_field_returns_error, url, 'abort_sound', s.random_string(256)
    yield s.check_bogus_field_returns_error, url, 'abort_sound', []
    yield s.check_bogus_field_returns_error, url, 'abort_sound', {}
    yield s.check_bogus_field_returns_error, url, 'greeting_sound', True
    yield s.check_bogus_field_returns_error, url, 'greeting_sound', 123
    yield s.check_bogus_field_returns_error, url, 'greeting_sound', s.random_string(256)
    yield s.check_bogus_field_returns_error, url, 'greeting_sound', []
    yield s.check_bogus_field_returns_error, url, 'greeting_sound', {}
    yield s.check_bogus_field_returns_error, url, 'invalid_sound', True
    yield s.check_bogus_field_returns_error, url, 'invalid_sound', 123
    yield s.check_bogus_field_returns_error, url, 'invalid_sound', s.random_string(256)
    yield s.check_bogus_field_returns_error, url, 'invalid_sound', []
    yield s.check_bogus_field_returns_error, url, 'invalid_sound', {}
    yield s.check_bogus_field_returns_error, url, 'menu_sound', True
    yield s.check_bogus_field_returns_error, url, 'menu_sound', 123
    yield s.check_bogus_field_returns_error, url, 'menu_sound', s.random_string(256)
    yield s.check_bogus_field_returns_error, url, 'menu_sound', []
    yield s.check_bogus_field_returns_error, url, 'menu_sound', {}
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'max_tries', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'max_tries', 0
    yield s.check_bogus_field_returns_error, url, 'max_tries', []
    yield s.check_bogus_field_returns_error, url, 'max_tries', {}
    yield s.check_bogus_field_returns_error, url, 'timeout', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'timeout', -1
    yield s.check_bogus_field_returns_error, url, 'timeout', []
    yield s.check_bogus_field_returns_error, url, 'timeout', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'choices', True
    yield s.check_bogus_field_returns_error, url, 'choices', 123
    yield s.check_bogus_field_returns_error, url, 'choices', {}
    yield s.check_bogus_field_returns_error, url, 'choices', ['invalid']
    yield s.check_bogus_field_returns_error, url, 'choices', [{'destination': {'type': 'none'}}]
    yield s.check_bogus_field_returns_error, url, 'choices', [{'exten': '1'}]
    yield s.check_bogus_field_returns_error, url, 'choices', [{'exten': 123, 'destination': {'type': 'none'}}]
    yield s.check_bogus_field_returns_error, url, 'choices', [{'exten': '1', 'destination': 'invalid'}]

    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'invalid_destination', destination
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'timeout_destination', destination
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'abort_destination', destination


@fixtures.ivr(description='search')
@fixtures.ivr(description='hidden')
def test_search(ivr, hidden):
    url = confd.ivr
    searches = {'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, ivr, hidden, field, term


def check_search(url, ivr, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, ivr[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: ivr[field]})

    expected = has_item(has_entry('id', ivr['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.ivr(description='sort1')
@fixtures.ivr(description='sort2')
def test_sorting(ivr1, ivr2):
    yield check_sorting, ivr1, ivr2, 'description', 'sort'


def check_sorting(ivr1, ivr2, field, search):
    response = confd.ivr.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=ivr1['id']),
                                         has_entries(id=ivr2['id'])))

    response = confd.ivr.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=ivr2['id']),
                                         has_entries(id=ivr1['id'])))


@fixtures.ivr()
def test_get(ivr):
    response = confd.ivr(ivr['id']).get()
    assert_that(response.item, has_entries(id=ivr['id'],
                                           name=ivr['name'],
                                           description=ivr['description'],
                                           menu_sound=ivr['menu_sound'],
                                           invalid_sound=ivr['invalid_sound'],
                                           abort_sound=ivr['abort_sound'],
                                           timeout=ivr['timeout'],
                                           max_tries=ivr['max_tries'],
                                           invalid_destination=ivr['invalid_destination'],
                                           timeout_destination=ivr['timeout_destination'],
                                           abort_destination=ivr['abort_destination'],
                                           choices=empty()))


def test_create_minimal_parameters():
    response = confd.ivr.post(name='ivr1', menu_sound='menu')
    response.assert_created('ivr')

    assert_that(response.item, has_entries(id=not_(empty())))


@fixtures.user
@fixtures.user
@fixtures.user
def test_create_all_parameters(user1, user2, user3):
    response = confd.ivr.post(name='ivr1',
                              greeting_sound='greeting',
                              menu_sound='menu',
                              invalid_sound='invalid',
                              abort_sound='abort',
                              timeout=4,
                              max_tries=2,
                              description='description',
                              invalid_destination={'type': 'user', 'user_id': user1['id']},
                              timeout_destination={'type': 'user', 'user_id': user2['id']},
                              abort_destination={'type': 'user', 'user_id': user3['id']},
                              choices=[{'exten': '1', 'destination': {'type': 'none'}}])
    response.assert_created('ivr')

    assert_that(response.item, has_entries(name='ivr1',
                                           greeting_sound='greeting',
                                           menu_sound='menu',
                                           invalid_sound='invalid',
                                           abort_sound='abort',
                                           timeout=4,
                                           max_tries=2,
                                           description='description',
                                           invalid_destination={'type': 'user', 'user_id': user1['id']},
                                           timeout_destination={'type': 'user', 'user_id': user2['id']},
                                           abort_destination={'type': 'user', 'user_id': user3['id']},
                                           choices=[{'exten': '1', 'destination': {'type': 'none'}}]))


@fixtures.ivr(name='ivr1', menu_sound='menu')
def test_edit_minimal_parameters(ivr):
    parameters = {'name': 'ivr2', 'menu_sound': 'menu2'}

    response = confd.ivr(ivr['id']).put(**parameters)
    response.assert_updated()


@fixtures.ivr()
def test_edit_all_parameters(ivr):
    parameters = {
        'name': 'ivr1337',
        'greeting_sound': 'greeting1337',
        'menu_sound': 'menu1337',
        'invalid_sound': 'invalid1337',
        'abort_sound': 'abort1337',
        'timeout': 1337,
        'max_tries': 42,
        'description': 'leet',
        'invalid_destination': {'type': 'none'},
        'timeout_destination': {'type': 'none'},
        'abort_destination': {'type': 'none'},
        'choices': [{'exten': '0', 'destination': {'type': 'none'}}],
    }

    response = confd.ivr(ivr['id']).put(**parameters)
    response.assert_updated()

    response = confd.ivr(ivr['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.ivr()
@fixtures.conference()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.user()
@fixtures.voicemail()
def test_valid_destinations(ivr, conference, dest_ivr, group, outcall, queue, user, voicemail):
    for destination in valid_destinations(conference, dest_ivr, group, outcall, queue, user, voicemail):
        yield create_ivr_with_destination, destination
        yield update_ivr_with_destination, ivr['id'], destination


def create_ivr_with_destination(destination):
    response = confd.ivr.post(name='ivr', menu_sound='beep', abort_destination=destination)
    response.assert_created('ivr')
    assert_that(response.item, has_entries(abort_destination=has_entries(**destination)))


def update_ivr_with_destination(ivr_id, destination):
    response = confd.ivr(ivr_id).put(abort_destination=destination)
    response.assert_updated()
    response = confd.ivr(ivr_id).get()
    assert_that(response.item, has_entries(abort_destination=has_entries(**destination)))


@fixtures.ivr()
def test_delete(ivr):
    response = confd.ivr(ivr['id']).delete()
    response.assert_deleted()
    response = confd.ivr(ivr['id']).get()
    response.assert_match(404, e.not_found(resource='IVR'))


@fixtures.ivr()
def test_bus_events(ivr):
    yield s.check_bus_event, 'config.ivr.created', confd.ivr.post, {'name': 'a', 'menu_sound': 'hello'}
    yield s.check_bus_event, 'config.ivr.edited', confd.ivr(ivr['id']).put
    yield s.check_bus_event, 'config.ivr.deleted', confd.ivr(ivr['id']).delete