
from pass_base import PassBase
from diagnostic import LintDiagnostic


class TokenPassBase(PassBase):

    needs = ['config', 'filename', 'cursor']

    def __init__(self):
        super(TokenPassBase, self).__init__()

        self.cursor_kind = None
        self.conditional = None
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

        diags = []

        for c in curs:

            msg = self.maybe_message(c)
            if msg:
                d = LintDiagnostic()
                d.line_number = c.location.line
                d.message = msg
                d.filename = c.location.file.name
                diags.append(d)

        return diags
