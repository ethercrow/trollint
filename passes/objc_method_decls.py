
from base.token_pass_base import TokenPassBase
import clang.cindex as cindex
from diagnostic import LintDiagnostic
import re
from utils import full_text_for_cursor

re_method_decl = re.compile(r'^- \([^\)]+\)\w.*$')


class ObjCMethodDecls(TokenPassBase):

    def __init__(self):

        super(ObjCMethodDecls, self).__init__()

        self.cursor_kind = cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL

        def maybe_diagnostic(cur):
            first_line = full_text_for_cursor(cur).split('\n')[0]

            if first_line[0] == '-' and not re_method_decl.match(first_line):

                d = LintDiagnostic()
                d.line_number = cur.location.line
                d.message = "method declaration whitespace doesn't match "\
                            "template '- (Foo)barBaz:(Baz)baz'"
                d.filename = cur.location.file.name
                d.context = first_line

                return d

            return None

        self.maybe_diagnostic = maybe_diagnostic
