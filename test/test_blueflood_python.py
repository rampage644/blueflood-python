#!/usr/bin/env python

from blueflood_python.blueflood import BluefloodEndpoint
import pytest


@pytest.fixture
def setup():
    return BluefloodEndpoint()

def testSingleIngest(setup):
    endpoint = setup
    name = 'example.metric.one'
    ttl = 10
    assert endpoint.ingest(name, 1376509892612, 50, ttl) == ''

def testListIngest(setup):
    endpoint = setup
    name = 'example.metric.one'
    ttl = 10
    assert endpoint.ingest(name,
                           [1376509892612, 1376509892613, 1376509892614], 
                           [50, 51, 52], 
                           ttl) == ''
    with pytest.raises(Exception):
        endpoint.ingest(name, 
                        [1376509892612, 1376509892613, 1376509892614], 
                        50, 
                        ttl)

def testRetrieve(setup):
    endpoint = setup
    name = 'example.metric.retrieve'
    ttl = 10
    time = 1376509892612
    value = 50
    # insert first
    assert endpoint.ingest(name, time, value, ttl) == ''
    # range is 0-time, 200 points
    data = endpoint.retrieve(name, 0, time + 10, 200)
    assert len(data) != 0
    assert len(data['values']) != 0
    assert data['values'][0]['numPoints'] == 1
    assert data['values'][0]['average'] == value


if __name__ == '__main__':
    pytest.main()
