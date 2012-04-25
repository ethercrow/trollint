
import clang.cindex as ci
from base.token_pass_base import TokenPassBase
from utils import full_text_for_cursor
from diagnostic import LintDiagnostic


class BinaryOperatorWhiteSpace(TokenPassBase):

    def __init__(self):

        super(BinaryOperatorWhiteSpace, self).__init__()

        self.cursor_kind = ci.CursorKind.BINARY_OPERATOR
        self.category = 'Style'

    def maybe_diagnostic(self, cur):

        if not cur.location.file:
            return None

        children = list(cur.get_children())

        if 2 != len(children):
            print 'WTF'

        lhs, rhs = children[0], children[1]

        start = lhs.extent.end.offset
        end = rhs.extent.start.offset

        if end-start <= 1:
            return None

        with open(cur.location.file.name) as fi:
            op_and_whitespace = fi.read()[start:end]

        if '\n' in op_and_whitespace:
            return None

        for i in range(len(op_and_whitespace)):
            left, right = op_and_whitespace[i], op_and_whitespace[-(i+1)]

            if left != ' ' and right != ' ':
                # no more whitespace at either side
                break
            elif left == ' ' and right == ' ':
                # whitespace is symmetric so far
                continue
            else:
                d = LintDiagnostic()
                d.line_number = cur.location.line
                d.message = "Whitespace around binary operator isn't symmetric"
                d.filename = cur.location.file.name
                d.context = full_text_for_cursor(cur)
                d.category = self.category
                return d

        return None
