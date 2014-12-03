#!/usr/bin/env python

from blueflood_python.blueflood import BluefloodEndpoint
import unittest


class BlueFloodTestCase(unittest.TestCase):

    def setUp(self):
        self.endpoint = BluefloodEndpoint()

    def testSingleIngest(self):
        name = 'example.metric.one'
        ttl = 10
        self.assertEqual(
            self.endpoint.ingest(name, 1376509892612, 50, ttl), '')

    def testListIngest(self):
        name = 'example.metric.one'
        ttl = 10
        self.assertEqual(self.endpoint.ingest(
            name, [1376509892612, 1376509892613, 1376509892614], [50, 51, 52], ttl), '')
        with self.assertRaises(Exception):
            self.endpoint.ingest(
                name, [1376509892612, 1376509892613, 1376509892614], 50, ttl)

    def testRetrieve(self):
        name = 'example.metric.retrieve'
        ttl = 10
        time = 1376509892612
        value = 50
        # insert first
        self.assertEqual(self.endpoint.ingest(name, time, value, ttl), '')
        # range is 0-time, 200 points
        data = self.endpoint.retrieve(name, 0, time + 10, 200)
        self.assertNotEquals(len(data), 0)
        self.assertNotEquals(len(data['values']), 0)
        self.assertEquals(data['values'][0]['numPoints'], 1)
        self.assertEquals(data['values'][0]['average'], value)


if __name__ == '__main__':
    unittest.main()
