
from pass_base import PassBase


class TokenPassBase(PassBase):

    needs = ['config', 'filename', 'cursors_by_kind']

    def __init__(self):
        super(TokenPassBase, self).__init__()

        self.cursor_kind = None
        self.conditional = None
        self.message = None

    def maybe_diagnostic(self, cursor):
        raise NotImplementedError

    def get_diagnostics(self):

        diags = []

        try:
            for c in self.cursors_by_kind[self.cursor_kind]:

                d = self.maybe_diagnostic(c)
                if d:
                    diags.append(d)
        except KeyError:
            pass

        return diags
