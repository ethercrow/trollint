
from base.regex_pass_base import LineRegexPassBase


class TrailingWhitespace(LineRegexPassBase):

    def __init__(self):

        super(TrailingWhitespace, self).__init__()

        self.enabled = False
        self.regex_string = r'\s+$'
        self.message = 'Line has trailing whitespace'
        self.category = 'Style'


class Tabs(LineRegexPassBase):

    def __init__(self):

        super(Tabs, self).__init__()

        self.regex_string = r'\t'
        self.message = 'Line has tabs'
        self.category = 'Style'
