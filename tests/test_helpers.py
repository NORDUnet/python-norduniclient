# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
from norduniclient import helpers

__author__ = 'lundberg'


class HelpersTests(unittest.TestCase):

    def test_update_item_properties(self):
        initial_props = {
            'string': 'hello world',
            'delete_me': 'byebye',
            'list': ['hello', 'world'],
            'int': 3
        }
        update_props = {
            'string': 'hola el mundo',
            'delete_me': '',
            'list': ['hello'],
            'int': 0
        }
        new_props = helpers.update_item_properties(initial_props, update_props)
        expected_props = {
            'string': 'hola el mundo',
            'list': ['hello'],
            'int': 0
        }
        self.assertEqual(new_props, expected_props)


