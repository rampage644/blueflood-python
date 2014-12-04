#!/usr/bin/env python

import os
import sys
# doing it to make sure collectd module mock will be found
sys.path.append(os.path.dirname(__file__))

import pytest
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

def test_write():
    path = os.path.join(os.path.dirname(__file__), 'types.db')
    types = blueflood_collectd.blueflood_plugin.parse_types_file(path)
    data = {}
    data['types'] = types
    vl = collectd.Values(type='load',plugin='load',host='localhost',time=1417702296.6129851,interval=10.0,values=[0.1, 0.18, 0.23])
    blueflood_collectd.blueflood_plugin.write(vl, data)

