
from base.pass_base import PassBase
from diagnostic import LintDiagnostic


class LongLines(PassBase):
    """
    Long lines reduce readability, diff-friendliness
    and usually look atrocious,
    especially in various web-based tools
    """

    needs = ['config', 'text', 'filename']

    def __init__(self):
        super(LongLines, self).__init__()

        # self.enabled = False
        self.category = 'Style'

    def get_diagnostics(self):
        result = []
        lines = enumerate(self.text.split('\n'))
        for i, l in lines:
            if len(l) > self.config.max_line_length(default=100):
                d = LintDiagnostic()
                d.line_number = i + 1
                d.message = 'Line too long ({0})'.format(len(l))
                d.filename = self.filename
                d.context = l.strip()
                d.category = self.category
                result.append(d)
        return result
