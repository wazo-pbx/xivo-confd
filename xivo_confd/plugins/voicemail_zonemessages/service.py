# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.voicemail_zonemessages.notifier import build_notifier

from xivo_dao.resources.voicemail_zonemessages import dao as voicemail_zonemessages_dao


class VoicemailZoneMessagesService(object):

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self):
        return self.dao.find_all()

    def edit(self, resource):
        self.dao.edit_all(resource)
        self.notifier.edited(resource)


def build_service():
    return VoicemailZoneMessagesService(voicemail_zonemessages_dao,
                                        build_notifier())