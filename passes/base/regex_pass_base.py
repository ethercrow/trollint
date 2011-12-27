
import re

from pass_base import PassBase
from diagnostic import LintDiagnostic


class LineRegexPassBase(PassBase):

    needs = ['config', 'text', 'filename']

    def __init__(self):
        super(LineRegexPassBase, self).__init__()

    def get_diagnostics(self):
        result = []
        lines = enumerate(self.text.split('\n'))

        regex = re.compile(self.regex_string)

        for i, l in lines:
            if regex.search(l):
                d = LintDiagnostic()
                d.line_number = i
                d.message = self.message
                d.filename = self.filename
                d.context = l
                d.category = self.category
                result.append(d)

        return result
