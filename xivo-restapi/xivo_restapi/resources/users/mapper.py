# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_restapi.helpers.mapper import AbstractMapper


class UserMapper(AbstractMapper):

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'callerid': 'callerid',
        'outcallerid': 'outcallerid',
        'username': 'username',
        'password': 'password',
        'musiconhold': 'musiconhold',
        'mobilephonenumber': 'mobilephonenumber',
        'userfield': 'userfield',
        'timezone': 'timezone',
        'language': 'language',
        'description': 'description'
    }