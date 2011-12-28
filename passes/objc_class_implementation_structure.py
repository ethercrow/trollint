
import clang.cindex as cindex
from base.token_pass_base import TokenPassBase
from diagnostic import LintDiagnostic
import re

INIT_TEMPLATE = '''
    all {0} instance methods of class {1} belonging to *init* family
    should be the first {0} methods in implementation section.
'''

DEALLOC_TEMPLATE = '''
    *dealloc* method of class {0} should be the next after *init*
    family methods in implementation section
'''

class ObjCClassImplementationStructure(TokenPassBase):

    def __init__(self):

        super(ObjCClassImplementationStructure, self).__init__()

        self.cursor_kind = cindex.CursorKind.OBJC_IMPLEMENTATION_DECL
        self.category = 'Structure'
        self.re_init_decl = re.compile('^init')
        self.re_dealloc_decl = re.compile('^dealloc$')

        def maybe_diagnostic(cur):

            class_name = cur.displayname

            instance_methods = [c for c in cur.get_children() if\
                    c.kind == cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL]

            def is_init(c):
                return self.re_init_decl.search(c.displayname)

            def is_dealloc(c):
                return self.re_dealloc_decl.search(c.displayname)

            init_count = len([m for m in instance_methods if is_init(m)])

            dealloc_present = any(map(is_dealloc, instance_methods))

            these_should_be_inits = instance_methods[:init_count]

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.filename = cur.location.file.name
            d.context = ''
            d.category = self.category

            if not all(map(is_init, these_should_be_inits)):
                d.message = INIT_TEMPLATE.format(len(these_should_be_inits),
                                                 class_name)

                return d

            if dealloc_present:
                this_should_be_dealloc = instance_methods[init_count]
                if not is_dealloc(this_should_be_dealloc):
                    d.message = DEALLOC_TEMPLATE.format(class_name)
                    return d


            return None

        self.maybe_diagnostic = maybe_diagnostic
