#!/usr/bin/env python

import os
import sys
import time
import threading
# doing it to make sure collectd module mock will be found
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import mock
import collectd
import blueflood_collectd.blueflood_plugin

def test_parse_type_file():
    path = os.path.join(os.path.dirname(__file__), 'types.db')
    data = blueflood_collectd.blueflood_plugin.parse_types_file(path)
    assert len(data) == 229
    assert 'load' in data
    assert len(data['load']) == 3

    short, mid, long = data['load']
    assert short == ('shortterm', 'GAUGE', str(0), str(5000))
    assert mid == ('midterm', 'GAUGE', str(0), str(5000))
    assert long == ('longterm', 'GAUGE', str(0), str(5000))

def test_parse_config():
    ingest_url = collectd.Config('IngestURL', ('some_ingest_url',))
    auth_url = collectd.Config('AuthURL', ('some_auth_url',))
    user = collectd.Config('User', ('user',))
    password = collectd.Config('Password', ('password',))
    tenant = collectd.Config('Tenant', ('tenant',))
    module = collectd.Config('Module', ('blueflood_collectd.blueflood_plugin',), 
                             [ingest_url, auth_url, user, password, tenant])
    blueflood_collectd.blueflood_plugin.config(module)
    cfg = blueflood_collectd.blueflood_plugin.cfg
    assert len(cfg) > 0
    assert 'IngestURL' in cfg and cfg['IngestURL'] == 'some_ingest_url'
    assert 'AuthURL' in cfg and cfg['AuthURL'] == 'some_auth_url'
    assert 'User' in cfg and cfg['User'] == 'user'
    assert 'Password' in cfg and cfg['Password'] == 'password'
    assert 'Tenant' in cfg and cfg['Tenant'] == 'tenant'

@mock.patch('blueflood_collectd.blueflood_plugin.queue')
def test_write(queue):
    path = os.path.join(os.path.dirname(__file__), 'types.db')
    types = blueflood_collectd.blueflood_plugin.parse_types_file(path)
    data = {}
    data['types'] = types
    # mocking collectd imported queue function

    vl = collectd.Values(type='load',plugin='load',host='localhost',time=1417702296.6129851,interval=10.0,values=[0.1, 0.18, 0.23])
    blueflood_collectd.blueflood_plugin.write(vl, data)
    queue.assert_any_call('localhost.load.load.shortterm', 1417702296.6129851, 0.1, data)
    queue.assert_any_call('localhost.load.load.midterm', 1417702296.6129851, 0.18, data)
    queue.assert_any_call('localhost.load.load.longterm', 1417702296.6129851, 0.23, data)

    vl = collectd.Values(type='if_octets',plugin='interface',plugin_instance='enp0s25',host='localhost',time=1417945871.3524115,interval=10.0,values=[0, 0])
    blueflood_collectd.blueflood_plugin.write(vl, data)
    queue.assert_any_call('localhost.interface.enp0s25.if_octets.rx', 1417945871.3524115, 0, data)
    queue.assert_any_call('localhost.interface.enp0s25.if_octets.tx', 1417945871.3524115, 0, data)
    
    vl = collectd.Values(type='memory',type_instance='buffered',plugin='memory',host='localhost',time=1417945871.3516226,interval=10.0,values=[76820480.0])
    blueflood_collectd.blueflood_plugin.write(vl, data)
    queue.assert_any_call('localhost.memory.memory.buffered.value', 1417945871.3516226, 76820480.0, data)

@mock.patch('blueflood_collectd.blueflood_plugin.flush')
def test_queue(flush):
    queue = blueflood_collectd.blueflood_plugin.queue

    data = {}
    data['metrics'] = {}
    conf = {'CacheTimeout': 0.2}
    data['conf'] = conf
    data['last_flush_time'] = time.time()
    data['lock'] = threading.Lock()

    values = [(1417702296.6129851, 0.1),
              (1417702297.6129851, 0.1),
              (1417702298.6129851, 0.1),
              (1417702299.6129851, 0.1)]
    for v in values:
        queue('localhost.load.load.shortterm', v[0], v[1], data)
    assert not flush.called
    time.sleep(0.3)
    queue('localhost.load.load.shortterm', 0, 0, data)
    data = {
        'localhost.load.load.shortterm': values + [(0, 0)]
    }
    flush.assert_called_once_with(data, conf)

@mock.patch('blueflood_collectd.blueflood_plugin.collectd.register_write')
def test_init(register_write):
    # testing all needed dict keys
    path = os.path.join(os.path.dirname(__file__), 'types.db')
    blueflood_collectd.blueflood_plugin.cfg = {'TypesDB': path}
    blueflood_collectd.blueflood_plugin.init()
    data = register_write.call_args[0][1]
    assert 'lock' in data
    assert 'conf' in data and isinstance(data['conf'], dict)
    assert 'last_flush_time' and data['last_flush_time'] >= 0
    assert 'metrics' in data and isinstance(data['metrics'], dict)
    assert 'types' in data and isinstance(data['types'], dict)

@mock.patch('blueflood_python.blueflood.BluefloodEndpoint.ingest')
def test_flush(ingest):
    values = [(1417702296.6129851, 0.1),
          (1417702297.6129851, 0.1),
          (1417702298.6129851, 0.1),
          (1417702299.6129851, 0.1)]
    data = {
        'localhost.load.load.shortterm': values,
    }
    blueflood_collectd.blueflood_plugin.flush(data, {})
    ingest.assert_called_once_with('localhost.load.load.shortterm',
        [1417702296.6129851, 1417702297.6129851, 1417702298.6129851, 1417702299.6129851],
        [0.1] * 4)
