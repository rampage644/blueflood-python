## Python Blueflood client

Python *Blueflood* client. Currently only supports simple *ingest* and *retrieve* operations. Created only for `collectd` support. Should be replaced once Blueflood exposes python bindings.

## Blueflood collectd plugin

`collectd` plugin written in python (that is, uses `collectd-python`). 

| Parameter         | Typical value                 | Description                                           |
| ----------------- | ----------------------------- |------------------------------------------             |
| URL               | http://host:port              | Full URL to Blueflood ingest endpoint                 |
| User              | username                      | Username used in auth (not implemented)               |
| Password          | pass                          | Password used in auth (not implemented)               |
| TypesDB           | /usr/share/collectd/types.db  | `collectd` types database location                    |
| CacheTimeout      | 60                            | Timeout in seconds between data flush to Blueflood    |


Sample configuration `/etc/collectd.conf`:

    <LoadPlugin python>
        Globals true
    </LoadPlugin>

    <Plugin python>
        ModulePath "<path-to-blueflood-plugin.py>"
        ModulePath "<path-to-blueflood.py>"
        LogTraces false
        Interactive false
        Import "blueflood-plugin"
        <Module "blueflood_collectd.blueflood_plugin">
            URL         "http::/localhost:19000"
            User        "user"
            Tenant      "tenant-id"
            Password    "password"
            TypesDB     "share/collectd/types.db"
        </Module>
    </Plugin>

