# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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
                      contains_inanyorder,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


def test_get_errors():
    fake_incall = confd.incalls(999999).get
    yield s.check_resource_not_found, fake_incall, 'Incall'


def test_delete_errors():
    fake_incall = confd.incalls(999999).delete
    yield s.check_resource_not_found, fake_incall, 'Incall'


def test_post_errors():
    url = confd.incalls.post
    for check in error_checks(url):
        yield check


@fixtures.incall()
def test_put_errors(incall):
    url = confd.incalls(incall['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'destination', {}
    yield s.check_bogus_field_returns_error, url, 'destination', None

    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'destination', destination


@fixtures.incall(description='search')
@fixtures.incall(description='hidden')
def test_search(incall, hidden):
    url = confd.incalls
    searches = {'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, incall, hidden, field, term


def check_search(url, incall, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, incall[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: incall[field]})

    expected = has_item(has_entry('id', incall['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.incall(description='sort1')
@fixtures.incall(description='sort2')
def test_sorting_offset_limit(incall1, incall2):
    url = confd.incalls.get
    yield s.check_sorting, url, incall1, incall2, 'description', 'sort'

    yield s.check_offset, url, incall1, incall2, 'description', 'sort'
    yield s.check_offset_legacy, url, incall1, incall2, 'description', 'sort'

    yield s.check_limit, url, incall1, incall2, 'description', 'sort'


@fixtures.incall()
def test_get(incall):
    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(id=incall['id'],
                                           preprocess_subroutine=incall['preprocess_subroutine'],
                                           description=incall['description'],
                                           caller_id_mode=incall['caller_id_mode'],
                                           caller_id_name=incall['caller_id_name'],
                                           destination=incall['destination'],
                                           extensions=empty()))


def test_create_minimal_parameters():
    response = confd.incalls.post(destination={'type': 'none'})
    response.assert_created('incalls')

    assert_that(response.item, has_entries(id=not_(empty())))


def test_create_all_parameters():
    response = confd.incalls.post(preprocess_subroutine='default',
                                  description='description',
                                  caller_id_mode='prepend',
                                  caller_id_name='name_',
                                  destination={'type': 'none'})
    response.assert_created('incalls')

    assert_that(response.item, has_entries(preprocess_subroutine='default',
                                           description='description',
                                           caller_id_mode='prepend',
                                           caller_id_name='name_',
                                           destination={'type': 'none'}))


@fixtures.incall(destination={'type': 'hangup'})
def test_edit_minimal_parameters(incall):
    parameters = {'destination': {'type': 'none'}}

    response = confd.incalls(incall['id']).put(**parameters)
    response.assert_updated()


@fixtures.incall()
def test_edit_all_parameters(incall):
    parameters = {'destination': {'type': 'none'},
                  'preprocess_subroutine': 'default',
                  'caller_id_mode': 'append',
                  'caller_id_name': '_name',
                  'description': 'description'}

    response = confd.incalls(incall['id']).put(**parameters)
    response.assert_updated()

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.incall()
@fixtures.meetme()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
def test_valid_destinations(incall, meetme, ivr, group, outcall, queue, user, voicemail, conference):
    for destination in valid_destinations(meetme, ivr, group, outcall, queue, user, voicemail, conference):
        yield create_incall_with_destination, destination
        yield update_incall_with_destination, incall['id'], destination


def create_incall_with_destination(destination):
    response = confd.incalls.post(destination=destination)
    response.assert_created('incalls')
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


def update_incall_with_destination(incall_id, destination):
    response = confd.incalls(incall_id).put(destination=destination)
    response.assert_updated()
    response = confd.incalls(incall_id).get()
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


@fixtures.incall()
def test_delete(incall):
    response = confd.incalls(incall['id']).delete()
    response.assert_deleted()
    response = confd.incalls(incall['id']).get()
    response.assert_match(404, e.not_found(resource='Incall'))


@fixtures.group()
def test_get_group_destination_relation(group):
    incall = confd.incalls.post(destination={'type': 'group',
                                             'group_id': group['id']}).item

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(
        destination=has_entries(group_id=group['id'],
                                group_name=group['name'])
    ))


@fixtures.user()
def test_get_user_destination_relation(user):
    incall = confd.incalls.post(destination={'type': 'user',
                                             'user_id': user['id']}).item

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(
        destination=has_entries(user_id=user['id'],
                                user_firstname=user['firstname'],
                                user_lastname=user['lastname'])
    ))


@fixtures.ivr()
def test_get_ivr_destination_relation(ivr):
    incall = confd.incalls.post(destination={'type': 'ivr',
                                             'ivr_id': ivr['id']}).item

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(
        destination=has_entries(ivr_id=ivr['id'],
                                ivr_name=ivr['name'])
    ))


@fixtures.voicemail()
def test_get_voicemail_destination_relation(voicemail):
    incall = confd.incalls.post(destination={'type': 'voicemail',
                                             'voicemail_id': voicemail['id']}).item

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(
        destination=has_entries(voicemail_id=voicemail['id'],
                                voicemail_name=voicemail['name'])
    ))


@fixtures.group()
def test_get_incalls_relation_when_group_destination(group):
    incall1 = confd.incalls.post(destination={'type': 'group',
                                              'group_id': group['id']}).item
    incall2 = confd.incalls.post(destination={'type': 'group',
                                              'group_id': group['id']}).item

    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(
        incalls=contains_inanyorder(has_entries(id=incall1['id'],
                                                extensions=incall1['extensions']),
                                    has_entries(id=incall2['id'],
                                                extensions=incall2['extensions']))
    ))


@fixtures.user()
def test_get_incalls_relation_when_user_destination(user):
    incall1 = confd.incalls.post(destination={'type': 'user',
                                              'user_id': user['id']}).item
    incall2 = confd.incalls.post(destination={'type': 'user',
                                              'user_id': user['id']}).item

    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(
        incalls=contains_inanyorder(has_entries(id=incall1['id'],
                                                extensions=incall1['extensions']),
                                    has_entries(id=incall2['id'],
                                                extensions=incall2['extensions']))
    ))


@fixtures.ivr()
def test_get_incalls_relation_when_ivr_destination(ivr):
    incall1 = confd.incalls.post(destination={'type': 'ivr',
                                              'ivr_id': ivr['id']}).item
    incall2 = confd.incalls.post(destination={'type': 'ivr',
                                              'ivr_id': ivr['id']}).item

    response = confd.ivr(ivr['id']).get()
    assert_that(response.item, has_entries(
        incalls=contains_inanyorder(has_entries(id=incall1['id'],
                                                extensions=incall1['extensions']),
                                    has_entries(id=incall2['id'],
                                                extensions=incall2['extensions']))
    ))
