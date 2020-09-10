#!/usr/bin/env python3
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages

setup(
    name='wazo-confd',
    version='0.1',
    description='Wazo configuration daemon',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    package_data={'wazo_confd.plugins': ['*/api.yml']},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'wazo-confd=wazo_confd.main:main',
            'wazo-confd-sync-db=wazo_confd.sync_db:main',
        ],
        'wazo_confd.plugins': [
            'access_feature = wazo_confd.plugins.access_feature.plugin:Plugin',
            'agent = wazo_confd.plugins.agent.plugin:Plugin',
            'agent_skill = wazo_confd.plugins.agent_skill.plugin:Plugin',
            'api = wazo_confd.plugins.api.plugin:Plugin',
            'application = wazo_confd.plugins.application.plugin:Plugin',
            'call_filter = wazo_confd.plugins.call_filter.plugin:Plugin',
            'call_filter_fallback = wazo_confd.plugins.call_filter_fallback.plugin:Plugin',
            'call_filter_user = wazo_confd.plugins.call_filter_user.plugin:Plugin',
            'call_permission = wazo_confd.plugins.call_permission.plugin:Plugin',
            'call_pickup = wazo_confd.plugins.call_pickup.plugin:Plugin',
            'call_pickup_member = wazo_confd.plugins.call_pickup_member.plugin:Plugin',
            'confbridge = wazo_confd.plugins.confbridge.plugin:Plugin',
            'conference = wazo_confd.plugins.conference.plugin:Plugin',
            'conference_extension = wazo_confd.plugins.conference_extension.plugin:Plugin',
            'configuration = wazo_confd.plugins.configuration.plugin:Plugin',
            'context = wazo_confd.plugins.context.plugin:Plugin',
            'context_context = wazo_confd.plugins.context_context.plugin:Plugin',
            'device = wazo_confd.plugins.device.plugin:Plugin',
            'dhcp = wazo_confd.plugins.dhcp.plugin:Plugin',
            'endpoint_custom = wazo_confd.plugins.endpoint_custom.plugin:Plugin',
            'endpoint_iax = wazo_confd.plugins.endpoint_iax.plugin:Plugin',
            'endpoint_sccp = wazo_confd.plugins.endpoint_sccp.plugin:Plugin',
            'endpoint_sip = wazo_confd.plugins.endpoint_sip.plugin:Plugin',
            'extension = wazo_confd.plugins.extension.plugin:Plugin',
            'extension_feature = wazo_confd.plugins.extension_feature.plugin:Plugin',
            'features = wazo_confd.plugins.features.plugin:Plugin',
            'func_key = wazo_confd.plugins.func_key.plugin:Plugin',
            'group = wazo_confd.plugins.group.plugin:Plugin',
            'group_call_permission = wazo_confd.plugins.group_call_permission.plugin:Plugin',
            'group_extension = wazo_confd.plugins.group_extension.plugin:Plugin',
            'group_fallback = wazo_confd.plugins.group_fallback.plugin:Plugin',
            'group_member_user = wazo_confd.plugins.group_member.plugin:Plugin',
            'group_schedule = wazo_confd.plugins.group_schedule.plugin:Plugin',
            'ha = wazo_confd.plugins.ha.plugin:Plugin',
            'hep = wazo_confd.plugins.hep.plugin:Plugin',
            'iax_callnumberlimits = wazo_confd.plugins.iax_callnumberlimits.plugin:Plugin',
            'iax_general = wazo_confd.plugins.iax_general.plugin:Plugin',
            'incall = wazo_confd.plugins.incall.plugin:Plugin',
            'incall_extension = wazo_confd.plugins.incall_extension.plugin:Plugin',
            'incall_schedule = wazo_confd.plugins.incall_schedule.plugin:Plugin',
            'info = wazo_confd.plugins.info.plugin:Plugin',
            'ivr = wazo_confd.plugins.ivr.plugin:Plugin',
            'line = wazo_confd.plugins.line.plugin:Plugin',
            'line_application = wazo_confd.plugins.line_application.plugin:Plugin',
            'line_device = wazo_confd.plugins.line_device.plugin:Plugin',
            'line_endpoint = wazo_confd.plugins.line_endpoint.plugin:Plugin',
            'line_extension = wazo_confd.plugins.line_extension.plugin:Plugin',
            'line_sip = wazo_confd.plugins.line_sip.plugin:Plugin',
            'moh = wazo_confd.plugins.moh.plugin:Plugin',
            'outcall = wazo_confd.plugins.outcall.plugin:Plugin',
            'outcall_call_permission = wazo_confd.plugins.outcall_call_permission.plugin:Plugin',
            'outcall_extension = wazo_confd.plugins.outcall_extension.plugin:Plugin',
            'outcall_schedule = wazo_confd.plugins.outcall_schedule.plugin:Plugin',
            'outcall_trunk = wazo_confd.plugins.outcall_trunk.plugin:Plugin',
            'paging = wazo_confd.plugins.paging.plugin:Plugin',
            'paging_user = wazo_confd.plugins.paging_user.plugin:Plugin',
            'parking_lot = wazo_confd.plugins.parking_lot.plugin:Plugin',
            'parking_lot_extension = wazo_confd.plugins.parking_lot_extension.plugin:Plugin',
            'pjsip = wazo_confd.plugins.pjsip.plugin:Plugin',
            'provisioning_networking = wazo_confd.plugins.provisioning_networking.plugin:Plugin',
            'queue = wazo_confd.plugins.queue.plugin:Plugin',
            'queue_extension = wazo_confd.plugins.queue_extension.plugin:Plugin',
            'queue_fallback = wazo_confd.plugins.queue_fallback.plugin:Plugin',
            'queue_general = wazo_confd.plugins.queue_general.plugin:Plugin',
            'queue_member = wazo_confd.plugins.queue_member.plugin:Plugin',
            'queue_schedule = wazo_confd.plugins.queue_schedule.plugin:Plugin',
            'rtp = wazo_confd.plugins.rtp.plugin:Plugin',
            'register_iax = wazo_confd.plugins.register_iax.plugin:Plugin',
            'registrar = wazo_confd.plugins.registrar.plugin:Plugin',
            'schedule = wazo_confd.plugins.schedule.plugin:Plugin',
            'sccp_general = wazo_confd.plugins.sccp_general.plugin:Plugin',
            'skill = wazo_confd.plugins.skill.plugin:Plugin',
            'skill_rule = wazo_confd.plugins.skill_rule.plugin:Plugin',
            'sound = wazo_confd.plugins.sound.plugin:Plugin',
            'sound_language = wazo_confd.plugins.sound_language.plugin:Plugin',
            'switchboard = wazo_confd.plugins.switchboard.plugin:Plugin',
            'switchboard_member = wazo_confd.plugins.switchboard_member.plugin:Plugin',
            'timezone = wazo_confd.plugins.timezone.plugin:Plugin',
            'trunk = wazo_confd.plugins.trunk.plugin:Plugin',
            'trunk_endpoint = wazo_confd.plugins.trunk_endpoint.plugin:Plugin',
            'trunk_register = wazo_confd.plugins.trunk_register.plugin:Plugin',
            'user = wazo_confd.plugins.user.plugin:Plugin',
            'user_agent = wazo_confd.plugins.user_agent.plugin:Plugin',
            'user_call_permission = wazo_confd.plugins.user_call_permission.plugin:Plugin',
            'user_fallback = wazo_confd.plugins.user_fallback.plugin:Plugin',
            'user_group = wazo_confd.plugins.user_group.plugin:Plugin',
            'user_import = wazo_confd.plugins.user_import.plugin:Plugin',
            'user_line = wazo_confd.plugins.user_line.plugin:Plugin',
            'user_line_associated = wazo_confd.plugins.user_line_associated.plugin:Plugin',
            'user_schedule = wazo_confd.plugins.user_schedule.plugin:Plugin',
            'user_voicemail = wazo_confd.plugins.user_voicemail.plugin:Plugin',
            'voicemail = wazo_confd.plugins.voicemail.plugin:Plugin',
            'voicemail_general = wazo_confd.plugins.voicemail_general.plugin:Plugin',
            'voicemail_zonemessages = wazo_confd.plugins.voicemail_zonemessages.plugin:Plugin',
            'wizard = wazo_confd.plugins.wizard.plugin:Plugin',
            'event_handlers = wazo_confd.plugins.event_handlers.plugin:Plugin',
        ],
    },
)
