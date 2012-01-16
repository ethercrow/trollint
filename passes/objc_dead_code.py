
import clang.cindex as ci
from base.pass_base import PassBase
from base.token_pass_base import TokenPassBase
from diagnostic import LintDiagnostic
from utils import full_text_for_cursor


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
            def __init__(self, classname, ivars):
                self.classname = classname
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
                    c.displayname == ext.classname][0]

            ivar_usages = {i.displayname: 0 for i in ext.ivars}

            method_impls = [c for c in class_impl.get_children()\
                    if c.kind == ci.CursorKind.OBJC_INSTANCE_METHOD_DECL]

            def collect_ivar_usages(cur):
                result = set()

                def go(cur):
                    if cur.kind == ci.CursorKind.MEMBER_REF_EXPR:
                        result.add(cur.displayname)

                    for child in cur.get_children():
                        go(child)

                go(cur)

                return result

            for mi in method_impls:
                ivar_usages_in_method = collect_ivar_usages(mi)
                for usage in ivar_usages_in_method:
                    if usage in ivar_usages:
                        ivar_usages[usage] += 1

            for ivar in ext.ivars:
                if ivar_usages[ivar.displayname] == 0:
                    d = LintDiagnostic()
                    d.category = self.category
                    d.filename = self.filename
                    d.line = ivar.location.line
                    d.context = full_text_for_cursor(ivar)
                    d.message = 'unused ivar ' + ivar.displayname
                    result.append(d)
                elif ivar_usages[ivar.displayname] == 1:
                    d = LintDiagnostic()
                    d.category = self.category
                    d.filename = self.filename
                    d.line = ivar.location.line
                    d.context = full_text_for_cursor(ivar)
                    d.message = 'ivar {0} is used in only one method'.format(
                            ivar.displayname)
                    result.append(d)

        return result


class ObjCDeadPrivateMethod(PassBase):

    needs = ['cursors', 'filename']

    def __init__(self):

        super(ObjCDeadPrivateMethod, self).__init__()

        self.category = 'DeadCode'

    def get_diagnostics(self):

        local_cursors = [c for c in self.cursors\
                if c.location.file.name == self.filename]

        def is_local_category(cur):
            return cur.kind == ci.CursorKind.OBJC_CATEGORY_DECL\
               and cur.displayname == ''
        local_categories = [c for c in local_cursors if is_local_category(c)]

        class Extension(object):
            def __init__(self, filename, methods):
                self.filename = filename
                self.methods = methods

        exts = []
        for lc in local_categories:
            class_cursor = list(lc.get_children())[0]
            ivars = [i for i in lc.get_children()\
                    if i.kind == ci.CursorKind.OBJC_INSTANCE_METHOD_DECL]

            exts.append(Extension(class_cursor.displayname, ivars))

        result = []
        for ext in exts:
            class_impls = [c for c in local_cursors\
                    if c.kind == ci.CursorKind.OBJC_IMPLEMENTATION_DECL and\
                       c.displayname == ext.filename]

            yet_unused_method_names = [i.displayname for i in ext.methods]

            def traverse(cur):
                if cur.kind == ci.CursorKind.OBJC_MESSAGE_EXPR\
                        and cur.displayname in yet_unused_method_names:
                    yet_unused_method_names.remove(cur.displayname)

                if cur.kind == ci.CursorKind.OBJC_SELECTOR_EXPR:
                    # '@selector(foo)' -> 'foo'
                    selector_name = full_text_for_cursor(cur)[10:-1]

                    if selector_name in yet_unused_method_names:
                        yet_unused_method_names.remove(selector_name)

                if not yet_unused_method_names:
                    return

                for child in cur.get_children():
                    traverse(child)

            for class_impl in class_impls:
                traverse(class_impl)

            for method in ext.methods:
                if method.displayname in yet_unused_method_names:
                    d = LintDiagnostic()
                    d.category = self.category
                    d.filename = self.filename
                    d.line = method.location.line
                    d.context = full_text_for_cursor(method)
                    d.message = 'unused method ' + method.displayname
                    result.append(d)

        return result


class ObjCEmptyMethods(TokenPassBase):

    def __init__(self):

        super(ObjCEmptyMethods, self).__init__()

        self.cursor_kind = ci.CursorKind.OBJC_INSTANCE_METHOD_DECL
        self.category = 'DeadCode'

    def maybe_diagnostic(self, cur):

        compound = None
        for c in cur.get_children():
            if c.kind == ci.CursorKind.COMPOUND_STMT:
                compound = c

        if not compound:
            return []

        children = list(compound.get_children())
        if not children:

            d = LintDiagnostic()
            d.line_number = cur.location.line
            d.message = "method {0} has empty implementation"\
                    .format(cur.displayname)
            d.filename = cur.location.file.name
            d.context = cur.displayname
            d.category = self.category

            return d

        elif len(children) == 1:

            only_statement = children[0]
            if only_statement.kind == ci.CursorKind.OBJC_MESSAGE_EXPR\
                    and only_statement.displayname == cur.displayname\
                    and '[super ' == full_text_for_cursor(only_statement)[0:7]:

                # TODO: verify that all parameters are passed through unchanged

                d = LintDiagnostic()
                d.line_number = cur.location.line
                d.message = "method {0} only calls super implementation"\
                        .format(cur.displayname)
                d.filename = cur.location.file.name
                d.context = cur.displayname
                d.category = self.category

                return d

        return None
