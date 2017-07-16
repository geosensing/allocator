#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for cluster_kahip.py

"""

import os
import unittest
from pkg_resources import resource_filename

from allocator.cluster_kahip import main
from . import capture


ROADS = resource_filename(__name__, "chonburi-roads-50.csv")


@unittest.skipIf(os.name == 'nt', 'KaHIP not available on Windows')
class TestClusterKaHIP(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cluster_kahip(self):
        print ROADS
        with capture(main, ['-n', '5', ROADS]) as output:
            print output
            self.assertRegexpMatches(output, r'Done$')


if __name__ == '__main__':
    unittest.main()
