
class Config(object):
    def __init__(self, key, values, children=[]):
        # also Config instance
        self.parent = None
        # key string 
        self.key = key
        # tuple of Config instances, mostly empty
        self.children = children
        for child in self.children:
            child.parent = self
        # tuple of strings, mostly one value
        self.values = values

class Values(object):
    def __init__(self, host, plugin, plugin_instance, type, type_instance, time, values):
        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance
        self.time = time
        self.type = type
        self.type_instance = type_instance
        self.values = values


def register_write(func):
    pass

def register_config(func):
    pass