from __future__ import absolute_import

from ninja_ide.tools import Console

class ConsoleGeneric(object):

    def __init__(self):
        self._console = Console()
        self.prompt = '>>> '
        self.history = []

    def write(self, line):
        return self._console.push(line)

    def read(self):
        return self._console.output

    def add_history(self, command):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

    def get_prev_history_entry(self):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            return self.history[self.history_index]
        return ''

    def get_next_history_entry(self):
        if self.history:
            hist_len = len(self.history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self.history[self.history_index]
        return ''
