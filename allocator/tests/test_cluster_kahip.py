#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for cluster_kahip.py

"""

import os
import unittest
from pathlib import Path

from allocator.cluster_kahip import main
from . import capture

TEST_DIR = Path(__file__).parent
ROADS = str(TEST_DIR / "chonburi-roads-50.csv")


def kahip_available():
    """Check if KaHIP dependencies are available"""
    try:
        import kahipwrapper  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipIf(os.name == 'nt', 'KaHIP not available on Windows')
@unittest.skipIf(not kahip_available(), 'KaHIP dependencies not available')
class TestClusterKaHIP(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cluster_kahip(self):
        with capture(main, ['-n', '5', ROADS]) as output:
            self.assertRegex(output, r'Done$')


if __name__ == '__main__':
    unittest.main()
