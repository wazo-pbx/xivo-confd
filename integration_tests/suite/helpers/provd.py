# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import docker

from datetime import datetime

from hamcrest import assert_that, equal_to, has_item, starts_with
from xivo_provd_client import new_provisioning_client, NotFoundError


class ProvdHelper(object):

    DOCKER_PROVD_IMAGE = "wazopbx/xivo-provd"

    DEFAULT_CONFIGS = [{'X_type': 'registrar',
                        'deletable': False,
                        'displayname': 'local',
                        'id': 'default',
                        'parent_ids': [],
                        'proxy_main': '127.0.0.1',
                        'raw_config': {'X_key': 'xivo'},
                        'registrar_main': '127.0.0.1',
                        },
                       {'X_type': 'internal',
                        'deletable': False,
                        'id': 'autoprov',
                        'parent_ids': ['base', 'defaultconfigdevice'],
                        'raw_config': {'sccp_call_managers': {'1': {'ip': '127.0.0.1'}},
                                       'sip_lines': {'1': {'display_name': 'Autoprov',
                                                           'number': 'autoprov',
                                                           'password': 'autoprov',
                                                           'proxy_ip': '127.0.0.1',
                                                           'registrar_ip': '127.0.0.1',
                                                           'username': 'apmy3dCQDw'}}},
                        'role': 'autocreate'},
                       {'X_type': 'internal',
                        'deletable': False,
                        'id': 'base',
                        'parent_ids': [],
                        'raw_config': {'X_xivo_phonebook_ip': '127.0.0.1',
                                       'ntp_enabled': True,
                                       'ntp_ip': '127.0.0.1'}},
                       {'X_type': 'device',
                        'deletable': False,
                        'id': 'defaultconfigdevice',
                        'label': 'Default config device',
                        'parent_ids': [],
                        'raw_config': {'ntp_enabled': True, 'ntp_ip': '127.0.0.1'}},
                       {'X_type': 'device',
                        'deletable': True,
                        'id': 'mockdevicetemplate',
                        'parent_ids': ['base'],
                        'raw_config': {}},
                       ]

    def __init__(self, client):
        self.client = client

    @property
    def configs(self):
        return self.client.config_manager()

    @property
    def devices(self):
        return self.client.device_manager()

    def reset(self):
        self.clean_devices()
        self.clean_configs()
        self.add_default_configs()

    def clean_devices(self):
        for device in self.devices.find():
            self.devices.remove(device['id'])

    def clean_configs(self):
        for config in self.configs.find():
            self.configs.remove(config['id'])

    def add_default_configs(self):
        for config in self.DEFAULT_CONFIGS:
            self.configs.add(config)

    def add_device_template(self):
        config = {
            'X_type': 'device',
            'deletable': True,
            'label': 'black-label',
            'parent_ids': [],
            'raw_config': {},
        }

        return self.configs.add(config)

    def associate_line_device(self, device_id):
        # line <-> device association is an operation that is currently performed
        # "completely" only by the web-interface -- fake a minimum amount of work here
        config = {
            'id': device_id,
            'parent_ids': [],
            'raw_config': {},
        }
        self.configs.add(config)

        device = self.devices.get(device_id)
        device['config'] = device_id
        self.devices.update(device)

    def assert_config_does_not_exist(self, config_id):
        try:
            self.configs.get(config_id)
        except NotFoundError:
            return
        else:
            raise AssertionError('config "{}" exists in xivo-provd'.format(config_id))

    def assert_device_has_autoprov_config(self, device):
        assert_that(device['config'], starts_with('autoprov'))

    def assert_config_use_device_template(self, config, template_id):
        assert_that(config['configdevice'], equal_to(template_id))
        assert_that(config['parent_ids'], has_item(template_id))

    def has_synchronized(self, device_id, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        line = "Synchronizing device {}".format(device_id)
        output = self.find_provd_logs(timestamp)
        for log in output.split("\n"):
            if line in log:
                return True
        return False

    def updated_count(self, device_id, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        expected_line = "Updating config {}".format(device_id)
        output = self.find_provd_logs(timestamp)
        count = len([line for line in output.split("\n") if expected_line in line])
        return count

    def find_provd_logs(self, timestamp):
        client = docker.from_env().api
        for container in client.containers(filters={'status': 'running'}):
            info = client.inspect_container(container['Id'])
            if info['Config']['Image'] == self.DOCKER_PROVD_IMAGE:
                return client.logs(container['Id'], since=timestamp)


def create_helper(host='localhost', port='8666'):
    url = "http://{host}:{port}/provd".format(host=host, port=port)
    client = new_provisioning_client(url)
    return ProvdHelper(client)
