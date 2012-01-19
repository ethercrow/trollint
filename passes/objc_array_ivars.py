
import clang.cindex as ci
from diagnostic import LintDiagnostic
from passes.base.token_pass_base import TokenPassBase
from utils import full_text_for_cursor


class ObjCIvarNaming(TokenPassBase):

    def __init__(self):

        super(ObjCIvarNaming, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_IVAR_DECL
        self.category = 'Structure'

    def maybe_diagnostic(self, cur):
        if cur.type.kind == ci.TypeKind.CONSTANTARRAY:

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = "ivar {0} is C array, do you really want to do this?"\
                    .format(cur.displayname)
            d.filename = cur.location.file.name
            d.context = full_text_for_cursor(cur)
            d.category = self.category

            return d

        return None
