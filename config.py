

class Config(object):

    def __getattr__(self, name):

        def lookup(default):
            # TODO: actually read some configs
            return default

        return lookup
