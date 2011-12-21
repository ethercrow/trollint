
from base.pass_base import PassBase
from diagnostic import LintDiagnostic

class LongLines(PassBase):
    """
    Long lines reduce readability, diff-friendliness and usually look atrocious,
    especially in various web-based tools
    """

    needs = ['config', 'text', 'filename']

    def __init__(self):
        self.name = "VeryLongLines"

    def get_diagnostics(self):
        result = []
        lines = enumerate(self.text.split('\n'))
        for i, l in lines:
            if len(l) > self.config.max_line_length(default=110):
                d = LintDiagnostic()
                d.line_number = i+1
                d.message = 'Line too long'
                d.filename = self.filename
                result.append(d)
        return result
