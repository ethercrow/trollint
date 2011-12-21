
import re

from pass_base import PassBase
from diagnostic import LintDiagnostic

class LineRegexPassBase(PassBase):

    needs = ['config', 'text', 'filename']

    def __init__(self):
        super(LineRegexPassBase, self).__init__()
        self.name = "VeryLongLines"

    def get_diagnostics(self):
        result = []
        lines = enumerate(self.text.split('\n'))

        regex = re.compile(self.regex_string)

        for i, l in lines:
            if regex.search(l):
                d = LintDiagnostic(None)
                d.line_number = i
                d.message = self.message
                d.filename = self.filename
                result.append(d)
        return result
