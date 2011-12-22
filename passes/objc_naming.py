
from base.token_regex_pass_base import TokenRegexPassBase
import clang.cindex as cindex

class ObjCNaming(TokenRegexPassBase):

    def __init__(self):

        super(ObjCNaming, self).__init__()

        self.name = 'ObjCNaming'
        self.message = 'ivar name "{cur.displayname}" is against convention'
        self.regex_string = r'^[a-zA-Z0-9]+_$'
        self.cursor_kind = cindex.CursorKind.OBJC_IVAR_DECL
