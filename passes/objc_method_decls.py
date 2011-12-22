
from base.token_pass_base import TokenPassBase
import clang.cindex as cindex
import re

re_method_decl = re.compile(r'^- \([^\)]+\)\w.*$')

class ObjCMethodDecls(TokenPassBase):

    def __init__(self):

        super(ObjCMethodDecls, self).__init__()

        self.cursor_kind = cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL
        self.name = 'ObjCMethodDecls'
        self.message = 'method declaration is against convention'

        def msg(cur):
            with open(cur.location.file.name) as fi:
                token_text = fi.read()[cur.extent.start.offset:cur.extent.end.offset]

            if token_text[0] == '-' and not re_method_decl.match(token_text):
                return 'method declaration "' + cur.displayname + '" is against convention'

            return None

        self.maybe_message = msg
