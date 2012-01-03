
import re
from pass_base import PassBase
from diagnostic import LintDiagnostic
from os.path import isabs
from itertools import chain


class TokenRegexPassBase(PassBase):

    needs = ['config', 'filename', 'cursors']

    def __init__(self):
        super(TokenRegexPassBase, self).__init__()

        self.cursor_kind = None
        self.regex_string = None
        self.message = None

    def get_diagnostics(self):

        def filter_cursors(cur):

            if cur.kind == self.cursor_kind:
                result = [cur]
            else:
                result = []

            for child in cur.get_children():
                if child.location.file and not isabs(child.location.file.name):
                    result += filter_cursors(child)

            return result

        curs = chain(*map(filter_cursors, self.cursors))

        regex = re.compile(self.regex_string)

        diags = []

        for c in curs:

            if not regex.search(c.displayname) and c.location.file:

                d = LintDiagnostic()
                d.line_number = c.location.line
                d.message = self.message.format(cur=c)
                d.filename = c.location.file.name
                d.context = c.displayname
                d.category = self.category
                diags.append(d)

        return diags
