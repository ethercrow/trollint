
import clang.cindex as ci
from diagnostic import LintDiagnostic
from passes.base.token_pass_base import TokenPassBase
from utils import full_text_for_cursor


class ObjCMethodComplexity(TokenPassBase):

    def __init__(self):

        super(ObjCMethodComplexity, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_INSTANCE_METHOD_DECL
        self.category = 'Structure'

    def maybe_diagnostic(self, cur):

        # depth -1 -- OBJC_INSTANCE_METHOD_DECL (method signature)
        # depth  0 -- COMPOUND_STATMENT (curly braces)
        # depth  1 -- actual method code
        def calculate_complexity(c, depth=-1):
            result = 0
            if c.kind == ci.CursorKind.COMPOUND_STMT and depth > 0:
                result = 1 if (depth < 3) else 2

            result += sum(calculate_complexity(child, depth + 1)
                          for child in c.get_children())

            return result

        complexity = calculate_complexity(cur)
        line_count = full_text_for_cursor(cur).count('\n')

        # TODO configurable thresholds
        if complexity > 15 or\
           complexity > 3 and line_count > 50:

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = "method {0} looks complex ({1} lines, {2} complexity)"\
                    .format(cur.displayname, line_count, complexity)
            d.filename = cur.location.file.name
            d.context = cur.spelling
            d.category = self.category

            return d

        return None
