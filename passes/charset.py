
from base.regex_pass_base import LineRegexPassBase


class NonAscii(LineRegexPassBase):
    def __init__(self):

        self.name = 'Non-ASCII Characters'
        self.regex_string = r'[\x80-\xff]'
        self.message = 'Line has non-ascii characters'
