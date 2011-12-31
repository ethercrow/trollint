

class LintDiagnostic(object):

    def __init__(self):
        self.line_number = 0
        self.filename = ''

        self._context = u''
        self._message = u''

    def __unicode__(self):
        return u'{0}:{1}: {2}'.format(self.filename,
                                  self.line_number, self.message)

    def __eq__(self, rhs):
        return self.filename == rhs.filename \
               and self.line_number == rhs.line_number \
               and self.message == rhs.message

    def __ne__(self, rhs):
        return not (self == rhs)

    def _get_message(self):
        return self._message

    def _set_message(self, msg):
        if isinstance(msg, unicode):
            self._message = msg
        else:
            self._message = msg.decode('utf8')

    message = property(_get_message, _set_message)

    def _get_context(self):
        return self._context

    def _set_context(self, context):
        if isinstance(context, unicode):
            self._context = context
        else:
            self._context = context.decode('utf8')

    context = property(_get_context, _set_context)


def from_clang_diagnostic(cd, filename):
    result = LintDiagnostic()

    result.line_number = cd.location.line
    result.filename = cd.location.file.name if cd.location.file else filename
    result.message = cd.spelling
    result.category = 'Clang'

    if cd.location.file:
        with open(cd.location.file.name) as fi:
            result.context = fi.readlines()[cd.location.line]

    return result
