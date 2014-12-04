#!/usr/bin/env python

import collectd
import time

def write(vl, data=None):
    # return 0
    print vl.plugin_instance, vl.type_instance
    # endpoint.ingest('{}.{}'.format(vl.plugin, vl.type), [int(vl.time)] * len(vl.values), list(vl.values), 60 * 60 * 24)

def config(config):
    global cfg
    for child in config.children:
        cfg[child.key] = child.values[0]
    return


collectd.register_write(write)
collectd.register_config(config)


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



# def flush(data):
#     """
#     POST a collection of gauges and counters to Librato Metrics.
#     """

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


def queue(name, time, value, data):
    pass
    # # Updating shared data structures
    # #
    # data['lock'].acquire()

    # data['gauges'].extend(gauges)
    # data['counters'].extend(counters)

    # curr_time = get_time()
    # last_flush = curr_time - data['last_flush_time']
    # length = len(data['gauges']) + len(data['counters'])

    # if (last_flush < config['flush_interval_secs'] and \
    #        length < config['flush_max_measurements']) or \
    #        length == 0:
    #     data['lock'].release()
    #     return

    # flush_gauges = data['gauges']
    # flush_counters = data['counters']
    # data['gauges'] = []
    # data['counters'] = []
    # data['last_flush_time'] = curr_time
    # data['lock'].release()

    # flush(data)

def write(v, data=None):
    types, cfg = data['types'], data['conf']

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
        if v.type_instance:
            name.append(v.type_instance)
        name.append(ds[0]) # that should describe value of particular type

        queue('.'.join(name), vl.time, vl.values[index], data)

# def librato_init():
#     import threading

#     try:
#         librato_parse_types_file(config['types_db'])
#     except:
#         msg = '%s: ERROR: Unable to open TypesDB file: %s.' % \
#               (plugin_name, config['types_db'])
#         raise Exception(msg)

#     d = {
#         'lock' : threading.Lock(),
#         'last_flush_time' : get_time(),
#         'gauges' : [],
#         'counters' : []
#         }

#     collectd.register_write(librato_write, data = d)

# collectd.register_config(librato_config)
# collectd.register_init(librato_init)
