
from pass_base import PassBase


class TokenPassBase(PassBase):

    needs = ['config', 'filename', 'cursor']

    def __init__(self):
        super(TokenPassBase, self).__init__()

        self.cursor_kind = None
        self.conditional = None
        self.message = None

    def maybe_diagnostic(self, cursor):
        raise NotImplementedError

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

            d = self.maybe_diagnostic(c)
            if d:
                diags.append(d)

        return diags
