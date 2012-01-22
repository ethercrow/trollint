
import clang.cindex as ci
from base.token_pass_base import TokenPassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor
import re


class ObjCIvarNaming(TokenPassBase):

    def __init__(self):

        super(ObjCIvarNaming, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_IVAR_DECL
        self.category = 'Naming'

        self.re_ivar_name = re.compile(r'^[a-zA-Z0-9]+_$')

    def maybe_diagnostic(self, cur):
        ivar_name = cur.displayname

        if cur.parent.kind == ci.CursorKind.OBJC_INTERFACE_DECL and\
                not self.re_ivar_name.match(ivar_name):

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = "ivar {0} is not named likeThis_"\
                    .format(cur.displayname)
            d.filename = cur.location.file.name
            d.context = cur.displayname
            d.category = self.category

            return d

        return None


class ObjCSynthesizedNaming(TokenPassBase):

    def __init__(self):

        super(ObjCSynthesizedNaming, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_SYNTHESIZE_DECL
        self.category = 'Naming'
        self.re_short_form = re.compile(r'^[a-zA-Z0-9]+$')
        self.re_long_form = re.compile(r'^([a-zA-Z0-9]+) = \1_$')
        self.re_macro_form = re.compile(r'SYNTHESIZE_IVAR\([a-zA-Z0-9]+\)')

    def maybe_diagnostic(self, cur):
        syn_statement = full_text_for_cursor(cur)
        syn_statement = syn_statement.replace('\n', '')
        syn_statement = syn_statement.replace('@synthesize ', '')
        if ',' in syn_statement:
            syn_statement = syn_statement.split(',')[-1]
        syn_statement = syn_statement.strip()

        d = LintDiagnostic()
        d.line_number = cur.location.line
        d.filename = cur.location.file.name
        d.context = '@synthesize ' + syn_statement
        d.category = self.category

        if '=' in syn_statement:
            if not self.re_long_form.match(syn_statement):
                d.message = "synthesize statement doesn't match "\
                        "template '@synthesize fooBar = fooBar_'"
                return d
        else:
            if not self.re_short_form.match(syn_statement) and\
               not self.re_macro_form.match(syn_statement):
                d.message = "synthesize statement doesn't match "\
                        "template '@synthesize fooBar'"
                return d

        return None
