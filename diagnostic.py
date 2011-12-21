

class LintDiagnostic(object):

    def __init__(self):
        self.line_number = 0
        self.message = ''
        self.filename = ''

    def __str__(self):
        return '{}:{}: {}'.format(self.filename,
                                  self.line_number, self.message)

