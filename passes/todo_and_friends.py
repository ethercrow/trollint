
from base.regex_pass_base import LineRegexPassBase


class TodoAndFriends(LineRegexPassBase):
    def __init__(self):

        super(TodoAndFriends, self).__init__()

        self.regex_string = r'(\bTODO\b|\bFIXME\b|\bXXX\b)'
        self.message = 'You are not done here yet'
        self.category = 'TODO'
