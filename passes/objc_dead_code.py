
import clang.cindex as ci
from base.pass_base import PassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor

INIT_TEMPLATE = '''
    all {0} instance methods of class {1} belonging to *init* family
    should be the first {0} methods in implementation section.
'''

DEALLOC_TEMPLATE = '''
    *dealloc* method of class {0} should be the next after *init*
    family methods in implementation section
'''


class ObjCDeadIvar(PassBase):

    needs = ['cursors', 'filename']

    def __init__(self):

        super(ObjCDeadIvar, self).__init__()

        self.category = 'DeadCode'

    def get_diagnostics(self):

        local_cursors = [c for c in self.cursors\
                if c.location.file.name == self.filename]

        def is_local_category(cur):
            return cur.kind == ci.CursorKind.OBJC_CATEGORY_DECL\
               and cur.displayname == ''
        local_categories = [c for c in local_cursors if is_local_category(c)]

        class Extension(object):
            def __init__(self, class_name, ivars):
                self.class_name = class_name
                self.ivars = ivars

        exts = []
        for lc in local_categories:
            class_cursor = list(lc.get_children())[0]
            ivars = [i for i in lc.get_children()\
                    if i.kind == ci.CursorKind.OBJC_IVAR_DECL]

            exts.append(Extension(class_cursor.displayname, ivars))

        result = []
        for ext in exts:
            class_impl = [c for c in local_cursors\
                    if c.kind == ci.CursorKind.OBJC_IMPLEMENTATION_DECL and\
                       c.displayname == ext.class_name][0]

            yet_unused_ivar_names = [i.displayname for i in ext.ivars]

            def traverse(cur):
                if cur.kind == ci.CursorKind.MEMBER_REF_EXPR\
                        and cur.displayname in yet_unused_ivar_names:
                    yet_unused_ivar_names.remove(cur.displayname)

                for child in cur.get_children():
                    traverse(child)

            traverse(class_impl)

            for ivar in ext.ivars:
                if ivar.displayname in yet_unused_ivar_names:
                    d = LintDiagnostic()
                    d.category = self.category
                    d.filename = self.filename
                    d.line = ivar.location.line
                    d.context = full_text_for_cursor(ivar)
                    d.message = 'unused ivar ' + ivar.displayname
                    result.append(d)

        return result
