
import clang.cindex as ci
from passes.base.token_pass_base import TokenPassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor


class EmptyCompoundStatement(TokenPassBase):

    def __init__(self):

        super(EmptyCompoundStatement, self).__init__()

        self.cursor_kind = ci.CursorKind.COMPOUND_STMT
        self.category = 'DeadCode'

    def maybe_diagnostic(self, cur):

        try:
            cur.get_children().next()
            return None
        except StopIteration:
            pass

        d = LintDiagnostic()
        d.line_number = cur.location.line
        d.message = "empty compound statement"
        d.filename = cur.location.file.name
        d.context = full_text_for_cursor(cur)
        d.category = self.category

        return d
