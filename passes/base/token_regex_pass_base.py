
import re
from pass_base import PassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor


class TokenRegexPassBase(PassBase):

    needs = ['config', 'filename', 'cursor']

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
                result += filter_cursors(child)

            return result

        curs = filter_cursors(self.cursor)

        regex = re.compile(self.regex_string)

        diags = []

        for c in curs:

            if not regex.search(c.displayname):
                d = LintDiagnostic()
                d.line_number = c.location.line
                d.message = self.message.format(cur=c)
                d.filename = c.location.file.name
                d.context = c.displayname
                diags.append(d)

        return diags
