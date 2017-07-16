#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for sort_by_distance.py

"""

import os
import shutil
import unittest
from pkg_resources import resource_filename

CENTROIDS = resource_filename(__name__, "worker-locations.csv")
ROADS = resource_filename(__name__, "chonburi-roads-50.csv")

import pandas as pd
from allocator.sort_by_distance import main
from . import capture


class TestSortByDistance(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sort_by_distance(self):
        with capture(main, ['-c', CENTROIDS, ROADS]) as output:
            self.assertRegexpMatches(output, r'Done$')

    def test_sort_by_distance_by_worker(self):
        with capture(main, ['-c', CENTROIDS, 
                            '--by-worker', ROADS]) as output:
            self.assertRegexpMatches(output, r'Done$')

    def test_sort_by_distace_haversine(self):
        with capture(main, ['-c', CENTROIDS,
                            '-d', 'haversine',
                            ROADS]) as output:
            self.assertRegexpMatches(output, r'Done$')

    def test_sort_by_distace_osrm(self):
        with capture(main, ['-c', CENTROIDS,
                            '-d', 'osrm',
                            ROADS]) as output:
            self.assertRegexpMatches(output, r'Done$')

if __name__ == '__main__':
    unittest.main()
