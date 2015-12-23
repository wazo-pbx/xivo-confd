# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import csv

from cStringIO import StringIO
from flask import make_response

from xivo_dao.helpers.db_manager import Session

from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.plugins.user_import import csvparse
from xivo_confd.database import user_export as user_export_db
from xivo_confd import sysconfd, bus


class UserImportResource(ConfdResource):

    def __init__(self, service):
        self.service = service

    def post(self):
        parser = csvparse.parse()
        entries, errors = self.service.import_rows(parser)

        if errors:
            status_code = 400
            response = {'errors': errors}
            self.rollback()
        else:
            status_code = 201
            response = {'created': [entry.extract_ids() for entry in entries]}

        return response, status_code

    def put(self):
        parser = csvparse.parse()
        entries, errors = self.service.update_rows(parser)

        if errors:
            status_code = 400
            response = {'errors': errors}
            self.rollback()
        else:
            status_code = 201
            response = {'updated': [entry.extract_ids() for entry in entries]}

        return response, status_code

    def rollback(self):
        Session.rollback()
        sysconfd.rollback()
        bus.rollback()


class UserExportResource(ConfdResource):

    def get(self):
        header, query = user_export_db.export_query()
        content = self.format_csv(header, query)
        return make_response((content,
                              200,
                              [('Content-Type', 'text/csv; charset=utf-8')]))

    def format_csv(self, header, query):
        content = StringIO()
        writer = csv.writer(content)
        writer.writerow(header)

        for row in query:
            encoded_row = tuple((v or "").encode('utf8') for v in row)
            writer.writerow(encoded_row)

        return content.getvalue()
