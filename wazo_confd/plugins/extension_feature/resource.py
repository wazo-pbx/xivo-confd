# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExtensionFeatureSchema


class ExtensionFeatureList(ListResource):

    schema = ExtensionFeatureSchema

    @required_acl('confd.extensions.features.read')
    def get(self):
        return super().get()

    def post(self):
        return '', 405


class ExtensionFeatureItem(ItemResource):

    schema = ExtensionFeatureSchema

    @required_acl('confd.extensions.features.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.extensions.features.{id}.update')
    def put(self, id):
        return super().put(id)

    def delete(self, id):
        return '', 405
