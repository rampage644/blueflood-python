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


# TODO add retrieve method
# TODO tenant id as parameter
# TODO replace urllib2 with requests(?)
class BluefloodEndpoint():

    def __init__(self, host='localhost', port='19000'):
        self.host = host
        self.port = port

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
        # print (_get_metrics_url(self.host, self.port, 'http', 'tenant-id'))
        # print (json.dumps(data))
        r = urllib2.urlopen(_get_metrics_url(self.host, self.port, 'http', 'tenant-id'),
                            data=json.dumps(data))
        return r.read()