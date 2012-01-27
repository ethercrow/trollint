
from base.token_pass_base import TokenPassBase
import clang.cindex as cindex
from diagnostic import LintDiagnostic
import re
from utils import full_text_for_cursor

re_method_decl = re.compile(r'^- \([^\)]+\)\w.*$')
re_class_method_decl = re.compile(r'^\+ \([^\)]+\)\w.*$')


class ObjCMethodDecls(TokenPassBase):

    def __init__(self):

        super(ObjCMethodDecls, self).__init__()

        self.cursor_kind = cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL
        self.category = 'Style'
        self.message = ("instance method declaration whitespace doesn't match "
                        "template '- (Foo)barBaz:(Baz)baz'")
        self.regex = re_method_decl
        self.first_char = '-'


    def maybe_diagnostic(self, cur):
        first_line = full_text_for_cursor(cur).split('\n')[0]

        if first_line[0] == self.first_char and\
                not self.regex.match(first_line):

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = self.message
            d.filename = cur.location.file.name
            d.context = first_line
            d.category = self.category

            return d

        return None

class ObjCClassMethodDecls(ObjCMethodDecls):

    def __init__(self):

        super(ObjCClassMethodDecls, self).__init__()

        self.cursor_kind = cindex.CursorKind.OBJC_CLASS_METHOD_DECL
        self.message = ("class method declaration whitespace doesn't match "
                        "template '+ (Foo)barBaz:(Baz)baz'")
        self.regex = re_class_method_decl
        self.first_char = '+'

