
import clang.cindex as ci
from base.token_pass_base import TokenPassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor
import re

# XXX: these rules are probably quite controversial
RULES = [(r'^date_?$', 'NSDate'),
         (r'[a-z](?<!display)Date_?$', 'NSDate'),
         (r'VC_?$', 'UIViewController'),
         (r'[a-z]View_?$', 'UIView'),
         (r'[a-z]Button_?$', 'UIButton'),
         (r'URL$', 'NSURL'),
         (r'^dict_?$', 'NSDictionary'),
         (r'[a-z]Dict_?$', 'NSDictionary'),
         (r'^is[A-Z]', 'BOOL'),
         (r'^as[A-Z]', 'BOOL'),
         (r'^should[A-Z]', 'BOOL'),
         ]


class ObjCNamingSanityBase(TokenPassBase):

    def __init__(self):

        super(ObjCNamingSanityBase, self).__init__()

        self.category = 'Naming'
        self.rules = [(re.compile(regex), typename)
                        for regex, typename in RULES]

    def maybe_diagnostic(self, cur):

        def get_objc_superclass(c):
            for child in c.get_children():
                if child.kind == ci.CursorKind.OBJC_SUPER_CLASS_REF:
                    return child.get_definition()

            return None

        if cur.type.kind != ci.TypeKind.OBJCOBJECTPOINTER:
            return None

        class_cursor = cur.type.get_pointee().get_declaration()
        var_name = cur.displayname

        for regex, expected_class_name in self.rules:
            if not regex.search(var_name):
                continue

            # walk objc class hierarchy trying to find
            # ancestor with name |expected_class_name|
            while class_cursor:
                class_name = class_cursor.displayname
                if class_name == expected_class_name:
                   return None
                class_cursor = get_objc_superclass(class_cursor)
            else:

                actual_class = cur.type.get_pointee().get_declaration()

                d = LintDiagnostic()
                d.line_number = cur.location.line
                d.message = self.message_template.format(cur.displayname,
                                                    actual_class.displayname,
                                                    expected_class_name)
                d.filename = cur.location.file.name
                d.context = full_text_for_cursor(cur)
                d.category = self.category

                return d

        return None


class ObjCVariableNamingSanity(ObjCNamingSanityBase):
    def __init__(self):
        super(ObjCVariableNamingSanity, self).__init__()
        self.cursor_kind = ci.CursorKind.VAR_DECL
        self.message_template = "variable {0} is declared as instance " +\
                                "of {1}, but the name implies {2}"


class ObjCIvarNamingSanity(ObjCNamingSanityBase):
    def __init__(self):
        super(ObjCIvarNamingSanity, self).__init__()
        self.cursor_kind = ci.CursorKind.OBJC_IVAR_DECL
        self.message_template = "ivar {0} is declared as instance " +\
                                "of {1}, but the name implies {2}"
