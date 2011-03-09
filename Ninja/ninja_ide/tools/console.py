import sys
from code import InteractiveConsole

class Cache(object):

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.out = []
    
    def write(self,line):
        self.out.append(line)
    
    def flush(self):
        if len(self.out) > 1:
            output = ''.join(self.out)[:-1]
            self.reset()
            return output

class Console(InteractiveConsole):

    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self._cache = Cache()
        InteractiveConsole.__init__(self)
        self.output = ''

    def get_output(self):
        sys.stdout = self._cache
        sys.stderr = self._cache
        
    def return_output(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def push(self, line):
        if(line == 'exit()'): return
        self.get_output()
        val = InteractiveConsole.push(self, line)
        self.return_output()
        self.output = self._cache.flush()
        return val
