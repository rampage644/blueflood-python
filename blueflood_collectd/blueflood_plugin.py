#!/usr/bin/env python

import collectd
import time

cfg = {} # has to be global due to `config` function

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


def flush(data):
#     """
#     POST a collection of gauges and counters to Librato Metrics.
#     """
    pass
#     headers = {
#         'Content-Type': 'application/json',
#         'User-Agent': config['user_agent'],
#         'Authorization': 'Basic %s' % config['auth_header']
#         }

#     body = json.dumps({ 'gauges' : gauges, 'counters' : counters })

#     url = "%s%s" % (config['api'], config['api_path'])
#     req = urllib2.Request(url, body, headers)
#     try:
#         f = urllib2.urlopen(req, timeout = config['flush_timeout_secs'])
#         response = f.read()
#         f.close()
#     except urllib2.HTTPError as error:
#         body = error.read()
#         collectd.warning('%s: Failed to send metrics to Librato: Code: %d. Response: %s' % \
#                          (plugin_name, error.code, body))
#     except IOError as error:
#         collectd.warning('%s: Error when sending metrics Librato (%s)' % \
#                          (plugin_name, error.reason))


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

    flush(flushdata)

def write(v, data=None):
    types = data['types']

    if v.type not in types:
        collectd.warning('%s: do not know how to handle type %s. ' \
                         'do you have all your types.db files configured?' % \
                         (plugin_name, v.type))
        return

    v_types = types[v.type]

    if len(v_types) != len(v.values):
        collectd.warning('%s: differing number of values for type %s' % \
                         (plugin_name, v.type))
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

    # can't register write earlier cause of threading import constraints
    collectd.register_write(write, data)

collectd.register_init(init)
collectd.register_config(config)