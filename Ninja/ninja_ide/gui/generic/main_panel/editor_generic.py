import re

class EditorGeneric(object):

    anyKeyEvent = []
    returnKeyEvent = []
    extraMenus = {}

    indent = 4
    patIndent = re.compile('^\s+')
    braces_strings = {"'":"'", '"':'"', '{':'}', '(':')', '[':']'}
    font_max_size = 28
    font_min_size = 6
    font_family = "Monospace"
    font_size = 11
    highlightVariables = True
    findErrors = False
    checkStyle = True
    codeCompletion = True

    def __init__(self):
        pass

    def get_indentation(self, line):
        indentation = ''
        if len(line) > 0 and line[-1] in [':', '{', '(', '[']:
            indentation = ' ' * 4
        space = self.patIndent.match(line)
        if space is not None:
            return space.group() + indentation
        return indentation

    def get_leading_spaces(self, line):
        space = self.patIndent.match(line)
        if space is not None:
            return space.group()
        return ''

    def eventKeyReturn(self):
        for plug in EditorGeneric.returnKeyEvent:
            plug.eventKeyReturn()

    def eventKeyAny(self):
        for plug in EditorGeneric.anyKeyEvent:
            plug.eventKeyAny()
