#!/usr/bin/env python

import blueflood
import unittest


class BlueFloodTestCase(unittest.TestCase):

    def setUp(self):
        self.endpoint = blueflood.BluefloodEndpoint()

    def testSingleIngest(self):
        name = 'example.metric.one'
        ttl = 10
        self.assertEqual(self.endpoint.ingest(name, 1376509892612, 50, ttl), '')

    def testListIngest(self):
        name = 'example.metric.one'
        ttl = 10
        self.assertEqual(self.endpoint.ingest(name, [1376509892612, 1376509892613, 1376509892614], [50, 51, 52], ttl), '')
        with self.assertRaises(Exception):
            self.endpoint.ingest(name, [1376509892612, 1376509892613, 1376509892614], 50, ttl)


if __name__ == '__main__':
    unittest.main()
