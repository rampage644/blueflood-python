#!/usr/bin/env python


import collectd
import time
import blueflood

endpoint = blueflood.BluefloodEndpoint()

def write(vl, data=None):
    endpoint.ingest('{}.{}'.format(vl.plugin, vl.type), [int(vl.time)] * len(vl.values), list(vl.values), 60 * 60 * 24)

collectd.register_write(write);