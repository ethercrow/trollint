
class PassBase(object):

    def __init__(self):
        self.name = 'Empty pass'
        self.enabled = True

        self.filename = None
        self.text = None
        self.config = None
        self.cursor = None

    def get_diagnostics(self):
        return []
