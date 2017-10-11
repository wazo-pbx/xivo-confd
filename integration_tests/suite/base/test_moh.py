# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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
from xivo_test_helpers.confd import new_client


from hamcrest import (assert_that,
                      contains,
                      empty,
                      equal_to,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not)

NOT_FOUND_UUID = 'uuid-not-found'


def test_get_errors():
    fake_moh = confd.moh(NOT_FOUND_UUID).get
    yield s.check_resource_not_found, fake_moh, 'MOH'


def test_delete_errors():
    fake_moh = confd.moh(NOT_FOUND_UUID).delete
    yield s.check_resource_not_found, fake_moh, 'MOH'


def test_post_errors():
    url = confd.moh.post
    for check in error_checks(url):
        yield check

    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(21)
    yield s.check_bogus_field_returns_error, url, 'name', 'general'
    yield s.check_bogus_field_returns_error, url, 'name', '.foo'
    yield s.check_bogus_field_returns_error, url, 'name', 'foo\nbar'
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.moh()
def test_put_errors(moh):
    url = confd.moh(moh['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', 1234
    yield s.check_bogus_field_returns_error, url, 'label', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'mode', True
    yield s.check_bogus_field_returns_error, url, 'mode', 1234
    yield s.check_bogus_field_returns_error, url, 'mode', 'hello'
    yield s.check_bogus_field_returns_error, url, 'mode', []
    yield s.check_bogus_field_returns_error, url, 'mode', {}
    yield s.check_bogus_field_returns_error, url, 'application', True
    yield s.check_bogus_field_returns_error, url, 'application', 1234
    yield s.check_bogus_field_returns_error, url, 'application', s.random_string(257)
    yield s.check_bogus_field_returns_error, url, 'application', []
    yield s.check_bogus_field_returns_error, url, 'application', {}
    yield s.check_bogus_field_returns_error, url, 'sort', True
    yield s.check_bogus_field_returns_error, url, 'sort', 1234
    yield s.check_bogus_field_returns_error, url, 'sort', 'hello'
    yield s.check_bogus_field_returns_error, url, 'sort', []
    yield s.check_bogus_field_returns_error, url, 'sort', {}


@fixtures.moh(name='unique')
def unique_error_checks(url, moh):
    yield s.check_bogus_field_returns_error, url, 'name', moh['name'], {'mode': 'files'}


@fixtures.moh(name='visible', label='hello')
@fixtures.moh(name='hidden', label='hidden')
def test_search(visible, hidden):
    url = confd.moh
    searches = {'name': 'visible',
                'label': 'hello'}

    for field, term in searches.items():
        yield check_search, url, visible, hidden, field, term


def check_search(url, visible, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, visible[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: visible[field]})

    expected = has_item(has_entry('uuid', visible['uuid']))
    not_expected = has_item(has_entry('uuid', hidden['uuid']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.moh(name='sort1')
@fixtures.moh(name='sort2')
def test_sorting_offset_limit(moh1, moh2):
    url = confd.moh.get
    yield s.check_sorting, url, moh1, moh2, 'name', 'sort', 'uuid'

    yield s.check_offset, url, moh1, moh2, 'name', 'sort', 'uuid'
    yield s.check_offset_legacy, url, moh1, moh2, 'name', 'sort', 'uuid'

    yield s.check_limit, url, moh1, moh2, 'name', 'sort', 'uuid'


@fixtures.moh()
def test_get(moh):
    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(uuid=moh['uuid'],
                                           name=moh['name'],
                                           label=moh['label'],
                                           mode=moh['mode'],
                                           application=moh['application'],
                                           sort=moh['sort'],
                                           files=empty()))


def test_create_minimal_parameters():
    response = confd.moh.post(name='moh1', mode='files')
    response.assert_created('moh')

    assert_that(response.item, has_entries(uuid=is_not(empty())))

    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    response = confd.moh.post(name='moh1',
                              label='MOH 1',
                              mode='custom',
                              application='/usr/bin/mpg123 xxx',
                              sort='alphabetical')
    response.assert_created('moh')

    assert_that(response.item, has_entries(name='moh1',
                                           label='MOH 1',
                                           mode='custom',
                                           application='/usr/bin/mpg123 xxx',
                                           sort='alphabetical',
                                           files=empty()))

    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_custom_mode_with_application():
    response = confd.moh.post(name='moh', mode='custom', application='/bin/false')
    response.assert_created('moh')
    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_custom_mode_without_application():
    response = confd.moh.post(name='moh', mode='custom')
    response.assert_status(400)


def test_create_valid_sort():
    valid_sorts = ['alphabetical', 'random', 'random_start']
    for sort in valid_sorts:
        response = confd.moh.post(name='moh', mode='files', sort=sort)
        response.assert_created('moh')
        confd.moh(response.item['uuid']).delete().assert_deleted()


@fixtures.moh()
def test_edit_minimal_parameters(moh):
    response = confd.moh(moh['uuid']).put()
    response.assert_updated()


@fixtures.moh()
def test_edit_all_parameters(moh):
    parameters = {
        'label': 'Foo',
        'application': '/bin/rm -rf /',
        'sort': 'random',
    }

    response = confd.moh(moh['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.moh(name='OriginalName')
def test_edit_name_unavailable(moh):
    response = confd.moh(moh['uuid']).put(name='ModifiedName')
    response.assert_updated()

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(name=moh['name']))


@fixtures.moh(mode='files', application=None)
def test_edit_custom_mode_with_application(moh):
    response = confd.moh(moh['uuid']).put(mode='custom', application='/bin/false')
    response.assert_updated()


@fixtures.moh(mode='files', application=None)
def test_edit_custom_mode_without_application(moh):
    response = confd.moh(moh['uuid']).put(mode='custom')
    response.assert_status(400)


@fixtures.moh()
def test_delete(moh):
    response = confd.moh(moh['uuid']).delete()
    response.assert_deleted()
    response = confd.moh(moh['uuid']).get()
    response.assert_match(404, e.not_found(resource='MOH'))


@fixtures.moh()
def test_add_update_delete_filename(moh):
    client = _new_moh_file_client()

    # add a new file
    response = client.url.moh(moh['uuid']).files('foo.wav').put(content='content is not checked')
    response.assert_status(204)

    response = client.url.moh(moh['uuid']).files('foo.wav').get()
    assert_that(response.raw, equal_to('content is not checked'))

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(files=contains({'name': 'foo.wav'})))

    # update/overwrite the file
    response = client.url.moh(moh['uuid']).files('foo.wav').put(content='some new content')
    response.assert_status(204)

    response = client.url.moh(moh['uuid']).files('foo.wav').get()
    assert_that(response.raw, equal_to('some new content'))

    # delete the file
    response = client.url.moh(moh['uuid']).files('foo.wav').delete()
    response.assert_deleted()

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(files=empty()))


@fixtures.moh()
def test_add_filename_errors(moh):
    client = _new_moh_file_client()
    filenames = [
        '.foo.wav',
        'foo/bar.wav',
        '../bar.wav',
    ]
    for filename in filenames:
        response = client.url.moh(moh['uuid']).files(filename).put(content='content is not checked')
        assert_that(response.status, equal_to(404),
                    'unexpected status for MOH filename {}'.format(filename))


def _new_moh_file_client():
    def encoder(data):
        if data is None:
            return None
        return data['content']

    return new_client(headers={"Content-Type": "application/octet-stream"}, encoder=encoder)


@fixtures.moh()
def test_bus_events(moh):
    yield s.check_bus_event, 'config.moh.created', confd.moh.post, {'name': 'bus_event', 'mode': 'files'}
    yield s.check_bus_event, 'config.moh.edited', confd.moh(moh['uuid']).put
    yield s.check_bus_event, 'config.moh.deleted', confd.moh(moh['uuid']).delete