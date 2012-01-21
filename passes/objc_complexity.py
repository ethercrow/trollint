
import clang.cindex as ci
from diagnostic import LintDiagnostic
from passes.base.token_pass_base import TokenPassBase
from utils import full_text_for_cursor

# blocks and branching points
COMPLEX_KINDS = (ci.CursorKind.IF_STMT,
                 ci.CursorKind.WHILE_STMT,
                 ci.CursorKind.FOR_STMT,
                 ci.CursorKind.SWITCH_STMT,
                 ci.CursorKind.BLOCK_EXPR)


class ObjCMethodComplexity(TokenPassBase):

    def __init__(self):

        super(ObjCMethodComplexity, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_INSTANCE_METHOD_DECL
        self.category = 'Structure'

    def maybe_diagnostic(self, cur):

        def calculate_complexity(c, depth=1):
            result = 0
            if c.kind in COMPLEX_KINDS:
                result = depth

            result += sum(calculate_complexity(child, depth + 1)
                          for child in c.get_children())

            return result

        complexity = calculate_complexity(cur)
        line_count = full_text_for_cursor(cur).count('\n')

        # TODO configurable thresholds
        if complexity > 30 or\
           complexity > 5 and line_count > 50:

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = "method {0} looks complex ({1} lines, {2} complexity)"\
                    .format(cur.displayname, line_count, complexity)
            d.filename = cur.location.file.name
            d.context = cur.spelling
            d.category = self.category

            return d

        return None
