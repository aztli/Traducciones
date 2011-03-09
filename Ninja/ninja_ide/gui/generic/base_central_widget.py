class BaseCentralWidget(object):

    def __init__(self):
        self.textModified = False
        self._path = ''
        self._newDocument = True

    def find_match(self, word, back=False, sensitive=False, whole=False):
        pass

    def get_new_document(self):
        return self._newDocument

    def set_new_document(self, boolean):
        self._newDocument = boolean

    #tricky to allow overwrite the property!
    newDocument = property(lambda self: self.get_new_document(), lambda self, boolean: self.set_new_document(boolean))

    def get_path(self):
        return self._path

    def get_project_folder(self):
        pass

    def set_path(self, fileName):
        self._path = fileName

    #tricky to allow overwrite the property!
    path = property(lambda self: self.get_path(), lambda self, fileName: self.set_path(fileName))

    def get_text(self):
        pass

    def set_cursor_position(self, val):
        pass

    def cut(self):
        '''
        Cut action should be re-implemented
        by subclass
        '''
        pass

    def copy(self):
        '''
        Copy action should be re-implemented
        by subclass
        '''
        pass

    def paste(self):
        '''
        Paste action should be re-implemented
        by subclass
        '''
        pass

    def redo(self):
        '''
        Redo action should be re-implemented
        by subclass
        '''
        pass

    def undo(self):
       '''
        Undo action should be re-implemented
        by subclass
       '''
       pass

    def indent_more(self):
        '''
        Indent more action should be re-implemented
        by subclass
        '''
        pass

    def indent_less(self):
        '''
        Indent less action should be re-implemented
        by subclass
        '''
        pass

    def comment(self):
        '''
        Comment action should be re-implemented
        by subclass
        '''
        pass

    def uncomment(self):
        '''
        Uncomment action should be re-implemented
        by subclass
        '''
        pass

    def zoom_out(self):
        '''
        Zoom Out action should be re-implemented
        by subclass
        '''
        pass

    def zoom_in(self):
        '''
        Zoom In action should be re-implemented
        by subclass
        '''
        pass

    def insert_horizontal_line(self):
        '''
        Insert Horizontal Line action should be re-implemented
        by subclass
        '''
        pass