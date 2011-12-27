

class PassBase(object):

    def __init__(self):
        self.enabled = True

        self.filename = None
        self.text = None
        self.config = None
        self.cursor = None

    def get_diagnostics(self):
        return []

    @property
    def name(self):
        return self.__class__.__name__
