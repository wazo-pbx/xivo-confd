#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from setuptools import setup


setup(
    name='xivo_confd_test_helpers',
    version='1.0.0',

    description='Wazo confd test helpers',

    author='Wazo Authors',
    author_email='dev@wazo.community',
    packages=['xivo_confd_test_helpers', 'xivo_confd_test_helpers.helpers'],
    package_dir={
        'xivo_confd_test_helpers': 'suite/helpers',
        'xivo_confd_test_helpers.helpers': 'suite/helpers/helpers',
    }
)