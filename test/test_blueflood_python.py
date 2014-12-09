#!/usr/bin/env python

from blueflood_python.blueflood import BluefloodEndpoint
import pytest


@pytest.fixture
def setup():
    return BluefloodEndpoint()

def testSingleIngest(setup):
    endpoint = setup
    name = 'example.metric.single.ingest'
    ttl = 10
    endpoint.ingest(name, 1376509892612, 50, ttl) 
    assert endpoint.commit() == ''

def testListIngest(setup):
    endpoint = setup
    name = 'example.metric.list.ingest'
    ttl = 10
    endpoint.ingest(name,
                    [1376509892612, 1376509892613, 1376509892614], 
                    [50, 51, 52], 
                    ttl)
    assert endpoint.commit() == ''
    with pytest.raises(Exception):
        endpoint.ingest(name, 
                        [1376509892612, 1376509892613, 1376509892614], 
                        50, 
                        ttl)

def testMultipleIngest(setup):
    endpoint = setup
    name = 'example.metric.multiple.ingest'
    ttl = 10
    times, values = list(range(5)), [50.0] * 5
    for t, v in zip(times, values):
         endpoint.ingest(name, t, v, ttl)
    assert endpoint.commit() == ''
    data = endpoint.retrieve(name, 0, 10, 200)
    print (data)
    assert len(data['values']) == 5


def testRetrieve(setup):
    endpoint = setup
    name = 'example.metric.retrieve'
    ttl = 10
    time = 1376509892612
    value = 50
    # insert first
    endpoint.ingest(name, time, value, ttl)
    assert endpoint.commit() == ''
    # range is 0-time, 200 points
    data = endpoint.retrieve(name, 0, time + 10, 200)
    assert len(data) != 0
    assert len(data['values']) != 0
    assert data['values'][0]['numPoints'] == 1
    assert data['values'][0]['average'] == value


if __name__ == '__main__':
    pytest.main()
