
from base.pass_base import PassBase
from diagnostic import LintDiagnostic
import clang.cindex as cindex
import re

re_ivar_decl = re.compile(r'^[a-zA-Z0-9]+_$')

class ObjCNaming(PassBase):

    needs = ['text', 'filename', 'cursor']

    def __init__(self):

        super(ObjCNaming, self).__init__()
        self.name = "ObjCNaming"

    def get_diagnostics(self):

        def find_all_ivar_declarations(cur):

            if cur.kind == cindex.CursorKind.OBJC_IVAR_DECL:
                result = [(cur.location.file.name, cur.location.line, cur.displayname)]
            else:
                result = []

            for child in cur.get_children():
                result += find_all_ivar_declarations(child)

            return result

        ivar_decls = find_all_ivar_declarations(self.cursor)

        diags = []

        for decl in ivar_decls:
            if not re_ivar_decl.match(decl[2]):
                d = LintDiagnostic()
                d.message = 'ivar name "' + decl[2] + '" is against convention'
                d.filename = decl[0]
                d.line_number = decl[1]
                diags.append(d)

        return diags
