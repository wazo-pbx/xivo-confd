# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.helpers import errors

from xivo_confd.database import device as device_db
from xivo_dao.resources.line import dao as line_dao

from xivo_confd.plugins.device.builder import build_device_updater
from xivo_confd.plugins.line_device.validator import build_validator
from xivo_confd.plugins.line_device.notifier import build_notifier


class LineDevice(object):

    @classmethod
    def from_line(cls, line):
        return cls(line.id, line.device_id)

    def __init__(self, line_id, device_id):
        self.line_id = line_id
        self.device_id = device_id


class LineDeviceService(object):

    def __init__(self, validator, line_dao, notifier, device_updater):
        self.validator = validator
        self.line_dao = line_dao
        self.notifier = notifier
        self.device_updater = device_updater

    def associate(self, line, device):
        self.validator.validate_association(line, device)
        self.associate_line_device(line, device)
        self.notifier.associated(line, device)

    def associate_line_device(self, line, device):
        line.associate_device(device)
        self.device_updater.update_device(device)
        if line.endpoint == "sccp":
            device_db.associate_sccp_device(line, device)

    def dissociate(self, line, device):
        self.validator.validate_dissociation(line, device)
        self.dissociate_line_device(line, device)
        self.device_updater.update_device(device)
        self.notifier.dissociated(line, device)

    def dissociate_line_device(self, line, device):
        line.remove_device()
        self.device_updater.update_device(device)
        if line.endpoint == "sccp":
            device_db.dissociate_sccp_device(line, device)

    def get_association_from_line(self, line):
        if not line.device_id:
            raise errors.not_found('LineDevice', line_id=line.id)
        return LineDevice.from_line(line)

    def find_all_associations_from_device(self, device):
        lines = self.line_dao.find_all_by(device=device.id)
        return [LineDevice.from_line(line) for line in lines]


def build_service(provd_client):
    validator = build_validator()
    updater = build_device_updater(provd_client)
    notifier = build_notifier()
    return LineDeviceService(validator, line_dao, notifier, updater)
