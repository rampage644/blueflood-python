## Python Blueflood client

## Blueflood collectd plugin

`/etc/collectd.conf`:

    <LoadPlugin python>
        Globals true
    </LoadPlugin>

    <Plugin python>
        ModulePath "<path-to-blueflood-plugin.py>"
        ModulePath "<path-to-blueflood.py>"
        LogTraces false
        Interactive false
        Import "blueflood-plugin"
    </Plugin>

