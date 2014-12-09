#!/usr/bin/env python

import urllib2
import urlparse
import json


def _get_metrics_url(host, port, scheme, tenantId):
    return scheme + '://' + host + ':' + str(port) + '/v2.0/'\
        + tenantId + '/ingest'

def _get_metrics_query_url(host, port, scheme, tenantId,
                           metricName, start, end, points):
    return scheme + '://' + host + ':' + port + '/v2.0/' + tenantId\
        + '/views/' + metricName\
        + '?from=' + str(start) + '&to=' + str(end) + '&points=' + str(points)


# TODO specify URL directly (without host/port/schema split): ingestion and retrieval
# TODO switch resolution/points on retrieve
class BluefloodEndpoint():

    def __init__(self, host='localhost', ingest_port='19000', retrieve_port='20000', tenant='tenant-id', schema='http'):
        self.ingest_port = ingest_port
        self.retrieve_port = retrieve_port
        self.host = host
        self.tenant = tenant
        self.schema = schema
        self._json_buffer = []

    def ingest(self, metric_name, time, value, ttl):
        if not isinstance(time, list):
            time = [time]
        if not isinstance(value, list):
            value = [value]
        if len(time) != len(value):
            raise Exception('time and value list lengths differ')


        data = [{
            "collectionTime": t,
            "ttlInSeconds": ttl,
            "metricValue": v,
            "metricName": metric_name
        } for t,v in zip(time, value)]
        self._json_buffer.extend(data)

    def commit(self):
        r = urllib2.urlopen(_get_metrics_url(self.host, self.ingest_port, self.schema, self.tenant),
                            data=json.dumps(self._json_buffer))
        self._json_buffer = []
        return r.read()


    def retrieve(self, metric_name, start, to, points):
        r = urllib2.urlopen(_get_metrics_query_url(self.host, self.retrieve_port, self.schema, self.tenant,
                                                   metric_name, start, to, points))
        response = r.read()
        return json.loads(response)
