

class PassBase(object):

    def __init__(self):
        self.enabled = True

        self.filename = None
        self.text = None
        self.config = None
        self.cursors = []
        self.cursors_by_kind = {}
        self.has_arc = False
        self.category = u'Other'

    def get_diagnostics(self):
        return []

    @property
    def name(self):
        return self.__class__.__name__
