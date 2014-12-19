#!/usr/bin/env python

import collectd
import time

from blueflood_python.blueflood import BluefloodEndpoint

cfg = {} # has to be global due to `config` function
plugin_name = 'blueflood_plugin'

def config(config):
    global cfg
    for child in config.children:
        cfg[child.key] = child.values[0]

def parse_types_file(path):
    output = {}
    with open(path, 'r') as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue

            fields = line.split()
            if len(fields) < 2:
                continue

            type, values = fields[0], ''.join(fields[1:]).split(',')
            output[type] = [tuple(v.split(':')) for v in values]
    return output


def flush(data, conf):
    endpoint = BluefloodEndpoint(conf.get('URL', 'http://localhost:19000'),
                                 conf.get('Tenant', 'tenant'))

    for metric, series in data.iteritems():
        time_s = [pt[0] for pt in series]
        values_s = [pt[1] for pt in series]
        endpoint.ingest(metric, time_s, values_s, conf.get('TTL', 60 * 60 * 24))
    if len(list(data.iteritems())):
        endpoint.commit()

def queue(name, t, v, data):
    with data['lock']:
        series = data['metrics'].get(name, [])
        series.append((t, v))
        data['metrics'][name] = series

        curr_time = time.time()
        last_time = data['last_flush_time']
        timeout = data['conf'].get('CacheTimeout', 60)
        if curr_time - last_time < timeout:
            return
        

        flushdata = data['metrics']
        data['metrics'] = {}
        data['last_flush_time'] = curr_time

    flush(flushdata, data['conf'])

def write(v, data=None):
    types = data['types']

    if v.type not in types:
        collectd.warning('{}: do not know how to handle type {}. ' \
                         'do you have all your types.db files configured?'.\
                         format(plugin_name, v.type))
        return

    v_types = types[v.type]

    if len(v_types) != len(v.values):
        collectd.warning('{}: differing number of values for type {}'.\
                         format(plugin_name, v.type))
        return

    for index, ds in enumerate(v_types):
        name = []
        name.append(v.host)
        name.append(v.plugin)
        if v.plugin_instance:
            name.append(v.plugin_instance)
        name.append(v.type)
        if v.type_instance:
            name.append(v.type_instance)
        name.append(ds[0]) # that should describe value of particular type

        queue('.'.join(name), v.time, v.values[index], data)

def init():
    import threading
    data = {
        'lock': threading.Lock(),
        'conf': cfg,
        'last_flush_time': time.time(),
        'types': parse_types_file(cfg.get('TypesDB', '/usr/share/collectd/types.db')),
        'metrics': {}
    }

    for key in ('URL', 'Tenant'):
        if key not in cfg:
            collectd.error('{}: No {} key is present in config file'.format(plugin_name, key))
            return

    # can't register write earlier cause of threading import constraints
    collectd.register_write(write, data)

collectd.register_init(init)
collectd.register_config(config)