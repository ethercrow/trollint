

class LintDiagnostic(object):

    def __init__(self):
        self.line_number = 0
        self.message = ''
        self.filename = ''

    def __str__(self):
        return '{0}:{1}: {2}'.format(self.filename,
                                  self.line_number, self.message)

    def __eq__(self, rhs):
        return self.filename == rhs.filename \
               and self.line_number == rhs.line_number \
               and self.message == rhs.message

    def __ne__(self, rhs):
        return not (self == rhs)
