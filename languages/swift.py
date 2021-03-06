'''
Language parser for Apple Swift
'''

from lizard import CodeReader, CCppCommentsMixin


class SwiftReader(CodeReader, CCppCommentsMixin):
    # pylint: disable=R0903

    ext = ['swift']
    language_names = ['swift']

    def __init__(self, context):
        super(SwiftReader, self).__init__(context)

    def _state_global(self, token):
        if token == 'func':
            self._state = self._function_name
        if token == 'init':
            self._function_name(token)
        if token in ('get', 'set', 'deinit'):
            self.context.start_new_function(token)
            self._state = self._expect_function_impl
        if token == 'protocol':
            self._state = self._protocol

    def _function_name(self, token):
        self.context.start_new_function(token)
        self._state = self._expect_function_dec

    def _expect_function_dec(self, token):
        if token == '(':
            self._state = self._function_dec

    def _function_dec(self, token):
        if token == ')':
            self._state = self._expect_function_impl
        else:
            self.context.parameter(token)

    def _expect_function_impl(self, token):
        if token == '{':
            self._state = self._function_impl
            self._state(token)

    @CodeReader.read_inside_brackets_then("{}")
    def _function_impl(self, _):
        self._state = self._state_global
        self.context.end_of_function()

    @CodeReader.read_inside_brackets_then("{}")
    def _protocol(self, end_token):
        if end_token == "}":
            self._state = self._state_global
